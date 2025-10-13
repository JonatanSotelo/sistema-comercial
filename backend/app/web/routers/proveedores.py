# app/web/routers/proveedores.py
"""
Router web para gestión de proveedores con HTMX.
"""
from typing import Optional
from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.web.core import web_settings
from app.web.api_client import APIClient
from app.web.routers.shared import build_hx_trigger

router = APIRouter(prefix="/proveedores", tags=["Proveedores Web"])
templates = Jinja2Templates(directory=web_settings.TEMPLATE_DIR)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def proveedores_index(request: Request):
    """Página principal de proveedores."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    user = request.session.get("user", {})
    return templates.TemplateResponse("proveedores/index.html", {
        "request": request,
        "user": user,
    })


@router.get("/table", response_class=HTMLResponse)
async def proveedores_table(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
):
    """Tabla de proveedores para HTMX."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": page, "size": size}
    if search:
        params["search"] = search
    
    with APIClient() as client:
        try:
            response = client.get("/proveedores", params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # El backend retorna lista o dict paginado
                if isinstance(data, dict) and "items" in data:
                    items = data.get("items", [])
                    total = data.get("total", 0)
                else:
                    items = data if isinstance(data, list) else []
                    total = len(items)
                
                page_size = size
                total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
                
                return templates.TemplateResponse("proveedores/_table.html", {
                    "request": request,
                    "items": items,
                    "page": page,
                    "size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "search": search or "",
                })
            else:
                return HTMLResponse(f"<div class='text-red-500'>Error: {response.status_code}</div>")
        
        except Exception as e:
            print(f"Error cargando proveedores: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>")


@router.get("/form", response_class=HTMLResponse)
async def proveedor_form(
    request: Request,
    id: Optional[int] = Query(None),
):
    """Formulario crear/editar proveedor."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    proveedor = None
    
    if id:
        headers = {"Authorization": f"Bearer {token}"}
        
        with APIClient() as client:
            try:
                response = client.get(f"/proveedores/{id}", headers=headers)
                if response.status_code == 200:
                    proveedor = response.json()
            except Exception as e:
                print(f"Error cargando proveedor {id}: {e}")
    
    return templates.TemplateResponse("proveedores/_form.html", {
        "request": request,
        "proveedor": proveedor,
    })


@router.post("/save", response_class=HTMLResponse)
async def proveedor_save(
    request: Request,
    id: Optional[int] = Form(None),
    nombre: str = Form(...),
    email: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    direccion: Optional[str] = Form(None),
    cuit: Optional[str] = Form(None),
):
    """Guarda proveedor."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "direccion": direccion,
        "cuit": cuit,
    }
    
    with APIClient() as client:
        try:
            if id:
                response = client.put(f"/proveedores/{id}", json=payload, headers=headers)
            else:
                response = client.post("/proveedores", json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                return Response(
                    content="",
                    status_code=200,
                    headers={
                        "HX-Trigger": build_hx_trigger("refreshTable"),
                        "HX-Redirect": "/app/proveedores",
                    }
                )
            else:
                error_detail = response.json().get("detail", "Error desconocido")
                return HTMLResponse(f"<div class='text-red-500'>Error: {error_detail}</div>", status_code=400)
        
        except Exception as e:
            print(f"Error guardando proveedor: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.delete("/{proveedor_id}", response_class=HTMLResponse)
async def proveedor_delete(request: Request, proveedor_id: int):
    """Elimina proveedor."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            response = client.delete(f"/proveedores/{proveedor_id}", headers=headers)
            
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
            print(f"Error eliminando proveedor {proveedor_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)
