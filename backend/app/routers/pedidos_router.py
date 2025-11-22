from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.deps import get_current_user
from app.db.database import get_db
from app.schemas.pedido_schema import (
    PedidoCreate,
    PedidoUpdate,
    PedidoEstadoChange,
    PedidoOut,
    PedidoFacturarResponse,
)
from app.services.pedidos_service import (
    create_pedido,
    obtener_pedido,
    listar_pedidos,
    update_pedido,
    change_estado,
    facturar_pedido,
    bulk_change_estado,
)
from app.services.pedidos_packing_service import generate_packing_html, generate_packing_pdf
from app.models.user_model import User

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/", response_model=dict)
def listar(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    cliente_id: Optional[int] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    """Listar pedidos con filtros opcionales"""
    return listar_pedidos(
        db,
        page=page,
        per_page=size,
        search=q,
        estado=estado,
        cliente_id=cliente_id,
        desde=desde,
        hasta=hasta,
    )


@router.get("/{pedido_id}", response_model=PedidoOut)
def obtener(pedido_id: int, db: Session = Depends(get_db)):
    """Obtener un pedido por ID"""
    pedido = obtener_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: PedidoCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Crear un nuevo pedido"""
    return create_pedido(db, data, user=user, request=request)


@router.put("/{pedido_id}", response_model=PedidoOut)
def actualizar(
    pedido_id: int,
    data: PedidoUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Actualizar un pedido (solo si estado lo permite)"""
    return update_pedido(db, pedido_id, data, user=user, request=request)


@router.post("/{pedido_id}/estado", response_model=PedidoOut)
def cambiar_estado(
    pedido_id: int,
    data: PedidoEstadoChange,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cambiar el estado de un pedido"""
    return change_estado(db, pedido_id, data.estado, user=user, request=request, background_tasks=background_tasks)


@router.post("/{pedido_id}/facturar", response_model=PedidoFacturarResponse)
def facturar(
    pedido_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Facturar un pedido: crea una venta y ajusta el stock"""
    return facturar_pedido(db, pedido_id, user=user, request=request)


@router.get("/{pedido_id}/packing", response_class=HTMLResponse)
def get_packing_html(
    pedido_id: int,
    db: Session = Depends(get_db),
):
    """Obtener packing slip en HTML para imprimir"""
    return generate_packing_html(db, pedido_id)


@router.get("/{pedido_id}/packing.pdf")
def get_packing_pdf(
    pedido_id: int,
    db: Session = Depends(get_db),
):
    """Obtener packing slip en PDF"""
    pdf_bytes = generate_packing_pdf(db, pedido_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=packing_pedido_{pedido_id}.pdf"
        }
    )


@router.get("/{pedido_id}/label.pdf", dependencies=[Depends(get_current_user)])
def get_label_pdf(
    pedido_id: int,
    db: Session = Depends(get_db),
):
    """Generar etiqueta con QR para el pedido"""
    from app.services.label_service import generate_label_pdf
    from app.services.pedidos_service import obtener_pedido
    
    pedido = obtener_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    pdf_content = generate_label_pdf(pedido)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=label_pedido_{pedido_id:06d}.pdf"
        }
    )


@router.post("/bulk_estado")
def bulk_cambiar_estado(
    pedido_ids: list[int],
    nuevo_estado: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cambiar estado de múltiples pedidos"""
    from app.models.pedido_model import EstadoPedido
    try:
        estado_enum = EstadoPedido(nuevo_estado)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Estado inválido: {nuevo_estado}")
    
    return bulk_change_estado(db, pedido_ids, estado_enum, user=user, request=request)

