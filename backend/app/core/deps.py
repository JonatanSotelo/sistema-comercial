import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.database import get_db
from app.core.security import decode_token
from app.services.user_service import get_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = get_by_username(db, username)
    # tolerar esquemas sin is_active
    if not user or not getattr(user, "is_active", True):
        raise credentials_exc
    return user


def require_admin(user = Depends(get_current_user)):
    """
    Política temporal:
    - Si existe flag/rol => respetarlo.
    - Fallback dev: usuario 'admin' (o SUPERUSER_USERNAME) o id==1.
    """
    is_admin = getattr(user, "is_admin", None)
    role = getattr(user, "role", None) or getattr(user, "rol", None)

    if is_admin is True:
        return user
    if isinstance(role, str) and role.lower() in {"admin", "administrator", "superuser", "superusuario"}:
        return user

    superuser_name = os.getenv("SUPERUSER_USERNAME", "admin")
    if getattr(user, "username", "") == superuser_name:
        return user
    if getattr(user, "id", None) == 1:
        return user

    raise HTTPException(status_code=403, detail="Requiere permisos de administrador")
