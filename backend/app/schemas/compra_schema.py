from pydantic import BaseModel
from typing import List, Optional
from pydantic.config import ConfigDict

from datetime import datetime

class CompraItemIn(BaseModel):
    producto_id: int
    cantidad: float
    costo_unitario: float

class CompraCreate(BaseModel):
    proveedor_id: int
    items: List[CompraItemIn]
    fecha: Optional[datetime] = None  # opcional, por si querés setearla

class CompraItemOut(BaseModel):
    id: int
    producto_id: int
    cantidad: float
    costo_unitario: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)

class CompraOut(BaseModel):
    id: int
    proveedor_id: int
    fecha: datetime
    total: float
    items: List[CompraItemOut]
    model_config = ConfigDict(from_attributes=True)

class StockOut(BaseModel):
    producto_id: int
    stock: float
