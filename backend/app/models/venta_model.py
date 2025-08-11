from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, default=0.0)

    # Lado directo de la relación con Cliente
    cliente = relationship("Cliente", back_populates="ventas")
