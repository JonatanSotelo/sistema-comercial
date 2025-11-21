# app/services/compra_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Any
from fastapi import HTTPException, Request
from app.models.compra_model import Compra, CompraItem
from app.models.producto_model import Producto
from app.models.proveedor_model import Proveedor
from app.schemas.compra_schema import CompraCreate, CompraOut
from app.services.stock_service import stock_actual, adjust_stock  # centralizamos el cálculo
from app.models.auditoria import AuditAction

def _producto_existe(db: Session, producto_id: int) -> bool:
    return db.query(Producto.id).filter(Producto.id == producto_id).first() is not None

def _proveedor_existe(db: Session, proveedor_id: int) -> bool:
    return db.query(Proveedor.id).filter(Proveedor.id == proveedor_id).first() is not None

def crear_compra(db: Session, data: CompraCreate, user: Optional[Any] = None, request: Optional[Request] = None) -> Compra:
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
        if data.observaciones:
            compra.observaciones = data.observaciones
        db.add(compra)
        db.flush()  # obtener compra.id

        total = 0.0
        for it in data.items:
            subtotal = float(it.cantidad) * float(it.costo_unitario)
            total += subtotal

            db.add(
                CompraItem(
                    compra_id=compra.id,
                    producto_id=it.producto_id,
                    cantidad=float(it.cantidad),
                    costo_unitario=float(it.costo_unitario),
                    subtotal=subtotal,
                )
            )

            adjust_stock(
                db,
                producto_id=it.producto_id,
                delta=float(it.cantidad),
                reason="COMPRA",
                ref_type="compra",
                ref_id=compra.id,
                user=user,
                request=request,
            )

        compra.total = total
        
        # Log de auditoría (dentro de la misma transacción)
        try:
            from app.services.auditoria_service import create_audit_log, get_client_ip
            items_detail = [
                {
                    "producto_id": it.producto_id,
                    "cantidad": float(it.cantidad),
                    "costo_unitario": float(it.costo_unitario),
                    "subtotal": float(it.cantidad) * float(it.costo_unitario),
                }
                for it in data.items
            ]
            create_audit_log(
                db,
                user_id=getattr(user, "id", None) if user else None,
                username=getattr(user, "username", None) if user else None,
                table_name="compras",
                action=AuditAction.CREATE,
                record_id=str(compra.id),
                details={
                    "proveedor_id": data.proveedor_id,
                    "items": items_detail,
                    "total": float(total),
                },
                path=request.url.path if request else None,
                method=request.method if request else None,
                ip=get_client_ip(request) if request else None,
            )
        except Exception as e:
            # Si falla el log, no afecta la compra (solo se registra el error)
            print(f"[auditoria] Error al registrar log de compra: {e}")
        
        db.commit()
        db.refresh(compra)
        return compra

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def obtener_compra(db: Session, compra_id: int):
    return db.query(Compra).filter(Compra.id == compra_id).first()

def listar_compras(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
) -> dict:
    query = db.query(Compra).order_by(Compra.fecha.desc())

    if search:
        like = f"%{search}%"
        query = query.join(Proveedor, isouter=True).filter(
            or_(
                Proveedor.nombre.ilike(like),
                Compra.observaciones.ilike(like),
            )
        )

    total = query.count()
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()

    return {
        "items": [CompraOut.model_validate(i).model_dump() for i in items],
        "total": total,
        "page": page,
        "size": per_page,
    }
