# app/web/routers/productos.py
"""
Router web para gestión de productos con HTMX.
"""
from typing import Optional
from fastapi import APIRouter, Request, Form, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
import httpx

from app.web.core import web_settings
from app.web.api_client import APIClient
from app.web.routers.shared import build_hx_trigger, parse_pagination_params

router = APIRouter(prefix="/productos", tags=["Productos Web"])
templates = Jinja2Templates(directory=web_settings.TEMPLATE_DIR)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def productos_index(request: Request):
    """Página principal de productos."""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    user = request.session.get("user", {})
    return templates.TemplateResponse("productos/index.html", {
        "request": request,
        "user": user,
    })


@router.get("/table", response_class=HTMLResponse)
async def productos_table(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
):
    """
    Fragmento HTML de la tabla de productos (para HTMX).
    """
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Llamar al API backend
    params = {"page": page, "size": size}
    if search:
        params["search"] = search
    
    with APIClient() as client:
        try:
            response = client.get("/productos", params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # El backend puede retornar paginado o lista simple
                if isinstance(data, dict) and "items" in data:
                    items = data.get("items", [])
                    total = data.get("total", 0)
                    current_page = data.get("page", page)
                    page_size = data.get("size", size)
                else:
                    # Lista simple sin paginación
                    items = data
                    total = len(items)
                    current_page = 1
                    page_size = len(items)
                
                total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
                
                return templates.TemplateResponse("productos/_table.html", {
                    "request": request,
                    "items": items,
                    "page": current_page,
                    "size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "search": search or "",
                })
            else:
                return HTMLResponse(f"<div class='text-red-500'>Error al cargar productos: {response.status_code}</div>")
        
        except Exception as e:
            print(f"Error cargando productos: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>")


@router.get("/form", response_class=HTMLResponse)
async def producto_form(
    request: Request,
    id: Optional[int] = Query(None),
):
    """
    Formulario para crear/editar producto (modal HTMX).
    """
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    producto = None
    
    # Si hay ID, cargar el producto existente
    if id:
        headers = {"Authorization": f"Bearer {token}"}
        
        with APIClient() as client:
            try:
                response = client.get(f"/productos/{id}", headers=headers)
                if response.status_code == 200:
                    producto = response.json()
            except Exception as e:
                print(f"Error cargando producto {id}: {e}")
    
    return templates.TemplateResponse("productos/_form.html", {
        "request": request,
        "producto": producto,
    })


@router.post("/save", response_class=HTMLResponse)
async def producto_save(
    request: Request,
    id: Optional[int] = Form(None),
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    codigo: Optional[str] = Form(None),
    categoria: Optional[str] = Form(None),
    precio: float = Form(...),
    costo: Optional[float] = Form(None),
    stock: int = Form(0),
    stock_minimo: int = Form(0),
    activo: bool = Form(True),
):
    """
    Guarda (crea o actualiza) un producto.
    """
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Preparar payload
    payload = {
        "nombre": nombre,
        "descripcion": descripcion,
        "codigo": codigo,
        "categoria": categoria,
        "precio": precio,
        "costo": costo,
        "stock": stock,
        "stock_minimo": stock_minimo,
        "activo": activo,
    }
    
    with APIClient() as client:
        try:
            if id:
                # Actualizar
                response = client.put(f"/productos/{id}", json=payload, headers=headers)
            else:
                # Crear
                response = client.post("/productos/", json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                # Éxito: cerrar modal y refrescar tabla
                return Response(
                    content="",
                    status_code=200,
                    headers={
                        "HX-Trigger": build_hx_trigger("refreshTable"),
                        "HX-Redirect": "/app/productos",
                    }
                )
            else:
                error_detail = response.json().get("detail", "Error desconocido")
                return HTMLResponse(
                    f"<div class='text-red-500'>Error: {error_detail}</div>",
                    status_code=400
                )
        
        except Exception as e:
            print(f"Error guardando producto: {e}")
            return HTMLResponse(
                f"<div class='text-red-500'>Error: {str(e)}</div>",
                status_code=500
            )


@router.delete("/{producto_id}", response_class=HTMLResponse)
async def producto_delete(
    request: Request,
    producto_id: int,
):
    """
    Elimina un producto.
    """
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            response = client.delete(f"/productos/{producto_id}", headers=headers)
        
            if response.status_code == 204:
                # Éxito: refrescar tabla
                return Response(
                    content="",
                    status_code=200,
                    headers={"HX-Trigger": build_hx_trigger("refreshTable")}
                )
            else:
                error_detail = response.json().get("detail", "Error al eliminar")
                return HTMLResponse(
                    f"<div class='text-red-500'>{error_detail}</div>",
                    status_code=400
                )
        
        except Exception as e:
            print(f"Error eliminando producto {producto_id}: {e}")
            return HTMLResponse(
                f"<div class='text-red-500'>Error: {str(e)}</div>",
                status_code=500
            )


@router.patch("/{producto_id}/toggle", response_class=HTMLResponse)
async def producto_toggle_activo(
    request: Request,
    producto_id: int,
):
    """
    Activa/desactiva un producto (toggle del campo activo).
    """
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<div>No autenticado</div>", status_code=401)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with APIClient() as client:
        try:
            # Primero obtener el producto actual
            response = client.get(f"/productos/{producto_id}", headers=headers)
        
            if response.status_code == 200:
                producto = response.json()
                nuevo_estado = not producto.get("activo", True)
                
                # Actualizar solo el campo activo
                update_response = client.put(
                    f"/productos/{producto_id}",
                    json={"activo": nuevo_estado},
                    headers=headers
                )
                
                if update_response.status_code == 200:
                    return Response(
                        content="",
                        status_code=200,
                        headers={"HX-Trigger": build_hx_trigger("refreshTable")}
                    )
            
            return HTMLResponse("<div class='text-red-500'>Error al cambiar estado</div>", status_code=400)
        
        except Exception as e:
            print(f"Error toggle producto {producto_id}: {e}")
            return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>", status_code=500)


@router.get("/export")
async def productos_export(
    request: Request,
    search: Optional[str] = Query(None),
):
    """
    Exporta productos a Excel.
    """
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/app/login", status_code=303)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {}
    if search:
        params["search"] = search
    
    with APIClient() as client:
        try:
            response = client.get("/productos/export", params=params, headers=headers)
        
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="productos.xlsx"'}
                )
            else:
                return HTMLResponse("<div>Error al exportar</div>", status_code=500)
        
        except Exception as e:
            print(f"Error exportando productos: {e}")
            return HTMLResponse(f"<div>Error: {str(e)}</div>", status_code=500)

