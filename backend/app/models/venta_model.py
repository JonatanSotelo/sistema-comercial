from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="SET NULL"), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    total = Column(Float, default=0.0, nullable=False)
    descuento = Column(Float, default=0)
    impuestos = Column(Float, default=0)
    estado = Column(String, default="pendiente")
    observaciones = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # LADO MUCHOS a UNO con Cliente (coincide el back_populates)
    cliente = relationship("Cliente", back_populates="ventas")
    items = relationship(
        "VentaItem",
        back_populates="venta",
        cascade="all, delete-orphan",
    )
    
    # Relación con Facturas (v0.9.0+)
    facturas = relationship("Factura", back_populates="venta", cascade="all, delete-orphan")
    
    # Relación con Cobros (v0.9.1+)
    cobros = relationship("Cobro", back_populates="venta", cascade="all, delete-orphan")


class VentaItem(Base):
    __tablename__ = "venta_items"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False)
    cantidad = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="items")
    producto = relationship("Producto")




