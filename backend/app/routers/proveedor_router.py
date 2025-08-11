from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorUpdate, ProveedorOut
from app.services.proveedor_service import (
    crear_proveedor, listar_proveedores, obtener_proveedor,
    actualizar_proveedor, eliminar_proveedor
)

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

@router.post("/", response_model=ProveedorOut, status_code=status.HTTP_201_CREATED)
def crear(data: ProveedorCreate, db: Session = Depends(get_db)):
    return crear_proveedor(db, data)

@router.get("/", response_model=List[ProveedorOut])
def listar(db: Session = Depends(get_db)):
    return listar_proveedores(db)

@router.get("/{prov_id}", response_model=ProveedorOut)
def obtener(prov_id: int, db: Session = Depends(get_db)):
    p = obtener_proveedor(db, prov_id)
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return p

@router.put("/{prov_id}", response_model=ProveedorOut)
def actualizar(prov_id: int, data: ProveedorUpdate, db: Session = Depends(get_db)):
    p = actualizar_proveedor(db, prov_id, data)
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return p

@router.delete("/{prov_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(prov_id: int, db: Session = Depends(get_db)):
    ok = eliminar_proveedor(db, prov_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return None
