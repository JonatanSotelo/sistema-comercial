from typing import Optional
from pydantic import BaseModel, EmailStr

class ProveedorBase(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None

class ProveedorOut(ProveedorBase):
    id: int
    class Config:
        from_attributes = True  # pydantic v2
