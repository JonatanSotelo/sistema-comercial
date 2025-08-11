from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ClienteOut(ClienteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
