# app/models/descuento_model.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.db.database import Base

class TipoDescuento(str, PyEnum):
    """Tipos de descuentos disponibles"""
    PORCENTAJE = "porcentaje"
    MONTO_FIJO = "monto_fijo"
    DESCUENTO_VOLUMEN = "descuento_volumen"
    DESCUENTO_CLIENTE = "descuento_cliente"
    PROMOCION_TEMPORAL = "promocion_temporal"

class EstadoDescuento(str, PyEnum):
    """Estados de los descuentos"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    EXPIRADO = "expirado"
    AGOTADO = "agotado"

class Descuento(Base):
    __tablename__ = "descuentos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Configuración del descuento
    tipo = Column(String(50), nullable=False, index=True)
    valor = Column(Float, nullable=False)  # Porcentaje o monto fijo
    valor_minimo = Column(Float, nullable=True)  # Compra mínima para aplicar
    valor_maximo = Column(Float, nullable=True)  # Descuento máximo aplicable
    
    # Límites y restricciones
    limite_usos = Column(Integer, nullable=True)  # Límite total de usos
    usos_por_cliente = Column(Integer, nullable=True)  # Límite por cliente
    usos_actuales = Column(Integer, default=0)  # Usos realizados
    
    # Fechas
    fecha_inicio = Column(DateTime, nullable=False, index=True)
    fecha_fin = Column(DateTime, nullable=True, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Estado y configuración
    estado = Column(String(20), default=EstadoDescuento.ACTIVO.value, index=True)
    es_activo = Column(Boolean, default=True, index=True)
    aplica_envio = Column(Boolean, default=False)  # Si aplica a envío
    aplica_impuestos = Column(Boolean, default=True)  # Si se aplica antes o después de impuestos
    
    # Restricciones por producto/cliente
    productos_ids = Column(Text, nullable=True)  # JSON con IDs de productos específicos
    clientes_ids = Column(Text, nullable=True)  # JSON con IDs de clientes específicos
    categorias_ids = Column(Text, nullable=True)  # JSON con IDs de categorías
    
    # Metadatos
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    notas_internas = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Descuento(id={self.id}, codigo='{self.codigo}', tipo='{self.tipo}')>"

class DescuentoUso(Base):
    __tablename__ = "descuento_usos"

    id = Column(Integer, primary_key=True, index=True)
    descuento_id = Column(Integer, ForeignKey("descuentos.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True, index=True)
    
    # Detalles del uso
    monto_original = Column(Float, nullable=False)
    monto_descuento = Column(Float, nullable=False)
    monto_final = Column(Float, nullable=False)
    
    # Metadatos
    fecha_uso = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_cliente = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relaciones
    descuento = relationship("Descuento", backref="usos")
    cliente = relationship("Cliente", backref="descuentos_usados")
    venta = relationship("Venta", backref="descuentos_aplicados")
    
    def __repr__(self):
        return f"<DescuentoUso(id={self.id}, descuento_id={self.descuento_id}, monto_descuento={self.monto_descuento})>"

class Promocion(Base):
    __tablename__ = "promociones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Configuración
    tipo = Column(Enum(TipoDescuento), nullable=False)
    valor = Column(Float, nullable=False)
    condicion_minima = Column(Float, nullable=True)  # Condición mínima para aplicar
    
    # Fechas
    fecha_inicio = Column(DateTime, nullable=False, index=True)
    fecha_fin = Column(DateTime, nullable=True, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Estado
    estado = Column(String(20), default=EstadoDescuento.ACTIVO.value, index=True)
    es_activo = Column(Boolean, default=True, index=True)
    
    # Restricciones
    productos_ids = Column(Text, nullable=True)  # JSON con IDs de productos
    clientes_ids = Column(Text, nullable=True)  # JSON con IDs de clientes
    
    # Metadatos
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    def __repr__(self):
        return f"<Promocion(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}')>"
