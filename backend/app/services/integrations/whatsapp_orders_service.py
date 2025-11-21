# app/services/integrations/whatsapp_orders_service.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, Dict, Any, List, Tuple
from fastapi import HTTPException, Request
import re
import os

from app.models.cliente_model import Cliente
from app.models.producto_model import Producto
from app.models.venta_model import Venta, VentaItem
from app.schemas.venta_schema import VentaCreate, VentaItemIn
from app.schemas.pedido_schema import PedidoCreate, PedidoItemIn
from app.services.venta_service import crear_venta
from app.services.stock_service import stock_actual
from app.core.settings import settings
from app.models.auditoria import AuditAction
from app.models.pedido_model import OrigenPedido


def normalize_phone(phone: str) -> str:
    """Normaliza teléfono a solo dígitos"""
    return re.sub(r'\D', '', phone)


def resolve_or_create_cliente_by_phone(
    db: Session,
    phone: str,
    customer_name: Optional[str] = None
) -> Cliente:
    """
    Busca cliente por teléfono o lo crea si no existe.
    
    Args:
        db: Sesión de base de datos
        phone: Teléfono del cliente
        customer_name: Nombre del cliente (opcional, requerido si no existe)
    
    Returns:
        Cliente encontrado o creado
    
    Raises:
        HTTPException: Si no existe y no se proporciona nombre
    """
    phone_normalized = normalize_phone(phone)
    
    # Buscar por teléfono normalizado (normalizar todos los teléfonos en la query)
    clientes = db.query(Cliente).all()
    cliente = None
    for c in clientes:
        if c.telefono and normalize_phone(c.telefono) == phone_normalized:
            cliente = c
            break
    
    if cliente:
        return cliente
    
    # Si no existe, crear si tenemos nombre
    if not customer_name:
        raise HTTPException(
            status_code=400,
            detail="Cliente no encontrado. Se requiere 'customer_name' para crear nuevo cliente."
        )
    
    # Crear cliente mínimo
    cliente = Cliente(
        nombre=customer_name,
        telefono=phone
    )
    db.add(cliente)
    db.flush()
    db.refresh(cliente)
    
    return cliente


def resolve_producto(
    db: Session,
    item: Dict[str, Any],
    fuzzy_match: bool = True
) -> Tuple[Optional[Producto], Optional[str]]:
    """
    Resuelve un producto por product_id, codigo o query.
    
    Args:
        db: Sesión de base de datos
        item: Diccionario con product_id, codigo o query
        fuzzy_match: Si True, permite búsqueda parcial por nombre
    
    Returns:
        Tupla (Producto o None, mensaje de error si hay ambigüedad)
    """
    # 1. Por product_id directo
    if "product_id" in item and item["product_id"]:
        producto = db.query(Producto).filter(Producto.id == item["product_id"]).first()
        if producto:
            return producto, None
        return None, f"Producto con ID {item['product_id']} no encontrado"
    
    # 2. Por código
    if "codigo" in item and item["codigo"]:
        producto = db.query(Producto).filter(Producto.codigo == item["codigo"]).first()
        if producto:
            return producto, None
        return None, f"Producto con código '{item['codigo']}' no encontrado"
    
    # 3. Por query (búsqueda por nombre)
    if "query" in item and item["query"]:
        query = item["query"].strip()
        if not query:
            return None, "Query vacío"
        
        if fuzzy_match:
            # Búsqueda ILIKE parcial
            productos = db.query(Producto).filter(
                Producto.nombre.ilike(f"%{query}%")
            ).all()
        else:
            # Búsqueda exacta
            productos = db.query(Producto).filter(
                Producto.nombre.ilike(query)
            ).all()
        
        if len(productos) == 0:
            return None, f"No se encontraron productos para '{query}'"
        
        if len(productos) == 1:
            return productos[0], None
        
        # Múltiples resultados - devolver sugerencias
        sugerencias = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "precio": float(p.precio),
                "stock": p.stock,
                "codigo": p.codigo
            }
            for p in productos
        ]
        return None, f"Búsqueda ambigua para '{query}'. Encontrados {len(productos)} productos."
    
    return None, "Se requiere product_id, codigo o query"


def quote_or_create_sale(
    db: Session,
    cliente_id: int,
    items: List[Dict[str, Any]],
    confirm: bool = False,
    request: Optional[Request] = None,
    as_order: bool = False,
    telefono: Optional[str] = None,
    external_ref: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Crea una cotización, pedido o venta según parámetros.
    
    Args:
        db: Sesión de base de datos
        cliente_id: ID del cliente
        items: Lista de items con product_id/codigo/query
        confirm: True para crear venta/pedido, False para cotización
        request: Request para auditoría
        as_order: True para crear pedido en lugar de venta (no toca stock)
        telefono: Teléfono asociado al pedido (opcional)
        external_ref: Referencia externa (ID mensaje/hilo del bot)
    
    Returns:
        Diccionario con cotización, pedido o venta creada
    """
    fuzzy_match = getattr(settings, "WHATS_FUZZY_MATCH", True)
    
    # Verificar variable de entorno para crear pedidos por defecto
    create_orders_env = os.environ.get("WHATS_CREATE_ORDERS", "false").lower() == "true"
    if create_orders_env:
        as_order = True
    
    resolved_items = []
    errors = []
    total = 0.0
    
    # Resolver productos
    for idx, item in enumerate(items):
        cantidad = item.get("cantidad", 1)
        if cantidad <= 0:
            errors.append(f"Item {idx + 1}: Cantidad inválida ({cantidad})")
            continue
        
        producto, error_msg = resolve_producto(db, item, fuzzy_match)
        
        if not producto:
            errors.append(f"Item {idx + 1}: {error_msg}")
            continue
        
        # Verificar stock si confirm=True
        if confirm:
            disponible = stock_actual(db, producto.id)
            if disponible < cantidad:
                errors.append(
                    f"Item {idx + 1} ({producto.nombre}): Stock insuficiente "
                    f"(disponible: {disponible}, solicitado: {cantidad})"
                )
                continue
        
        # Precio: usar precio_unitario si viene, sino producto.precio
        precio_unitario = item.get("precio_unitario")
        if precio_unitario is None:
            precio_unitario = float(producto.precio)
        else:
            precio_unitario = float(precio_unitario)
        
        if precio_unitario < 0:
            errors.append(f"Item {idx + 1}: Precio inválido ({precio_unitario})")
            continue
        
        subtotal = cantidad * precio_unitario
        total += subtotal
        
        resolved_items.append({
            "producto_id": producto.id,
            "producto_nombre": producto.nombre,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal
        })
    
    # Si hay errores, devolverlos
    if errors:
        raise HTTPException(
            status_code=400 if not confirm else 409,
            detail={
                "errors": errors,
                "resolved_items": resolved_items,
                "total": total
            }
        )
    
    # Si es cotización (confirm=False), devolver preview
    if not confirm:
        return {
            "type": "quote",
            "cliente_id": cliente_id,
            "items": resolved_items,
            "total": total,
            "stock_check": "ok"
        }
    
    # Si confirm=True y as_order=True, crear pedido (sin tocar stock)
    if as_order:
        from app.services.pedidos_service import create_pedido
        
        pedido_items = [
            PedidoItemIn(
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"]
            )
            for item in resolved_items
        ]
        
        pedido_data = PedidoCreate(
            cliente_id=cliente_id,
            items=pedido_items,
            origen=OrigenPedido.WHATSAPP,
            telefono=telefono,
            external_ref=external_ref,
        )
        
        pedido = create_pedido(db, pedido_data, user=None, request=request)
        
        return {
            "type": "order",
            "pedido_id": pedido.id,
            "cliente_id": cliente_id,
            "items": resolved_items,
            "total": float(pedido.total),
            "estado": pedido.estado.value
        }
    
    # Si confirm=True y as_order=False, crear venta (comportamiento original)
    venta_items = [
        VentaItemIn(
            producto_id=item["producto_id"],
            cantidad=item["cantidad"],
            precio_unitario=item["precio_unitario"]
        )
        for item in resolved_items
    ]
    
    venta_data = VentaCreate(
        cliente_id=cliente_id,
        items=venta_items
    )
    
    # Crear venta (usa el servicio existente que maneja stock y auditoría)
    venta = crear_venta(db, venta_data, user=None, request=request)
    
    return {
        "type": "sale",
        "venta_id": venta.id,
        "cliente_id": cliente_id,
        "items": resolved_items,
        "total": float(venta.total)
    }

