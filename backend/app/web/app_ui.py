
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

async def _get_features(request: Request):
    api = get_api(request)
    try:
        data = await api.get_features()
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    # fallback: todo visible
    return {"productos": True, "clientes": True, "proveedores": True, "ventas": True, "compras": True, "auditoria": True}

@router.get("/")
async def root_redirect():
    return RedirectResponse("/app/dashboard", status_code=HTTP_302_FOUND)

@router.get("/dashboard")
async def dashboard(request: Request):
    user = request.session.get("user", "—")
    features = await _get_features(request)
    return templates.TemplateResponse("dashboard.html", {"request": request, "features": features, "user": user, "title": "Dashboard"})
