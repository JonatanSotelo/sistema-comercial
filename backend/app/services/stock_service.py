from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, Any

from app.models.compra_model import StockMovimiento
from app.models.producto_model import Producto
from app.models.auditoria import AuditAction


def stock_actual(db: Session, producto_id: int) -> float:
    stmt = select(Producto.stock).where(Producto.id == producto_id)
    result = db.execute(stmt).scalar()
    if result is None:
        return 0.0
    return float(result)


def adjust_stock(
    db: Session,
    producto_id: int,
    delta: float,
    reason: str,
    ref_type: str,
    ref_id: int,
    user: Optional[Any] = None,
    request: Optional[Request] = None,
) -> float:
    producto: Producto | None = (
        db.query(Producto)
        .filter(Producto.id == producto_id)
        .with_for_update()
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail=f"Producto {producto_id} no encontrado")

    stock_pre = float(producto.stock or 0)
    nuevo_stock = stock_pre + float(delta)
    if nuevo_stock < 0:
        raise HTTPException(status_code=409, detail=f"Stock insuficiente para producto {producto_id}")

    producto.stock = nuevo_stock

    movimiento = StockMovimiento(
        producto_id=producto_id,
        tipo="IN" if delta >= 0 else "OUT",
        cantidad=abs(float(delta)),
        motivo=reason,
        ref_tipo=ref_type,
        ref_id=ref_id,
    )
    db.add(movimiento)
    
    # Log de auditoría para ajustes de stock
    try:
        from app.services.auditoria_service import create_audit_log, get_client_ip
        create_audit_log(
            db,
            user_id=getattr(user, "id", None) if user else None,
            username=getattr(user, "username", None) if user else None,
            table_name="stock",
            action=AuditAction.ADJUST,  # Usar ADJUST para ajustes de stock
            record_id=str(producto_id),
            details={
                "producto_id": producto_id,
                "delta": float(delta),
                "stock_pre": stock_pre,
                "stock_post": nuevo_stock,
                "ref_type": ref_type,
                "ref_id": ref_id,
                "reason": reason,
            },
            path=request.url.path if request else None,
            method=request.method if request else None,
            ip=get_client_ip(request) if request else None,
        )
    except Exception as e:
        # Si falla el log, no afecta el ajuste de stock (solo se registra el error)
        print(f"[auditoria] Error al registrar log de ajuste de stock: {e}")

    return nuevo_stock
