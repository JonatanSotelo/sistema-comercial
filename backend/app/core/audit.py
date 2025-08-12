from typing import Any, Dict, Optional
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.auditoria import AuditAction
from app.services.auditoria_service import create_audit_log

def _serialize_model(obj) -> Dict[str, Any]:
    """Convierte un objeto SQLAlchemy en dict (solo columnas)."""
    if obj is None:
        return {}
    data = {}
    for col in obj.__table__.columns:
        data[col.name] = getattr(obj, col.name)
    return data

def diff_models(before: Any, after: Any) -> Dict[str, Any]:
    """Devuelve cambios entre before y after (solo campos distintos)."""
    b = _serialize_model(before)
    a = _serialize_model(after)
    changed = {}
    for k in set(b.keys()) | set(a.keys()):
        if b.get(k) != a.get(k):
            changed[k] = {"before": b.get(k), "after": a.get(k)}
    return changed

def log_action(
    db: Session,
    *,
    request: Optional[Request],
    user: Optional[Any],  # objeto usuario autenticado
    table_name: str,
    action: AuditAction,
    record_id: Optional[str] = None,
    before: Any = None,
    after: Any = None,
    extra: Optional[Dict[str, Any]] = None,
):
    details: Dict[str, Any] = {}
    if before is not None or after is not None:
        details["changes"] = diff_models(before, after)
        if action == AuditAction.CREATE and after is not None:
            details["after_full"] = _serialize_model(after)
        if action == AuditAction.DELETE and before is not None:
            details["before_full"] = _serialize_model(before)
    if extra:
        details["extra"] = extra

    ip = None
    path = None
    method = None
    if request is not None:
        ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else None)
        path = str(request.url.path)
        method = request.method

    user_id = getattr(user, "id", None) if user else None
    username = getattr(user, "username", None) if user else None

    create_audit_log(
        db,
        user_id=user_id,
        username=username,
        table_name=table_name,
        action=action,
        record_id=str(record_id) if record_id is not None else None,
        details=details or None,
        path=path,
        method=method,
        ip=ip,
    )
