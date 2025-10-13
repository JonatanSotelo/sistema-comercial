# app/web/router.py
"""
Router principal del módulo web.
Monta todos los sub-routers y configura Jinja2.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from app.web.core import web_settings

# Crear el router principal con prefijo /app
router = APIRouter(prefix="/app", tags=["Web UI"])

# Configurar Jinja2Templates
templates = Jinja2Templates(directory=web_settings.TEMPLATE_DIR)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Página principal - redirige al login si no está autenticado,
    o al dashboard si ya está autenticado.
    """
    token = request.session.get("access_token")
    if token:
        return RedirectResponse(url="/app/dashboard", status_code=303)
    return RedirectResponse(url="/app/login", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal con enlaces a las secciones."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    user = request.session.get("user", {})
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
    })


# Importar y montar sub-routers
from app.web.routers import productos, clientes, proveedores, ventas, compras, auth

router.include_router(auth.router)
router.include_router(productos.router)
router.include_router(clientes.router)
router.include_router(proveedores.router)
router.include_router(ventas.router)
router.include_router(compras.router)


