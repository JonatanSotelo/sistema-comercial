from sqlalchemy.orm import Session
from app.models.producto_model import Producto
from app.schemas.producto_schema import ProductoCreate, ProductoUpdate

def crear_producto(db: Session, data: ProductoCreate) -> Producto:
    prod = Producto(**data.dict())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod

def obtener_productos(db: Session):
    return db.query(Producto).all()

def obtener_producto(db: Session, prod_id: int):
    return db.query(Producto).filter(Producto.id == prod_id).first()

def actualizar_producto(db: Session, prod_id: int, data: ProductoUpdate):
    prod = obtener_producto(db, prod_id)
    if not prod:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(prod, field, value)
    db.commit()
    db.refresh(prod)
    return prod

def eliminar_producto(db: Session, prod_id: int):
    prod = obtener_producto(db, prod_id)
    if not prod:
        return False
    db.delete(prod)
    db.commit()
    return True
