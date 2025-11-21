from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    cuit = Column(String, nullable=True, index=True)
    # direccion = Column(String, nullable=True)  # TODO: Agregar en migración futura si es necesario
    
    # Campos fiscales para facturación (v0.9.0+)
    condicion_iva = Column(String, nullable=True)  # RI, MONO, CF, EXENTO
    doc_tipo = Column(Integer, nullable=True)  # 80=CUIT, 96=DNI, 99=CF
    doc_nro = Column(String, nullable=True)

    # Relación esperada por Venta (Venta.back_populates="cliente")
    # No crea columnas nuevas; usa la FK en ventas.cliente_id
    ventas = relationship(
        "Venta",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    # Relación con Pedidos
    pedidos = relationship(
        "Pedido",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )