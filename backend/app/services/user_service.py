# backend/app/services/user_service.py
from typing import Optional, List
from sqlalchemy.orm import Session

# Ajustá estos imports si tus módulos están en otras rutas:
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate

# Intentamos usar tus funciones reales de seguridad; si no existen, hacemos fallback simple
try:
    from app.core.security import hash_password, verify_password  # type: ignore
except Exception:  # fallback básico
    import hashlib

    def hash_password(password: str) -> str:
        # NO usar en prod; es solo fallback por si no existe core.security
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return hash_password(plain) == hashed
        except Exception:
            return plain == hashed


# Atributos posibles donde podría estar guardado el hash (según tu modelo)
PASSWORD_ATTRS = ("hashed_password", "password_hash", "password")


def _get_stored_hash(u: User) -> Optional[str]:
    """Devuelve el hash almacenado en el primer atributo de password disponible."""
    for attr in PASSWORD_ATTRS:
        if hasattr(u, attr):
            val = getattr(u, attr)
            if val:
                return val
    return None


def _set_stored_hash(u: User, hashed: str) -> None:
    """Setea el hash en el primer atributo disponible; si no hay ninguno, crea 'hashed_password'."""
    for attr in PASSWORD_ATTRS:
        if hasattr(u, attr):
            setattr(u, attr, hashed)
            return
    # si el modelo no tiene campo de hash, creamos uno dinámico (no ideal, pero evita crash)
    setattr(u, "hashed_password", hashed)


class UserService:
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def list_users(db: Session) -> List[User]:
        return db.query(User).all()

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        # Crea con los campos garantizados por el modelo actual
        u = User(
            username=data.username,
        )
        # Hash de password
        if getattr(data, "password", None):
            _set_stored_hash(u, hash_password(data.password))
        # Rol: usar role directamente
        if hasattr(u, "role") and getattr(data, "role", None) is not None:
            setattr(u, "role", data.role)
        # Campos opcionales que podrían no existir en el modelo actual
        if hasattr(u, "email") and getattr(data, "email", None) is not None:
            setattr(u, "email", data.email)
        if hasattr(u, "is_active") and getattr(data, "is_active", None) is not None:
            setattr(u, "is_active", data.is_active)

        db.add(u)
        db.commit()
        db.refresh(u)
        return u

    @staticmethod
    def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
        u: Optional[User] = db.query(User).get(user_id)  # type: ignore
        if not u:
            return None

        # Campos opcionales
        if getattr(data, "email", None) is not None and hasattr(u, "email"):
            u.email = data.email
        if getattr(data, "role", None) is not None and hasattr(u, "role"):
            u.role = data.role  # type: ignore
        if getattr(data, "is_active", None) is not None and hasattr(u, "is_active"):
            u.is_active = data.is_active
        if getattr(data, "username", None):
            u.username = data.username
        if getattr(data, "password", None):
            _set_stored_hash(u, hash_password(data.password))

        db.add(u)
        db.commit()
        db.refresh(u)
        return u

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        u: Optional[User] = db.query(User).get(user_id)  # type: ignore
        if not u:
            return False
        db.delete(u)
        db.commit()
        return True

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        u = UserService.get_by_username(db, username)
        if not u:
            return None

        stored = _get_stored_hash(u)

        # Si no hay hash, toleramos password en texto plano como fallback
        if stored is None:
            ok = (getattr(u, "password", None) == password)
        else:
            try:
                ok = verify_password(password, stored)
            except Exception:
                ok = (password == stored)

        if not ok:
            return None

        if hasattr(u, "is_active") and u.is_active is False:
            return None

        return u


# ========= Wrappers de módulo para compatibilidad con tu user_router =========

def list_users(db: Session) -> List[User]:
    return UserService.list_users(db)

def get_by_username(db: Session, username: str) -> Optional[User]:
    return UserService.get_by_username(db, username)

def create_user(db: Session, data: UserCreate) -> User:
    return UserService.create_user(db, data)

def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    return UserService.update_user(db, user_id, data)

def delete_user(db: Session, user_id: int) -> bool:
    return UserService.delete_user(db, user_id)

def authenticate(db: Session, username: str, password: str) -> Optional[User]:
    return UserService.authenticate(db, username, password)

def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).get(user_id)  # type: ignore
