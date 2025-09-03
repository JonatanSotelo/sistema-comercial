# backend/app/routers/auth_router.py
from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app.core.settings import settings  # ajusta si tu settings está en otro lugar
from app.db.database import get_db
from app.services.user_service import UserService  # ajusta el import si difiere

router = APIRouter(prefix="/auth", tags=["Auth"])

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(subject: str, minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    # 👇 sub debe ser un STRING (no un objeto) y hay que usar el parámetro 'subject'
    to_encode = {"sub": subject, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


@router.post("/oauth2/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = UserService.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o clave inválidos",
        )
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

# (opcional) atajo para probar rápido con JSON (si lo usas, bórralo en prod)
@router.post("/login")
def login_json(data: dict, db: Session = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")
    user = UserService.authenticate(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o clave inválidos")
    return {"access_token": create_access_token(subject=user.username), "token_type": "bearer"}
