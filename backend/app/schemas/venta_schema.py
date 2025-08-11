# 2. ESQUEMAS - schemas/venta_schema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VentaCreate(BaseModel):
    cliente_id: int
    total: float

class VentaOut(BaseModel):
    id: int
    cliente_id: int
    fecha: datetime
    total: float

    class Config:
        orm_mode = True