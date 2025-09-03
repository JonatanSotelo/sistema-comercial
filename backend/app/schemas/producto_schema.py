# app/schemas/producto_schema.py
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
from pydantic.config import ConfigDict  # Pydantic v2

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None

class ProductoOut(ProductoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ProductoPageOut(BaseModel):
    items: List[ProductoOut]
    total: int
    page: int
    size: int
