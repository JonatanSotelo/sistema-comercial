# app/services/pedidos_service.py
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, and_
from typing import Optional, Any
from datetime import datetime

from app.models.pedido_model import Pedido, PedidoItem, EstadoPedido, OrigenPedido
from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.schemas.pedido_schema import PedidoCreate, PedidoUpdate, PedidoEstadoChange, PedidoOut
from app.schemas.venta_schema import VentaCreate, VentaItemIn
from app.services.stock_service import stock_actual
from app.services.venta_service import crear_venta
from app.models.auditoria import AuditAction
from app.services.stock_reservations_service import (
    ensure_reservas_for_pedido,
    release_reservas_for_pedido,
    consume_reservas_for_pedido
)


def _producto_precio(db: Session, producto_id: int) -> float | None:
    """Obtener precio actual del producto"""
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        return None
    return float(prod.precio)


def create_pedido(
    db: Session,
    data: PedidoCreate,
    user: Optional[Any] = None,
    request: Optional[Request] = None
) -> Pedido:
    """Crear un nuevo pedido"""
    if not data.items:
        raise HTTPException(status_code=400, detail="Se requiere al menos un ítem")

    # Validar cliente si se proporciona
    if data.cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == data.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail=f"Cliente {data.cliente_id} no encontrado")

    # Calcular precios
    precios: dict[int, float] = {}
    for it in data.items:
        if it.cantidad <= 0:
            raise HTTPException(status_code=400, detail="Cantidad debe ser mayor a 0")
        
        pu = (
            float(it.precio_unitario)
            if it.precio_unitario is not None
            else _producto_precio(db, it.producto_id)
        )
        if pu is None:
            raise HTTPException(status_code=404, detail=f"Producto {it.producto_id} no existe")
        if pu < 0:
            raise HTTPException(status_code=400, detail="Precio unitario no puede ser negativo")
        precios[it.producto_id] = float(pu)

    try:
        # Crear pedido
        pedido = Pedido(
            cliente_id=data.cliente_id,
            estado=EstadoPedido.NUEVO,
            origen=data.origen,
            telefono=data.telefono,
            nota=data.nota,
            created_by=getattr(user, "id", None) if user else None,
            external_ref=data.external_ref,
        )
        db.add(pedido)
        db.flush()

        # Crear items y calcular total
        total = 0.0
        for it in data.items:
            pu = precios[it.producto_id]
            cantidad = int(it.cantidad)
            subtotal = cantidad * pu
            total += subtotal

            db.add(
                PedidoItem(
                    pedido_id=pedido.id,
                    producto_id=it.producto_id,
                    cantidad=cantidad,
                    precio_unitario=pu,
                    subtotal=subtotal,
                )
            )

        pedido.total = total

        # Log de auditoría
        try:
            from app.services.auditoria_service import create_audit_log, get_client_ip
            items_detail = [
                {
                    "producto_id": it.producto_id,
                    "cantidad": int(it.cantidad),
                    "precio_unitario": precios[it.producto_id],
                    "subtotal": int(it.cantidad) * precios[it.producto_id],
                }
                for it in data.items
            ]
            create_audit_log(
                db,
                user_id=getattr(user, "id", None) if user else None,
                username=getattr(user, "username", None) if user else None,
                table_name="pedidos",
                action=AuditAction.CREATE,
                record_id=str(pedido.id),
                details={
                    "cliente_id": data.cliente_id,
                    "items": items_detail,
                    "total": float(total),
                    "origen": data.origen.value,
                },
                path=request.url.path if request else None,
                method=request.method if request else None,
                ip=get_client_ip(request) if request else None,
            )
        except Exception as e:
            print(f"[auditoria] Error al registrar log de pedido: {e}")

        db.commit()
        db.refresh(pedido)
        return pedido

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear pedido: {str(e)}")


def obtener_pedido(db: Session, pedido_id: int) -> Pedido | None:
    """Obtener un pedido por ID"""
    return db.query(Pedido).filter(Pedido.id == pedido_id).first()


def listar_pedidos(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
) -> dict:
    """Listar pedidos con filtros"""
    query = db.query(Pedido).order_by(desc(Pedido.created_at))

    # Filtro de búsqueda por texto
    if search:
        like = f"%{search}%"
        query = query.join(Cliente, isouter=True).filter(
            or_(
                Cliente.nombre.ilike(like),
                Cliente.telefono.ilike(like),
                Pedido.telefono.ilike(like),
                Pedido.nota.ilike(like),
            )
        )

    # Filtro por estado
    if estado:
        estados = [e.strip() for e in estado.split(",") if e.strip()]
        if estados:
            query = query.filter(Pedido.estado.in_(estados))

    # Filtro por cliente
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)

    # Filtro por rango de fechas
    if desde:
        query = query.filter(Pedido.created_at >= desde)
    if hasta:
        query = query.filter(Pedido.created_at <= hasta)

    total = query.count()
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()

    return {
        "items": [PedidoOut.model_validate(i).model_dump() for i in items],
        "total": total,
        "page": page,
        "size": per_page,
    }


def update_pedido(
    db: Session,
    pedido_id: int,
    data: PedidoUpdate,
    user: Optional[Any] = None,
    request: Optional[Request] = None
) -> Pedido:
    """Actualizar un pedido (solo si estado permite)"""
    pedido = obtener_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Solo permitir edición en estados NUEVO o EN_PREPARACION
    if pedido.estado not in [EstadoPedido.NUEVO, EstadoPedido.EN_PREPARACION]:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede editar un pedido en estado {pedido.estado.value}"
        )
    
    # Guardar si estaba en EN_PREPARACION para reajustar reservas después
    tenia_reservas = (pedido.estado == EstadoPedido.EN_PREPARACION)

    if not data.items:
        raise HTTPException(status_code=400, detail="Se requiere al menos un ítem")

    # Calcular precios
    precios: dict[int, float] = {}
    for it in data.items:
        if it.cantidad <= 0:
            raise HTTPException(status_code=400, detail="Cantidad debe ser mayor a 0")
        
        pu = (
            float(it.precio_unitario)
            if it.precio_unitario is not None
            else _producto_precio(db, it.producto_id)
        )
        if pu is None:
            raise HTTPException(status_code=404, detail=f"Producto {it.producto_id} no existe")
        if pu < 0:
            raise HTTPException(status_code=400, detail="Precio unitario no puede ser negativo")
        precios[it.producto_id] = float(pu)

    try:
        # Eliminar items anteriores
        db.query(PedidoItem).filter(PedidoItem.pedido_id == pedido_id).delete()

        # Crear nuevos items y calcular total
        total = 0.0
        for it in data.items:
            pu = precios[it.producto_id]
            cantidad = int(it.cantidad)
            subtotal = cantidad * pu
            total += subtotal

            db.add(
                PedidoItem(
                    pedido_id=pedido_id,
                    producto_id=it.producto_id,
                    cantidad=cantidad,
                    precio_unitario=pu,
                    subtotal=subtotal,
                )
            )

        pedido.total = total
        pedido.nota = data.nota

        # Log de auditoría
        try:
            from app.services.auditoria_service import create_audit_log, get_client_ip
            items_detail = [
                {
                    "producto_id": it.producto_id,
                    "cantidad": int(it.cantidad),
                    "precio_unitario": precios[it.producto_id],
                    "subtotal": int(it.cantidad) * precios[it.producto_id],
                }
                for it in data.items
            ]
            create_audit_log(
                db,
                user_id=getattr(user, "id", None) if user else None,
                username=getattr(user, "username", None) if user else None,
                table_name="pedidos",
                action=AuditAction.UPDATE,
                record_id=str(pedido.id),
                details={
                    "items": items_detail,
                    "total": float(total),
                },
                path=request.url.path if request else None,
                method=request.method if request else None,
                ip=get_client_ip(request) if request else None,
            )
        except Exception as e:
            print(f"[auditoria] Error al registrar log de actualización de pedido: {e}")

        # Si el pedido estaba en EN_PREPARACION, reajustar reservas
        if tenia_reservas:
            try:
                ensure_reservas_for_pedido(db, pedido_id, user=user, request=request)
            except HTTPException as e:
                db.rollback()
                raise HTTPException(
                    status_code=e.status_code,
                    detail=f"Error al reajustar reservas: {e.detail}"
                )
        
        db.commit()
        db.refresh(pedido)
        return pedido

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar pedido: {str(e)}")


def change_estado(
    db: Session,
    pedido_id: int,
    nuevo_estado: EstadoPedido,
    user: Optional[Any] = None,
    request: Optional[Request] = None,
    background_tasks: Optional[Any] = None
) -> Pedido:
    """Cambiar estado del pedido con validación de transiciones"""
    pedido = obtener_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    estado_actual = pedido.estado

    # Validar transiciones permitidas
    transiciones_validas = {
        EstadoPedido.NUEVO: [EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADO],
        EstadoPedido.EN_PREPARACION: [EstadoPedido.LISTO, EstadoPedido.CANCELADO],
        EstadoPedido.LISTO: [EstadoPedido.FACTURADO, EstadoPedido.CANCELADO],
        EstadoPedido.FACTURADO: [],  # Terminal
        EstadoPedido.CANCELADO: [],  # Terminal
    }

    if nuevo_estado not in transiciones_validas.get(estado_actual, []):
        raise HTTPException(
            status_code=400,
            detail=f"Transición no válida: {estado_actual.value} -> {nuevo_estado.value}"
        )

    try:
        estado_anterior = pedido.estado.value
        pedido.estado = nuevo_estado
        
        # Hooks de reservas de stock
        # NUEVO → EN_PREPARACION: crear reservas
        if estado_anterior == "NUEVO" and nuevo_estado == EstadoPedido.EN_PREPARACION:
            try:
                ensure_reservas_for_pedido(db, pedido_id, user=user, request=request)
            except HTTPException as e:
                db.rollback()
                raise HTTPException(
                    status_code=e.status_code,
                    detail=f"Error al crear reservas: {e.detail}"
                )
        
        # EN_PREPARACION → LISTO: revalidar reservas
        if estado_anterior == "EN_PREPARACION" and nuevo_estado == EstadoPedido.LISTO:
            try:
                ensure_reservas_for_pedido(db, pedido_id, user=user, request=request)
            except HTTPException as e:
                db.rollback()
                raise HTTPException(
                    status_code=e.status_code,
                    detail=f"Error al revalidar reservas: {e.detail}"
                )
        
        # * → CANCELADO: liberar reservas
        if nuevo_estado == EstadoPedido.CANCELADO:
            try:
                release_reservas_for_pedido(db, pedido_id, user=user, request=request)
            except Exception as e:
                print(f"[reservas] Error al liberar reservas: {e}")
                # No fallar el cambio de estado si falla la liberación

        # Log de auditoría
        try:
            from app.services.auditoria_service import create_audit_log, get_client_ip
            create_audit_log(
                db,
                user_id=getattr(user, "id", None) if user else None,
                username=getattr(user, "username", None) if user else None,
                table_name="pedidos",
                action=AuditAction.UPDATE,
                record_id=str(pedido.id),
                details={
                    "action": "CHANGE_STATE",
                    "estado_anterior": estado_anterior,
                    "estado_nuevo": nuevo_estado.value,
                },
                path=request.url.path if request else None,
                method=request.method if request else None,
                ip=get_client_ip(request) if request else None,
            )
        except Exception as e:
            print(f"[auditoria] Error al registrar cambio de estado: {e}")

        db.commit()
        db.refresh(pedido)
        
        # Hook de notificación: si pasa a LISTO, enviar notificación en background
        if nuevo_estado == EstadoPedido.LISTO and background_tasks:
            try:
                from app.services.notifications_service import notify_order_ready
                background_tasks.add_task(notify_order_ready, db, pedido_id)
                print(f"[notif] Notificación programada para pedido {pedido_id}")
            except Exception as e:
                print(f"[notif] Error al programar notificación: {e}")
                # No fallar el cambio de estado si falla la notificación
        
        return pedido

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cambiar estado: {str(e)}")


def bulk_change_estado(
    db: Session,
    pedido_ids: list[int],
    nuevo_estado: EstadoPedido,
    user: Optional[Any] = None,
    request: Optional[Request] = None
) -> dict:
    """Cambiar estado de múltiples pedidos a la vez"""
    if not pedido_ids:
        raise HTTPException(status_code=400, detail="Se requiere al menos un pedido")
    
    resultados = {
        "exitosos": [],
        "fallidos": [],
        "total": len(pedido_ids)
    }
    
    for pedido_id in pedido_ids:
        try:
            pedido = change_estado(db, pedido_id, nuevo_estado, user=user, request=request)
            resultados["exitosos"].append({"pedido_id": pedido_id, "nuevo_estado": pedido.estado.value})
        except HTTPException as e:
            resultados["fallidos"].append({"pedido_id": pedido_id, "error": str(e.detail)})
        except Exception as e:
            resultados["fallidos"].append({"pedido_id": pedido_id, "error": str(e)})
    
    return resultados


def facturar_pedido(
    db: Session,
    pedido_id: int,
    user: Optional[Any] = None,
    request: Optional[Request] = None
) -> dict:
    """Facturar pedido: validar stock, crear venta, ajustar stock, marcar como FACTURADO"""
    pedido = obtener_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Validar que el pedido esté en estado LISTO
    if pedido.estado != EstadoPedido.LISTO:
        raise HTTPException(
            status_code=400,
            detail=f"Solo se pueden facturar pedidos en estado LISTO (actual: {pedido.estado.value})"
        )

    try:
        # Consumir reservas (esto valida stock y lo descuenta)
        try:
            consume_reservas_for_pedido(db, pedido_id, user=user, request=request)
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error al consumir reservas: {e.detail}"
            )

        # Crear venta a partir del pedido (sin ajustar stock, ya lo hicimos con reservas)
        venta_items = [
            VentaItemIn(
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=float(item.precio_unitario)
            )
            for item in pedido.items
        ]

        venta_data = VentaCreate(
            cliente_id=pedido.cliente_id,
            items=venta_items,
            observaciones=f"Generada desde Pedido #{pedido.id}" + (f" - {pedido.nota}" if pedido.nota else "")
        )

        # IMPORTANTE: No usar crear_venta porque ajusta stock nuevamente
        # El stock ya fue ajustado al consumir reservas
        # Crear venta manualmente
        from app.models.venta_model import Venta, VentaItem
        venta = Venta(cliente_id=pedido.cliente_id)
        if venta_data.observaciones:
            venta.observaciones = venta_data.observaciones
        db.add(venta)
        db.flush()

        total = 0.0
        for vit in venta_items:
            cantidad = float(vit.cantidad)
            pu = float(vit.precio_unitario)
            subtotal = cantidad * pu
            total += subtotal

            db.add(
                VentaItem(
                    venta_id=venta.id,
                    producto_id=vit.producto_id,
                    cantidad=cantidad,
                    precio_unitario=pu,
                    subtotal=subtotal,
                )
            )

        venta.total = total
        
        # Guardar venta_id en el pedido (v0.8.0)
        pedido.venta_id = venta.id
        
        # Log de auditoría de la venta
        try:
            from app.services.auditoria_service import create_audit_log, get_client_ip
            items_detail = [
                {
                    "producto_id": vit.producto_id,
                    "cantidad": float(vit.cantidad),
                    "precio_unitario": float(vit.precio_unitario),
                    "subtotal": float(vit.cantidad) * float(vit.precio_unitario),
                }
                for vit in venta_items
            ]
            create_audit_log(
                db,
                user_id=getattr(user, "id", None) if user else None,
                username=getattr(user, "username", None) if user else None,
                table_name="ventas",
                action=AuditAction.CREATE,
                record_id=str(venta.id),
                details={
                    "cliente_id": pedido.cliente_id,
                    "items": items_detail,
                    "total": float(total),
                    "origen": "pedido",
                    "pedido_id": pedido_id,
                },
                path=request.url.path if request else None,
                method=request.method if request else None,
                ip=get_client_ip(request) if request else None,
            )
        except Exception as e:
            print(f"[auditoria] Error al registrar log de venta: {e}")

        # Marcar pedido como FACTURADO
        pedido.estado = EstadoPedido.FACTURADO

        # Log de auditoría
        try:
            from app.services.auditoria_service import create_audit_log, get_client_ip
            create_audit_log(
                db,
                user_id=getattr(user, "id", None) if user else None,
                username=getattr(user, "username", None) if user else None,
                table_name="pedidos",
                action=AuditAction.UPDATE,
                record_id=str(pedido.id),
                details={
                    "action": "FACTURAR",
                    "venta_id": venta.id,
                    "total": float(venta.total),
                },
                path=request.url.path if request else None,
                method=request.method if request else None,
                ip=get_client_ip(request) if request else None,
            )
        except Exception as e:
            print(f"[auditoria] Error al registrar facturación: {e}")

        db.commit()

        return {
            "venta_id": venta.id,
            "total": float(venta.total),
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al facturar pedido: {str(e)}")

