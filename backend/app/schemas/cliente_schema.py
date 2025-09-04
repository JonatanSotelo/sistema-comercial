from typing import Optional
from pydantic import BaseModel, EmailStr

class ClienteBase(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

class ClienteOut(ClienteBase):
    id: int
    class Config:
        from_attributes = True  # pydantic v2
