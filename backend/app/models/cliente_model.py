from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)

    # Relación UNO a MUCHOS con Venta (solo back_populates, sin backref)
    ventas = relationship(
        "Venta",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
