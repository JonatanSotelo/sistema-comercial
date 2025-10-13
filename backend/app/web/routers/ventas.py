# app/web/routers/ventas.py
"""
Router web para gestión de ventas con items.
"""
from typing import Optional
from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
import json

from app.web.core import web_settings
from app.web.api_client import APIClient
from app.web.routers.shared import build_hx_trigger

router = APIRouter(prefix="/ventas", tags=["Ventas Web"])
templates = Jinja2Templates(directory=web_settings.TEMPLATE_DIR)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def ventas_index(request: Request):
    """Página principal de ventas."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    user = request.session.get("user", {})
    return templates.TemplateResponse("ventas/index.html", {
        "request": request,
        "user": user,
    })


@router.get("/table", response_class=HTMLResponse)
async def ventas_table(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
):
    """Tabla de ventas para HTMX."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": page, "per_page": per_page}
    if search:
        params["q"] = search
    
    with APIClient() as client:
        try:
            response = client.get("/ventas/", params=params, headers=headers)
            
            if response.status_code == 200:
                items = response.json()
                if not isinstance(items, list):
                    items = []
                
                # Enriquecer con nombres de clientes
                clientes_map = {}
                cliente_ids = [v.get("cliente_id") for v in items if v.get("cliente_id")]
                
                if cliente_ids:
                    cli_response = client.get("/clientes", headers=headers)
                    if cli_response.status_code == 200:
                        cli_data = cli_response.json()
                        clientes_list = cli_data.get("items", []) if isinstance(cli_data, dict) else cli_data
                        for c in clientes_list:
                            clientes_map[c["id"]] = c["nombre"]
                
                # Agregar nombre del cliente a cada venta
                for item in items:
                    if item.get("cliente_id"):
                        item["cliente_nombre"] = clientes_map.get(item["cliente_id"], f"Cliente #{item['cliente_id']}")
                    else:
                        item["cliente_nombre"] = "Consumidor Final"
                
                total = len(items)
                total_pages = 1
                
                return templates.TemplateResponse("ventas/_table.html", {
                    "request": request,
                    "items": items,
                    "page": page,
                    "size": per_page,
                    "total": total,
                    "total_pages": total_pages,
                    "search": search or "",
                })
            else:
                return HTMLResponse(f"<div class='text-red-500'>Error: {response.status_code}</div>")
        
        except Exception as e:
            print(f"Error cargando ventas: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>")


@router.get("/form", response_class=HTMLResponse)
async def venta_form(request: Request):
    """Formulario para crear venta con items."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Cargar productos y clientes disponibles
    productos = []
    clientes = []
    
    with APIClient() as client:
        try:
            # Cargar productos activos
            prod_response = client.get("/productos", headers=headers)
            if prod_response.status_code == 200:
                prod_data = prod_response.json()
                if isinstance(prod_data, dict) and "items" in prod_data:
                    productos = [p for p in prod_data.get("items", []) if p.get("activo", True)]
                elif isinstance(prod_data, list):
                    productos = [p for p in prod_data if p.get("activo", True)]
            
            # Cargar clientes
            cli_response = client.get("/clientes", headers=headers)
            if cli_response.status_code == 200:
                cli_data = cli_response.json()
                if isinstance(cli_data, dict) and "items" in cli_data:
                    clientes = cli_data.get("items", [])
                elif isinstance(cli_data, list):
                    clientes = cli_data
        
        except Exception as e:
            print(f"Error cargando datos para form: {e}")
    
    return templates.TemplateResponse("ventas/_form.html", {
        "request": request,
        "productos": productos,
        "clientes": clientes,
    })


@router.post("/save", response_class=HTMLResponse)
async def venta_save(
    request: Request,
    cliente_id: Optional[int] = Form(None),
    observaciones: Optional[str] = Form(None),
    items_json: str = Form(...),
):
    """Guarda venta con items."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Parsear items
        items = json.loads(items_json)
        
        if not items:
            return HTMLResponse("<div class='text-red-500'>Debe agregar al menos un producto</div>", status_code=400)
        
        # Preparar payload
        payload = {
            "cliente_id": cliente_id,
            "observaciones": observaciones,
            "items": items,
        }
        
        with APIClient() as client:
            response = client.post("/ventas/", json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                return Response(
                    content="",
                    status_code=200,
                    headers={
                        "HX-Trigger": build_hx_trigger("refreshTable"),
                        "HX-Redirect": "/app/ventas",
                    }
                )
            else:
                error_data = response.json()
                error_detail = error_data.get("detail", "Error desconocido")
                # Mensaje amigable para stock insuficiente
                if "stock insuficiente" in str(error_detail).lower():
                    error_detail = "⚠️ Stock insuficiente. Verifica el stock disponible del producto."
                return HTMLResponse(
                    f"<div class='bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded'>{error_detail}</div>",
                    status_code=400
                )
    
    except json.JSONDecodeError:
        return HTMLResponse("<div class='text-red-500'>Error en formato de items</div>", status_code=400)
    except Exception as e:
        print(f"Error guardando venta: {e}")
        return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.get("/{venta_id}/detalle", response_class=HTMLResponse)
async def venta_detalle(request: Request, venta_id: int):
    """Ver detalle de una venta."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            response = client.get(f"/ventas/{venta_id}", headers=headers)
            
            if response.status_code == 200:
                venta = response.json()
                user = request.session.get("user", {})
                
                return templates.TemplateResponse("ventas/_detalle.html", {
                    "request": request,
                    "venta": venta,
                    "user": user,
                })
            else:
                return HTMLResponse(f"<div class='text-red-500'>Venta no encontrada</div>", status_code=404)
        
        except Exception as e:
            print(f"Error cargando venta {venta_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.patch("/{venta_id}/completar", response_class=HTMLResponse)
async def venta_completar(request: Request, venta_id: int):
    """Marca una venta como completada."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            # Actualizar el estado a completada
            response = client.patch(
                f"/ventas/{venta_id}/estado?estado=completada",
                headers=headers
            )
            
            if response.status_code == 200:
                return Response(
                    content="",
                    status_code=200,
                    headers={"HX-Trigger": build_hx_trigger("refreshTable")}
                )
            else:
                error_detail = response.json().get("detail", "Error al completar")
                return HTMLResponse(f"<div class='text-red-500'>{error_detail}</div>", status_code=400)
        
        except Exception as e:
            print(f"Error completando venta {venta_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.delete("/{venta_id}", response_class=HTMLResponse)
async def venta_delete(request: Request, venta_id: int):
    """Elimina venta."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            response = client.delete(f"/ventas/{venta_id}", headers=headers)
            
            if response.status_code == 204:
                return Response(
                    content="",
                    status_code=200,
                    headers={"HX-Trigger": build_hx_trigger("refreshTable")}
                )
            else:
                error_detail = response.json().get("detail", "Error al eliminar")
                return HTMLResponse(f"<div class='text-red-500'>{error_detail}</div>", status_code=400)
        
        except Exception as e:
            print(f"Error eliminando venta {venta_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)
