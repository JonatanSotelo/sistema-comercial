# app/schemas/proveedor_integracion_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from app.models.proveedor_integracion_model import TipoIntegracion, EstadoIntegracion, TipoSincronizacion, EstadoPedido

# === ESQUEMAS BASE ===

class ProveedorIntegracionBase(BaseModel):
    """Esquema base para integraciones con proveedores"""
    proveedor_id: int = Field(..., description="ID del proveedor")
    tipo_integracion: TipoIntegracion = Field(..., description="Tipo de integración")
    nombre_integracion: str = Field(..., max_length=255, description="Nombre de la integración")
    descripcion: Optional[str] = Field(None, description="Descripción de la integración")
    endpoint_url: Optional[str] = Field(None, max_length=500, description="URL del endpoint")
    api_key: Optional[str] = Field(None, max_length=255, description="API Key")
    username: Optional[str] = Field(None, max_length=255, description="Usuario")
    password: Optional[str] = Field(None, max_length=255, description="Contraseña")
    headers: Optional[Dict[str, Any]] = Field(None, description="Headers personalizados")
    parametros: Optional[Dict[str, Any]] = Field(None, description="Parámetros de configuración")
    tipo_sincronizacion: TipoSincronizacion = Field(TipoSincronizacion.MANUAL, description="Tipo de sincronización")
    frecuencia_sincronizacion: Optional[int] = Field(None, ge=1, le=1440, description="Frecuencia en minutos")
    hora_sincronizacion: Optional[str] = Field(None, description="Hora de sincronización (HH:MM)")
    dias_sincronizacion: Optional[List[int]] = Field(None, description="Días de la semana [1-7]")
    sincronizar_productos: bool = Field(True, description="Sincronizar productos")
    sincronizar_precios: bool = Field(True, description="Sincronizar precios")
    sincronizar_stock: bool = Field(True, description="Sincronizar stock")
    sincronizar_categorias: bool = Field(True, description="Sincronizar categorías")
    permitir_pedidos_automaticos: bool = Field(False, description="Permitir pedidos automáticos")
    pedido_minimo: Optional[float] = Field(None, ge=0, description="Pedido mínimo")
    tiempo_entrega_dias: Optional[int] = Field(None, ge=1, description="Tiempo de entrega en días")

    @validator('hora_sincronizacion')
    def validar_hora_sincronizacion(cls, v):
        if v and not v.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'):
            raise ValueError('Hora debe estar en formato HH:MM')
        return v

    @validator('dias_sincronizacion')
    def validar_dias_sincronizacion(cls, v):
        if v:
            for dia in v:
                if dia < 1 or dia > 7:
                    raise ValueError('Días deben estar entre 1 y 7')
        return v

class ProveedorIntegracionCreate(ProveedorIntegracionBase):
    """Esquema para crear integraciones con proveedores"""
    pass

class ProveedorIntegracionUpdate(BaseModel):
    """Esquema para actualizar integraciones con proveedores"""
    nombre_integracion: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    endpoint_url: Optional[str] = Field(None, max_length=500)
    api_key: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, max_length=255)
    headers: Optional[Dict[str, Any]] = None
    parametros: Optional[Dict[str, Any]] = None
    tipo_sincronizacion: Optional[TipoSincronizacion] = None
    frecuencia_sincronizacion: Optional[int] = Field(None, ge=1, le=1440)
    hora_sincronizacion: Optional[str] = None
    dias_sincronizacion: Optional[List[int]] = None
    sincronizar_productos: Optional[bool] = None
    sincronizar_precios: Optional[bool] = None
    sincronizar_stock: Optional[bool] = None
    sincronizar_categorias: Optional[bool] = None
    permitir_pedidos_automaticos: Optional[bool] = None
    pedido_minimo: Optional[float] = Field(None, ge=0)
    tiempo_entrega_dias: Optional[int] = Field(None, ge=1)
    activo: Optional[bool] = None

class ProveedorIntegracionOut(ProveedorIntegracionBase):
    """Esquema de salida para integraciones con proveedores"""
    id: int
    estado: EstadoIntegracion
    fecha_creacion: datetime
    fecha_ultima_sincronizacion: Optional[datetime] = None
    fecha_ultima_actualizacion: datetime
    creado_por: Optional[int] = None
    activo: bool
    total_sincronizaciones: int
    sincronizaciones_exitosas: int
    sincronizaciones_fallidas: int
    ultimo_error: Optional[str] = None
    
    class Config:
        from_attributes = True

# === CATÁLOGO DE PROVEEDOR ===

class CatalogoProveedorBase(BaseModel):
    """Esquema base para catálogo de proveedor"""
    codigo_proveedor: str = Field(..., max_length=255, description="Código del producto en el proveedor")
    nombre_proveedor: str = Field(..., max_length=255, description="Nombre del producto en el proveedor")
    descripcion_proveedor: Optional[str] = Field(None, description="Descripción del producto")
    categoria_proveedor: Optional[str] = Field(None, max_length=255, description="Categoría del proveedor")
    marca_proveedor: Optional[str] = Field(None, max_length=255, description="Marca del proveedor")
    modelo_proveedor: Optional[str] = Field(None, max_length=255, description="Modelo del proveedor")
    sku_proveedor: Optional[str] = Field(None, max_length=255, description="SKU del proveedor")
    precio_proveedor: Optional[float] = Field(None, ge=0, description="Precio del proveedor")
    stock_proveedor: Optional[int] = Field(None, ge=0, description="Stock del proveedor")
    disponible: bool = Field(True, description="Disponibilidad del producto")
    sincronizar_precio: bool = Field(True, description="Sincronizar precio")
    sincronizar_stock: bool = Field(True, description="Sincronizar stock")
    margen_minimo: Optional[float] = Field(None, ge=0, description="Margen mínimo para actualizar precio")
    stock_minimo: Optional[int] = Field(None, ge=0, description="Stock mínimo para alertas")

class CatalogoProveedorCreate(CatalogoProveedorBase):
    """Esquema para crear catálogo de proveedor"""
    integracion_id: int = Field(..., description="ID de la integración")
    producto_id: Optional[int] = Field(None, description="ID del producto interno")
    mapeo_automatico: bool = Field(False, description="Mapeo automático con producto interno")

class CatalogoProveedorUpdate(BaseModel):
    """Esquema para actualizar catálogo de proveedor"""
    nombre_proveedor: Optional[str] = Field(None, max_length=255)
    descripcion_proveedor: Optional[str] = None
    categoria_proveedor: Optional[str] = Field(None, max_length=255)
    marca_proveedor: Optional[str] = Field(None, max_length=255)
    modelo_proveedor: Optional[str] = Field(None, max_length=255)
    sku_proveedor: Optional[str] = Field(None, max_length=255)
    precio_proveedor: Optional[float] = Field(None, ge=0)
    stock_proveedor: Optional[int] = Field(None, ge=0)
    disponible: Optional[bool] = None
    sincronizar_precio: Optional[bool] = None
    sincronizar_stock: Optional[bool] = None
    margen_minimo: Optional[float] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    producto_id: Optional[int] = None
    mapeo_automatico: Optional[bool] = None

class CatalogoProveedorOut(CatalogoProveedorBase):
    """Esquema de salida para catálogo de proveedor"""
    id: int
    integracion_id: int
    producto_id: Optional[int] = None
    mapeo_automatico: bool
    confianza_mapeo: Optional[float] = None
    precio_anterior: Optional[float] = None
    stock_anterior: Optional[int] = None
    fecha_creacion: datetime
    fecha_ultima_sincronizacion: Optional[datetime] = None
    fecha_ultima_actualizacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True

# === PEDIDOS A PROVEEDORES ===

class PedidoProveedorItemBase(BaseModel):
    """Esquema base para items de pedido a proveedor"""
    catalogo_id: int = Field(..., description="ID del catálogo del proveedor")
    codigo_proveedor: str = Field(..., max_length=255, description="Código del producto en el proveedor")
    nombre_producto: str = Field(..., max_length=255, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    cantidad_solicitada: int = Field(..., ge=1, description="Cantidad solicitada")
    precio_unitario: float = Field(..., ge=0, description="Precio unitario")
    descuento_unitario: float = Field(0.0, ge=0, description="Descuento unitario")

class PedidoProveedorItemCreate(PedidoProveedorItemBase):
    """Esquema para crear items de pedido a proveedor"""
    pass

class PedidoProveedorItemOut(PedidoProveedorItemBase):
    """Esquema de salida para items de pedido a proveedor"""
    id: int
    pedido_id: int
    cantidad_confirmada: Optional[int] = None
    cantidad_recibida: Optional[int] = None
    cantidad_pendiente: Optional[int] = None
    precio_total: float
    fecha_creacion: datetime
    fecha_ultima_actualizacion: datetime
    
    class Config:
        from_attributes = True

class PedidoProveedorBase(BaseModel):
    """Esquema base para pedidos a proveedores"""
    numero_pedido_interno: str = Field(..., max_length=255, description="Número de pedido interno")
    fecha_entrega_estimada: Optional[datetime] = Field(None, description="Fecha de entrega estimada")
    tipo_pedido: str = Field("manual", description="Tipo de pedido")
    prioridad: str = Field("normal", description="Prioridad del pedido")
    observaciones: Optional[str] = Field(None, description="Observaciones del pedido")
    items: List[PedidoProveedorItemCreate] = Field(..., min_items=1, description="Items del pedido")

    @validator('prioridad')
    def validar_prioridad(cls, v):
        prioridades_validas = ['baja', 'normal', 'alta', 'urgente']
        if v not in prioridades_validas:
            raise ValueError(f'Prioridad debe ser una de: {prioridades_validas}')
        return v

    @validator('tipo_pedido')
    def validar_tipo_pedido(cls, v):
        tipos_validos = ['manual', 'automatico', 'programado']
        if v not in tipos_validos:
            raise ValueError(f'Tipo de pedido debe ser uno de: {tipos_validos}')
        return v

class PedidoProveedorCreate(PedidoProveedorBase):
    """Esquema para crear pedidos a proveedores"""
    integracion_id: int = Field(..., description="ID de la integración")

class PedidoProveedorUpdate(BaseModel):
    """Esquema para actualizar pedidos a proveedores"""
    estado: Optional[EstadoPedido] = None
    fecha_entrega_estimada: Optional[datetime] = None
    fecha_entrega_real: Optional[datetime] = None
    observaciones: Optional[str] = None
    prioridad: Optional[str] = None

class PedidoProveedorOut(PedidoProveedorBase):
    """Esquema de salida para pedidos a proveedores"""
    id: int
    integracion_id: int
    numero_pedido_proveedor: Optional[str] = None
    estado: EstadoPedido
    fecha_pedido: datetime
    fecha_entrega_real: Optional[datetime] = None
    subtotal: float
    descuento: float
    impuestos: float
    total: float
    creado_por: Optional[int] = None
    procesado_por: Optional[int] = None
    fecha_creacion: datetime
    fecha_ultima_actualizacion: datetime
    items: List[PedidoProveedorItemOut] = []
    
    class Config:
        from_attributes = True

# === NOTIFICACIONES DE PROVEEDORES ===

class NotificacionProveedorBase(BaseModel):
    """Esquema base para notificaciones de proveedores"""
    tipo: str = Field(..., description="Tipo de notificación")
    titulo: str = Field(..., max_length=255, description="Título de la notificación")
    mensaje: str = Field(..., description="Mensaje de la notificación")
    prioridad: str = Field("normal", description="Prioridad de la notificación")
    datos_adicionales: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")
    accion_requerida: Optional[str] = Field(None, max_length=255, description="Acción requerida")

    @validator('tipo')
    def validar_tipo(cls, v):
        tipos_validos = ['precio', 'stock', 'pedido', 'error', 'info']
        if v not in tipos_validos:
            raise ValueError(f'Tipo debe ser uno de: {tipos_validos}')
        return v

    @validator('prioridad')
    def validar_prioridad(cls, v):
        prioridades_validas = ['baja', 'normal', 'alta', 'urgente']
        if v not in prioridades_validas:
            raise ValueError(f'Prioridad debe ser una de: {prioridades_validas}')
        return v

class NotificacionProveedorCreate(NotificacionProveedorBase):
    """Esquema para crear notificaciones de proveedores"""
    integracion_id: int = Field(..., description="ID de la integración")
    usuario_asignado: Optional[int] = Field(None, description="Usuario asignado")

class NotificacionProveedorUpdate(BaseModel):
    """Esquema para actualizar notificaciones de proveedores"""
    leida: Optional[bool] = None
    procesada: Optional[bool] = None
    usuario_asignado: Optional[int] = None

class NotificacionProveedorOut(NotificacionProveedorBase):
    """Esquema de salida para notificaciones de proveedores"""
    id: int
    integracion_id: int
    leida: bool
    procesada: bool
    fecha_creacion: datetime
    fecha_lectura: Optional[datetime] = None
    fecha_procesamiento: Optional[datetime] = None
    usuario_asignado: Optional[int] = None
    
    class Config:
        from_attributes = True

# === LOGS DE INTEGRACIÓN ===

class LogIntegracionBase(BaseModel):
    """Esquema base para logs de integración"""
    tipo_operacion: str = Field(..., description="Tipo de operación")
    nivel: str = Field(..., description="Nivel del log")
    mensaje: str = Field(..., description="Mensaje del log")
    endpoint: Optional[str] = Field(None, max_length=500, description="Endpoint")
    metodo_http: Optional[str] = Field(None, max_length=10, description="Método HTTP")
    codigo_respuesta: Optional[int] = Field(None, description="Código de respuesta")
    tiempo_respuesta_ms: Optional[int] = Field(None, ge=0, description="Tiempo de respuesta en ms")
    datos_enviados: Optional[Dict[str, Any]] = Field(None, description="Datos enviados")
    datos_recibidos: Optional[Dict[str, Any]] = Field(None, description="Datos recibidos")
    error_detalle: Optional[str] = Field(None, description="Detalle del error")

    @validator('nivel')
    def validar_nivel(cls, v):
        niveles_validos = ['debug', 'info', 'warning', 'error', 'critical']
        if v not in niveles_validos:
            raise ValueError(f'Nivel debe ser uno de: {niveles_validos}')
        return v

class LogIntegracionCreate(LogIntegracionBase):
    """Esquema para crear logs de integración"""
    integracion_id: int = Field(..., description="ID de la integración")

class LogIntegracionOut(LogIntegracionBase):
    """Esquema de salida para logs de integración"""
    id: int
    integracion_id: int
    fecha_creacion: datetime
    usuario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# === CONFIGURACIONES DE INTEGRACIÓN ===

class ConfiguracionIntegracionBase(BaseModel):
    """Esquema base para configuraciones de integración"""
    nombre: str = Field(..., max_length=255, description="Nombre de la configuración")
    descripcion: Optional[str] = Field(None, description="Descripción de la configuración")
    valor: str = Field(..., description="Valor de la configuración")
    tipo_valor: str = Field(..., description="Tipo del valor")

    @validator('tipo_valor')
    def validar_tipo_valor(cls, v):
        tipos_validos = ['string', 'integer', 'float', 'boolean', 'json']
        if v not in tipos_validos:
            raise ValueError(f'Tipo de valor debe ser uno de: {tipos_validos}')
        return v

class ConfiguracionIntegracionCreate(ConfiguracionIntegracionBase):
    """Esquema para crear configuraciones de integración"""
    integracion_id: int = Field(..., description="ID de la integración")

class ConfiguracionIntegracionUpdate(BaseModel):
    """Esquema para actualizar configuraciones de integración"""
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    valor: Optional[str] = None
    tipo_valor: Optional[str] = None
    activo: Optional[bool] = None

class ConfiguracionIntegracionOut(ConfiguracionIntegracionBase):
    """Esquema de salida para configuraciones de integración"""
    id: int
    integracion_id: int
    fecha_creacion: datetime
    fecha_ultima_actualizacion: datetime
    creado_por: Optional[int] = None
    activo: bool
    
    class Config:
        from_attributes = True

# === ESQUEMAS DE CONSULTA Y FILTROS ===

class IntegracionFiltros(BaseModel):
    """Filtros para consultar integraciones"""
    proveedor_id: Optional[int] = Field(None, description="Filtrar por proveedor")
    tipo_integracion: Optional[TipoIntegracion] = Field(None, description="Filtrar por tipo")
    estado: Optional[EstadoIntegracion] = Field(None, description="Filtrar por estado")
    activo: Optional[bool] = Field(True, description="Solo integraciones activas")
    sincronizar_productos: Optional[bool] = Field(None, description="Filtrar por sincronización de productos")
    permitir_pedidos_automaticos: Optional[bool] = Field(None, description="Filtrar por pedidos automáticos")

class CatalogoFiltros(BaseModel):
    """Filtros para consultar catálogos"""
    integracion_id: Optional[int] = Field(None, description="Filtrar por integración")
    producto_id: Optional[int] = Field(None, description="Filtrar por producto interno")
    disponible: Optional[bool] = Field(None, description="Filtrar por disponibilidad")
    sincronizar_precio: Optional[bool] = Field(None, description="Filtrar por sincronización de precio")
    sincronizar_stock: Optional[bool] = Field(None, description="Filtrar por sincronización de stock")
    categoria_proveedor: Optional[str] = Field(None, description="Filtrar por categoría")
    marca_proveedor: Optional[str] = Field(None, description="Filtrar por marca")

class PedidoFiltros(BaseModel):
    """Filtros para consultar pedidos"""
    integracion_id: Optional[int] = Field(None, description="Filtrar por integración")
    estado: Optional[EstadoPedido] = Field(None, description="Filtrar por estado")
    tipo_pedido: Optional[str] = Field(None, description="Filtrar por tipo de pedido")
    prioridad: Optional[str] = Field(None, description="Filtrar por prioridad")
    fecha_desde: Optional[date] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[date] = Field(None, description="Fecha hasta")
    creado_por: Optional[int] = Field(None, description="Filtrar por creador")

class NotificacionFiltros(BaseModel):
    """Filtros para consultar notificaciones"""
    integracion_id: Optional[int] = Field(None, description="Filtrar por integración")
    tipo: Optional[str] = Field(None, description="Filtrar por tipo")
    prioridad: Optional[str] = Field(None, description="Filtrar por prioridad")
    leida: Optional[bool] = Field(None, description="Filtrar por estado de lectura")
    procesada: Optional[bool] = Field(None, description="Filtrar por estado de procesamiento")
    usuario_asignado: Optional[int] = Field(None, description="Filtrar por usuario asignado")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta")

# === ESQUEMAS DE RESUMEN Y ESTADÍSTICAS ===

class ResumenIntegracion(BaseModel):
    """Resumen de integraciones"""
    total_integraciones: int
    integraciones_activas: int
    integraciones_inactivas: int
    integraciones_con_error: int
    total_sincronizaciones: int
    sincronizaciones_exitosas: int
    sincronizaciones_fallidas: int
    tasa_exito: float
    ultima_sincronizacion: Optional[datetime] = None
    integracion_mas_activa: Optional[str] = None

class ResumenCatalogo(BaseModel):
    """Resumen de catálogos"""
    total_productos: int
    productos_mapeados: int
    productos_sin_mapear: int
    productos_disponibles: int
    productos_agotados: int
    precio_promedio: float
    stock_total: int
    categorias_unicas: int
    marcas_unicas: int

class ResumenPedidos(BaseModel):
    """Resumen de pedidos"""
    total_pedidos: int
    pedidos_pendientes: int
    pedidos_en_proceso: int
    pedidos_entregados: int
    pedidos_cancelados: int
    valor_total_pedidos: float
    valor_promedio_pedido: float
    tiempo_promedio_entrega: Optional[float] = None
    proveedor_mas_utilizado: Optional[str] = None

class DashboardProveedores(BaseModel):
    """Dashboard de proveedores"""
    # Métricas principales
    total_proveedores: int
    proveedores_activos: int
    integraciones_activas: int
    productos_sincronizados: int
    
    # Métricas de rendimiento
    tasa_sincronizacion_exitosa: float
    tiempo_promedio_sincronizacion: float
    pedidos_pendientes: int
    notificaciones_pendientes: int
    
    # Top performers
    proveedores_mas_utilizados: List[Dict[str, Any]] = []
    productos_mas_solicitados: List[Dict[str, Any]] = []
    categorias_mas_populares: List[Dict[str, Any]] = []
    
    # Alertas
    alertas: List[Dict[str, Any]] = []
    
    # Tendencias
    tendencia_pedidos: str  # "creciente", "decreciente", "estable"
    tendencia_sincronizaciones: str  # "creciente", "decreciente", "estable"
    tendencia_precios: str  # "creciente", "decreciente", "estable"

class EstadisticasIntegracion(BaseModel):
    """Estadísticas detalladas de integración"""
    integracion_id: int
    nombre_integracion: str
    proveedor_nombre: str
    
    # Estadísticas de sincronización
    total_sincronizaciones: int
    sincronizaciones_exitosas: int
    sincronizaciones_fallidas: int
    tasa_exito: float
    ultima_sincronizacion: Optional[datetime] = None
    tiempo_promedio_sincronizacion: float
    
    # Estadísticas de productos
    total_productos: int
    productos_actualizados: int
    productos_nuevos: int
    productos_eliminados: int
    
    # Estadísticas de pedidos
    total_pedidos: int
    pedidos_exitosos: int
    pedidos_fallidos: int
    valor_total_pedidos: float
    
    # Estadísticas de errores
    errores_por_tipo: Dict[str, int] = {}
    errores_recientes: List[Dict[str, Any]] = []
    
    # Recomendaciones
    recomendaciones: List[str] = []

