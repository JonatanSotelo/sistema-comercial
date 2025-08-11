from sqlalchemy.orm import Session
from app.models.proveedor_model import Proveedor
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorUpdate

def crear_proveedor(db: Session, data: ProveedorCreate) -> Proveedor:
    p = Proveedor(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def listar_proveedores(db: Session):
    return db.query(Proveedor).all()

def obtener_proveedor(db: Session, prov_id: int):
    return db.query(Proveedor).filter(Proveedor.id == prov_id).first()

def actualizar_proveedor(db: Session, prov_id: int, data: ProveedorUpdate):
    p = obtener_proveedor(db, prov_id)
    if not p:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p

def eliminar_proveedor(db: Session, prov_id: int) -> bool:
    p = obtener_proveedor(db, prov_id)
    if not p:
        return False
    db.delete(p)
    db.commit()
    return True
