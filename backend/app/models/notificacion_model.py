# app/models/notificacion_model.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.db.database import Base

class TipoNotificacion(str, PyEnum):
    """Tipos de notificaciones del sistema"""
    STOCK_BAJO = "stock_bajo"
    VENTA_IMPORTANTE = "venta_importante"
    SISTEMA = "sistema"
    MANTENIMIENTO = "mantenimiento"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"

class EstadoNotificacion(str, PyEnum):
    """Estados de las notificaciones"""
    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    LEIDA = "leida"
    ARCHIVADA = "archivada"

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False, index=True)
    mensaje = Column(Text, nullable=False)
    tipo = Column(Enum(TipoNotificacion), nullable=False, index=True)
    estado = Column(Enum(EstadoNotificacion), default=EstadoNotificacion.PENDIENTE, index=True)
    
    # Metadatos
    usuario_id = Column(Integer, nullable=True, index=True)  # NULL = notificación global
    entidad_tipo = Column(String(50), nullable=True)  # 'producto', 'venta', 'cliente', etc.
    entidad_id = Column(Integer, nullable=True)  # ID de la entidad relacionada
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    fecha_envio = Column(DateTime, nullable=True)
    fecha_lectura = Column(DateTime, nullable=True)
    
    # Configuración
    es_urgente = Column(Boolean, default=False, index=True)
    requiere_accion = Column(Boolean, default=False)
    datos_adicionales = Column(Text, nullable=True)  # JSON string con datos extra
    
    def __repr__(self):
        return f"<Notificacion(id={self.id}, titulo='{self.titulo}', tipo='{self.tipo}')>"

class NotificacionUsuario(Base):
    """Tabla de relación para notificaciones por usuario"""
    __tablename__ = "notificaciones_usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    notificacion_id = Column(Integer, nullable=False, index=True)
    usuario_id = Column(Integer, nullable=False, index=True)
    estado = Column(Enum(EstadoNotificacion), default=EstadoNotificacion.PENDIENTE)
    fecha_lectura = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<NotificacionUsuario(notificacion_id={self.notificacion_id}, usuario_id={self.usuario_id})>"
