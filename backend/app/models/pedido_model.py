from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Text, CheckConstraint, func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base

class EstadoPedido(str, enum.Enum):
    NUEVO = "NUEVO"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO = "LISTO"
    FACTURADO = "FACTURADO"
    CANCELADO = "CANCELADO"

class OrigenPedido(str, enum.Enum):
    MANUAL = "MANUAL"
    WHATSAPP = "WHATSAPP"

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=True)
    estado = Column(Enum(EstadoPedido), default=EstadoPedido.NUEVO, nullable=False, index=True)
    origen = Column(Enum(OrigenPedido), default=OrigenPedido.MANUAL, nullable=False)
    telefono = Column(String, nullable=True)
    nota = Column(Text, nullable=True)
    total = Column(Numeric(12, 2), default=0, nullable=False)
    created_by = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    external_ref = Column(String, nullable=True)
    
    # Relationships
    cliente = relationship("Cliente", back_populates="pedidos")
    items = relationship(
        "PedidoItem",
        back_populates="pedido",
        cascade="all, delete-orphan",
    )
    created_by_user = relationship("User", foreign_keys=[created_by])


class PedidoItem(Base):
    __tablename__ = "pedido_items"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    
    # Relationships
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="ck_pedido_items_cantidad_pos"),
        CheckConstraint("precio_unitario >= 0", name="ck_pedido_items_precio_pos"),
    )

