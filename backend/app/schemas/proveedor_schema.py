from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic.config import ConfigDict

class ProveedorBase(BaseModel):
    nombre: str
    cuit: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = True

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    cuit: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

class ProveedorOut(ProveedorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
