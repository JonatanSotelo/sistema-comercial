from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.security import hash_password, verify_password
from app.models.user_model import Usuario  # ajustá si tu modelo está en otro módulo
from app.schemas.user_schema import UserCreate, UserUpdate

# nombres posibles del campo donde guardás el hash
PASSWORD_ATTRS = ("hashed_password", "password_hash", "password")


def _get_stored_hash(u: Usuario) -> Optional[str]:
    """Devuelve el hash almacenado en el primer atributo de password disponible."""
    for attr in PASSWORD_ATTRS:
        if hasattr(u, attr):
            val = getattr(u, attr)
            if val:
                return val
    return None


def _set_password_hash(u: Usuario, raw_password: str) -> Optional[str]:
    """Setea el hash en el primer atributo de password disponible."""
    hashed = hash_password(raw_password)
    for attr in PASSWORD_ATTRS:
        if hasattr(u, attr):
            setattr(u, attr, hashed)
            return attr
    return None


def get_by_id(db: Session, user_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == user_id).first()


def get_by_username(db: Session, username: str) -> Optional[Usuario]:
    # asumimos que username existe en tu modelo
    return db.query(Usuario).filter(Usuario.username == username).first()


def get_by_email(db: Session, email: str) -> Optional[Usuario]:
    # solo intentamos si tu modelo realmente tiene email
    if not hasattr(Usuario, "email"):
        return None
    return db.query(Usuario).filter(Usuario.email == email).first()


def list_users(db: Session) -> List[Usuario]:
    return db.query(Usuario).order_by(Usuario.id.asc()).all()


def create_user(db: Session, data: UserCreate) -> Usuario:
    if get_by_username(db, data.username):
        raise ValueError("El username ya existe")
    # la verificación de email solo si el modelo tiene ese campo
    if hasattr(Usuario, "email") and get_by_email(db, data.email):
        raise ValueError("El email ya existe")

    # no pases kwargs que tu modelo no tenga: creá y asigná condicionalmente
    u = Usuario()

    # campos base
    if hasattr(u, "username"):
        u.username = data.username
    if hasattr(u, "email"):
        u.email = data.email

    # password hash en el campo disponible
    target = _set_password_hash(u, data.password)
    if target is None:
        raise ValueError("No encontré un campo para almacenar la contraseña (hashed_password/password_hash/password)")

    # flags solo si existen en tu modelo
    if hasattr(u, "is_admin"):
        u.is_admin = data.is_admin
    if hasattr(u, "is_active"):
        u.is_active = data.is_active

    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[Usuario]:
    u = get_by_id(db, user_id)
    if not u:
        return None

    if data.email is not None and hasattr(u, "email"):
        u.email = data.email
    if data.password:
        _set_password_hash(u, data.password)
    if data.is_admin is not None and hasattr(u, "is_admin"):
        u.is_admin = data.is_admin
    if data.is_active is not None and hasattr(u, "is_active"):
        u.is_active = data.is_active

    db.commit()
    db.refresh(u)
    return u


def delete_user(db: Session, user_id: int) -> bool:
    u = get_by_id(db, user_id)
    if not u:
        return False
    db.delete(u)
    db.commit()
    return True


def authenticate(db: Session, username: str, password: str) -> Optional[Usuario]:
    u = db.query(Usuario).filter(Usuario.username == username).first()
    if not u:
        return None

    stored = _get_stored_hash(u)
    if not stored:
        return None

    # verificación robusta del password
    try:
        ok = verify_password(password, stored)
    except Exception:
        # fallback si por alguna razón quedó texto plano
        ok = (password == stored)

    if not ok:
        return None

    # tolerar modelos sin is_active
    if hasattr(u, "is_active") and not u.is_active:
        return None

    return u
