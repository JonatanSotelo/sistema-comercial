from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, CheckConstraint, func, Index
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class EstadoReserva(str, enum.Enum):
    RESERVADA = "RESERVADA"
    CANCELADA = "CANCELADA"
    CONSUMIDA = "CONSUMIDA"


class StockReservation(Base):
    __tablename__ = "stock_reservations"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False, index=True)
    pedido_item_id = Column(Integer, ForeignKey("pedido_items.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    estado = Column(Enum(EstadoReserva), default=EstadoReserva.RESERVADA, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    pedido = relationship("Pedido")
    pedido_item = relationship("PedidoItem")
    producto = relationship("Producto")

    # Constraints
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="ck_stock_reservations_cantidad_pos"),
        Index("ix_stock_reservations_producto_estado", "producto_id", "estado"),
        # Índice parcial: solo una reserva activa por pedido_item
        Index(
            "ix_stock_reservations_pedido_item_active",
            "pedido_item_id",
            postgresql_where=(estado == "RESERVADA"),
            unique=True
        ),
    )

