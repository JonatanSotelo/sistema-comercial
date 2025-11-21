# app/web/iva_compras_ui.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_user
from app.models.user_model import User
from app.web.services_api_client import ApiClient

router = APIRouter(prefix="/app/iva-compras", tags=["IVA Compras UI"])
templates = Jinja2Templates(directory="app/templates")


def _get_api_client(request: Request) -> ApiClient:
    token = request.cookies.get("access_token")
    return ApiClient(token=token)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def iva_compras_index(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Página principal de IVA Compras"""
    return templates.TemplateResponse(
        "iva-compras/index.html",
        {"request": request, "user": user}
    )


@router.get("/table", response_class=HTMLResponse)
def iva_compras_table(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Tabla de IVA Compras (HTMX endpoint)"""
    import asyncio
    client = _get_api_client(request)
    
    # Obtener registros desde la API
    items = asyncio.run(client.list_iva_compras())
    
    return templates.TemplateResponse(
        "iva-compras/_table.html",
        {"request": request, "items": items}
    )

