from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user
from app.db.database import get_db
from app.schemas.compra_schema import CompraCreate, CompraOut, StockOut
from app.services.compra_service import crear_compra, obtener_compra, stock_actual, listar_compras, eliminar_compra

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.get("/", response_model=List[CompraOut])
def listar(
    q: Optional[str] = Query(None, description="Búsqueda"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return listar_compras(db, page=page, per_page=per_page, search=q)

@router.post("/", response_model=CompraOut, status_code=status.HTTP_201_CREATED)
def crear(data: CompraCreate, db: Session = Depends(get_db)):
    try:
        return crear_compra(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{compra_id}", response_model=CompraOut)
def obtener(compra_id: int, db: Session = Depends(get_db)):
    c = obtener_compra(db, compra_id)
    if not c:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return c

@router.get("/stock/{producto_id}", response_model=StockOut)
def stock(producto_id: int, db: Session = Depends(get_db)):
    s = stock_actual(db, producto_id)
    return StockOut(producto_id=producto_id, stock=s)

@router.patch("/{compra_id}/estado", response_model=CompraOut,
              dependencies=[Depends(get_current_user)])
def cambiar_estado(compra_id: int, estado: str, db: Session = Depends(get_db)):
    """Cambia el estado de una compra."""
    from app.models.compra_model import Compra
    compra = db.query(Compra).filter(Compra.id == compra_id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    if estado not in ["pendiente", "completada", "cancelada"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    compra.estado = estado
    db.commit()
    db.refresh(compra)
    return compra


@router.delete("/{compra_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_user)])
def eliminar(compra_id: int, db: Session = Depends(get_db)):
    ok = eliminar_compra(db, compra_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return None
