from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)

    # Relación esperada por Compra (Compra.back_populates="proveedor")
    # No crea columnas nuevas; usa la FK en compras.proveedor_id
    compras = relationship(
        "Compra",
        back_populates="proveedor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
