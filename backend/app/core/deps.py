# app/core/deps.py
from __future__ import annotations

from typing import Optional
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.database import get_db
from app.models.user_model import User

# Para que el candadito de /docs funcione bien
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/oauth2/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if isinstance(sub, dict):
            username = sub.get("sub")
        else:
            username = sub
        if not username:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exc
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Admin si role == 'admin' o is_admin == True."""
    role_ok = getattr(current_user, "role", None) == "admin"
    flag_ok = bool(getattr(current_user, "is_admin", False))
    if not (role_ok or flag_ok):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo admin")
    return current_user

def require_user(current_user: User = Depends(get_current_user)) -> User:
    """Cualquier usuario autenticado."""
    return current_user

# -----------------------------
# Paginación / filtros comunes
# -----------------------------
class CommonQueryParams(BaseModel):
    page: Optional[int] = Field(default=None, ge=1, description="Página (1..n)")
    size: Optional[int] = Field(default=None, ge=1, le=200, description="Tamaño de página (1..200)")
    search: Optional[str] = Field(default=None, description="Búsqueda texto (ilike)")
    sort: Optional[str] = Field(
        default=None,
        description="Campos separados por coma. Prefijo '-' = DESC. Ej: nombre,-precio"
    )

def common_params(
    page: Optional[int] = Query(default=None, ge=1),
    size: Optional[int] = Query(default=None, ge=1, le=200),
    search: Optional[str] = Query(default=None),
    sort: Optional[str] = Query(default=None),
) -> CommonQueryParams:
    return CommonQueryParams(page=page, size=size, search=search, sort=sort)
