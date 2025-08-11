from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db, Base, engine
from app.schemas.producto_schema import ProductoCreate, ProductoUpdate, ProductoOut
from app.services.producto_service import (
    crear_producto, obtener_productos, obtener_producto,
    actualizar_producto, eliminar_producto
)

# Crear tablas automáticamente (solo en desarrollo)
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=List[ProductoOut])
def listar(db: Session = Depends(get_db)):
    return obtener_productos(db)

@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear(data: ProductoCreate, db: Session = Depends(get_db)):
    return crear_producto(db, data)

@router.get("/{prod_id}", response_model=ProductoOut)
def obtener(prod_id: int, db: Session = Depends(get_db)):
    prod = obtener_producto(db, prod_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

@router.put("/{prod_id}", response_model=ProductoOut)
def actualizar(prod_id: int, data: ProductoUpdate, db: Session = Depends(get_db)):
    prod = actualizar_producto(db, prod_id, data)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

@router.delete("/{prod_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(prod_id: int, db: Session = Depends(get_db)):
    ok = eliminar_producto(db, prod_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None
