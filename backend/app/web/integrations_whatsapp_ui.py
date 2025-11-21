# app/web/integrations_whatsapp_ui.py
from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/app/integraciones/whatsapp")
async def integrations_whatsapp_index(request: Request):
    """Vista principal del monitor de integraciones WhatsApp"""
    user = request.session.get("user", "—")
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {}
    return templates.TemplateResponse(
        "integrations/whatsapp/index.html",
        {"request": request, "features": features, "user": user, "title": "Integraciones WhatsApp"},
    )


@router.get("/app/integraciones/whatsapp/table")
async def integrations_whatsapp_table(
    request: Request,
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),  # cotización|venta|error
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=1000),
):
    """Tabla de eventos de integración WhatsApp (desde auditoría)"""
    api = get_api(request)
    
    # Construir filtros
    params = {
        "page": page,
        "size": size,
        "table_name": "integraciones",
        "action": "CREATE"
    }
    
    if fecha_desde:
        params["fecha_desde"] = fecha_desde
    if fecha_hasta:
        params["fecha_hasta"] = fecha_hasta
    if phone:
        params["record_id"] = phone  # Usar record_id para buscar por phone en details
    
    # Obtener logs de auditoría
    try:
        response = await api.list_audit_logs(**params)
        items = response.get("items", []) if isinstance(response, dict) else response
        total = response.get("total", len(items)) if isinstance(response, dict) else len(items)
    except Exception as e:
        items = []
        total = 0
        print(f"[integrations_whatsapp] Error al obtener logs: {e}")
    
    # Filtrar por estado si viene
    if estado:
        items = [
            item for item in items
            if item.get("details", {}).get("status") == estado
        ]
    
    # Formatear items para la tabla
    table_rows = []
    for item in items[:size]:  # Limitar a size
        details = item.get("details", {})
        result = details.get("result", {})
        venta_id = result.get("venta_id") if isinstance(result, dict) else None
        
        # Determinar estado
        status = details.get("status", "unknown")
        tipo = result.get("type", "unknown") if isinstance(result, dict) else "unknown"
        
        # Determinar estado visual
        if status == "error":
            estado_display = "error"
        elif tipo == "sale":
            estado_display = "venta"
        elif tipo == "quote":
            estado_display = "cotización"
        else:
            estado_display = "unknown"
        
        # Filtrar por estado si viene
        if estado and estado_display != estado:
            continue
        
        table_rows.append({
            "id": item.get("id"),
            "fecha": item.get("created_at", ""),
            "phone": details.get("phone", "—"),
            "cliente_id": details.get("cliente_id"),
            "venta_id": venta_id,
            "estado": estado_display,
            "total": result.get("total", 0) if isinstance(result, dict) else 0,
            "items_count": details.get("items_count", 0),
            "error": details.get("error")
        })
    
    return templates.TemplateResponse(
        "integrations/whatsapp/table.html",
        {
            "request": request,
            "items": table_rows,
            "total": len(table_rows),
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "phone": phone,
            "estado": estado,
        },
    )


