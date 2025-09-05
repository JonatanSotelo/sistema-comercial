# app/schemas/notificacion_schema.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.notificacion_model import TipoNotificacion, EstadoNotificacion

class NotificacionBase(BaseModel):
    """Esquema base para notificaciones"""
    titulo: str = Field(..., max_length=255, description="Título de la notificación")
    mensaje: str = Field(..., description="Mensaje de la notificación")
    tipo: TipoNotificacion = Field(..., description="Tipo de notificación")
    es_urgente: bool = Field(False, description="Si la notificación es urgente")
    requiere_accion: bool = Field(False, description="Si requiere acción del usuario")
    datos_adicionales: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales en formato JSON")

class NotificacionCreate(NotificacionBase):
    """Esquema para crear notificaciones"""
    usuario_id: Optional[int] = Field(None, description="ID del usuario (NULL para notificación global)")
    entidad_tipo: Optional[str] = Field(None, max_length=50, description="Tipo de entidad relacionada")
    entidad_id: Optional[int] = Field(None, description="ID de la entidad relacionada")

class NotificacionUpdate(BaseModel):
    """Esquema para actualizar notificaciones"""
    estado: Optional[EstadoNotificacion] = Field(None, description="Nuevo estado de la notificación")
    fecha_lectura: Optional[datetime] = Field(None, description="Fecha de lectura")

class NotificacionOut(NotificacionBase):
    """Esquema de salida para notificaciones"""
    id: int
    estado: EstadoNotificacion
    usuario_id: Optional[int] = None
    entidad_tipo: Optional[str] = None
    entidad_id: Optional[int] = None
    fecha_creacion: datetime
    fecha_envio: Optional[datetime] = None
    fecha_lectura: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NotificacionResumen(BaseModel):
    """Resumen de notificaciones para el dashboard"""
    total: int = Field(..., description="Total de notificaciones")
    pendientes: int = Field(..., description="Notificaciones pendientes")
    leidas: int = Field(..., description="Notificaciones leídas")
    urgentes: int = Field(..., description="Notificaciones urgentes")
    por_tipo: Dict[str, int] = Field(..., description="Conteo por tipo")

class NotificacionFiltros(BaseModel):
    """Filtros para consultar notificaciones"""
    tipo: Optional[TipoNotificacion] = Field(None, description="Filtrar por tipo")
    estado: Optional[EstadoNotificacion] = Field(None, description="Filtrar por estado")
    es_urgente: Optional[bool] = Field(None, description="Filtrar por urgencia")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta")
    usuario_id: Optional[int] = Field(None, description="Filtrar por usuario")

class NotificacionBulkUpdate(BaseModel):
    """Esquema para actualizaciones masivas"""
    notificacion_ids: List[int] = Field(..., description="IDs de notificaciones a actualizar")
    estado: EstadoNotificacion = Field(..., description="Nuevo estado")
    fecha_lectura: Optional[datetime] = Field(None, description="Fecha de lectura")

class NotificacionStats(BaseModel):
    """Estadísticas de notificaciones"""
    total_notificaciones: int
    notificaciones_hoy: int
    notificaciones_semana: int
    notificaciones_mes: int
    tasa_lectura: float  # Porcentaje
    notificaciones_por_tipo: Dict[str, int]
    notificaciones_urgentes: int
    notificaciones_pendientes: int

class NotificacionTemplate(BaseModel):
    """Plantilla para crear notificaciones automáticas"""
    tipo: TipoNotificacion
    titulo_template: str
    mensaje_template: str
    es_urgente: bool = False
    requiere_accion: bool = False
    condiciones: Optional[Dict[str, Any]] = Field(None, description="Condiciones para activar la notificación")
