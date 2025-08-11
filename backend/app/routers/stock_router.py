from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pydantic.config import ConfigDict
from app.db.database import get_db
from app.services.stock_service import stock_actual

class StockOut(BaseModel):
    producto_id: int
    stock: float
    model_config = ConfigDict(from_attributes=True)

router = APIRouter(prefix="/stock", tags=["Stock"])

@router.get("/{producto_id}", response_model=StockOut)
def get_stock(producto_id: int, db: Session = Depends(get_db)):
    s = stock_actual(db, producto_id)
    return StockOut(producto_id=producto_id, stock=s)
