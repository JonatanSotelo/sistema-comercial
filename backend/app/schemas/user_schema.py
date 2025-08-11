from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioOut(UsuarioBase):
    id: int

    class Config:
        orm_mode = True

class UsuarioUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
