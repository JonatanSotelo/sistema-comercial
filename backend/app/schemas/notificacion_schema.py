from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from app.models.notificacion_model import TipoNotificacion, EstadoNotificacion

class NotificacionBase(BaseModel):
    titulo: str
    mensaje: str
    tipo: TipoNotificacion
    estado: Optional[EstadoNotificacion] = None
    usuario_id: Optional[int] = None
    entidad_id: Optional[int] = None
    entidad_tipo: Optional[str] = None
    es_urgente: Optional[bool] = False
    requiere_accion: Optional[bool] = False
    datos_adicionales: Optional[str] = None

class NotificacionCreate(NotificacionBase):
    pass

class NotificacionUpdate(BaseModel):
    estado: Optional[EstadoNotificacion] = None
    es_urgente: Optional[bool] = None
    requiere_accion: Optional[bool] = None
    datos_adicionales: Optional[str] = None

class NotificacionOut(NotificacionBase):
    id: int
    fecha_creacion: datetime
    fecha_envio: Optional[datetime] = None
    fecha_lectura: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, json_encoders={
        datetime: lambda v: v.isoformat()
    })

class NotificacionBulkUpdate(BaseModel):
    notificacion_ids: List[int]
    estado: Optional[EstadoNotificacion] = None
    es_urgente: Optional[bool] = None
    requiere_accion: Optional[bool] = None

class NotificacionStats(BaseModel):
    total: int
    no_leidas: int
    urgentes: int
    por_tipo: Dict[str, int]
    por_estado: Dict[str, int]

class NotificacionFiltros(BaseModel):
    tipo: Optional[TipoNotificacion] = None
    estado: Optional[EstadoNotificacion] = None
    es_urgente: Optional[bool] = None
    requiere_accion: Optional[bool] = None
    usuario_id: Optional[int] = None
    entidad_tipo: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    page: int = 1
    per_page: int = 50