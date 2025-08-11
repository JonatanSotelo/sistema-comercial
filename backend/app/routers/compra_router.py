from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.compra_schema import CompraCreate, CompraOut, StockOut
from app.services.compra_service import crear_compra, obtener_compra, stock_actual

router = APIRouter(prefix="/compras", tags=["Compras"])

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
