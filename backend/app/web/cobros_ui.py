# app/web/cobros_ui.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_user
from app.models.user_model import User
from app.web.services_api_client import ApiClient

router = APIRouter(prefix="/app/cobros", tags=["Cobros UI"])
templates = Jinja2Templates(directory="app/templates")


def _get_api_client(request: Request) -> ApiClient:
    token = request.cookies.get("access_token")
    return ApiClient(token=token)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def cobros_index(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Página principal de cobros"""
    return templates.TemplateResponse(
        "cobros/index.html",
        {"request": request, "user": user}
    )


@router.get("/table", response_class=HTMLResponse)
def cobros_table(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Tabla de cobros (HTMX endpoint)"""
    import asyncio
    client = _get_api_client(request)
    
    # Obtener cobros desde la API
    cobros = asyncio.run(client.list_cobros())
    
    return templates.TemplateResponse(
        "cobros/_table.html",
        {"request": request, "items": cobros}
    )


@router.get("/form-cobrar/{venta_id}", response_class=HTMLResponse)
def form_cobrar(
    venta_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Formulario para cobrar una venta (HTMX partial)"""
    import asyncio
    client = _get_api_client(request)
    
    # Obtener venta y su saldo
    try:
        venta = asyncio.run(client.get_venta(venta_id))
        saldo_response = asyncio.run(client.get_saldo_venta(venta_id))
        saldo = saldo_response.get("saldo", venta.get("total", 0))
    except:
        venta = {"id": venta_id, "total": 0}
        saldo = 0
    
    return templates.TemplateResponse(
        "cobros/_form_cobrar.html",
        {"request": request, "venta": venta, "saldo": saldo}
    )


@router.post("/submit-cobro", response_class=HTMLResponse)
def submit_cobro(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Procesa el cobro (HTMX endpoint)"""
    import asyncio
    from fastapi import Form
    
    # Esto se maneja mejor con Form data
    # Por ahora retornamos la tabla actualizada
    return templates.TemplateResponse(
        "cobros/_table.html",
        {"request": request, "items": [], "oob_clear": True}
    )

