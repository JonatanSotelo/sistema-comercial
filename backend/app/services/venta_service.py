# app/services/venta_service.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.models.venta_model import Venta, VentaItem
from app.models.compra_model import StockMovimiento
from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.schemas.venta_schema import VentaCreate
from app.services.stock_service import stock_actual  # usamos la versión robusta (Python)

def _producto_precio(db: Session, producto_id: int) -> float | None:
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        return None
    return float(prod.precio)

def crear_venta(db: Session, data: VentaCreate) -> Venta:
    if not data.items:
        raise ValueError("Se requiere al menos un item")

    # Validar stock suficiente y determinar precio_unitario
    precios: dict[int, float] = {}
    for it in data.items:
        disponible = stock_actual(db, it.producto_id)
        if it.cantidad <= 0:
            raise ValueError("Cantidad inválida")
        if disponible < it.cantidad:
            raise ValueError(
                f"Stock insuficiente para producto {it.producto_id} (disp: {disponible})"
            )

        pu = it.precio_unitario if it.precio_unitario is not None else _producto_precio(db, it.producto_id)
        if pu is None:
            raise ValueError(f"Producto {it.producto_id} no existe")
        precios[it.producto_id] = float(pu)

    try:
        # Crear cabecera
        venta = Venta(cliente_id=data.cliente_id)
        if data.fecha:
            venta.fecha = data.fecha
        if data.observaciones:
            venta.observaciones = data.observaciones
        db.add(venta)
        db.flush()  # para obtener venta.id

        # Crear items + movimientos OUT + total
        total = 0.0
        for it in data.items:
            pu = precios[it.producto_id]
            subtotal = float(it.cantidad) * pu
            total += subtotal

            db.add(VentaItem(
                venta_id=venta.id,
                producto_id=it.producto_id,
                cantidad=float(it.cantidad),
                precio_unitario=pu,
                subtotal=subtotal,
            ))

            db.add(StockMovimiento(
                producto_id=it.producto_id,
                tipo="OUT",
                cantidad=float(it.cantidad),
                motivo="VENTA",
                ref_tipo="venta",
                ref_id=venta.id,
            ))

        venta.total = total
        db.commit()
        db.refresh(venta)
        return venta

    except Exception:
        db.rollback()
        raise

def obtener_venta(db: Session, venta_id: int) -> Venta | None:
    return db.query(Venta).filter(Venta.id == venta_id).first()

def listar_ventas(db: Session, page: int = 1, per_page: int = 20, search: Optional[str] = None) -> list[Venta]:
    """Lista las ventas con paginación y búsqueda"""
    query = db.query(Venta)
    
    # Aplicar filtro de búsqueda si se proporciona
    if search:
        query = query.join(Cliente).filter(
            or_(
                Venta.id.ilike(f"%{search}%"),
                Cliente.nombre.ilike(f"%{search}%"),
                Venta.observaciones.ilike(f"%{search}%")
            )
        )
    
    # Aplicar paginación
    offset = (page - 1) * per_page
    return query.offset(offset).limit(per_page).all()

def actualizar_venta(db: Session, venta_id: int, data: VentaCreate) -> Venta | None:
    """
    MVP: solo permite cambiar el cliente_id.
    (Editar items requiere recalcular stock y movimientos; lo vemos en la próxima iteración.)
    """
    v = obtener_venta(db, venta_id)
    if not v:
        return None
    v.cliente_id = data.cliente_id
    db.commit()
    db.refresh(v)
    return v

def eliminar_venta(db: Session, venta_id: int) -> bool:
    """
    Elimina la venta.
    Nota: Los items asociados se eliminan en cascada.
    ATENCIÓN: No revierte stock automáticamente.
    """
    v = obtener_venta(db, venta_id)
    if not v:
        return False
    try:
        db.delete(v)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        # Re-raise la excepción para que el router la maneje
        raise e
