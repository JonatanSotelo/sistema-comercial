# app/models/inventario_model.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.db.database import Base

class TipoAlertaInventario(str, PyEnum):
    """Tipos de alertas de inventario"""
    STOCK_BAJO = "stock_bajo"
    STOCK_CRITICO = "stock_critico"
    STOCK_AGOTADO = "stock_agotado"
    REORDEN_URGENTE = "reorden_urgente"
    VENCIMIENTO_PROXIMO = "vencimiento_proximo"
    VENCIMIENTO_VENCIDO = "vencimiento_vencido"
    MOVIMIENTO_SOSPECHOSO = "movimiento_sospechoso"

class EstadoAlerta(str, PyEnum):
    """Estados de las alertas"""
    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    RESUELTA = "resuelta"
    IGNORADA = "ignorada"

class ConfiguracionInventario(Base):
    __tablename__ = "configuracion_inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, unique=True, index=True)
    
    # Configuración de stock
    stock_minimo = Column(Float, nullable=False, default=0.0)
    stock_maximo = Column(Float, nullable=True)
    punto_reorden = Column(Float, nullable=True)  # Cuando reordenar automáticamente
    cantidad_reorden = Column(Float, nullable=True)  # Cuánto reordenar
    
    # Configuración de alertas
    alerta_stock_bajo = Column(Boolean, default=True)
    alerta_stock_critico = Column(Boolean, default=True)
    alerta_vencimiento = Column(Boolean, default=True)
    dias_vencimiento_alerta = Column(Integer, default=30)  # Días antes del vencimiento
    
    # Configuración de movimiento
    alerta_movimiento_grande = Column(Boolean, default=True)
    umbral_movimiento_grande = Column(Float, nullable=True)  # % de cambio para alertar
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Boolean, default=True, index=True)
    
    # Relaciones
    producto = relationship("Producto", backref="configuracion_inventario")
    
    def __repr__(self):
        return f"<ConfiguracionInventario(id={self.id}, producto_id={self.producto_id}, stock_minimo={self.stock_minimo})>"

class AlertaInventario(Base):
    __tablename__ = "alertas_inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    tipo = Column(Enum(TipoAlertaInventario), nullable=False, index=True)
    estado = Column(Enum(EstadoAlerta), default=EstadoAlerta.PENDIENTE, index=True)
    
    # Detalles de la alerta
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)
    prioridad = Column(Integer, default=1, index=True)  # 1=alta, 2=media, 3=baja
    
    # Valores relacionados
    stock_actual = Column(Float, nullable=True)
    stock_minimo = Column(Float, nullable=True)
    stock_critico = Column(Float, nullable=True)
    dias_vencimiento = Column(Integer, nullable=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    fecha_resolucion = Column(DateTime, nullable=True)
    resuelta_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    notas_resolucion = Column(Text, nullable=True)
    
    # Relaciones
    producto = relationship("Producto", backref="alertas_inventario")
    resolutor = relationship("User", backref="alertas_resueltas")
    
    def __repr__(self):
        return f"<AlertaInventario(id={self.id}, tipo='{self.tipo}', estado='{self.estado}')>"

class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    
    # Detalles del movimiento
    tipo_movimiento = Column(String(50), nullable=False, index=True)  # 'entrada', 'salida', 'ajuste'
    cantidad = Column(Float, nullable=False)
    cantidad_anterior = Column(Float, nullable=False)
    cantidad_nueva = Column(Float, nullable=False)
    
    # Referencias
    referencia_tipo = Column(String(50), nullable=True)  # 'compra', 'venta', 'ajuste', 'transferencia'
    referencia_id = Column(Integer, nullable=True)  # ID de la compra/venta/etc.
    
    # Metadatos
    fecha_movimiento = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    motivo = Column(Text, nullable=True)
    costo_unitario = Column(Float, nullable=True)
    costo_total = Column(Float, nullable=True)
    
    # Relaciones
    producto = relationship("Producto", backref="movimientos_inventario")
    usuario = relationship("User", backref="movimientos_inventario")
    
    def __repr__(self):
        return f"<MovimientoInventario(id={self.id}, producto_id={self.producto_id}, tipo='{self.tipo_movimiento}', cantidad={self.cantidad})>"

class ReordenAutomatico(Base):
    __tablename__ = "reorden_automatico"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True, index=True)
    
    # Configuración del reorden
    cantidad_sugerida = Column(Float, nullable=False)
    costo_estimado = Column(Float, nullable=True)
    fecha_sugerida = Column(DateTime, nullable=False, index=True)
    
    # Estado del reorden
    estado = Column(String(20), default="pendiente", index=True)  # 'pendiente', 'aprobado', 'rechazado', 'completado'
    aprobado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_aprobacion = Column(DateTime, nullable=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    notas = Column(Text, nullable=True)
    
    # Relaciones
    producto = relationship("Producto", backref="reordenes_automaticos")
    proveedor = relationship("Proveedor", backref="reordenes_automaticos")
    aprobador = relationship("User", backref="reordenes_aprobados")
    
    def __repr__(self):
        return f"<ReordenAutomatico(id={self.id}, producto_id={self.producto_id}, cantidad={self.cantidad_sugerida}, estado='{self.estado}')>"
