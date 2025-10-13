# app/web/routers/compras.py
"""
Router web para gestión de compras con items.
"""
from typing import Optional
from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
import json

from app.web.core import web_settings
from app.web.api_client import APIClient
from app.web.routers.shared import build_hx_trigger

router = APIRouter(prefix="/compras", tags=["Compras Web"])
templates = Jinja2Templates(directory=web_settings.TEMPLATE_DIR)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def compras_index(request: Request):
    """Página principal de compras."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    user = request.session.get("user", {})
    return templates.TemplateResponse("compras/index.html", {
        "request": request,
        "user": user,
    })


@router.get("/table", response_class=HTMLResponse)
async def compras_table(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
):
    """Tabla de compras para HTMX."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": page, "per_page": per_page}
    if search:
        params["q"] = search
    
    with APIClient() as client:
        try:
            response = client.get("/compras/", params=params, headers=headers)
            
            if response.status_code == 200:
                items = response.json()
                if not isinstance(items, list):
                    items = []
                
                # Enriquecer con nombres de proveedores
                proveedores_map = {}
                proveedor_ids = [c.get("proveedor_id") for c in items if c.get("proveedor_id")]
                
                if proveedor_ids:
                    prov_response = client.get("/proveedores", headers=headers)
                    if prov_response.status_code == 200:
                        prov_data = prov_response.json()
                        proveedores_list = prov_data.get("items", []) if isinstance(prov_data, dict) else prov_data
                        for p in proveedores_list:
                            proveedores_map[p["id"]] = p["nombre"]
                
                # Agregar nombre del proveedor a cada compra
                for item in items:
                    if item.get("proveedor_id"):
                        item["proveedor_nombre"] = proveedores_map.get(item["proveedor_id"], f"Proveedor #{item['proveedor_id']}")
                    else:
                        item["proveedor_nombre"] = "Sin especificar"
                
                total = len(items)
                total_pages = 1
                
                return templates.TemplateResponse("compras/_table.html", {
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
            print(f"Error cargando compras: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>")


@router.get("/form", response_class=HTMLResponse)
async def compra_form(request: Request):
    """Formulario para crear compra con items."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Cargar productos y proveedores disponibles
    productos = []
    proveedores = []
    
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
            
            # Cargar proveedores
            prov_response = client.get("/proveedores", headers=headers)
            if prov_response.status_code == 200:
                prov_data = prov_response.json()
                if isinstance(prov_data, dict) and "items" in prov_data:
                    proveedores = prov_data.get("items", [])
                elif isinstance(prov_data, list):
                    proveedores = prov_data
        
        except Exception as e:
            print(f"Error cargando datos para form: {e}")
    
    return templates.TemplateResponse("compras/_form.html", {
        "request": request,
        "productos": productos,
        "proveedores": proveedores,
    })


@router.post("/save", response_class=HTMLResponse)
async def compra_save(
    request: Request,
    proveedor_id: int = Form(...),
    observaciones: Optional[str] = Form(None),
    items_json: str = Form(...),
):
    """Guarda compra con items."""
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
            "proveedor_id": proveedor_id,
            "observaciones": observaciones,
            "items": items,
        }
        
        with APIClient() as client:
            response = client.post("/compras/", json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                return Response(
                    content="",
                    status_code=200,
                    headers={
                        "HX-Trigger": build_hx_trigger("refreshTable"),
                        "HX-Redirect": "/app/compras",
                    }
                )
            else:
                error_data = response.json()
                error_detail = error_data.get("detail", "Error desconocido")
                return HTMLResponse(
                    f"<div class='bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded'>{error_detail}</div>",
                    status_code=400
                )
    
    except json.JSONDecodeError:
        return HTMLResponse("<div class='text-red-500'>Error en formato de items</div>", status_code=400)
    except Exception as e:
        print(f"Error guardando compra: {e}")
        return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.get("/{compra_id}/detalle", response_class=HTMLResponse)
async def compra_detalle(request: Request, compra_id: int):
    """Ver detalle de una compra."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            response = client.get(f"/compras/{compra_id}", headers=headers)
            
            if response.status_code == 200:
                compra = response.json()
                user = request.session.get("user", {})
                
                return templates.TemplateResponse("compras/_detalle.html", {
                    "request": request,
                    "compra": compra,
                    "user": user,
                })
            else:
                return HTMLResponse(f"<div class='text-red-500'>Compra no encontrada</div>", status_code=404)
        
        except Exception as e:
            print(f"Error cargando compra {compra_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.patch("/{compra_id}/completar", response_class=HTMLResponse)
async def compra_completar(request: Request, compra_id: int):
    """Marca una compra como completada."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            # Actualizar el estado a completada
            response = client.patch(
                f"/compras/{compra_id}/estado?estado=completada",
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
            print(f"Error completando compra {compra_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.delete("/{compra_id}", response_class=HTMLResponse)
async def compra_delete(request: Request, compra_id: int):
    """Elimina compra."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            response = client.delete(f"/compras/{compra_id}", headers=headers)
            
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
            print(f"Error eliminando compra {compra_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)
