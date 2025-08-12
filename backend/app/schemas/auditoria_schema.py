from typing import Any, Optional, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.auditoria import AuditAction  # fuente única del enum

class AuditLogOut(BaseModel):
    id: int
    created_at: datetime

    user_id: Optional[int] = None
    username: Optional[str] = None

    table_name: str
    action: AuditAction
    record_id: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None
    ip: Optional[str] = None

    details: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
