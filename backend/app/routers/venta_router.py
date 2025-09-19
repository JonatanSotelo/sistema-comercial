from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_current_user
from app.db.database import get_db
from app.schemas.venta_schema import VentaCreate, VentaOut
from app.services.venta_service import (
    crear_venta, listar_ventas, obtener_venta, eliminar_venta, actualizar_venta  # 👈 faltaba
)

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.get("/", response_model=List[VentaOut])
def listar(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return listar_ventas(db, page=page, per_page=per_page, search=search)

@router.get("/{venta_id}", response_model=VentaOut)
def obtener(venta_id: int, db: Session = Depends(get_db)):
    v = obtener_venta(db, venta_id)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v

@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_user)])
def crear(data: VentaCreate, db: Session = Depends(get_db)):
    return crear_venta(db, data)

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
