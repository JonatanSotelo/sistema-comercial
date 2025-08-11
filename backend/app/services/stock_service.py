from sqlalchemy.orm import Session
from app.models.compra_model import StockMovimiento

def stock_actual(db: Session, producto_id: int) -> float:
    movs = (
        db.query(StockMovimiento)
        .filter(StockMovimiento.producto_id == producto_id)
        .all()
    )
    total = 0.0
    for m in movs:
        total += float(m.cantidad) if m.tipo == "IN" else -float(m.cantidad)
    return total
