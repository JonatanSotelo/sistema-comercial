from pydantic import BaseModel
from typing import List, Optional
from pydantic.config import ConfigDict
from datetime import datetime

class VentaItemIn(BaseModel):
    producto_id: int
    cantidad: float
    # Permite fijar precio explícito; si no viene, se toma del producto
    precio_unitario: Optional[float] = None

class VentaCreate(BaseModel):
    cliente_id: Optional[int] = None
    items: List[VentaItemIn]
    fecha: Optional[datetime] = None

class VentaItemOut(BaseModel):
    id: int
    producto_id: int
    cantidad: float
    precio_unitario: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)

class VentaOut(BaseModel):
    id: int
    cliente_id: Optional[int] = None
    fecha: datetime
    total: float
    items: List[VentaItemOut]
    model_config = ConfigDict(from_attributes=True)
