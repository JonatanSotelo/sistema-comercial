# app/schemas/descuento_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.descuento_model import TipoDescuento, EstadoDescuento

class DescuentoBase(BaseModel):
    """Esquema base para descuentos"""
    codigo: str = Field(..., max_length=50, description="Código único del descuento")
    nombre: str = Field(..., max_length=255, description="Nombre del descuento")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    tipo: TipoDescuento = Field(..., description="Tipo de descuento")
    valor: float = Field(..., gt=0, description="Valor del descuento (porcentaje o monto)")
    valor_minimo: Optional[float] = Field(None, ge=0, description="Compra mínima para aplicar")
    valor_maximo: Optional[float] = Field(None, ge=0, description="Descuento máximo aplicable")
    limite_usos: Optional[int] = Field(None, ge=1, description="Límite total de usos")
    usos_por_cliente: Optional[int] = Field(None, ge=1, description="Límite de usos por cliente")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio del descuento")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin del descuento")
    aplica_envio: bool = Field(False, description="Si aplica a costos de envío")
    aplica_impuestos: bool = Field(True, description="Si se aplica antes o después de impuestos")
    productos_ids: Optional[List[int]] = Field(None, description="IDs de productos específicos")
    clientes_ids: Optional[List[int]] = Field(None, description="IDs de clientes específicos")
    categorias_ids: Optional[List[int]] = Field(None, description="IDs de categorías")
    notas_internas: Optional[str] = Field(None, description="Notas internas")

    @validator('valor')
    def validar_valor_por_tipo(cls, v, values):
        tipo = values.get('tipo')
        if tipo == TipoDescuento.PORCENTAJE and v > 100:
            raise ValueError('El porcentaje no puede ser mayor a 100')
        if tipo == TipoDescuento.DESCUENTO_VOLUMEN and v > 100:
            raise ValueError('El porcentaje de descuento por volumen no puede ser mayor a 100')
        return v

    @validator('fecha_fin')
    def validar_fechas(cls, v, values):
        fecha_inicio = values.get('fecha_inicio')
        if v and fecha_inicio and v <= fecha_inicio:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class DescuentoCreate(DescuentoBase):
    """Esquema para crear descuentos"""
    pass

class DescuentoUpdate(BaseModel):
    """Esquema para actualizar descuentos"""
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    valor: Optional[float] = Field(None, gt=0)
    valor_minimo: Optional[float] = Field(None, ge=0)
    valor_maximo: Optional[float] = Field(None, ge=0)
    limite_usos: Optional[int] = Field(None, ge=1)
    usos_por_cliente: Optional[int] = Field(None, ge=1)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[EstadoDescuento] = None
    es_activo: Optional[bool] = None
    aplica_envio: Optional[bool] = None
    aplica_impuestos: Optional[bool] = None
    productos_ids: Optional[List[int]] = None
    clientes_ids: Optional[List[int]] = None
    categorias_ids: Optional[List[int]] = None
    notas_internas: Optional[str] = None

class DescuentoOut(DescuentoBase):
    """Esquema de salida para descuentos"""
    id: int
    usos_actuales: int
    fecha_creacion: datetime
    estado: EstadoDescuento
    es_activo: bool
    creado_por: Optional[int] = None
    
    class Config:
        from_attributes = True

class DescuentoUsoOut(BaseModel):
    """Esquema de salida para usos de descuentos"""
    id: int
    descuento_id: int
    cliente_id: Optional[int] = None
    venta_id: Optional[int] = None
    monto_original: float
    monto_descuento: float
    monto_final: float
    fecha_uso: datetime
    ip_cliente: Optional[str] = None
    
    class Config:
        from_attributes = True

class DescuentoAplicacion(BaseModel):
    """Esquema para aplicar descuentos"""
    codigo: str = Field(..., description="Código del descuento a aplicar")
    monto_total: float = Field(..., gt=0, description="Monto total de la compra")
    productos_ids: List[int] = Field(..., description="IDs de productos en la compra")
    cliente_id: Optional[int] = Field(None, description="ID del cliente (opcional)")

class DescuentoResultado(BaseModel):
    """Resultado de la aplicación de un descuento"""
    aplicable: bool
    monto_descuento: float = 0.0
    monto_final: float = 0.0
    mensaje: str
    descuento: Optional[DescuentoOut] = None
    restricciones: Optional[Dict[str, Any]] = None

class DescuentoEstadisticas(BaseModel):
    """Estadísticas de descuentos"""
    total_descuentos: int
    descuentos_activos: int
    descuentos_expirados: int
    total_usos: int
    monto_total_descuentado: float
    descuentos_por_tipo: Dict[str, int]
    top_descuentos: List[Dict[str, Any]]
    usos_por_mes: List[Dict[str, Any]]

class PromocionBase(BaseModel):
    """Esquema base para promociones"""
    nombre: str = Field(..., max_length=255, description="Nombre de la promoción")
    descripcion: Optional[str] = Field(None, description="Descripción de la promoción")
    tipo: TipoDescuento = Field(..., description="Tipo de promoción")
    valor: float = Field(..., gt=0, description="Valor de la promoción")
    condicion_minima: Optional[float] = Field(None, ge=0, description="Condición mínima para aplicar")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin")
    productos_ids: Optional[List[int]] = Field(None, description="IDs de productos")
    clientes_ids: Optional[List[int]] = Field(None, description="IDs de clientes")

class PromocionCreate(PromocionBase):
    """Esquema para crear promociones"""
    pass

class PromocionOut(PromocionBase):
    """Esquema de salida para promociones"""
    id: int
    fecha_creacion: datetime
    estado: EstadoDescuento
    es_activo: bool
    creado_por: Optional[int] = None
    
    class Config:
        from_attributes = True

class DescuentoFiltros(BaseModel):
    """Filtros para consultar descuentos"""
    codigo: Optional[str] = Field(None, description="Filtrar por código")
    tipo: Optional[TipoDescuento] = Field(None, description="Filtrar por tipo")
    estado: Optional[EstadoDescuento] = Field(None, description="Filtrar por estado")
    es_activo: Optional[bool] = Field(None, description="Filtrar por estado activo")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta")
    cliente_id: Optional[int] = Field(None, description="Filtrar por cliente")
    producto_id: Optional[int] = Field(None, description="Filtrar por producto")
