# app/routers/notificacion_router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db
from app.core.deps import require_user, require_admin
from app.services.notificacion_service import NotificacionService
from app.schemas.notificacion_schema import (
    NotificacionCreate, NotificacionUpdate, NotificacionOut, 
    NotificacionResumen, NotificacionFiltros, NotificacionStats,
    NotificacionBulkUpdate, TipoNotificacion, EstadoNotificacion
)

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router.post("", response_model=NotificacionOut, summary="Crear notificación")
def crear_notificacion(
    notificacion: NotificacionCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin)  # Solo admins pueden crear notificaciones
):
    """
    Crea una nueva notificación en el sistema.
    Solo usuarios administradores pueden crear notificaciones.
    """
    return NotificacionService.crear_notificacion(db, notificacion)

@router.get("", response_model=List[NotificacionOut], summary="Listar notificaciones")
def listar_notificaciones(
    skip: int = Query(0, ge=0, description="Número de notificaciones a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de notificaciones a retornar"),
    tipo: Optional[TipoNotificacion] = Query(None, description="Filtrar por tipo de notificación"),
    estado: Optional[EstadoNotificacion] = Query(None, description="Filtrar por estado"),
    es_urgente: Optional[bool] = Query(None, description="Filtrar por urgencia"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista notificaciones del usuario actual con filtros opcionales.
    Incluye notificaciones globales y del usuario específico.
    """
    filtros = NotificacionFiltros(
        tipo=tipo,
        estado=estado,
        es_urgente=es_urgente,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        usuario_id=current_user.id
    )
    
    return NotificacionService.obtener_notificaciones(
        db, 
        usuario_id=current_user.id,
        filtros=filtros,
        skip=skip,
        limit=limit
    )

@router.get("/{notificacion_id}", response_model=NotificacionOut, summary="Obtener notificación")
def obtener_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene una notificación específica por ID.
    Solo se pueden acceder a notificaciones propias o globales.
    """
    notificacion = NotificacionService.obtener_notificacion(db, notificacion_id)
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    # Verificar acceso (global o del usuario)
    if notificacion.usuario_id and notificacion.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta notificación")
    
    return notificacion

@router.put("/{notificacion_id}", response_model=NotificacionOut, summary="Actualizar notificación")
def actualizar_notificacion(
    notificacion_id: int,
    notificacion_update: NotificacionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Actualiza una notificación específica.
    Los usuarios solo pueden actualizar sus propias notificaciones.
    """
    notificacion = NotificacionService.obtener_notificacion(db, notificacion_id)
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    # Verificar acceso
    if notificacion.usuario_id and notificacion.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta notificación")
    
    return NotificacionService.actualizar_notificacion(db, notificacion_id, notificacion_update)

@router.patch("/{notificacion_id}/leer", summary="Marcar como leída")
def marcar_como_leida(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Marca una notificación como leída.
    """
    success = NotificacionService.marcar_como_leida(db, notificacion_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notificación no encontrada o sin acceso")
    
    return {"message": "Notificación marcada como leída"}

@router.patch("/bulk/leer", summary="Marcar múltiples como leídas")
def marcar_multiples_como_leidas(
    notificacion_ids: List[int],
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Marca múltiples notificaciones como leídas.
    """
    marcadas = 0
    for notificacion_id in notificacion_ids:
        if NotificacionService.marcar_como_leida(db, notificacion_id, current_user.id):
            marcadas += 1
    
    return {"message": f"{marcadas} notificaciones marcadas como leídas"}

@router.get("/resumen", response_model=NotificacionResumen, summary="Resumen de notificaciones")
def obtener_resumen(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un resumen de las notificaciones del usuario.
    Incluye contadores por estado y tipo.
    """
    return NotificacionService.obtener_resumen(db, current_user.id)

@router.get("/estadisticas", response_model=NotificacionStats, summary="Estadísticas de notificaciones")
def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene estadísticas detalladas de las notificaciones.
    Incluye métricas temporales y tasas de lectura.
    """
    return NotificacionService.obtener_estadisticas(db, current_user.id)

@router.get("/pendientes", response_model=List[NotificacionOut], summary="Notificaciones pendientes")
def obtener_pendientes(
    limit: int = Query(50, ge=1, le=200, description="Número máximo de notificaciones"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene notificaciones pendientes del usuario.
    Útil para mostrar alertas en tiempo real.
    """
    filtros = NotificacionFiltros(
        estado=EstadoNotificacion.PENDIENTE,
        usuario_id=current_user.id
    )
    
    return NotificacionService.obtener_notificaciones(
        db,
        usuario_id=current_user.id,
        filtros=filtros,
        skip=0,
        limit=limit
    )

@router.get("/urgentes", response_model=List[NotificacionOut], summary="Notificaciones urgentes")
def obtener_urgentes(
    limit: int = Query(20, ge=1, le=100, description="Número máximo de notificaciones"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene notificaciones urgentes del usuario.
    Incluye notificaciones marcadas como urgentes.
    """
    filtros = NotificacionFiltros(
        es_urgente=True,
        usuario_id=current_user.id
    )
    
    return NotificacionService.obtener_notificaciones(
        db,
        usuario_id=current_user.id,
        filtros=filtros,
        skip=0,
        limit=limit
    )

@router.delete("/{notificacion_id}", summary="Eliminar notificación")
def eliminar_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin)  # Solo admins pueden eliminar
):
    """
    Elimina una notificación del sistema.
    Solo usuarios administradores pueden eliminar notificaciones.
    """
    notificacion = NotificacionService.obtener_notificacion(db, notificacion_id)
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    db.delete(notificacion)
    db.commit()
    
    return {"message": "Notificación eliminada"}

@router.post("/limpiar", summary="Limpiar notificaciones antiguas")
def limpiar_antiguas(
    dias: int = Query(30, ge=1, le=365, description="Días de antigüedad para limpiar"),
    db: Session = Depends(get_db),
    _auth=Depends(require_admin)  # Solo admins pueden limpiar
):
    """
    Limpia notificaciones antiguas del sistema.
    Solo elimina notificaciones leídas y no urgentes.
    """
    eliminadas = NotificacionService.limpiar_notificaciones_antiguas(db, dias)
    
    return {"message": f"{eliminadas} notificaciones eliminadas"}

# Endpoints para notificaciones automáticas (solo para admins)
@router.post("/stock-bajo", response_model=NotificacionOut, summary="Crear notificación de stock bajo")
def crear_notificacion_stock_bajo(
    producto_id: int,
    producto_nombre: str,
    stock_actual: float,
    stock_minimo: float,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin)
):
    """
    Crea una notificación automática de stock bajo.
    """
    return NotificacionService.crear_notificacion_stock_bajo(
        db, producto_id, producto_nombre, stock_actual, stock_minimo
    )

@router.post("/venta-importante", response_model=NotificacionOut, summary="Crear notificación de venta importante")
def crear_notificacion_venta_importante(
    venta_id: int,
    monto: float,
    cliente_nombre: Optional[str] = None,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin)
):
    """
    Crea una notificación automática de venta importante.
    """
    return NotificacionService.crear_notificacion_venta_importante(
        db, venta_id, monto, cliente_nombre
    )

@router.post("/sistema", response_model=NotificacionOut, summary="Crear notificación del sistema")
def crear_notificacion_sistema(
    titulo: str,
    mensaje: str,
    es_urgente: bool = False,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin)
):
    """
    Crea una notificación del sistema.
    """
    return NotificacionService.crear_notificacion_sistema(db, titulo, mensaje, es_urgente)
