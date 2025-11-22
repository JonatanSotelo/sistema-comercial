# app/web/facturacion_ui.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_user
from app.models.user_model import User
from app.web.services_api_client import ApiClient

router = APIRouter(prefix="/app/facturacion", tags=["Facturación UI"])
templates = Jinja2Templates(directory="app/templates")


def _get_api_client(request: Request) -> ApiClient:
    token = request.cookies.get("access_token")
    return ApiClient(token=token)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def facturacion_index(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Página principal de facturación"""
    return templates.TemplateResponse(
        "facturacion/index.html",
        {"request": request, "user": user}
    )


@router.get("/table", response_class=HTMLResponse)
def facturacion_table(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Tabla de facturas (HTMX endpoint)"""
    import asyncio
    client = _get_api_client(request)
    
    # Obtener facturas desde la API
    try:
        facturas = asyncio.run(client.list_facturas())
    except:
        facturas = []
    
    return templates.TemplateResponse(
        "facturacion/_table.html",
        {"request": request, "items": facturas}
    )

