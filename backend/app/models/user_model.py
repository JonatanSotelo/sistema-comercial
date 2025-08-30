# app/models/user_model.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.db.database import Base  # 👈 IMPORTA DIRECTO DE database, NO de base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="consulta", nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

# Alias de compatibilidad para código legado que importe 'Usuario'
Usuario = User
