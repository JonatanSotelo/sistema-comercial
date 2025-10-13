# app/web/routers/clientes.py
"""
Router web para gestión de clientes.
"""
from typing import Optional
from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
import httpx

from app.web.core import web_settings
from app.web.api_client import APIClient
from app.web.routers.shared import build_hx_trigger

router = APIRouter(prefix="/clientes", tags=["Clientes Web"])
templates = Jinja2Templates(directory=web_settings.TEMPLATE_DIR)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def clientes_index(request: Request):
    """Página principal de clientes."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    user = request.session.get("user", {})
    return templates.TemplateResponse("clientes/index.html", {
        "request": request,
        "user": user,
    })


@router.get("/table", response_class=HTMLResponse)
async def clientes_table(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
):
    """Tabla de clientes para HTMX."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # TODO: Ajustar parámetros según el endpoint real del backend
    params = {"page": page, "per_page": per_page}
    if search:
        params["search"] = search
    
    with APIClient() as client:
        try:
            response = client.get("/clientes", params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # El backend retorna lista o dict paginado
                if isinstance(data, dict) and "items" in data:
                    items = data.get("items", [])
                    total = data.get("total", 0)
                else:
                    items = data
                    total = len(items)
                
                page_size = per_page
                total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
                
                return templates.TemplateResponse("clientes/_table.html", {
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
            print(f"Error cargando clientes: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>")


@router.get("/form", response_class=HTMLResponse)
async def cliente_form(
    request: Request,
    id: Optional[int] = Query(None),
):
    """Formulario crear/editar cliente."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    cliente = None
    
    if id:
        headers = {"Authorization": f"Bearer {token}"}
        
        with APIClient() as client:
            try:
                response = client.get(f"/clientes/{id}", headers=headers)
                if response.status_code == 200:
                    cliente = response.json()
            except Exception as e:
                print(f"Error cargando cliente {id}: {e}")
    
    return templates.TemplateResponse("clientes/_form.html", {
        "request": request,
        "cliente": cliente,
    })


@router.post("/save", response_class=HTMLResponse)
async def cliente_save(
    request: Request,
    id: Optional[int] = Form(None),
    nombre: str = Form(...),
    email: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
):
    """Guarda cliente."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
    }
    
    with APIClient() as client:
        try:
            if id:
                response = client.put(f"/clientes/{id}", json=payload, headers=headers)
            else:
                response = client.post("/clientes", json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                return Response(
                    content="",
                    status_code=200,
                    headers={
                        "HX-Trigger": build_hx_trigger("refreshTable"),
                        "HX-Redirect": "/app/clientes",
                    }
                )
            else:
                error_detail = response.json().get("detail", "Error desconocido")
                return HTMLResponse(f"<div class='text-red-500'>Error: {error_detail}</div>", status_code=400)
        
        except Exception as e:
            print(f"Error guardando cliente: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.delete("/{cliente_id}", response_class=HTMLResponse)
async def cliente_delete(request: Request, cliente_id: int):
    """Elimina cliente."""
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            response = client.delete(f"/clientes/{cliente_id}", headers=headers)
            
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
            print(f"Error eliminando cliente {cliente_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.get("/export")
async def clientes_export(request: Request, search: Optional[str] = Query(None)):
    """Exporta clientes a Excel."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    client = get_api_client()
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {}
    if search:
        params["search"] = search
    
    with APIClient() as client:
        try:
            response = client.get("/clientes/export", params=params, headers=headers)
            
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="clientes.xlsx"'}
                )
            else:
                return HTMLResponse("<div>Error al exportar</div>", status_code=500)
        
        except Exception as e:
            print(f"Error exportando clientes: {e}")
            return HTMLResponse(f"<div>Error: {str(e)}</div>", status_code=500)

