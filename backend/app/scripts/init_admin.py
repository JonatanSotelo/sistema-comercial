# backend/app/scripts/init_admin.py
import os
from app.db.database import SessionLocal
from sqlalchemy import inspect

# Intentamos importar tu modelo
try:
    from app.models.user_model import Usuario
except ImportError:
    from app.models.usuario import Usuario  # type: ignore

# Hash local simple
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(p: str) -> str:
    return pwd_context.hash(p)

USERNAME = os.getenv("ADMIN_USERNAME", "admin")
EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def main():
    db = SessionLocal()
    try:
        exists = db.query(Usuario).filter(Usuario.username == USERNAME).first()
        if exists:
            print(f"[OK] Ya existe el usuario '{USERNAME}'. Nada que hacer.")
            return

        # Columnas disponibles en tu modelo/tabla
        cols = {c.key for c in inspect(Usuario).mapper.column_attrs}

        u = Usuario()
        if "username" in cols:
            u.username = USERNAME
        if "email" in cols:
            u.email = EMAIL

        # Nombre posible del campo de hash
        if "hashed_password" in cols:
            u.hashed_password = hash_password(PASSWORD)
        elif "password_hash" in cols:
            u.password_hash = hash_password(PASSWORD)
        elif "password" in cols:
            u.password = hash_password(PASSWORD)  # no recomiendo este nombre, pero por si acaso

        # Seteamos flags solo si existen en tu esquema actual
        if "is_active" in cols:
            setattr(u, "is_active", True)
        # Si tenés 'rol' o 'role', lo seteamos a 'admin'
        if "is_admin" in cols:
            setattr(u, "is_admin", True)
        elif "rol" in cols:
            setattr(u, "rol", "admin")
        elif "role" in cols:
            setattr(u, "role", "admin")

        db.add(u)
        db.commit()
        print(f"[OK] Usuario admin creado: {USERNAME} / {EMAIL}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
