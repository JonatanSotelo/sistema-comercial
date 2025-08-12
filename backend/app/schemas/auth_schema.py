# app/schemas/auth_schema.py
from pydantic import BaseModel
from pydantic.config import ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    model_config = ConfigDict(from_attributes=True)

class LoginInput(BaseModel):
    username: str
    password: str
