# app/routers/descuento_router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db
from app.core.deps import require_user, require_admin
from app.services.descuento_service import DescuentoService
from app.schemas.descuento_schema import (
    DescuentoCreate, DescuentoUpdate, DescuentoOut, DescuentoAplicacion,
    DescuentoResultado, DescuentoEstadisticas, DescuentoFiltros,
    DescuentoUsoOut, TipoDescuento, EstadoDescuento
)

router = APIRouter(prefix="/descuentos", tags=["Descuentos"])

@router.post("", response_model=DescuentoOut, summary="Crear descuento")
def crear_descuento(
    descuento: DescuentoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear descuentos
):
    """
    Crea un nuevo descuento en el sistema.
    Solo usuarios administradores pueden crear descuentos.
    """
    # Verificar que el código no exista
    descuento_existente = DescuentoService.obtener_descuento_por_codigo(db, descuento.codigo)
    if descuento_existente:
        raise HTTPException(
            status_code=400, 
            detail="Ya existe un descuento con este código"
        )
    
    return DescuentoService.crear_descuento(db, descuento, current_user.id)

@router.get("", response_model=List[DescuentoOut], summary="Listar descuentos")
def listar_descuentos(
    skip: int = Query(0, ge=0, description="Número de descuentos a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de descuentos a retornar"),
    codigo: Optional[str] = Query(None, description="Filtrar por código"),
    tipo: Optional[TipoDescuento] = Query(None, description="Filtrar por tipo"),
    estado: Optional[EstadoDescuento] = Query(None, description="Filtrar por estado"),
    es_activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista descuentos con filtros opcionales.
    Los usuarios pueden ver descuentos activos, los admins pueden ver todos.
    """
    filtros = DescuentoFiltros(
        codigo=codigo,
        tipo=tipo,
        estado=estado,
        es_activo=es_activo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        cliente_id=cliente_id,
        producto_id=producto_id
    )
    
    # Si no es admin, solo mostrar descuentos activos
    if current_user.role != "admin":
        filtros.estado = EstadoDescuento.ACTIVO
        filtros.es_activo = True
    
    return DescuentoService.obtener_descuentos(db, filtros, skip, limit)

@router.get("/{descuento_id}", response_model=DescuentoOut, summary="Obtener descuento")
def obtener_descuento(
    descuento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un descuento específico por ID.
    """
    descuento = DescuentoService.obtener_descuento(db, descuento_id)
    
    if not descuento:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    # Si no es admin, solo mostrar descuentos activos
    if current_user.role != "admin" and not descuento.es_activo:
        raise HTTPException(status_code=403, detail="No tienes acceso a este descuento")
    
    return descuento

@router.put("/{descuento_id}", response_model=DescuentoOut, summary="Actualizar descuento")
def actualizar_descuento(
    descuento_id: int,
    descuento_update: DescuentoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza un descuento existente.
    Solo usuarios administradores pueden actualizar descuentos.
    """
    descuento = DescuentoService.actualizar_descuento(db, descuento_id, descuento_update)
    
    if not descuento:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    return descuento

@router.delete("/{descuento_id}", summary="Eliminar descuento")
def eliminar_descuento(
    descuento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden eliminar
):
    """
    Elimina un descuento del sistema.
    Solo usuarios administradores pueden eliminar descuentos.
    """
    descuento = DescuentoService.obtener_descuento(db, descuento_id)
    
    if not descuento:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    # Verificar si tiene usos
    if descuento.usos_actuales > 0:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar un descuento que ya ha sido usado"
        )
    
    db.delete(descuento)
    db.commit()
    
    return {"message": "Descuento eliminado correctamente"}

@router.post("/aplicar", response_model=DescuentoResultado, summary="Aplicar descuento")
def aplicar_descuento(
    aplicacion: DescuentoAplicacion,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Aplica un descuento a una compra.
    Retorna el resultado de la aplicación del descuento.
    """
    # Obtener IP del cliente
    ip_cliente = request.client.host if request.client else None
    
    # Aplicar descuento
    resultado = DescuentoService.aplicar_descuento(db, aplicacion)
    
    # Si es aplicable, registrar el uso
    if resultado.aplicable and resultado.descuento:
        DescuentoService.registrar_uso_descuento(
            db=db,
            descuento_id=resultado.descuento.id,
            cliente_id=aplicacion.cliente_id,
            venta_id=None,  # Se actualizará cuando se cree la venta
            monto_original=aplicacion.monto_total,
            monto_descuento=resultado.monto_descuento,
            monto_final=resultado.monto_final,
            ip_cliente=ip_cliente,
            user_agent=request.headers.get("user-agent")
        )
    
    return resultado

@router.get("/codigo/{codigo}", response_model=DescuentoOut, summary="Obtener descuento por código")
def obtener_descuento_por_codigo(
    codigo: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un descuento por su código.
    """
    descuento = DescuentoService.obtener_descuento_por_codigo(db, codigo)
    
    if not descuento:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    # Si no es admin, solo mostrar descuentos activos
    if current_user.role != "admin" and not descuento.es_activo:
        raise HTTPException(status_code=403, detail="No tienes acceso a este descuento")
    
    return descuento

@router.get("/estadisticas", response_model=DescuentoEstadisticas, summary="Estadísticas de descuentos")
def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden ver estadísticas
):
    """
    Obtiene estadísticas detalladas de los descuentos.
    Solo usuarios administradores pueden ver estadísticas.
    """
    return DescuentoService.obtener_estadisticas(db)

@router.get("/usos/{descuento_id}", response_model=List[DescuentoUsoOut], summary="Usos de descuento")
def obtener_usos_descuento(
    descuento_id: int,
    skip: int = Query(0, ge=0, description="Número de usos a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de usos a retornar"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden ver usos
):
    """
    Obtiene el historial de usos de un descuento específico.
    Solo usuarios administradores pueden ver el historial de usos.
    """
    descuento = DescuentoService.obtener_descuento(db, descuento_id)
    
    if not descuento:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    # Obtener usos del descuento
    from app.models.descuento_model import DescuentoUso
    usos = db.query(DescuentoUso)\
        .filter(DescuentoUso.descuento_id == descuento_id)\
        .order_by(DescuentoUso.fecha_uso.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return usos

@router.post("/actualizar-estados", summary="Actualizar estados de descuentos")
def actualizar_estados(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar estados
):
    """
    Actualiza los estados de los descuentos según las fechas.
    Útil para ejecutar como tarea programada.
    """
    actualizados = DescuentoService.actualizar_estados_descuentos(db)
    
    return {
        "message": f"Estados actualizados: {actualizados} descuentos",
        "actualizados": actualizados
    }

@router.get("/disponibles", response_model=List[DescuentoOut], summary="Descuentos disponibles")
def obtener_descuentos_disponibles(
    cliente_id: Optional[int] = Query(None, description="ID del cliente"),
    producto_id: Optional[int] = Query(None, description="ID del producto"),
    monto_minimo: Optional[float] = Query(None, ge=0, description="Monto mínimo de compra"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene descuentos disponibles para un cliente/producto específico.
    Útil para mostrar opciones de descuento en el frontend.
    """
    filtros = DescuentoFiltros(
        estado=EstadoDescuento.ACTIVO,
        es_activo=True,
        cliente_id=cliente_id,
        producto_id=producto_id
    )
    
    descuentos = DescuentoService.obtener_descuentos(db, filtros, 0, 50)
    
    # Filtrar por monto mínimo si se especifica
    if monto_minimo:
        descuentos_disponibles = []
        for descuento in descuentos:
            if not descuento.valor_minimo or descuento.valor_minimo <= monto_minimo:
                descuentos_disponibles.append(descuento)
        return descuentos_disponibles
    
    return descuentos

@router.patch("/{descuento_id}/activar", response_model=DescuentoOut, summary="Activar descuento")
def activar_descuento(
    descuento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden activar
):
    """
    Activa un descuento inactivo.
    """
    descuento = DescuentoService.obtener_descuento(db, descuento_id)
    
    if not descuento:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    descuento.estado = EstadoDescuento.ACTIVO
    descuento.es_activo = True
    
    db.commit()
    db.refresh(descuento)
    
    return descuento

@router.patch("/{descuento_id}/desactivar", response_model=DescuentoOut, summary="Desactivar descuento")
def desactivar_descuento(
    descuento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden desactivar
):
    """
    Desactiva un descuento activo.
    """
    descuento = DescuentoService.obtener_descuento(db, descuento_id)
    
    if not descuento:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    descuento.estado = EstadoDescuento.INACTIVO
    descuento.es_activo = False
    
    db.commit()
    db.refresh(descuento)
    
    return descuento
