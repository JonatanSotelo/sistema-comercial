from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.deps import get_current_user, require_admin
from app.schemas.user_schema import UserCreate, UserUpdate, UserOut
from app.services import user_service as svc
from app.core.audit import log_action
from app.models.auditoria import AuditAction

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", response_model=List[UserOut])
def listar(db: Session = Depends(get_db), _: any = Depends(require_admin)):
    return svc.list_users(db)

@router.get("/me", response_model=UserOut)
def yo(user=Depends(get_current_user)):
    return user

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    try:
        u = svc.create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Audit CREATE
    log_action(
        db,
        request=request,
        user=admin,
        table_name="usuarios",
        action=AuditAction.CREATE,
        record_id=u.id,
        after=u,
        extra={"payload": {**data.model_dump(), "password": "***"}},
    )
    return u

@router.put("/{user_id}", response_model=UserOut)
def editar(
    user_id: int,
    data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    before = svc.get_by_id(db, user_id)
    if not before:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    u = svc.update_user(db, user_id, data)
    # Audit UPDATE (ocultar pass)
    log_action(
        db,
        request=request,
        user=admin,
        table_name="usuarios",
        action=AuditAction.UPDATE,
        record_id=user_id,
        before=before,
        after=u,
        extra={"payload": {**data.model_dump(), "password": "***" if data.password else None}},
    )
    return u

@router.delete("/{user_id}", status_code=204)
def borrar(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    before = svc.get_by_id(db, user_id)
    if not before:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    svc.delete_user(db, user_id)
    # Audit DELETE
    log_action(
        db,
        request=request,
        user=admin,
        table_name="usuarios",
        action=AuditAction.DELETE,
        record_id=user_id,
        before=before,
    )
    return
