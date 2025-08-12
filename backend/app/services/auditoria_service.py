from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
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
