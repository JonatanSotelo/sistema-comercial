# app/schemas/precio_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.models.precio_model import TipoPrecio, EstadoPrecio

# === ESQUEMAS BASE ===

class PrecioProductoBase(BaseModel):
    """Esquema base para precios de producto"""
    producto_id: int = Field(..., description="ID del producto")
    tipo: TipoPrecio = Field(..., description="Tipo de precio")
    precio_base: float = Field(..., ge=0, description="Precio base del producto")
    precio_especial: Optional[float] = Field(None, ge=0, description="Precio especial aplicado")
    descuento_porcentaje: Optional[float] = Field(None, ge=0, le=100, description="Descuento en porcentaje")
    descuento_monto: Optional[float] = Field(None, ge=0, description="Descuento en monto fijo")
    cliente_id: Optional[int] = Field(None, description="ID del cliente específico")
    categoria_id: Optional[int] = Field(None, description="ID de la categoría")
    cantidad_minima: Optional[float] = Field(None, ge=0, description="Cantidad mínima para aplicar")
    cantidad_maxima: Optional[float] = Field(None, ge=0, description="Cantidad máxima para aplicar")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio de vigencia")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin de vigencia")
    nombre: Optional[str] = Field(None, max_length=255, description="Nombre descriptivo del precio")
    descripcion: Optional[str] = Field(None, description="Descripción del precio")
    prioridad: int = Field(1, ge=1, le=3, description="Prioridad (1=alta, 2=media, 3=baja)")

    @validator('precio_especial')
    def validar_precio_especial(cls, v, values):
        if v and 'precio_base' in values and v >= values['precio_base']:
            raise ValueError('El precio especial debe ser menor al precio base')
        return v

    @validator('descuento_porcentaje')
    def validar_descuento_porcentaje(cls, v, values):
        if v and 'precio_base' in values:
            descuento_maximo = values['precio_base'] * 0.95  # Máximo 95% de descuento
            if v > 95:
                raise ValueError('El descuento no puede ser mayor al 95%')
        return v

    @validator('fecha_fin')
    def validar_fecha_fin(cls, v, values):
        if v and 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class PrecioProductoCreate(PrecioProductoBase):
    """Esquema para crear precios de producto"""
    pass

class PrecioProductoUpdate(BaseModel):
    """Esquema para actualizar precios de producto"""
    precio_especial: Optional[float] = Field(None, ge=0)
    descuento_porcentaje: Optional[float] = Field(None, ge=0, le=100)
    descuento_monto: Optional[float] = Field(None, ge=0)
    cantidad_minima: Optional[float] = Field(None, ge=0)
    cantidad_maxima: Optional[float] = Field(None, ge=0)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    prioridad: Optional[int] = Field(None, ge=1, le=3)
    activo: Optional[bool] = None

class PrecioProductoOut(PrecioProductoBase):
    """Esquema de salida para precios de producto"""
    id: int
    estado: EstadoPrecio
    creado_por: Optional[int] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True

# === PRECIOS POR VOLUMEN ===

class PrecioVolumenBase(BaseModel):
    """Esquema base para precios por volumen"""
    producto_id: int = Field(..., description="ID del producto")
    cantidad_minima: float = Field(..., ge=0, description="Cantidad mínima")
    cantidad_maxima: Optional[float] = Field(None, ge=0, description="Cantidad máxima")
    descuento_porcentaje: Optional[float] = Field(None, ge=0, le=100, description="Descuento en porcentaje")
    descuento_monto: Optional[float] = Field(None, ge=0, description="Descuento en monto fijo")
    precio_especial: Optional[float] = Field(None, ge=0, description="Precio especial")
    cliente_id: Optional[int] = Field(None, description="ID del cliente específico")
    categoria_id: Optional[int] = Field(None, description="ID de la categoría")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin")
    nombre: Optional[str] = Field(None, max_length=255, description="Nombre del precio")
    descripcion: Optional[str] = Field(None, description="Descripción")
    prioridad: int = Field(1, ge=1, le=3, description="Prioridad")

    @validator('cantidad_maxima')
    def validar_cantidad_maxima(cls, v, values):
        if v and 'cantidad_minima' in values and v <= values['cantidad_minima']:
            raise ValueError('La cantidad máxima debe ser mayor a la mínima')
        return v

class PrecioVolumenCreate(PrecioVolumenBase):
    """Esquema para crear precios por volumen"""
    pass

class PrecioVolumenUpdate(BaseModel):
    """Esquema para actualizar precios por volumen"""
    cantidad_minima: Optional[float] = Field(None, ge=0)
    cantidad_maxima: Optional[float] = Field(None, ge=0)
    descuento_porcentaje: Optional[float] = Field(None, ge=0, le=100)
    descuento_monto: Optional[float] = Field(None, ge=0)
    precio_especial: Optional[float] = Field(None, ge=0)
    cliente_id: Optional[int] = None
    categoria_id: Optional[int] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    prioridad: Optional[int] = Field(None, ge=1, le=3)
    activo: Optional[bool] = None

class PrecioVolumenOut(PrecioVolumenBase):
    """Esquema de salida para precios por volumen"""
    id: int
    creado_por: Optional[int] = None
    fecha_creacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True

# === PRECIOS POR CATEGORÍA ===

class PrecioCategoriaBase(BaseModel):
    """Esquema base para precios por categoría"""
    categoria_id: int = Field(..., description="ID de la categoría")
    descuento_porcentaje: Optional[float] = Field(None, ge=0, le=100, description="Descuento en porcentaje")
    descuento_monto: Optional[float] = Field(None, ge=0, description="Descuento en monto fijo")
    multiplicador: Optional[float] = Field(None, ge=0, le=10, description="Multiplicador del precio base")
    cliente_id: Optional[int] = Field(None, description="ID del cliente específico")
    producto_id: Optional[int] = Field(None, description="ID del producto específico")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin")
    nombre: Optional[str] = Field(None, max_length=255, description="Nombre del precio")
    descripcion: Optional[str] = Field(None, description="Descripción")
    prioridad: int = Field(1, ge=1, le=3, description="Prioridad")

class PrecioCategoriaCreate(PrecioCategoriaBase):
    """Esquema para crear precios por categoría"""
    pass

class PrecioCategoriaUpdate(BaseModel):
    """Esquema para actualizar precios por categoría"""
    descuento_porcentaje: Optional[float] = Field(None, ge=0, le=100)
    descuento_monto: Optional[float] = Field(None, ge=0)
    multiplicador: Optional[float] = Field(None, ge=0, le=10)
    cliente_id: Optional[int] = None
    producto_id: Optional[int] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    prioridad: Optional[int] = Field(None, ge=1, le=3)
    activo: Optional[bool] = None

class PrecioCategoriaOut(PrecioCategoriaBase):
    """Esquema de salida para precios por categoría"""
    id: int
    creado_por: Optional[int] = None
    fecha_creacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True

# === PRECIOS ESTACIONALES ===

class PrecioEstacionalBase(BaseModel):
    """Esquema base para precios estacionales"""
    producto_id: int = Field(..., description="ID del producto")
    nombre_temporada: str = Field(..., max_length=100, description="Nombre de la temporada")
    descuento_porcentaje: Optional[float] = Field(None, ge=0, le=100, description="Descuento en porcentaje")
    descuento_monto: Optional[float] = Field(None, ge=0, description="Descuento en monto fijo")
    precio_especial: Optional[float] = Field(None, ge=0, description="Precio especial")
    cliente_id: Optional[int] = Field(None, description="ID del cliente específico")
    categoria_id: Optional[int] = Field(None, description="ID de la categoría")
    fecha_inicio: date = Field(..., description="Fecha de inicio")
    fecha_fin: date = Field(..., description="Fecha de fin")
    descripcion: Optional[str] = Field(None, description="Descripción")
    prioridad: int = Field(1, ge=1, le=3, description="Prioridad")

    @validator('fecha_fin')
    def validar_fecha_fin(cls, v, values):
        if v and 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class PrecioEstacionalCreate(PrecioEstacionalBase):
    """Esquema para crear precios estacionales"""
    pass

class PrecioEstacionalUpdate(BaseModel):
    """Esquema para actualizar precios estacionales"""
    nombre_temporada: Optional[str] = Field(None, max_length=100)
    descuento_porcentaje: Optional[float] = Field(None, ge=0, le=100)
    descuento_monto: Optional[float] = Field(None, ge=0)
    precio_especial: Optional[float] = Field(None, ge=0)
    cliente_id: Optional[int] = None
    categoria_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    descripcion: Optional[str] = None
    prioridad: Optional[int] = Field(None, ge=1, le=3)
    activo: Optional[bool] = None

class PrecioEstacionalOut(PrecioEstacionalBase):
    """Esquema de salida para precios estacionales"""
    id: int
    creado_por: Optional[int] = None
    fecha_creacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True

# === HISTORIAL DE PRECIOS ===

class PrecioHistorialOut(BaseModel):
    """Esquema de salida para historial de precios"""
    id: int
    producto_id: int
    tipo_cambio: str
    precio_anterior: Optional[float] = None
    precio_nuevo: Optional[float] = None
    descuento_anterior: Optional[float] = None
    descuento_nuevo: Optional[float] = None
    precio_id: Optional[int] = None
    precio_tabla: Optional[str] = None
    motivo: Optional[str] = None
    usuario_id: Optional[int] = None
    fecha_cambio: datetime
    ip_address: Optional[str] = None
    
    class Config:
        from_attributes = True

# === PRECIOS APLICADOS ===

class PrecioAplicadoOut(BaseModel):
    """Esquema de salida para precios aplicados"""
    id: int
    venta_id: int
    producto_id: int
    cliente_id: Optional[int] = None
    precio_base: float
    precio_final: float
    descuento_aplicado: Optional[float] = None
    porcentaje_descuento: Optional[float] = None
    tipo_precio: str
    precio_id: Optional[int] = None
    precio_tabla: Optional[str] = None
    cantidad: float
    subtotal: float
    fecha_aplicacion: datetime
    
    class Config:
        from_attributes = True

# === ESQUEMAS DE APLICACIÓN ===

class PrecioAplicarRequest(BaseModel):
    """Esquema para aplicar precios a una venta"""
    venta_id: int = Field(..., description="ID de la venta")
    producto_id: int = Field(..., description="ID del producto")
    cliente_id: Optional[int] = Field(None, description="ID del cliente")
    cantidad: float = Field(..., ge=0, description="Cantidad del producto")
    precio_base: float = Field(..., ge=0, description="Precio base del producto")

class PrecioAplicarResponse(BaseModel):
    """Esquema de respuesta para aplicación de precios"""
    aplicado: bool = Field(..., description="Si se aplicó algún precio especial")
    precio_base: float = Field(..., description="Precio base original")
    precio_final: float = Field(..., description="Precio final aplicado")
    descuento_aplicado: Optional[float] = Field(None, description="Descuento aplicado")
    porcentaje_descuento: Optional[float] = Field(None, description="Porcentaje de descuento")
    tipo_precio: Optional[str] = Field(None, description="Tipo de precio aplicado")
    precio_id: Optional[int] = Field(None, description="ID del precio aplicado")
    mensaje: str = Field(..., description="Mensaje descriptivo")

# === FILTROS Y CONSULTAS ===

class PrecioFiltros(BaseModel):
    """Filtros para consultar precios"""
    producto_id: Optional[int] = Field(None, description="Filtrar por producto")
    cliente_id: Optional[int] = Field(None, description="Filtrar por cliente")
    categoria_id: Optional[int] = Field(None, description="Filtrar por categoría")
    tipo: Optional[TipoPrecio] = Field(None, description="Filtrar por tipo")
    estado: Optional[EstadoPrecio] = Field(None, description="Filtrar por estado")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta")
    solo_activos: Optional[bool] = Field(True, description="Solo precios activos")
    solo_vigentes: Optional[bool] = Field(True, description="Solo precios vigentes")

class PrecioResumen(BaseModel):
    """Resumen de precios"""
    total_precios: int
    precios_activos: int
    precios_por_tipo: Dict[str, int]
    precios_por_cliente: int
    precios_por_volumen: int
    precios_estacionales: int
    descuento_promedio: float
    ahorro_total: float

class PrecioEstadisticas(BaseModel):
    """Estadísticas de precios"""
    total_precios: int
    precios_por_tipo: Dict[str, int]
    precios_por_estado: Dict[str, int]
    descuento_promedio_por_tipo: Dict[str, float]
    productos_mas_descontados: List[Dict[str, Any]]
    clientes_mas_descontados: List[Dict[str, Any]]
    tendencia_precios: List[Dict[str, Any]]
    ahorro_total_mes: float
    ahorro_promedio_por_venta: float
