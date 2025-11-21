# app/services/venta_service.py
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, String
from typing import Optional, Any
from app.models.venta_model import Venta, VentaItem
from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.schemas.venta_schema import VentaCreate, VentaOut
from app.services.stock_service import stock_actual, adjust_stock
from app.models.auditoria import AuditAction

def _producto_precio(db: Session, producto_id: int) -> float | None:
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        return None
    return float(prod.precio)

def crear_venta(db: Session, data: VentaCreate, user: Optional[Any] = None, request: Optional[Request] = None) -> Venta:
    if not data.items:
        raise HTTPException(status_code=400, detail="Se requiere al menos un ítem")

    precios: dict[int, float] = {}

    for it in data.items:
        if it.cantidad <= 0:
            raise HTTPException(status_code=400, detail="Cantidad inválida")
        disponible = stock_actual(db, it.producto_id)
        if disponible < it.cantidad:
            raise HTTPException(
                status_code=409,
                detail=f"Stock insuficiente para producto {it.producto_id} (disp: {disponible})",
            )

        pu = (
            float(it.precio_unitario)
            if it.precio_unitario is not None
            else _producto_precio(db, it.producto_id)
        )
        if pu is None:
            raise HTTPException(status_code=404, detail=f"Producto {it.producto_id} no existe")
        precios[it.producto_id] = float(pu)

    try:
        venta = Venta(cliente_id=data.cliente_id)
        if data.fecha:
            venta.fecha = data.fecha
        if data.observaciones:
            venta.observaciones = data.observaciones
        db.add(venta)
        db.flush()

        total = 0.0
        for it in data.items:
            pu = precios[it.producto_id]
            cantidad = float(it.cantidad)
            subtotal = cantidad * pu
            total += subtotal

            db.add(
                VentaItem(
                    venta_id=venta.id,
                    producto_id=it.producto_id,
                    cantidad=cantidad,
                    precio_unitario=pu,
                    subtotal=subtotal,
                )
            )

            adjust_stock(
                db,
                producto_id=it.producto_id,
                delta=-cantidad,
                reason="VENTA",
                ref_type="venta",
                ref_id=venta.id,
                user=user,
                request=request,
            )

        venta.total = total
        
        # Log de auditoría (dentro de la misma transacción)
        try:
            from app.services.auditoria_service import create_audit_log, get_client_ip
            items_detail = [
                {
                    "producto_id": it.producto_id,
                    "cantidad": float(it.cantidad),
                    "precio_unitario": precios[it.producto_id],
                    "subtotal": float(it.cantidad) * precios[it.producto_id],
                }
                for it in data.items
            ]
            create_audit_log(
                db,
                user_id=getattr(user, "id", None) if user else None,
                username=getattr(user, "username", None) if user else None,
                table_name="ventas",
                action=AuditAction.CREATE,
                record_id=str(venta.id),
                details={
                    "cliente_id": data.cliente_id,
                    "items": items_detail,
                    "total": float(total),
                },
                path=request.url.path if request else None,
                method=request.method if request else None,
                ip=get_client_ip(request) if request else None,
            )
        except Exception as e:
            # Si falla el log, no afecta la venta (solo se registra el error)
            print(f"[auditoria] Error al registrar log de venta: {e}")
        
        db.commit()
        db.refresh(venta)
        return venta

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def obtener_venta(db: Session, venta_id: int) -> Venta | None:
    return db.query(Venta).filter(Venta.id == venta_id).first()

def listar_ventas(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
) -> dict:
    query = db.query(Venta).order_by(desc(Venta.fecha))

    if search:
        like = f"%{search}%"
        query = query.join(Cliente, isouter=True).filter(
            or_(
                Cliente.nombre.ilike(like),
                Venta.observaciones.ilike(like),
            )
        )

    total = query.count()
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()

    return {
        "items": [VentaOut.model_validate(i).model_dump() for i in items],
        "total": total,
        "page": page,
        "size": per_page,
    }

def actualizar_venta(db: Session, venta_id: int, data: VentaCreate) -> Venta | None:
    """
    MVP: solo permite cambiar el cliente_id.
    (Editar items requiere recalcular stock y movimientos; lo vemos en la próxima iteración.)
    """
    v = obtener_venta(db, venta_id)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    v.cliente_id = data.cliente_id
    db.commit()
    db.refresh(v)
    return v

def eliminar_venta(db: Session, venta_id: int) -> bool:
    """
    MVP: elimina la venta y (ATENCIÓN) no revierte stock.
    Lo correcto sería agregar movimientos de reversa (IN) por cada item.
    Lo implementamos en la siguiente iteración.
    """
    v = obtener_venta(db, venta_id)
    if not v:
        return False
    db.delete(v)
    db.commit()
    return True
