# backend/app/scripts/init_admin.py
from app.db.database import SessionLocal
from app.models.user_model import User
from app.core.security import hash_password

def main():
    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.username == "admin").first()
        if exists:
            print("[OK] El usuario admin ya existe. Nada que hacer.")
            return

        admin = User(
            username="admin",
            hashed_password=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("[OK] Usuario admin creado: admin / admin123")
    finally:
        db.close()

if __name__ == "__main__":
    main()
