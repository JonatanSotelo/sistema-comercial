# app/services/stock_reservations_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, Request
from typing import Optional, Any

from app.models.stock_reservation_model import StockReservation, EstadoReserva
from app.models.pedido_model import Pedido, PedidoItem, EstadoPedido
from app.models.producto_model import Producto
from app.models.auditoria import AuditAction


def get_disponible_producto(db: Session, producto_id: int) -> int:
    """
    Calcula el stock disponible de un producto
    Disponible = stock - SUM(reservas RESERVADA)
    """
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        return 0
    
    reservado = db.query(func.sum(StockReservation.cantidad)).filter(
        StockReservation.producto_id == producto_id,
        StockReservation.estado == EstadoReserva.RESERVADA
    ).scalar() or 0
    
    return max(0, producto.stock - reservado)


def ensure_reservas_for_pedido(
    db: Session,
    pedido_id: int,
    user: Optional[Any] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Asegura que existan reservas para todos los items del pedido
    Solo válido en estados EN_PREPARACION o LISTO
    Usa locks para evitar condiciones de carrera
    """
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if pedido.estado not in [EstadoPedido.EN_PREPARACION, EstadoPedido.LISTO]:
        raise HTTPException(
            status_code=400,
            detail=f"No se pueden crear reservas en estado {pedido.estado.value}"
        )
    
    creadas = []
    ajustadas = []
    errores = []
    
    for item in pedido.items:
        try:
            # Lock del producto para evitar condiciones de carrera
            producto = db.query(Producto).filter(Producto.id == item.producto_id).with_for_update().first()
            if not producto:
                errores.append(f"Producto {item.producto_id} no encontrado")
                continue
            
            # Buscar reserva activa existente para este item
            reserva = db.query(StockReservation).filter(
                StockReservation.pedido_item_id == item.id,
                StockReservation.estado == EstadoReserva.RESERVADA
            ).first()
            
            if reserva:
                # Si la cantidad cambió, ajustar
                if reserva.cantidad != item.cantidad:
                    old_cantidad = reserva.cantidad
                    reserva.cantidad = item.cantidad
                    ajustadas.append({
                        "producto_id": item.producto_id,
                        "old_cantidad": old_cantidad,
                        "new_cantidad": item.cantidad
                    })
            else:
                # Crear nueva reserva
                reserva = StockReservation(
                    pedido_id=pedido_id,
                    pedido_item_id=item.id,
                    producto_id=item.producto_id,
                    cantidad=item.cantidad,
                    estado=EstadoReserva.RESERVADA
                )
                db.add(reserva)
                creadas.append({
                    "producto_id": item.producto_id,
                    "cantidad": item.cantidad
                })
            
            # Verificar que el disponible no sea negativo
            disponible = get_disponible_producto(db, item.producto_id)
            if disponible < 0:
                raise HTTPException(
                    status_code=409,
                    detail=f"Stock insuficiente para {producto.nombre}: disponible {producto.stock}, reservado {disponible + item.cantidad}, requerido {item.cantidad}"
                )
        
        except HTTPException:
            raise
        except Exception as e:
            errores.append(f"Error en producto {item.producto_id}: {str(e)}")
    
    if errores:
        db.rollback()
        raise HTTPException(status_code=400, detail={"errores": errores})
    
    # Auditoría
    try:
        from app.services.auditoria_service import create_audit_log, get_client_ip
        create_audit_log(
            db,
            user_id=getattr(user, "id", None) if user else None,
            username=getattr(user, "username", None) if user else None,
            table_name="reservas",
            action=AuditAction.CREATE,
            record_id=str(pedido_id),
            details={
                "pedido_id": pedido_id,
                "creadas": creadas,
                "ajustadas": ajustadas,
            },
            path=request.url.path if request else None,
            method=request.method if request else None,
            ip=get_client_ip(request) if request else None,
        )
    except Exception as e:
        print(f"[auditoria] Error al registrar reservas: {e}")
    
    db.flush()
    
    return {
        "pedido_id": pedido_id,
        "creadas": len(creadas),
        "ajustadas": len(ajustadas),
        "detalles_creadas": creadas,
        "detalles_ajustadas": ajustadas,
    }


def release_reservas_for_pedido(
    db: Session,
    pedido_id: int,
    user: Optional[Any] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Libera (cancela) todas las reservas activas de un pedido
    Usado cuando se cancela el pedido
    """
    # Obtener todas las reservas activas del pedido
    reservas = db.query(StockReservation).filter(
        StockReservation.pedido_id == pedido_id,
        StockReservation.estado == EstadoReserva.RESERVADA
    ).all()
    
    if not reservas:
        return {"pedido_id": pedido_id, "liberadas": 0}
    
    liberadas = []
    for reserva in reservas:
        reserva.estado = EstadoReserva.CANCELADA
        liberadas.append({
            "producto_id": reserva.producto_id,
            "cantidad": reserva.cantidad
        })
    
    # Auditoría
    try:
        from app.services.auditoria_service import create_audit_log, get_client_ip
        create_audit_log(
            db,
            user_id=getattr(user, "id", None) if user else None,
            username=getattr(user, "username", None) if user else None,
            table_name="reservas",
            action=AuditAction.UPDATE,
            record_id=str(pedido_id),
            details={
                "action": "CANCEL",
                "pedido_id": pedido_id,
                "liberadas": liberadas,
            },
            path=request.url.path if request else None,
            method=request.method if request else None,
            ip=get_client_ip(request) if request else None,
        )
    except Exception as e:
        print(f"[auditoria] Error al registrar liberación de reservas: {e}")
    
    db.flush()
    
    return {
        "pedido_id": pedido_id,
        "liberadas": len(liberadas),
        "detalles": liberadas
    }


def consume_reservas_for_pedido(
    db: Session,
    pedido_id: int,
    user: Optional[Any] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Consume las reservas de un pedido:
    - Marca reservas como CONSUMIDA
    - Descuenta el stock real de los productos
    - Debe ejecutarse en la misma transacción que la creación de la Venta
    """
    # Obtener reservas activas
    reservas = db.query(StockReservation).filter(
        StockReservation.pedido_id == pedido_id,
        StockReservation.estado == EstadoReserva.RESERVADA
    ).all()
    
    if not reservas:
        raise HTTPException(
            status_code=400,
            detail="No hay reservas activas para consumir"
        )
    
    consumidas = []
    
    for reserva in reservas:
        # Lock del producto
        producto = db.query(Producto).filter(Producto.id == reserva.producto_id).with_for_update().first()
        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto {reserva.producto_id} no encontrado"
            )
        
        # Revalidar que hay stock suficiente
        if producto.stock < reserva.cantidad:
            raise HTTPException(
                status_code=409,
                detail=f"Stock insuficiente para {producto.nombre}: disponible {producto.stock}, requerido {reserva.cantidad}"
            )
        
        # Descontar stock real
        stock_anterior = producto.stock
        producto.stock -= reserva.cantidad
        
        # Marcar reserva como consumida
        reserva.estado = EstadoReserva.CONSUMIDA
        
        consumidas.append({
            "producto_id": reserva.producto_id,
            "cantidad": reserva.cantidad,
            "stock_anterior": stock_anterior,
            "stock_nuevo": producto.stock
        })
    
    # Auditoría
    try:
        from app.services.auditoria_service import create_audit_log, get_client_ip
        create_audit_log(
            db,
            user_id=getattr(user, "id", None) if user else None,
            username=getattr(user, "username", None) if user else None,
            table_name="reservas",
            action=AuditAction.UPDATE,
            record_id=str(pedido_id),
            details={
                "action": "CONSUME",
                "pedido_id": pedido_id,
                "consumidas": consumidas,
            },
            path=request.url.path if request else None,
            method=request.method if request else None,
            ip=get_client_ip(request) if request else None,
        )
    except Exception as e:
        print(f"[auditoria] Error al registrar consumo de reservas: {e}")
    
    db.flush()
    
    return {
        "pedido_id": pedido_id,
        "consumidas": len(consumidas),
        "detalles": consumidas
    }


def get_disponible_for_productos(db: Session, producto_ids: list[int]) -> dict[int, float]:
    """
    Calcula el stock disponible de múltiples productos en una sola consulta
    Retorna un dict {producto_id: disponible}
    """
    if not producto_ids:
        return {}
    
    # Obtener stocks de productos
    productos = db.query(Producto).filter(Producto.id.in_(producto_ids)).all()
    stocks = {p.id: float(p.stock) for p in productos}
    
    # Sumar reservas activas por producto
    reservas_query = (
        db.query(
            StockReservation.producto_id,
            func.sum(StockReservation.cantidad).label("total_reservado")
        )
        .filter(
            StockReservation.producto_id.in_(producto_ids),
            StockReservation.estado == EstadoReserva.RESERVADA
        )
        .group_by(StockReservation.producto_id)
    ).all()
    
    reservas_dict = {r.producto_id: float(r.total_reservado) for r in reservas_query}
    
    # Calcular disponible para cada producto
    return {
        pid: max(0.0, stocks.get(pid, 0.0) - reservas_dict.get(pid, 0.0))
        for pid in producto_ids
    }

