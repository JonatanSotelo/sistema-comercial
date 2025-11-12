
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/productos")
async def productos_index(request: Request):
    user = request.session.get("user", "—")
    # Intentar cargar features para navbar
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"productos": True}
    return templates.TemplateResponse("products/index.html", {"request": request, "features": features, "user": user, "title": "Productos"})

@router.get("/productos/table")
async def productos_table(request: Request, q: str = Query("", alias="q"), page: int = 1, size: int = 20):
    api = get_api(request)
    try:
        data = await api.list_productos(q=q, page=page, size=size)
    except Exception:
        data = {"items": [], "total": 0, "page": page, "size": size}
    items = data.get("items", [])
    total = data.get("total", 0)
    page = data.get("page", page)
    size = data.get("size", size)
    return templates.TemplateResponse("products/_table.html", {"request": request, "items": items, "total": total, "page": page, "size": size, "q": q})

@router.get("/productos/export")
async def productos_export(request: Request, format: str = "csv"):
    api = get_api(request)
    if format not in {"csv", "xlsx"}:
        raise HTTPException(status_code=400, detail="Formato inválido")
    content = await api.export_productos(fmt=format)
    media = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"productos.{format}"
    return StreamingResponse(iter([content]), media_type=media, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
