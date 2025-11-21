from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.core.deps import get_current_user
from app.schemas.compra_schema import CompraCreate, CompraOut, StockOut
from app.services.compra_service import crear_compra, obtener_compra, stock_actual, listar_compras
from app.models.user_model import User

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.get("/", response_model=dict)
def listar(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return listar_compras(db, page=page, per_page=per_page, search=search)

@router.post("/", response_model=CompraOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: CompraCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return crear_compra(db, data, user=user, request=request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e

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
