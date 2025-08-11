# 3. SERVICIO - services/venta_service.py
from sqlalchemy.orm import Session
from app.models.venta_model import Venta
from app.schemas.venta_schema import VentaCreate

def crear_venta(db: Session, venta_data: VentaCreate):
    venta = Venta(**venta_data.dict())
    db.add(venta)
    db.commit()
    db.refresh(venta)
    return venta

def listar_ventas(db: Session):
    return db.query(Venta).all()


def obtener_venta(db: Session, venta_id: int) -> Venta | None:
    return db.query(Venta).filter(Venta.id == venta_id).first()

def actualizar_venta(db: Session, venta_id: int, data: VentaCreate) -> Venta | None:
    v = obtener_venta(db, venta_id)
    if not v:
        return None
    v.cliente_id = data.cliente_id
    v.total = data.total
    db.commit()
    db.refresh(v)
    return v

def eliminar_venta(db: Session, venta_id: int) -> bool:
    v = obtener_venta(db, venta_id)
    if not v:
        return False
    db.delete(v)
    db.commit()
    return True