from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)

    # Lado inverso de la relación con Venta
    ventas = relationship(
        "Venta",
        back_populates="cliente",
        cascade="all, delete-orphan"  # opcional: borra ventas al borrar cliente
    )
