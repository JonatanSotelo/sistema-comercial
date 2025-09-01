# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
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
        # Soportar tokens viejos (sub como dict) y nuevos (sub como string)
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
    """
    Acepta admin si:
      - role == 'admin'  (tabla users de tu proyecto)
      - o is_admin == True (si existiera en algún otro modelo)
    """
    role_ok = getattr(current_user, "role", None) == "admin"
    flag_ok = bool(getattr(current_user, "is_admin", False))
    if not (role_ok or flag_ok):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo admin")
    return current_user
