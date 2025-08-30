# backend/app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user_model import User

router = APIRouter()  # sin prefix; en main.py ya se incluye con prefix="/auth"


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", tags=["Auth"])
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login con JSON:
    POST /auth/login
    {
      "username": "admin",
      "password": "admin123"
    }
    """
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}
