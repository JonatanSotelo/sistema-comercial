# app/services/compra_service.py
from sqlalchemy.orm import Session
from app.models.compra_model import Compra, CompraItem, StockMovimiento
from app.models.producto_model import Producto
from app.models.proveedor_model import Proveedor
from app.schemas.compra_schema import CompraCreate
from app.services.stock_service import stock_actual  # centralizamos el cálculo

def _producto_existe(db: Session, producto_id: int) -> bool:
    return db.query(Producto.id).filter(Producto.id == producto_id).first() is not None

def _proveedor_existe(db: Session, proveedor_id: int) -> bool:
    return db.query(Proveedor.id).filter(Proveedor.id == proveedor_id).first() is not None

def crear_compra(db: Session, data: CompraCreate) -> Compra:
    # Validaciones previas
    if not _proveedor_existe(db, data.proveedor_id):
        raise ValueError("Proveedor no existe")

    if not data.items:
        raise ValueError("Se requiere al menos un item")

    for it in data.items:
        if not _producto_existe(db, it.producto_id):
            raise ValueError(f"Producto {it.producto_id} no existe")
        if it.cantidad <= 0 or it.costo_unitario < 0:
            raise ValueError("Cantidad/costo inválidos")

    try:
        # Cabecera de compra
        compra = Compra(proveedor_id=data.proveedor_id)
        if data.fecha:
            compra.fecha = data.fecha
        db.add(compra)
        db.flush()  # obtener compra.id

        total = 0.0
        for it in data.items:
            subtotal = float(it.cantidad) * float(it.costo_unitario)
            total += subtotal

            # Item de compra
            db.add(CompraItem(
                compra_id=compra.id,
                producto_id=it.producto_id,
                cantidad=float(it.cantidad),
                costo_unitario=float(it.costo_unitario),
                subtotal=subtotal,
            ))

            # Movimiento de stock (IN)
            db.add(StockMovimiento(
                producto_id=it.producto_id,
                tipo="IN",
                cantidad=float(it.cantidad),
                motivo="COMPRA",
                ref_tipo="compra",
                ref_id=compra.id,
            ))

        compra.total = total
        db.commit()
        db.refresh(compra)
        return compra

    except Exception:
        db.rollback()
        raise

def obtener_compra(db: Session, compra_id: int):
    return db.query(Compra).filter(Compra.id == compra_id).first()
