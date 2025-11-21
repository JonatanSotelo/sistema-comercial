# app/routers/audit_log_router.py
from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, func, desc
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, common_params, CommonQueryParams
from app.db.database import get_db
from app.models.auditoria import AuditLog, AuditAction
from app.schemas.auditoria_schema import AuditLogOut

router = APIRouter(prefix="/audit-logs", tags=["Auditoría"])

# -------------------------
# Helpers de filtrado/orden
# -------------------------
def _build_search_filter(search: str | None):
    """Búsqueda full-text en details (JSONB), username, table_name, record_id"""
    if not search:
        return None
    pattern = f"%{search.strip()}%"
    # Buscar en múltiples campos: details (JSONB como texto), username, table_name, record_id
    filters = []
    # Búsqueda en details (cast JSONB a texto) - puede ser None, usar coalesce para evitar NULL
    filters.append(func.coalesce(AuditLog.details.cast(func.text), "").ilike(pattern))
    # Búsqueda en username, table_name, record_id (pueden ser None, usar coalesce)
    filters.append(func.coalesce(AuditLog.username, "").ilike(pattern))
    filters.append(func.coalesce(AuditLog.table_name, "").ilike(pattern))
    filters.append(func.coalesce(AuditLog.record_id, "").ilike(pattern))
    return or_(*filters)

def _parse_sort(sort: str | None):
    allowed = {
        "id": AuditLog.id,
        "created_at": AuditLog.created_at,
        "table_name": AuditLog.table_name,
        "action": AuditLog.action,
        "username": AuditLog.username,
    }
    
    if not sort:
        return [desc(AuditLog.created_at), desc(AuditLog.id)]
    
    order = []
    for raw in [p.strip() for p in sort.split(",") if p.strip()]:
        desc_order = raw.startswith("-")
        key = raw[1:] if desc_order else raw
        col = allowed.get(key)
        if not col:
            continue
        order.append(col.desc() if desc_order else col.asc())
    return order or [desc(AuditLog.created_at), desc(AuditLog.id)]

# -------------------------
# Lectura (lista / paginado)
# -------------------------
@router.get("", response_model=Union[List[AuditLogOut], dict],
            dependencies=[Depends(require_admin)])
@router.get("/", response_model=Union[List[AuditLogOut], dict],
            dependencies=[Depends(require_admin)])
def listar(
    q: CommonQueryParams = Depends(common_params),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    table_name: Optional[str] = Query(None, description="Filtrar por módulo (table_name)"),
    action: Optional[str] = Query(None, description="Filtrar por acción (CREATE, UPDATE, DELETE, ADJUST)"),
    username: Optional[str] = Query(None, description="Filtrar por usuario"),
    record_id: Optional[str] = Query(None, description="Filtrar por entidad_id"),
    db: Session = Depends(get_db),
):
    """
    Lista logs de auditoría con filtros opcionales.
    - Si NO se envían page/size/search/sort -> list[AuditLogOut] (modo legacy)
    - Si se envía cualquiera -> dict con items, total, page, size (paginado)
    """
    filters = []
    
    # Filtros de fecha
    if fecha_desde:
        filters.append(AuditLog.created_at >= datetime.combine(fecha_desde, datetime.min.time()))
    if fecha_hasta:
        filters.append(AuditLog.created_at <= datetime.combine(fecha_hasta, datetime.max.time()))
    
    # Filtros de módulo, acción, usuario, entidad
    if table_name:
        filters.append(AuditLog.table_name == table_name)
    if action:
        try:
            action_enum = AuditAction(action.upper())
            filters.append(AuditLog.action == action_enum)
        except ValueError:
            pass  # Ignorar acciones inválidas
    if username:
        filters.append(AuditLog.username.ilike(f"%{username}%"))
    if record_id:
        filters.append(AuditLog.record_id == record_id)
    
    # Búsqueda full-text en details
    search_filter = _build_search_filter(q.search)
    if search_filter:
        filters.append(search_filter)
    
    # Query base
    query = db.query(AuditLog)
    if filters:
        query = query.filter(*filters)
    
    # Orden
    order = _parse_sort(q.sort)
    query = query.order_by(*order)
    
    # Modo legacy (sin paginación)
    if q.page is None and q.size is None and q.search is None and q.sort is None:
        items = query.limit(100).all()
        return [AuditLogOut.model_validate(item) for item in items]
    
    # Modo paginado
    page = q.page or 1
    size = q.size or 20
    
    # Total
    total = query.count()
    
    # Items paginados
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    return {
        "items": [AuditLogOut.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "size": size,
    }

@router.get("/{log_id}", response_model=AuditLogOut,
            dependencies=[Depends(require_admin)])
def obtener(log_id: int, db: Session = Depends(get_db)):
    """Obtener un log de auditoría por ID"""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log no encontrado")
    return AuditLogOut.model_validate(log)

