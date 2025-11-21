# app/web/audit_ui.py
from datetime import date
from typing import Optional
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/app/auditoria")
async def auditoria_index(request: Request):
    user = request.session.get("user", "—")
    # Intentar cargar features para navbar
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"auditoria": True}
    return templates.TemplateResponse(
        "audit/index.html",
        {"request": request, "features": features, "user": user, "title": "Auditoría"},
    )


@router.get("/app/auditoria/table")
async def auditoria_table(
    request: Request,
    q: str = Query("", alias="q"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    table_name: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    record_id: Optional[str] = Query(None),
):
    api = get_api(request)
    try:
        data = await api.list_audit_logs(
            q=q,
            page=page,
            size=size,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            table_name=table_name,
            action=action,
            username=username,
            record_id=record_id,
        )
    except Exception:
        data = {"items": [], "total": 0, "page": page, "size": size}
    
    items = data.get("items", [])
    total = data.get("total", 0)
    page = data.get("page", page)
    size = data.get("size", size)
    
    return templates.TemplateResponse(
        "audit/_table.html",
        {
            "request": request,
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "q": q,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "table_name": table_name,
            "action": action,
            "username": username,
            "record_id": record_id,
        },
    )

