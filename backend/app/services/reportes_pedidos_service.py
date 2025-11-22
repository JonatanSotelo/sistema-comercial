# app/services/reportes_pedidos_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, date
from typing import Optional

from app.models.pedido_model import Pedido, EstadoPedido
from app.models.cliente_model import Cliente


def reporte_pedidos(
    db: Session,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    group_by: str = "estado"
) -> dict:
    """
    Genera reporte de pedidos agrupado por estado, día o cliente
    
    Args:
        db: Sesión de base de datos
        desde: Fecha desde (opcional)
        hasta: Fecha hasta (opcional)
        group_by: Agrupar por 'estado', 'dia' o 'cliente'
    
    Returns:
        Diccionario con resultados del reporte
    """
    query = db.query(Pedido)
    
    # Filtros de fecha
    if desde:
        query = query.filter(Pedido.created_at >= desde)
    if hasta:
        query = query.filter(Pedido.created_at <= hasta)
    
    if group_by == "estado":
        # Agrupar por estado
        results = (
            query.with_entities(
                Pedido.estado,
                func.count(Pedido.id).label("cantidad"),
                func.sum(Pedido.total).label("total")
            )
            .group_by(Pedido.estado)
            .order_by(Pedido.estado)
            .all()
        )
        
        return {
            "group_by": "estado",
            "desde": desde.isoformat() if desde else None,
            "hasta": hasta.isoformat() if hasta else None,
            "items": [
                {
                    "grupo": r.estado.value,
                    "cantidad": r.cantidad,
                    "total": float(r.total or 0)
                }
                for r in results
            ]
        }
    
    elif group_by == "dia":
        # Agrupar por día
        results = (
            query.with_entities(
                func.date(Pedido.created_at).label("fecha"),
                func.count(Pedido.id).label("cantidad"),
                func.sum(Pedido.total).label("total")
            )
            .group_by(func.date(Pedido.created_at))
            .order_by(func.date(Pedido.created_at).desc())
            .all()
        )
        
        return {
            "group_by": "dia",
            "desde": desde.isoformat() if desde else None,
            "hasta": hasta.isoformat() if hasta else None,
            "items": [
                {
                    "grupo": r.fecha.isoformat() if isinstance(r.fecha, date) else str(r.fecha),
                    "cantidad": r.cantidad,
                    "total": float(r.total or 0)
                }
                for r in results
            ]
        }
    
    elif group_by == "cliente":
        # Agrupar por cliente
        results = (
            query.join(Cliente, Cliente.id == Pedido.cliente_id, isouter=True)
            .with_entities(
                Cliente.id.label("cliente_id"),
                Cliente.nombre.label("cliente_nombre"),
                func.count(Pedido.id).label("cantidad"),
                func.sum(Pedido.total).label("total")
            )
            .group_by(Cliente.id, Cliente.nombre)
            .order_by(func.sum(Pedido.total).desc())
            .all()
        )
        
        return {
            "group_by": "cliente",
            "desde": desde.isoformat() if desde else None,
            "hasta": hasta.isoformat() if hasta else None,
            "items": [
                {
                    "grupo": r.cliente_nombre or f"Sin Cliente",
                    "cliente_id": r.cliente_id,
                    "cantidad": r.cantidad,
                    "total": float(r.total or 0)
                }
                for r in results
            ]
        }
    
    else:
        raise ValueError(f"group_by inválido: {group_by}. Use 'estado', 'dia' o 'cliente'")

