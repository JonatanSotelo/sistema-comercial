# 4. RUTA - routers/venta_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.venta_schema import VentaCreate, VentaOut
from app.services.venta_service import (
    crear_venta, listar_ventas, obtener_venta, actualizar_venta, eliminar_venta
)

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def crear(data: VentaCreate, db: Session = Depends(get_db)):
    try:
        return crear_venta(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{venta_id}", response_model=VentaOut)
def obtener(venta_id: int, db: Session = Depends(get_db)):
    v = obtener_venta(db, venta_id)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v

@router.put("/{venta_id}", response_model=VentaOut)
def actualizar(venta_id: int, data: VentaCreate, db: Session = Depends(get_db)):
    v = actualizar_venta(db, venta_id, data)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v

@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(venta_id: int, db: Session = Depends(get_db)):
    ok = eliminar_venta(db, venta_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return None

@router.get("/{venta_id}", response_model=VentaOut)
def obtener(venta_id: int, db: Session = Depends(get_db)):
    v = obtener_venta(db, venta_id)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v