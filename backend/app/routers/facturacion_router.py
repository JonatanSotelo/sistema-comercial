# app/routers/facturacion_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user, require_user
from app.models.user_model import User
from app.models.factura_model import Factura
from app.schemas.factura_schema import FacturaOut, FacturaEmitirRequest
from app.services.facturacion_service import emitir_factura

router = APIRouter(prefix="/facturacion", tags=["Facturación"])


@router.post("/emitir", response_model=FacturaOut, summary="Emitir factura electrónica AFIP")
def emitir_factura_endpoint(
    data: FacturaEmitirRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Emite una factura electrónica AFIP desde una venta o pedido.
    
    - **venta_id**: ID de la venta (al menos uno de venta_id o pedido_id requerido)
    - **pedido_id**: ID del pedido
    - **tipo_cbte**: Tipo de comprobante (1=A, 6=B, 11=C)
    - **pto_vta**: Punto de venta (opcional, default: config)
    
    Retorna la factura creada con CAE.
    """
    factura = emitir_factura(
        db=db,
        venta_id=data.venta_id,
        pedido_id=data.pedido_id,
        tipo_cbte=data.tipo_cbte,
        pto_vta=data.pto_vta,
        user=current_user,
        request=request,
    )
    return factura


@router.get("", response_model=List[FacturaOut], summary="Listar facturas")
@router.get("/", response_model=List[FacturaOut], summary="Listar facturas")
def listar_facturas(
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    tipo_cbte: Optional[int] = Query(None, description="Tipo de comprobante"),
    pto_vta: Optional[int] = Query(None, description="Punto de venta"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Lista facturas con filtros opcionales.
    
    - **fecha_desde**: Filtrar desde fecha (YYYY-MM-DD)
    - **fecha_hasta**: Filtrar hasta fecha (YYYY-MM-DD)
    - **tipo_cbte**: Filtrar por tipo de comprobante
    - **pto_vta**: Filtrar por punto de venta
    - **page**: Página (default: 1)
    - **size**: Tamaño de página (default: 20)
    """
    query = db.query(Factura).options(joinedload(Factura.items))
    
    # Filtros
    if fecha_desde:
        try:
            dt_desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
            query = query.filter(Factura.created_at >= dt_desde)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha_desde inválido (YYYY-MM-DD)")
    
    if fecha_hasta:
        try:
            dt_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            # Agregar un día para incluir todo el día hasta
            dt_hasta = dt_hasta.replace(hour=23, minute=59, second=59)
            query = query.filter(Factura.created_at <= dt_hasta)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha_hasta inválido (YYYY-MM-DD)")
    
    if tipo_cbte:
        query = query.filter(Factura.tipo_cbte == tipo_cbte)
    
    if pto_vta:
        query = query.filter(Factura.pto_vta == pto_vta)
    
    # Ordenar por fecha desc
    query = query.order_by(desc(Factura.created_at))
    
    # Paginación
    offset = (page - 1) * size
    facturas = query.offset(offset).limit(size).all()
    
    return facturas


@router.get("/{factura_id}", response_model=FacturaOut, summary="Obtener factura por ID")
def obtener_factura(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Obtiene una factura por su ID con todos sus ítems."""
    factura = db.query(Factura).options(joinedload(Factura.items)).filter(Factura.id == factura_id).first()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return factura


@router.get("/{factura_id}/pdf", response_class=Response, summary="Descargar PDF de factura")
def descargar_pdf_factura(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Genera y descarga el PDF de una factura con QR AFIP.
    
    El PDF incluye todos los datos fiscales requeridos y el código QR para validación en AFIP.
    """
    from app.services.factura_pdf_service import generate_factura_pdf
    
    pdf_bytes = generate_factura_pdf(db, factura_id)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=factura_{factura_id}.pdf"}
    )

