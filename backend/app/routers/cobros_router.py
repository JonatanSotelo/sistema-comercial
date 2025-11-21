# app/routers/cobros_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user, require_user
from app.models.user_model import User
from app.models.cobro_model import Cobro
from app.services.cobros_service import crear_cobro, anular_cobro, get_saldo_venta, get_saldo_cliente
from app.services.recibo_pdf_service import generate_recibo_pdf
from pydantic import BaseModel, Field

router = APIRouter(prefix="/cobros", tags=["Cobros"])


# Schemas
class CobroCreateRequest(BaseModel):
    venta_id: int
    medio: str
    importe: float = Field(..., gt=0)
    referencia: Optional[str] = None
    observaciones: Optional[str] = None


class CobroOut(BaseModel):
    id: int
    created_at: datetime
    venta_id: int
    medio: str
    importe: float
    referencia: Optional[str]
    observaciones: Optional[str]
    estado: str
    
    class Config:
        from_attributes = True


@router.post("", response_model=CobroOut, summary="Crear cobro")
@router.post("/", response_model=CobroOut, summary="Crear cobro")
def crear_cobro_endpoint(
    data: CobroCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Crea un cobro para una venta.
    
    - **venta_id**: ID de la venta
    - **medio**: Medio de cobro (EFECTIVO, TRANSFERENCIA, MERCADOPAGO, TARJETA, CHEQUE, OTRO)
    - **importe**: Importe cobrado (debe ser > 0)
    - **referencia**: Referencia opcional (nro de transferencia, MP, etc.)
    - **observaciones**: Observaciones adicionales
    """
    cobro = crear_cobro(
        db=db,
        venta_id=data.venta_id,
        medio=data.medio,
        importe=data.importe,
        referencia=data.referencia,
        observaciones=data.observaciones,
        user=current_user,
        request=request,
    )
    return cobro


@router.get("", response_model=List[CobroOut], summary="Listar cobros")
@router.get("/", response_model=List[CobroOut], summary="Listar cobros")
def listar_cobros(
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    medio: Optional[str] = Query(None, description="Medio de cobro"),
    venta_id: Optional[int] = Query(None, description="ID de venta"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Lista cobros con filtros opcionales"""
    query = db.query(Cobro).options(joinedload(Cobro.venta))
    
    filters = []
    if fecha_desde:
        try:
            dt_desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
            filters.append(Cobro.created_at >= dt_desde)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha_desde inválido")
    
    if fecha_hasta:
        try:
            dt_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            dt_hasta = dt_hasta.replace(hour=23, minute=59, second=59)
            filters.append(Cobro.created_at <= dt_hasta)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha_hasta inválido")
    
    if medio:
        filters.append(Cobro.medio == medio)
    
    if venta_id:
        filters.append(Cobro.venta_id == venta_id)
    
    if filters:
        query = query.filter(and_(*filters))
    
    query = query.order_by(desc(Cobro.created_at))
    
    offset = (page - 1) * size
    cobros = query.offset(offset).limit(size).all()
    
    return cobros


@router.post("/{cobro_id}/anular", response_model=CobroOut, summary="Anular cobro")
def anular_cobro_endpoint(
    cobro_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Anula un cobro (no lo borra, lo marca como ANULADO).
    
    - **cobro_id**: ID del cobro a anular
    """
    cobro = anular_cobro(db=db, cobro_id=cobro_id, user=current_user, request=request)
    return cobro


@router.get("/{cobro_id}/pdf", response_class=Response, summary="Descargar recibo PDF")
def descargar_recibo_pdf(
    cobro_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Genera y descarga el PDF del recibo de cobro.
    
    Incluye:
    - Número de recibo con serie
    - Datos del cliente
    - Detalle del pago
    - Saldo pendiente post-cobro
    """
    pdf_bytes = generate_recibo_pdf(db, cobro_id)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=recibo_{cobro_id}.pdf"}
    )


@router.get("/venta/{venta_id}/saldo", summary="Obtener saldo de venta")
def obtener_saldo_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Calcula el saldo pendiente de una venta.
    Saldo = Total Venta - Suma(Cobros Confirmados)
    """
    saldo = get_saldo_venta(db, venta_id)
    return {"venta_id": venta_id, "saldo": saldo}


@router.get("/cliente/{cliente_id}/saldo", summary="Obtener saldo de cliente")
def obtener_saldo_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Calcula el saldo total pendiente de un cliente.
    Suma los saldos de todas sus ventas.
    """
    saldo = get_saldo_cliente(db, cliente_id)
    return {"cliente_id": cliente_id, "saldo": saldo}

