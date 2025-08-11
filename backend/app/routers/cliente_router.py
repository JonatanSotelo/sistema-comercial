from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteOut
from app.services.cliente_service import (
    crear_cliente, listar_clientes, obtener_cliente,
    actualizar_cliente, eliminar_cliente,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.get("/", response_model=List[ClienteOut])
def listar(db: Session = Depends(get_db)):
    return listar_clientes(db)

@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def crear(data: ClienteCreate, db: Session = Depends(get_db)):
    return crear_cliente(db, data)

@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener(cliente_id: int, db: Session = Depends(get_db)):
    c = obtener_cliente(db, cliente_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return c

@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar(cliente_id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    c = actualizar_cliente(db, cliente_id, data)
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return c

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(cliente_id: int, db: Session = Depends(get_db)):
    ok = eliminar_cliente(db, cliente_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return None
