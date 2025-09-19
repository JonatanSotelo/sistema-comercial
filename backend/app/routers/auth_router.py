# backend/app/routers/auth_router.py
from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app.core.settings import settings  # ajusta si tu settings está en otro lugar
from app.db.database import get_db
from app.services.user_service import UserService  # ajusta el import si difiere
from app.schemas.user_schema import UserCreate, UserOut
from app.core.security import hash_password
from app.models.user_model import User

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

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    existing_user = UserService.get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    # Verificar si el email ya existe (si se proporciona)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
    
    # Crear nuevo usuario
    hashed_password = hash_password(user_data.password)
    role = user_data.role if hasattr(user_data, 'role') else "consulta"
    
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email,
        role=role,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserOut.model_validate(new_user)
