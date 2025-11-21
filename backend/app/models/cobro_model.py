# app/models/cobro_model.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Text, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class MedioCobro(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    MERCADOPAGO = "MERCADOPAGO"
    TARJETA = "TARJETA"
    CHEQUE = "CHEQUE"
    OTRO = "OTRO"


class EstadoCobro(str, enum.Enum):
    CONFIRMADO = "CONFIRMADO"
    ANULADO = "ANULADO"


class Cobro(Base):
    __tablename__ = "cobros"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relación con venta (requerido)
    venta_id = Column(Integer, ForeignKey("ventas.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Detalles del cobro
    medio = Column(Enum(MedioCobro), nullable=False, index=True)
    importe = Column(Numeric(12, 2), nullable=False)
    moneda = Column(String(3), default="ARS", nullable=False)
    referencia = Column(String, nullable=True)  # Nro de transferencia, MP, etc.
    observaciones = Column(Text, nullable=True)
    
    # Estado
    estado = Column(Enum(EstadoCobro), default=EstadoCobro.CONFIRMADO, nullable=False, index=True)
    
    # Relaciones
    venta = relationship("Venta", back_populates="cobros")
    user = relationship("User", foreign_keys=[user_id])
    
    # Constraints
    __table_args__ = (
        CheckConstraint("importe >= 0", name="ck_cobros_importe_pos"),
    )

