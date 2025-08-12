from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user_schema import Token, LoginIn
from app.core.security import create_access_token
from app.services.user_service import authenticate
from app.core.deps import get_current_user
from app.core.audit import log_action
from app.models.auditoria import AuditAction

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token(subject=user.username)
    # Audit LOGIN
    log_action(
        db,
        request=request,
        user=user,
        table_name="usuarios",
        action=AuditAction.LOGIN,
        record_id=user.id,
        extra={"username": user.username},
    )
    return Token(access_token=token)

@router.post("/logout", status_code=204)
def logout(
    request: Request,
    user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # JWT es stateless; acá solo auditamos el evento
    log_action(
        db,
        request=request,
        user=user,
        table_name="usuarios",
        action=AuditAction.LOGOUT,
        record_id=user.id,
        extra={"username": user.username},
    )
    return
