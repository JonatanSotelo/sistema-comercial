# app/web/backups_ui.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/app/backups")
async def backups_index(request: Request):
    user = request.session.get("user", "—")
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"backups": True}
    return templates.TemplateResponse(
        "backups/index.html",
        {"request": request, "features": features, "user": user, "title": "Backups"},
    )


@router.get("/app/backups/table")
async def backups_table(request: Request):
    api = get_api(request)
    try:
        data = await api.list_backups()
    except Exception as e:
        print(f"Error al listar backups: {e}")
        data = {"items": [], "total": 0}
    
    items = data.get("items", [])
    total = data.get("total", 0)
    
    return templates.TemplateResponse(
        "backups/_table.html",
        {"request": request, "items": items, "total": total},
    )


@router.post("/app/backups/create")
async def backups_create(request: Request):
    api = get_api(request)
    try:
        result = await api.create_backup()
        # Refrescar tabla
        data = await api.list_backups()
    except Exception as e:
        print(f"Error al crear backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    items = data.get("items", [])
    total = data.get("total", 0)
    
    # Retornar tabla actualizada + OOB clear
    response = templates.TemplateResponse(
        "backups/_table.html",
        {"request": request, "items": items, "total": total},
    )
    response.headers["HX-Trigger"] = "refreshTable"
    return response

