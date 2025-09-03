# backend/app/services/auditoria_service.py
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.models.auditoria import AuditLog, AuditAction

def create_audit_log(
    db: Session,
    *,
    user_id: Optional[int],
    username: Optional[str],
    table_name: str,
    action: AuditAction,
    record_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    ip: Optional[str] = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        username=username,
        table_name=table_name,
        action=action,
        record_id=record_id,
        details=details,
        path=path,
        method=method,
        ip=ip,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

# --- Helpers cómodos para routers ---

def _to_dict(obj: Any) -> Dict[str, Any]:
    """Convierte ORM/Pydantic a dict sin romper si hay _sa_instance_state."""
    if obj is None:
        return {}
    if hasattr(obj, "model_dump"):       # Pydantic v2
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        d = dict(obj.__dict__)
        d.pop("_sa_instance_state", None)
        return d
    return {"repr": repr(obj)}

def get_client_ip(request: Optional[Request]) -> Optional[str]:
    if not request:
        return None
    xfwd = request.headers.get("x-forwarded-for")
    if xfwd:
        return xfwd.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None

def log_action(
    db: Session,
    *,
    user: Any,                # objeto User (ORM/Pydantic)
    table_name: str,
    action: AuditAction,
    record_id: Optional[int] = None,
    request: Optional[Request] = None,
    before: Any = None,
    after: Any = None,
    extra: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    details: Dict[str, Any] = {
        "before": _to_dict(before),
        "after": _to_dict(after),
    }
    if extra:
        details["extra"] = extra
    return create_audit_log(
        db,
        user_id=getattr(user, "id", None),
        username=getattr(user, "username", None),
        table_name=table_name,
        action=action,
        record_id=str(record_id) if record_id is not None else None,
        details=details,
        path=request.url.path if request else None,
        method=request.method if request else None,
        ip=get_client_ip(request),
    )
