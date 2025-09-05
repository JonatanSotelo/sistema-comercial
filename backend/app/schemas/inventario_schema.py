# app/schemas/inventario_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.inventario_model import TipoAlertaInventario, EstadoAlerta

class ConfiguracionInventarioBase(BaseModel):
    """Esquema base para configuración de inventario"""
    producto_id: int = Field(..., description="ID del producto")
    stock_minimo: float = Field(..., ge=0, description="Stock mínimo del producto")
    stock_maximo: Optional[float] = Field(None, ge=0, description="Stock máximo del producto")
    punto_reorden: Optional[float] = Field(None, ge=0, description="Punto de reorden")
    cantidad_reorden: Optional[float] = Field(None, ge=0, description="Cantidad a reordenar")
    alerta_stock_bajo: bool = Field(True, description="Activar alerta de stock bajo")
    alerta_stock_critico: bool = Field(True, description="Activar alerta de stock crítico")
    alerta_vencimiento: bool = Field(True, description="Activar alerta de vencimiento")
    dias_vencimiento_alerta: int = Field(30, ge=1, le=365, description="Días antes del vencimiento para alertar")
    alerta_movimiento_grande: bool = Field(True, description="Activar alerta de movimientos grandes")
    umbral_movimiento_grande: Optional[float] = Field(None, ge=0, le=100, description="Umbral de cambio para alertar (%)")

    @validator('stock_maximo')
    def validar_stock_maximo(cls, v, values):
        if v and 'stock_minimo' in values and v <= values['stock_minimo']:
            raise ValueError('El stock máximo debe ser mayor al stock mínimo')
        return v

    @validator('punto_reorden')
    def validar_punto_reorden(cls, v, values):
        if v and 'stock_minimo' in values and v < values['stock_minimo']:
            raise ValueError('El punto de reorden debe ser mayor o igual al stock mínimo')
        return v

class ConfiguracionInventarioCreate(ConfiguracionInventarioBase):
    """Esquema para crear configuración de inventario"""
    pass

class ConfiguracionInventarioUpdate(BaseModel):
    """Esquema para actualizar configuración de inventario"""
    stock_minimo: Optional[float] = Field(None, ge=0)
    stock_maximo: Optional[float] = Field(None, ge=0)
    punto_reorden: Optional[float] = Field(None, ge=0)
    cantidad_reorden: Optional[float] = Field(None, ge=0)
    alerta_stock_bajo: Optional[bool] = None
    alerta_stock_critico: Optional[bool] = None
    alerta_vencimiento: Optional[bool] = None
    dias_vencimiento_alerta: Optional[int] = Field(None, ge=1, le=365)
    alerta_movimiento_grande: Optional[bool] = None
    umbral_movimiento_grande: Optional[float] = Field(None, ge=0, le=100)
    activo: Optional[bool] = None

class ConfiguracionInventarioOut(ConfiguracionInventarioBase):
    """Esquema de salida para configuración de inventario"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True

class AlertaInventarioBase(BaseModel):
    """Esquema base para alertas de inventario"""
    producto_id: int = Field(..., description="ID del producto")
    tipo: TipoAlertaInventario = Field(..., description="Tipo de alerta")
    titulo: str = Field(..., max_length=255, description="Título de la alerta")
    mensaje: str = Field(..., description="Mensaje de la alerta")
    prioridad: int = Field(1, ge=1, le=3, description="Prioridad de la alerta (1=alta, 2=media, 3=baja)")
    stock_actual: Optional[float] = Field(None, description="Stock actual del producto")
    stock_minimo: Optional[float] = Field(None, description="Stock mínimo configurado")
    stock_critico: Optional[float] = Field(None, description="Stock crítico")
    dias_vencimiento: Optional[int] = Field(None, description="Días hasta el vencimiento")

class AlertaInventarioCreate(AlertaInventarioBase):
    """Esquema para crear alertas de inventario"""
    pass

class AlertaInventarioUpdate(BaseModel):
    """Esquema para actualizar alertas de inventario"""
    estado: Optional[EstadoAlerta] = None
    notas_resolucion: Optional[str] = Field(None, description="Notas de resolución")

class AlertaInventarioOut(AlertaInventarioBase):
    """Esquema de salida para alertas de inventario"""
    id: int
    estado: EstadoAlerta
    fecha_creacion: datetime
    fecha_resolucion: Optional[datetime] = None
    resuelta_por: Optional[int] = None
    notas_resolucion: Optional[str] = None
    
    class Config:
        from_attributes = True

class MovimientoInventarioBase(BaseModel):
    """Esquema base para movimientos de inventario"""
    producto_id: int = Field(..., description="ID del producto")
    tipo_movimiento: str = Field(..., max_length=50, description="Tipo de movimiento")
    cantidad: float = Field(..., description="Cantidad del movimiento")
    referencia_tipo: Optional[str] = Field(None, max_length=50, description="Tipo de referencia")
    referencia_id: Optional[int] = Field(None, description="ID de la referencia")
    motivo: Optional[str] = Field(None, description="Motivo del movimiento")
    costo_unitario: Optional[float] = Field(None, ge=0, description="Costo unitario")
    costo_total: Optional[float] = Field(None, ge=0, description="Costo total")

class MovimientoInventarioCreate(MovimientoInventarioBase):
    """Esquema para crear movimientos de inventario"""
    pass

class MovimientoInventarioOut(MovimientoInventarioBase):
    """Esquema de salida para movimientos de inventario"""
    id: int
    cantidad_anterior: float
    cantidad_nueva: float
    fecha_movimiento: datetime
    usuario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class ReordenAutomaticoBase(BaseModel):
    """Esquema base para reorden automático"""
    producto_id: int = Field(..., description="ID del producto")
    proveedor_id: Optional[int] = Field(None, description="ID del proveedor")
    cantidad_sugerida: float = Field(..., ge=0, description="Cantidad sugerida para reorden")
    costo_estimado: Optional[float] = Field(None, ge=0, description="Costo estimado del reorden")
    fecha_sugerida: datetime = Field(..., description="Fecha sugerida para el reorden")
    notas: Optional[str] = Field(None, description="Notas del reorden")

class ReordenAutomaticoCreate(ReordenAutomaticoBase):
    """Esquema para crear reorden automático"""
    pass

class ReordenAutomaticoUpdate(BaseModel):
    """Esquema para actualizar reorden automático"""
    estado: Optional[str] = Field(None, description="Estado del reorden")
    notas: Optional[str] = Field(None, description="Notas del reorden")

class ReordenAutomaticoOut(ReordenAutomaticoBase):
    """Esquema de salida para reorden automático"""
    id: int
    estado: str
    fecha_creacion: datetime
    aprobado_por: Optional[int] = None
    fecha_aprobacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class InventarioResumen(BaseModel):
    """Resumen del inventario"""
    total_productos: int
    productos_stock_bajo: int
    productos_stock_critico: int
    productos_agotados: int
    alertas_pendientes: int
    alertas_urgentes: int
    valor_total_inventario: float
    movimientos_hoy: int
    reordenes_pendientes: int

class InventarioFiltros(BaseModel):
    """Filtros para consultar inventario"""
    producto_id: Optional[int] = Field(None, description="Filtrar por producto")
    tipo_alerta: Optional[TipoAlertaInventario] = Field(None, description="Filtrar por tipo de alerta")
    estado_alerta: Optional[EstadoAlerta] = Field(None, description="Filtrar por estado de alerta")
    prioridad: Optional[int] = Field(None, ge=1, le=3, description="Filtrar por prioridad")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta")
    solo_activos: Optional[bool] = Field(True, description="Solo configuraciones activas")

class InventarioEstadisticas(BaseModel):
    """Estadísticas del inventario"""
    total_productos: int
    productos_configurados: int
    alertas_por_tipo: Dict[str, int]
    movimientos_por_tipo: Dict[str, int]
    valor_inventario_por_categoria: Dict[str, float]
    productos_mas_movidos: List[Dict[str, Any]]
    tendencia_stock: List[Dict[str, Any]]
    alertas_resueltas_mes: int
    tiempo_promedio_resolucion: float  # En horas
