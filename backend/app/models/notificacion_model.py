from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class TipoNotificacion(str, enum.Enum):
    STOCK_BAJO = "STOCK_BAJO"
    VENTA_IMPORTANTE = "VENTA_IMPORTANTE"
    SISTEMA = "SISTEMA"
    MANTENIMIENTO = "MANTENIMIENTO"
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARNING"

class EstadoNotificacion(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    ENVIADA = "ENVIADA"
    LEIDA = "LEIDA"
    ARCHIVADA = "ARCHIVADA"

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(Enum(TipoNotificacion), nullable=False)
    estado = Column(Enum(EstadoNotificacion), nullable=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    entidad_tipo = Column(String(50), nullable=True)
    entidad_id = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_envio = Column(DateTime(timezone=True), nullable=True)
    fecha_lectura = Column(DateTime(timezone=True), nullable=True)
    es_urgente = Column(Boolean, nullable=True, default=False)
    requiere_accion = Column(Boolean, nullable=True, default=False)
    datos_adicionales = Column(Text, nullable=True)

    # Relaciones
    usuario = relationship("User", back_populates="notificaciones")

    def __repr__(self) -> str:
        return f"<Notificacion(id={self.id}, tipo={self.tipo}, estado={self.estado})>"