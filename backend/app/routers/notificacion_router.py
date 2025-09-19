from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.database import get_db
from app.services.notificacion_service import NotificacionService
from app.schemas.notificacion_schema import (
    NotificacionCreate,
    NotificacionUpdate,
    NotificacionOut,
    NotificacionBulkUpdate,
    NotificacionStats,
    NotificacionFiltros
)
from app.core.auth import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router.get("/", response_model=List[NotificacionOut])
def get_notificaciones(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de notificación"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    es_urgente: Optional[bool] = Query(None, description="Filtrar por urgencia"),
    requiere_accion: Optional[bool] = Query(None, description="Filtrar por requerimiento de acción"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    entidad_tipo: Optional[str] = Query(None, description="Filtrar por tipo de entidad"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(50, ge=1, le=100, description="Elementos por página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todas las notificaciones con filtros"""
    filtros = NotificacionFiltros(
        tipo=tipo,
        estado=estado,
        es_urgente=es_urgente,
        requiere_accion=requiere_accion,
        usuario_id=usuario_id or current_user.id,
        entidad_tipo=entidad_tipo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        page=page,
        per_page=per_page
    )
    
    notificaciones = NotificacionService.get_all(db, filtros)
    return notificaciones

@router.get("/pendientes", response_model=List[NotificacionOut])
def get_notificaciones_pendientes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener notificaciones pendientes (no leídas)"""
    notificaciones = NotificacionService.get_pendientes(db, current_user.id)
    return notificaciones

@router.get("/urgentes", response_model=List[NotificacionOut])
def get_notificaciones_urgentes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener notificaciones urgentes"""
    notificaciones = NotificacionService.get_urgentes(db, current_user.id)
    return notificaciones

@router.get("/stats", response_model=NotificacionStats)
def get_notificaciones_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de notificaciones"""
    stats = NotificacionService.get_stats(db, current_user.id)
    return stats

@router.get("/{notificacion_id}", response_model=NotificacionOut)
def get_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener notificación por ID"""
    notificacion = NotificacionService.get_by_id(db, notificacion_id)
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Verificar que la notificación pertenece al usuario (si no es admin)
    if current_user.role != "admin" and notificacion.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta notificación"
        )
    
    return notificacion

@router.post("/", response_model=NotificacionOut, status_code=status.HTTP_201_CREATED)
def create_notificacion(
    notificacion: NotificacionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva notificación"""
    # Solo admins pueden crear notificaciones manualmente
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear notificaciones manualmente"
        )
    
    db_notificacion = NotificacionService.create(db, notificacion)
    return db_notificacion

@router.patch("/{notificacion_id}/leer", response_model=NotificacionOut)
def marcar_como_leida(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marcar notificación como leída"""
    notificacion = NotificacionService.get_by_id(db, notificacion_id)
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Verificar que la notificación pertenece al usuario (si no es admin)
    if current_user.role != "admin" and notificacion.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar esta notificación"
        )
    
    notificacion_actualizada = NotificacionService.marcar_como_leida(db, notificacion_id)
    return notificacion_actualizada

@router.patch("/bulk/leer", response_model=dict)
def marcar_todas_como_leidas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marcar todas las notificaciones como leídas"""
    count = NotificacionService.marcar_todas_como_leidas(db, current_user.id)
    return {"message": f"Se marcaron {count} notificaciones como leídas"}

@router.patch("/{notificacion_id}/procesar", response_model=NotificacionOut)
def marcar_como_procesada(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marcar notificación como procesada"""
    notificacion = NotificacionService.get_by_id(db, notificacion_id)
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Verificar que la notificación pertenece al usuario (si no es admin)
    if current_user.role != "admin" and notificacion.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar esta notificación"
        )
    
    notificacion_actualizada = NotificacionService.marcar_como_procesada(db, notificacion_id)
    return notificacion_actualizada

@router.put("/{notificacion_id}", response_model=NotificacionOut)
def update_notificacion(
    notificacion_id: int,
    notificacion_update: NotificacionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar notificación"""
    notificacion = NotificacionService.get_by_id(db, notificacion_id)
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Solo admins pueden actualizar notificaciones
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden actualizar notificaciones"
        )
    
    # Actualizar campos
    for field, value in notificacion_update.dict(exclude_unset=True).items():
        setattr(notificacion, field, value)
    
    db.commit()
    db.refresh(notificacion)
    return notificacion

@router.delete("/{notificacion_id}")
def delete_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar notificación"""
    notificacion = NotificacionService.get_by_id(db, notificacion_id)
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Verificar que la notificación pertenece al usuario (si no es admin)
    if current_user.role != "admin" and notificacion.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta notificación"
        )
    
    success = NotificacionService.delete(db, notificacion_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la notificación"
        )
    
    return {"message": "Notificación eliminada correctamente"}

@router.post("/limpiar-antiguas")
def limpiar_notificaciones_antiguas(
    dias: int = Query(30, ge=1, le=365, description="Días de antigüedad para limpiar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Limpiar notificaciones antiguas (solo admins)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden limpiar notificaciones"
        )
    
    count = NotificacionService.limpiar_notificaciones_antiguas(db, dias)
    return {"message": f"Se eliminaron {count} notificaciones antiguas"}

# Endpoints para crear notificaciones específicas (solo admins)
@router.post("/stock-bajo")
def crear_notificacion_stock_bajo(
    producto_id: int,
    stock_actual: int,
    stock_minimo: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear notificación de stock bajo (solo admins)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear notificaciones de stock"
        )
    
    notificacion = NotificacionService.crear_notificacion_stock_bajo(
        db, producto_id, stock_actual, stock_minimo, current_user.id
    )
    return notificacion

@router.post("/venta-nueva")
def crear_notificacion_venta_nueva(
    venta_id: int,
    monto: float,
    cliente_nombre: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear notificación de venta nueva (solo admins)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear notificaciones de ventas"
        )
    
    notificacion = NotificacionService.crear_notificacion_venta_nueva(
        db, venta_id, monto, cliente_nombre, current_user.id
    )
    return notificacion

@router.post("/sistema")
def crear_notificacion_sistema(
    titulo: str,
    mensaje: str,
    prioridad: str = "normal",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear notificación del sistema (solo admins)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear notificaciones del sistema"
        )
    
    notificacion = NotificacionService.crear_notificacion_sistema(
        db, titulo, mensaje, prioridad, current_user.id
    )
    return notificacion