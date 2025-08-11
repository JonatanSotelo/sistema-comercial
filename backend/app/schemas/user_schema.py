from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict  # <-- nuevo import


class UsuarioBase(BaseModel):
    username: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioOut(UsuarioBase):
    id: int

    class Config:
        model_config = ConfigDict(from_attributes=True)

class UsuarioUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
