# app/web/reports_ui.py
from datetime import date
from typing import Optional
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/app/reportes")
async def reportes_index(request: Request):
    user = request.session.get("user", "—")
    # Intentar cargar features para navbar
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"reportes": True}
    return templates.TemplateResponse(
        "reports/index.html",
        {"request": request, "features": features, "user": user, "title": "Reportes"},
    )


@router.get("/app/reportes/ventas/table")
async def reportes_ventas_table(
    request: Request,
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    group_by: str = Query("dia"),
):
    api = get_api(request)
    try:
        data = await api.get_reporte_ventas(
            desde=desde,
            hasta=hasta,
            group_by=group_by,
        )
    except Exception as e:
        print(f"Error al obtener reporte de ventas: {e}")
        data = {"items": [], "total_general": {"cantidad_items": 0, "total_cantidad": 0.0, "total_monto": 0.0}, "group_by": group_by}
    
    items = data.get("items", [])
    total_general = data.get("total_general", {"cantidad_items": 0, "total_cantidad": 0.0, "total_monto": 0.0})
    group_by = data.get("group_by", group_by)
    
    return templates.TemplateResponse(
        "reports/_ventas_table.html",
        {
            "request": request,
            "items": items,
            "total_general": total_general,
            "group_by": group_by,
            "desde": desde,
            "hasta": hasta,
        },
    )


@router.get("/app/reportes/compras/table")
async def reportes_compras_table(
    request: Request,
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    group_by: str = Query("dia"),
):
    api = get_api(request)
    try:
        data = await api.get_reporte_compras(
            desde=desde,
            hasta=hasta,
            group_by=group_by,
        )
    except Exception as e:
        print(f"Error al obtener reporte de compras: {e}")
        data = {"items": [], "total_general": {"cantidad_items": 0, "total_cantidad": 0.0, "total_monto": 0.0}, "group_by": group_by}
    
    items = data.get("items", [])
    total_general = data.get("total_general", {"cantidad_items": 0, "total_cantidad": 0.0, "total_monto": 0.0})
    group_by = data.get("group_by", group_by)
    
    return templates.TemplateResponse(
        "reports/_compras_table.html",
        {
            "request": request,
            "items": items,
            "total_general": total_general,
            "group_by": group_by,
            "desde": desde,
            "hasta": hasta,
        },
    )

