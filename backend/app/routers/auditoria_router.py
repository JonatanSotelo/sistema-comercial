from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.core.deps import get_current_user
from app.schemas.auditoria_schema import AuditLogOut
from app.models.auditoria import AuditLog

router = APIRouter(prefix="/auditoria", tags=["Auditoría"])

@router.get("/", response_model=List[AuditLogOut])
def listar_logs(
    table: Optional[str] = Query(None),
    record_id: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if table:
        q = q.filter(AuditLog.table_name == table)
    if record_id:
        q = q.filter(AuditLog.record_id == record_id)
    if since:
        q = q.filter(AuditLog.created_at >= since)
    return q.limit(500).all()
