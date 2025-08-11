from sqlalchemy.orm import Session
from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate

def crear_cliente(db: Session, cliente: ClienteCreate):
    db_cliente = Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def listar_clientes(db: Session):
    return db.query(Cliente).all()

def obtener_cliente(db: Session, cliente_id: int) -> Cliente | None:
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()

def actualizar_cliente(db: Session, cliente_id: int, data: ClienteCreate) -> Cliente | None:
    c = obtener_cliente(db, cliente_id)
    if not c:
        return None
    c.nombre = data.nombre
    c.email = data.email
    # si usás telefono/direccion, agregalos también
    db.commit()
    db.refresh(c)
    return c

def eliminar_cliente(db: Session, cliente_id: int) -> bool:
    c = obtener_cliente(db, cliente_id)
    if not c:
        return False
    db.delete(c)
    db.commit()
    return True