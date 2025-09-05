# app/routers/inventario_router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db
from app.core.deps import require_user, require_admin
from app.services.inventario_service import InventarioService
from app.schemas.inventario_schema import (
    ConfiguracionInventarioCreate, ConfiguracionInventarioUpdate, ConfiguracionInventarioOut,
    AlertaInventarioCreate, AlertaInventarioUpdate, AlertaInventarioOut,
    MovimientoInventarioCreate, MovimientoInventarioOut,
    ReordenAutomaticoCreate, ReordenAutomaticoUpdate, ReordenAutomaticoOut,
    InventarioResumen, InventarioFiltros, InventarioEstadisticas,
    TipoAlertaInventario, EstadoAlerta
)

router = APIRouter(prefix="/inventario", tags=["Inventario"])

# === CONFIGURACIONES DE INVENTARIO ===

@router.post("/configuraciones", response_model=ConfiguracionInventarioOut, summary="Crear configuración de inventario")
def crear_configuracion(
    configuracion: ConfiguracionInventarioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear configuraciones
):
    """
    Crea una nueva configuración de inventario para un producto.
    Solo usuarios administradores pueden crear configuraciones.
    """
    # Verificar que el producto existe
    from app.models.producto_model import Producto
    producto = db.query(Producto).filter(Producto.id == configuracion.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar que no existe configuración para este producto
    config_existente = db.query(ConfiguracionInventario).filter(
        ConfiguracionInventario.producto_id == configuracion.producto_id
    ).first()
    if config_existente:
        raise HTTPException(status_code=400, detail="Ya existe configuración para este producto")
    
    return InventarioService.crear_configuracion(db, configuracion)

@router.get("/configuraciones", response_model=List[ConfiguracionInventarioOut], summary="Listar configuraciones")
def listar_configuraciones(
    skip: int = Query(0, ge=0, description="Número de configuraciones a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de configuraciones a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    solo_activos: bool = Query(True, description="Solo configuraciones activas"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista configuraciones de inventario con filtros opcionales.
    """
    filtros = InventarioFiltros(
        producto_id=producto_id,
        solo_activos=solo_activos
    )
    
    return InventarioService.obtener_configuraciones(db, filtros, skip, limit)

@router.put("/configuraciones/{config_id}", response_model=ConfiguracionInventarioOut, summary="Actualizar configuración")
def actualizar_configuracion(
    config_id: int,
    configuracion_update: ConfiguracionInventarioUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza una configuración de inventario existente.
    Solo usuarios administradores pueden actualizar configuraciones.
    """
    configuracion = InventarioService.actualizar_configuracion(db, config_id, configuracion_update)
    
    if not configuracion:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    return configuracion

# === MOVIMIENTOS DE INVENTARIO ===

@router.post("/movimientos", response_model=MovimientoInventarioOut, summary="Crear movimiento de inventario")
def crear_movimiento(
    movimiento: MovimientoInventarioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Crea un movimiento de inventario (entrada, salida, ajuste).
    """
    try:
        return InventarioService.crear_movimiento(db, movimiento, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/movimientos", response_model=List[MovimientoInventarioOut], summary="Listar movimientos")
def listar_movimientos(
    skip: int = Query(0, ge=0, description="Número de movimientos a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de movimientos a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    tipo_movimiento: Optional[str] = Query(None, description="Filtrar por tipo de movimiento"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista movimientos de inventario con filtros opcionales.
    """
    from app.models.inventario_model import MovimientoInventario
    from sqlalchemy import and_
    
    query = db.query(MovimientoInventario)
    
    if producto_id:
        query = query.filter(MovimientoInventario.producto_id == producto_id)
    if tipo_movimiento:
        query = query.filter(MovimientoInventario.tipo_movimiento == tipo_movimiento)
    if fecha_desde:
        query = query.filter(MovimientoInventario.fecha_movimiento >= fecha_desde)
    if fecha_hasta:
        query = query.filter(MovimientoInventario.fecha_movimiento <= fecha_hasta)
    
    movimientos = query.order_by(desc(MovimientoInventario.fecha_movimiento)).offset(skip).limit(limit).all()
    
    return movimientos

# === ALERTAS DE INVENTARIO ===

@router.get("/alertas", response_model=List[AlertaInventarioOut], summary="Listar alertas")
def listar_alertas(
    skip: int = Query(0, ge=0, description="Número de alertas a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de alertas a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    tipo_alerta: Optional[TipoAlertaInventario] = Query(None, description="Filtrar por tipo de alerta"),
    estado_alerta: Optional[EstadoAlerta] = Query(None, description="Filtrar por estado de alerta"),
    prioridad: Optional[int] = Query(None, ge=1, le=3, description="Filtrar por prioridad"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista alertas de inventario con filtros opcionales.
    """
    filtros = InventarioFiltros(
        producto_id=producto_id,
        tipo_alerta=tipo_alerta,
        estado_alerta=estado_alerta,
        prioridad=prioridad,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
    
    return InventarioService.obtener_alertas(db, filtros, skip, limit)

@router.patch("/alertas/{alerta_id}/resolver", response_model=AlertaInventarioOut, summary="Resolver alerta")
def resolver_alerta(
    alerta_id: int,
    notas: Optional[str] = Query(None, description="Notas de resolución"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Resuelve una alerta de inventario.
    """
    alerta = InventarioService.resolver_alerta(db, alerta_id, current_user.id, notas)
    
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    
    return alerta

@router.get("/alertas/pendientes", response_model=List[AlertaInventarioOut], summary="Alertas pendientes")
def obtener_alertas_pendientes(
    limit: int = Query(50, ge=1, le=200, description="Número máximo de alertas"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene alertas pendientes de inventario.
    """
    filtros = InventarioFiltros(estado_alerta=EstadoAlerta.PENDIENTE)
    return InventarioService.obtener_alertas(db, filtros, 0, limit)

@router.get("/alertas/urgentes", response_model=List[AlertaInventarioOut], summary="Alertas urgentes")
def obtener_alertas_urgentes(
    limit: int = Query(20, ge=1, le=100, description="Número máximo de alertas"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene alertas urgentes de inventario (prioridad 1).
    """
    filtros = InventarioFiltros(
        estado_alerta=EstadoAlerta.PENDIENTE,
        prioridad=1
    )
    return InventarioService.obtener_alertas(db, filtros, 0, limit)

# === REORDENES AUTOMÁTICOS ===

@router.get("/reordenes", response_model=List[ReordenAutomaticoOut], summary="Listar reordenes")
def listar_reordenes(
    skip: int = Query(0, ge=0, description="Número de reordenes a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de reordenes a retornar"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista reordenes automáticos con filtros opcionales.
    """
    from app.models.inventario_model import ReordenAutomatico
    from sqlalchemy import and_
    
    query = db.query(ReordenAutomatico)
    
    if estado:
        query = query.filter(ReordenAutomatico.estado == estado)
    if producto_id:
        query = query.filter(ReordenAutomatico.producto_id == producto_id)
    
    reordenes = query.order_by(desc(ReordenAutomatico.fecha_creacion)).offset(skip).limit(limit).all()
    
    return reordenes

@router.patch("/reordenes/{reorden_id}/aprobar", response_model=ReordenAutomaticoOut, summary="Aprobar reorden")
def aprobar_reorden(
    reorden_id: int,
    notas: Optional[str] = Query(None, description="Notas de aprobación"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden aprobar
):
    """
    Aprueba un reorden automático.
    Solo usuarios administradores pueden aprobar reordenes.
    """
    from app.models.inventario_model import ReordenAutomatico
    
    reorden = db.query(ReordenAutomatico).filter(ReordenAutomatico.id == reorden_id).first()
    
    if not reorden:
        raise HTTPException(status_code=404, detail="Reorden no encontrado")
    
    reorden.estado = "aprobado"
    reorden.aprobado_por = current_user.id
    reorden.fecha_aprobacion = datetime.utcnow()
    if notas:
        reorden.notas = notas
    
    db.commit()
    db.refresh(reorden)
    
    return reorden

@router.patch("/reordenes/{reorden_id}/rechazar", response_model=ReordenAutomaticoOut, summary="Rechazar reorden")
def rechazar_reorden(
    reorden_id: int,
    notas: Optional[str] = Query(None, description="Motivo del rechazo"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden rechazar
):
    """
    Rechaza un reorden automático.
    Solo usuarios administradores pueden rechazar reordenes.
    """
    from app.models.inventario_model import ReordenAutomatico
    
    reorden = db.query(ReordenAutomatico).filter(ReordenAutomatico.id == reorden_id).first()
    
    if not reorden:
        raise HTTPException(status_code=404, detail="Reorden no encontrado")
    
    reorden.estado = "rechazado"
    reorden.aprobado_por = current_user.id
    reorden.fecha_aprobacion = datetime.utcnow()
    if notas:
        reorden.notas = notas
    
    db.commit()
    db.refresh(reorden)
    
    return reorden

# === RESUMEN Y ESTADÍSTICAS ===

@router.get("/resumen", response_model=InventarioResumen, summary="Resumen del inventario")
def obtener_resumen(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un resumen del estado del inventario.
    """
    return InventarioService.obtener_resumen(db)

@router.get("/estadisticas", response_model=InventarioEstadisticas, summary="Estadísticas del inventario")
def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden ver estadísticas
):
    """
    Obtiene estadísticas detalladas del inventario.
    Solo usuarios administradores pueden ver estadísticas.
    """
    # Implementación básica - se puede expandir
    resumen = InventarioService.obtener_resumen(db)
    
    return InventarioEstadisticas(
        total_productos=resumen.total_productos,
        productos_configurados=0,  # Se calcularía
        alertas_por_tipo={},
        movimientos_por_tipo={},
        valor_inventario_por_categoria={},
        productos_mas_movidos=[],
        tendencia_stock=[],
        alertas_resueltas_mes=0,
        tiempo_promedio_resolucion=0.0
    )

# === PROCESAMIENTO AUTOMÁTICO ===

@router.post("/procesar-alertas", summary="Procesar alertas pendientes")
def procesar_alertas(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden procesar
):
    """
    Procesa todas las alertas pendientes del sistema.
    Útil para ejecutar como tarea programada.
    """
    procesadas = InventarioService.procesar_alertas_pendientes(db)
    
    return {
        "message": f"Alertas procesadas: {procesadas} productos",
        "procesadas": procesadas
    }

@router.post("/generar-reorden/{producto_id}", response_model=ReordenAutomaticoOut, summary="Generar reorden automático")
def generar_reorden(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden generar
):
    """
    Genera un reorden automático para un producto específico.
    Solo usuarios administradores pueden generar reordenes.
    """
    reorden = InventarioService.generar_reorden_automatico(db, producto_id)
    
    if not reorden:
        raise HTTPException(
            status_code=400, 
            detail="No se puede generar reorden para este producto (no configurado o stock suficiente)"
        )
    
    return reorden
