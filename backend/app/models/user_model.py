# app/models/user_model.py
from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean
from app.db.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    is_admin = Column(Boolean, server_default="false", nullable=False)
    is_active = Column(Boolean, server_default="true", nullable=False)
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('username', name='uq_usuarios_username'),
        UniqueConstraint('email', name='uq_usuarios_email'),
    )
