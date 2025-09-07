# app/models/proveedor_integracion_model.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum as PyEnum
from app.db.database import Base

class TipoIntegracion(str, PyEnum):
    """Tipos de integración con proveedores"""
    API_REST = "api_rest"
    API_SOAP = "api_soap"
    FTP = "ftp"
    EMAIL = "email"
    MANUAL = "manual"
    WEBHOOK = "webhook"

class EstadoIntegracion(str, PyEnum):
    """Estados de integración"""
    ACTIVA = "activa"
    INACTIVA = "inactiva"
    ERROR = "error"
    CONFIGURANDO = "configurando"
    TESTING = "testing"

class TipoSincronizacion(str, PyEnum):
    """Tipos de sincronización"""
    AUTOMATICA = "automatica"
    MANUAL = "manual"
    PROGRAMADA = "programada"
    EVENTO = "evento"

class EstadoPedido(str, PyEnum):
    """Estados de pedidos a proveedores"""
    PENDIENTE = "pendiente"
    ENVIADO = "enviado"
    CONFIRMADO = "confirmado"
    EN_PROCESO = "en_proceso"
    DESPACHADO = "despachado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"
    DEVUELTO = "devuelto"

class ProveedorIntegracion(Base):
    __tablename__ = "proveedores_integracion"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False, index=True)
    
    # Configuración de integración
    tipo_integracion = Column(String(50), nullable=False, index=True)
    estado = Column(String(20), default=EstadoIntegracion.CONFIGURANDO.value, index=True)
    nombre_integracion = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Configuración técnica
    endpoint_url = Column(String(500), nullable=True)
    api_key = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    headers = Column(JSON, nullable=True)  # Headers personalizados
    parametros = Column(JSON, nullable=True)  # Parámetros de configuración
    
    # Configuración de sincronización
    tipo_sincronizacion = Column(String(20), default=TipoSincronizacion.MANUAL.value, index=True)
    frecuencia_sincronizacion = Column(Integer, nullable=True)  # En minutos
    hora_sincronizacion = Column(String(10), nullable=True)  # HH:MM
    dias_sincronizacion = Column(JSON, nullable=True)  # Días de la semana [1,2,3,4,5]
    
    # Configuración de productos
    sincronizar_productos = Column(Boolean, default=True)
    sincronizar_precios = Column(Boolean, default=True)
    sincronizar_stock = Column(Boolean, default=True)
    sincronizar_categorias = Column(Boolean, default=True)
    
    # Configuración de pedidos
    permitir_pedidos_automaticos = Column(Boolean, default=False)
    pedido_minimo = Column(Float, nullable=True)
    tiempo_entrega_dias = Column(Integer, nullable=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_sincronizacion = Column(DateTime, nullable=True)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Estadísticas
    total_sincronizaciones = Column(Integer, default=0)
    sincronizaciones_exitosas = Column(Integer, default=0)
    sincronizaciones_fallidas = Column(Integer, default=0)
    ultimo_error = Column(Text, nullable=True)
    
    # Relaciones
    proveedor = relationship("Proveedor", backref="integraciones")
    creador = relationship("User", backref="integraciones_creadas")
    
    def __repr__(self):
        return f"<ProveedorIntegracion(id={self.id}, proveedor_id={self.proveedor_id}, tipo='{self.tipo_integracion}')>"

class CatalogoProveedor(Base):
    __tablename__ = "catalogos_proveedor"

    id = Column(Integer, primary_key=True, index=True)
    integracion_id = Column(Integer, ForeignKey("proveedores_integracion.id"), nullable=False, index=True)
    
    # Identificación del producto en el proveedor
    codigo_proveedor = Column(String(255), nullable=False, index=True)
    nombre_proveedor = Column(String(255), nullable=False)
    descripcion_proveedor = Column(Text, nullable=True)
    
    # Mapeo con productos internos
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=True, index=True)
    mapeo_automatico = Column(Boolean, default=False)
    confianza_mapeo = Column(Float, nullable=True)  # 0.0 a 1.0
    
    # Información del producto
    categoria_proveedor = Column(String(255), nullable=True)
    marca_proveedor = Column(String(255), nullable=True)
    modelo_proveedor = Column(String(255), nullable=True)
    sku_proveedor = Column(String(255), nullable=True)
    
    # Precios y disponibilidad
    precio_proveedor = Column(Float, nullable=True)
    precio_anterior = Column(Float, nullable=True)
    stock_proveedor = Column(Integer, nullable=True)
    stock_anterior = Column(Integer, nullable=True)
    disponible = Column(Boolean, default=True, index=True)
    
    # Configuración de sincronización
    sincronizar_precio = Column(Boolean, default=True)
    sincronizar_stock = Column(Boolean, default=True)
    margen_minimo = Column(Float, nullable=True)  # Margen mínimo para actualizar precio
    stock_minimo = Column(Integer, nullable=True)  # Stock mínimo para alertas
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_sincronizacion = Column(DateTime, nullable=True)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, index=True)
    
    # Relaciones
    integracion = relationship("ProveedorIntegracion", backref="catalogos")
    producto = relationship("Producto", backref="catalogos_proveedor")
    
    def __repr__(self):
        return f"<CatalogoProveedor(id={self.id}, codigo_proveedor='{self.codigo_proveedor}', producto_id={self.producto_id})>"

class PedidoProveedor(Base):
    __tablename__ = "pedidos_proveedor"

    id = Column(Integer, primary_key=True, index=True)
    integracion_id = Column(Integer, ForeignKey("proveedores_integracion.id"), nullable=False, index=True)
    
    # Identificación del pedido
    numero_pedido_proveedor = Column(String(255), nullable=True, index=True)
    numero_pedido_interno = Column(String(255), nullable=False, index=True)
    estado = Column(String(20), default=EstadoPedido.PENDIENTE.value, index=True)
    
    # Información del pedido
    fecha_pedido = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega_estimada = Column(DateTime, nullable=True)
    fecha_entrega_real = Column(DateTime, nullable=True)
    
    # Totales
    subtotal = Column(Float, nullable=False, default=0.0)
    descuento = Column(Float, nullable=False, default=0.0)
    impuestos = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    
    # Configuración
    tipo_pedido = Column(String(50), default="manual")  # manual, automatico, programado
    prioridad = Column(String(20), default="normal")  # baja, normal, alta, urgente
    observaciones = Column(Text, nullable=True)
    
    # Metadatos
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    procesado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    integracion = relationship("ProveedorIntegracion", backref="pedidos")
    creador = relationship("User", foreign_keys=[creado_por], backref="pedidos_creados")
    procesador = relationship("User", foreign_keys=[procesado_por], backref="pedidos_procesados")
    items = relationship("PedidoProveedorItem", backref="pedido", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PedidoProveedor(id={self.id}, numero_interno='{self.numero_pedido_interno}', estado='{self.estado}')>"

class PedidoProveedorItem(Base):
    __tablename__ = "pedidos_proveedor_items"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_proveedor.id"), nullable=False, index=True)
    catalogo_id = Column(Integer, ForeignKey("catalogos_proveedor.id"), nullable=False, index=True)
    
    # Información del producto
    codigo_proveedor = Column(String(255), nullable=False)
    nombre_producto = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Cantidades
    cantidad_solicitada = Column(Integer, nullable=False)
    cantidad_confirmada = Column(Integer, nullable=True)
    cantidad_recibida = Column(Integer, nullable=True)
    cantidad_pendiente = Column(Integer, nullable=True)
    
    # Precios
    precio_unitario = Column(Float, nullable=False)
    descuento_unitario = Column(Float, nullable=False, default=0.0)
    precio_total = Column(Float, nullable=False)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    catalogo = relationship("CatalogoProveedor", backref="items_pedidos")
    
    def __repr__(self):
        return f"<PedidoProveedorItem(id={self.id}, pedido_id={self.pedido_id}, cantidad={self.cantidad_solicitada})>"

class NotificacionProveedor(Base):
    __tablename__ = "notificaciones_proveedor"

    id = Column(Integer, primary_key=True, index=True)
    integracion_id = Column(Integer, ForeignKey("proveedores_integracion.id"), nullable=False, index=True)
    
    # Información de la notificación
    tipo = Column(String(50), nullable=False, index=True)  # precio, stock, pedido, error, info
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)
    prioridad = Column(String(20), default="normal")  # baja, normal, alta, urgente
    
    # Estado
    leida = Column(Boolean, default=False, index=True)
    procesada = Column(Boolean, default=False, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_lectura = Column(DateTime, nullable=True)
    fecha_procesamiento = Column(DateTime, nullable=True)
    
    # Datos adicionales
    datos_adicionales = Column(JSON, nullable=True)
    accion_requerida = Column(String(255), nullable=True)
    usuario_asignado = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relaciones
    integracion = relationship("ProveedorIntegracion", backref="notificaciones")
    usuario = relationship("User", backref="notificaciones_proveedor")
    
    def __repr__(self):
        return f"<NotificacionProveedor(id={self.id}, tipo='{self.tipo}', titulo='{self.titulo}')>"

class LogIntegracion(Base):
    __tablename__ = "logs_integracion"

    id = Column(Integer, primary_key=True, index=True)
    integracion_id = Column(Integer, ForeignKey("proveedores_integracion.id"), nullable=False, index=True)
    
    # Información del log
    tipo_operacion = Column(String(50), nullable=False, index=True)  # sincronizacion, pedido, error, info
    nivel = Column(String(20), nullable=False, index=True)  # debug, info, warning, error, critical
    mensaje = Column(Text, nullable=False)
    
    # Detalles técnicos
    endpoint = Column(String(500), nullable=True)
    metodo_http = Column(String(10), nullable=True)
    codigo_respuesta = Column(Integer, nullable=True)
    tiempo_respuesta_ms = Column(Integer, nullable=True)
    
    # Datos de la operación
    datos_enviados = Column(JSON, nullable=True)
    datos_recibidos = Column(JSON, nullable=True)
    error_detalle = Column(Text, nullable=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relaciones
    integracion = relationship("ProveedorIntegracion", backref="logs")
    usuario = relationship("User", backref="logs_integracion")
    
    def __repr__(self):
        return f"<LogIntegracion(id={self.id}, tipo='{self.tipo_operacion}', nivel='{self.nivel}')>"

class ConfiguracionIntegracion(Base):
    __tablename__ = "configuraciones_integracion"

    id = Column(Integer, primary_key=True, index=True)
    integracion_id = Column(Integer, ForeignKey("proveedores_integracion.id"), nullable=False, index=True)
    
    # Configuración general
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    valor = Column(Text, nullable=False)
    tipo_valor = Column(String(50), nullable=False)  # string, integer, float, boolean, json
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Relaciones
    integracion = relationship("ProveedorIntegracion", backref="configuraciones")
    creador = relationship("User", backref="configuraciones_integracion")
    
    def __repr__(self):
        return f"<ConfiguracionIntegracion(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo_valor}')>"

