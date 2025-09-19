# app/schemas/producto_schema.py
from __future__ import annotations

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict  # Pydantic v2

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    codigo: str
    categoria: str
    precio: float
    costo: float
    stock: int = 0
    stock_minimo: int = 0
    activo: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    codigo: Optional[str] = None
    categoria: Optional[str] = None
    precio: Optional[float] = None
    costo: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    activo: Optional[bool] = None

class ProductoOut(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True, json_encoders={
        datetime: lambda v: v.isoformat()
    })

class ProductoPageOut(BaseModel):
    items: List[ProductoOut]
    total: int
    page: int
    size: int
