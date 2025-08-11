from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db, Base, engine
from app.schemas.user_schema import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services.user_service import (
    crear_usuario, listar_usuarios, obtener_usuario,
    actualizar_usuario, eliminar_usuario
)

# Crear tablas si no existen (simple para dev)
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear(data: UsuarioCreate, db: Session = Depends(get_db)):
    return crear_usuario(db, data)

@router.get("/", response_model=List[UsuarioOut])
def listar(db: Session = Depends(get_db)):
    return listar_usuarios(db)

@router.get("/{user_id}", response_model=UsuarioOut)
def obtener(user_id: int, db: Session = Depends(get_db)):
    usuario = obtener_usuario(db, user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/{user_id}", response_model=UsuarioOut)
def actualizar(user_id: int, data: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = actualizar_usuario(db, user_id, data)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(user_id: int, db: Session = Depends(get_db)):
    ok = eliminar_usuario(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return None
