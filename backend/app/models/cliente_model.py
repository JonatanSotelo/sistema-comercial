from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)

    # Relación esperada por Venta (Venta.back_populates="cliente")
    # No crea columnas nuevas; usa la FK en ventas.cliente_id
    ventas = relationship(
        "Venta",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
