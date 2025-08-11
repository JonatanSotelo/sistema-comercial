from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False, index=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    total = Column(Float, default=0)

    proveedor = relationship("Proveedor")  # lazy simple
    items = relationship("CompraItem", cascade="all, delete-orphan", back_populates="compra")

class CompraItem(Base):
    __tablename__ = "compra_items"

    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey("compras.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    cantidad = Column(Float, nullable=False)
    costo_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    compra = relationship("Compra", back_populates="items")
    producto = relationship("Producto")  # referencia simple

class StockMovimiento(Base):
    __tablename__ = "stock_movimientos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    tipo = Column(String, nullable=False)  # 'IN' | 'OUT'
    cantidad = Column(Float, nullable=False)
    motivo = Column(String, nullable=True)  # 'COMPRA' | 'VENTA' | 'AJUSTE'
    ref_tipo = Column(String, nullable=True)  # 'compra' | 'venta' | ...
    ref_id = Column(Integer, nullable=True)   # id de la compra/venta
    fecha = Column(DateTime(timezone=True), server_default=func.now())
