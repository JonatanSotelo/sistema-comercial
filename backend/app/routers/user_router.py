# backend/app/routers/user_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_user, require_admin
from app.schemas.user_schema import UserCreate, UserUpdate, UserOut
from app.services import user_service as svc
from app.services.auditoria_service import log_action
from app.models.auditoria import AuditAction

router = APIRouter(prefix="/users", tags=["Usuarios"])

@router.get("/", response_model=List[UserOut], dependencies=[Depends(require_admin)])
def listar(db: Session = Depends(get_db)):
    return svc.list_users(db)

@router.get("/usuarios/me", response_model=UserOut)
def yo(user = Depends(get_current_user)):
    return user

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)])
def crear(
    data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    try:
        u = svc.create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Audit CREATE (ocultar password en payload)
    payload = data.model_dump()
    if "password" in payload:
        payload["password"] = "***"
    log_action(
        db,
        user=admin,
        table_name="usuarios",
        action=AuditAction.CREATE,
        record_id=u.id,
        request=request,
        after=u,
        extra={"payload": payload},
    )
    return u

@router.put("/{user_id}", response_model=UserOut,
            dependencies=[Depends(require_admin)])
def editar(
    user_id: int,
    data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    before = svc.get_by_id(db, user_id)
    if not before:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    u = svc.update_user(db, user_id, data)

    payload = data.model_dump()
    if "password" in payload and payload["password"]:
        payload["password"] = "***"

    log_action(
        db,
        user=admin,
        table_name="usuarios",
        action=AuditAction.UPDATE,
        record_id=user_id,
        request=request,
        before=before,
        after=u,
        extra={"payload": payload},
    )
    return u

@router.delete("/{user_id}", status_code=204,
               dependencies=[Depends(require_admin)])
def borrar(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    before = svc.get_by_id(db, user_id)
    if not before:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    svc.delete_user(db, user_id)

    log_action(
        db,
        user=admin,
        table_name="usuarios",
        action=AuditAction.DELETE,
        record_id=user_id,
        request=request,
        before=before,
    )
    return
