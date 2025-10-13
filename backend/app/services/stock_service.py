from sqlalchemy.orm import Session
from app.models.compra_model import StockMovimiento
from app.models.producto_model import Producto

def stock_actual(db: Session, producto_id: int) -> float:
    """
    Calcula el stock actual de un producto.
    Prioridad:
    1. Si hay movimientos → suma de (IN - OUT)
    2. Si no hay movimientos → stock inicial del producto
    """
    movs = (
        db.query(StockMovimiento)
        .filter(StockMovimiento.producto_id == producto_id)
        .all()
    )
    
    if movs:
        # Hay movimientos, calcular basándose en ellos
        total = 0.0
        for m in movs:
            total += float(m.cantidad) if m.tipo == "IN" else -float(m.cantidad)
        return total
    else:
        # No hay movimientos, usar stock inicial del producto
        prod = db.query(Producto).filter(Producto.id == producto_id).first()
        if prod:
            return float(prod.stock) if prod.stock is not None else 0.0
        return 0.0
