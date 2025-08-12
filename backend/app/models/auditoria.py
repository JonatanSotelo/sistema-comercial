from sqlalchemy import Column, Integer, String, DateTime, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
import enum

from app.db.database import Base

class AuditAction(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN  = "LOGIN"
    LOGOUT = "LOGOUT"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Usuario (cacheado por si cambia el username)
    user_id = Column(Integer, nullable=True)
    username = Column(String(120), nullable=True)

    # Contexto
    table_name = Column(String(120), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    record_id = Column(String(120), nullable=True)   # ID afectado (str por flexibilidad)
    path = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)
    ip = Column(String(64), nullable=True)

    # Detalles extra (diff, payload, snapshot)
    details = Column(JSONB, nullable=True)

# Índices útiles para filtros
Index("ix_audit_tbl_rec_time", AuditLog.table_name, AuditLog.record_id, AuditLog.created_at.desc())
Index("ix_audit_created_at", AuditLog.created_at.desc())
