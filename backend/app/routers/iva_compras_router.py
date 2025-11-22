# app/routers/iva_compras_router.py
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.deps import get_db, require_user
from app.models.user_model import User
from app.models.purchase_invoice_model import PurchaseInvoice
from app.services.libro_iva_compras_service import (
    crear_purchase_invoice,
    actualizar_purchase_invoice,
    eliminar_purchase_invoice,
    listar_purchase_invoices,
    export_libro_iva_compras,
)
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/iva-compras", tags=["Libro IVA Compras"])


# Schemas
class PurchaseInvoiceCreate(BaseModel):
    proveedor_id: Optional[int] = None
    proveedor_nombre: Optional[str] = None
    fecha: date
    tipo_cbte: int
    pto_vta: int
    nro_cbte: int
    doc_tipo: Optional[int] = None
    doc_nro: Optional[str] = None
    imp_neto: float
    imp_iva: float = 0.0
    imp_exento: float = 0.0
    imp_total: float
    alicuota_principal: float = 21.0
    compra_id: Optional[int] = None


class PurchaseInvoiceUpdate(BaseModel):
    proveedor_id: Optional[int] = None
    proveedor_nombre: Optional[str] = None
    fecha: Optional[date] = None
    tipo_cbte: Optional[int] = None
    pto_vta: Optional[int] = None
    nro_cbte: Optional[int] = None
    doc_tipo: Optional[int] = None
    doc_nro: Optional[str] = None
    imp_neto: Optional[float] = None
    imp_iva: Optional[float] = None
    imp_exento: Optional[float] = None
    imp_total: Optional[float] = None
    alicuota_principal: Optional[float] = None
    compra_id: Optional[int] = None


class PurchaseInvoiceOut(BaseModel):
    id: int
    proveedor_id: Optional[int]
    proveedor_nombre: Optional[str]
    fecha: date
    tipo_cbte: int
    pto_vta: int
    nro_cbte: int
    doc_tipo: Optional[int]
    doc_nro: Optional[str]
    imp_neto: Decimal
    imp_iva: Decimal
    imp_exento: Decimal
    imp_total: Decimal
    alicuota_principal: Decimal
    compra_id: Optional[int]
    
    class Config:
        from_attributes = True


@router.post("", response_model=PurchaseInvoiceOut, summary="Crear factura de compra")
@router.post("/", response_model=PurchaseInvoiceOut, summary="Crear factura de compra")
def crear_factura_compra(
    data: PurchaseInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Crea un registro manual de factura de compra para el Libro IVA"""
    invoice = crear_purchase_invoice(
        db=db,
        proveedor_id=data.proveedor_id,
        proveedor_nombre=data.proveedor_nombre,
        fecha=data.fecha,
        tipo_cbte=data.tipo_cbte,
        pto_vta=data.pto_vta,
        nro_cbte=data.nro_cbte,
        doc_tipo=data.doc_tipo,
        doc_nro=data.doc_nro,
        imp_neto=data.imp_neto,
        imp_iva=data.imp_iva,
        imp_exento=data.imp_exento,
        imp_total=data.imp_total,
        alicuota_principal=data.alicuota_principal,
        compra_id=data.compra_id,
    )
    return invoice


@router.get("", response_model=List[PurchaseInvoiceOut], summary="Listar facturas de compra")
@router.get("/", response_model=List[PurchaseInvoiceOut], summary="Listar facturas de compra")
def listar_facturas_compra(
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    proveedor_id: Optional[int] = Query(None),
    tipo_cbte: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Lista facturas de compra con filtros"""
    from datetime import datetime as dt
    
    dt_desde = dt.strptime(fecha_desde, "%Y-%m-%d").date() if fecha_desde else None
    dt_hasta = dt.strptime(fecha_hasta, "%Y-%m-%d").date() if fecha_hasta else None
    
    invoices, total = listar_purchase_invoices(
        db=db,
        fecha_desde=dt_desde,
        fecha_hasta=dt_hasta,
        proveedor_id=proveedor_id,
        tipo_cbte=tipo_cbte,
        page=page,
        size=size,
    )
    
    return invoices


@router.put("/{invoice_id}", response_model=PurchaseInvoiceOut, summary="Actualizar factura de compra")
def actualizar_factura_compra(
    invoice_id: int,
    data: PurchaseInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Actualiza un registro de factura de compra"""
    invoice = actualizar_purchase_invoice(db=db, invoice_id=invoice_id, data=data.dict(exclude_unset=True))
    return invoice


@router.delete("/{invoice_id}", summary="Eliminar factura de compra")
def eliminar_factura_compra(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Elimina un registro de factura de compra"""
    eliminar_purchase_invoice(db=db, invoice_id=invoice_id)
    return {"message": "Factura de compra eliminada"}


@router.get("/export", response_class=Response, summary="Exportar Libro IVA Compras")
def exportar_libro_iva(
    desde: str = Query(..., description="Fecha desde (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha hasta (YYYY-MM-DD)"),
    format: str = Query("csv", regex="^(csv|xlsx)$"),
    proveedor_id: Optional[int] = Query(None),
    tipo_cbte: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Exporta el Libro IVA Compras en formato CSV o XLSX.
    
    Incluye todas las facturas de compra registradas en el período especificado.
    """
    try:
        archivo_bytes = export_libro_iva_compras(
            db=db,
            fecha_desde=desde,
            fecha_hasta=hasta,
            formato=format,
            proveedor_id=proveedor_id,
            tipo_cbte=tipo_cbte,
        )
        
        media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = format
        
        return Response(
            content=archivo_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="libro_iva_compras_{desde}_{hasta}.{extension}"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

