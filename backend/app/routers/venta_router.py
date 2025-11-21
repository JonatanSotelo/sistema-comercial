from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.deps import get_current_user
from app.db.database import get_db
from app.schemas.venta_schema import VentaCreate, VentaOut
from app.services.venta_service import (
    crear_venta, listar_ventas, obtener_venta, eliminar_venta, actualizar_venta  # 👈 faltaba
)
from app.models.user_model import User

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("/", response_model=dict)
def listar(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return listar_ventas(db, page=page, per_page=per_page, search=search)

@router.get("/{venta_id}", response_model=VentaOut)
def obtener(venta_id: int, db: Session = Depends(get_db)):
    v = obtener_venta(db, venta_id)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v

@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: VentaCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return crear_venta(db, data, user=user, request=request)

@router.put("/{venta_id}", response_model=VentaOut,
            dependencies=[Depends(get_current_user)])  # 👈 proteger PUT
def actualizar(venta_id: int, data: VentaCreate, db: Session = Depends(get_db)):
    v = actualizar_venta(db, venta_id, data)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v

@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_user)])
def eliminar(venta_id: int, db: Session = Depends(get_db)):
    ok = eliminar_venta(db, venta_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return None


# ============ REMITOS ============

@router.get("/{venta_id}/remito", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
def get_remito_html(venta_id: int, db: Session = Depends(get_db)):
    """Generar remito HTML imprimible"""
    from app.services.remito_service import generate_remito_html
    
    venta = obtener_venta(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    html = generate_remito_html(venta)
    return HTMLResponse(content=html)


@router.get("/{venta_id}/remito.pdf", response_class=Response, dependencies=[Depends(get_current_user)])
def get_remito_pdf(venta_id: int, db: Session = Depends(get_db)):
    """Generar remito PDF con ReportLab"""
    from app.services.remito_service import generate_remito_pdf
    
    venta = obtener_venta(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    pdf_content = generate_remito_pdf(venta)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=remito_{venta_id:06d}.pdf"}
    )
