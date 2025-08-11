from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.models.user_model import Usuario
from app.schemas.user_schema import UsuarioCreate, UsuarioUpdate

def crear_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    hashed = bcrypt.hash(data.password)
    usuario = Usuario(username=data.username, email=data.email, hashed_password=hashed)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def listar_usuarios(db: Session) -> list[Usuario]:
    return db.query(Usuario).all()

def obtener_usuario(db: Session, user_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == user_id).first()

def actualizar_usuario(db: Session, user_id: int, data: UsuarioUpdate) -> Usuario | None:
    usuario = obtener_usuario(db, user_id)
    if not usuario:
        return None
    if data.username is not None:
        usuario.username = data.username
    if data.email is not None:
        usuario.email = data.email
    if data.password is not None:
        usuario.hashed_password = bcrypt.hash(data.password)
    db.commit()
    db.refresh(usuario)
    return usuario

def eliminar_usuario(db: Session, user_id: int) -> bool:
    usuario = obtener_usuario(db, user_id)
    if not usuario:
        return False
    db.delete(usuario)
    db.commit()
    return True
