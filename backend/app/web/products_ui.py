
from fastapi import APIRouter, Request, Query, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/productos")
async def productos_index(request: Request):
    user = request.session.get("user", "—")
    # Intentar cargar features para navbar
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"productos": True}
    return templates.TemplateResponse("products/index.html", {"request": request, "features": features, "user": user, "title": "Productos"})

@router.get("/productos/table")
async def productos_table(request: Request, q: str = Query("", alias="q"), page: int = 1, size: int = 20):
    api = get_api(request)
    try:
        data = await api.list_productos(q=q, page=page, size=size)
    except Exception:
        data = {"items": [], "total": 0, "page": page, "size": size}
    items = data.get("items", [])
    total = data.get("total", 0)
    page = data.get("page", page)
    size = data.get("size", size)
    return templates.TemplateResponse("products/_table.html", {"request": request, "items": items, "total": total, "page": page, "size": size, "q": q})

@router.get("/productos/export")
async def productos_export(request: Request, format: str = "csv"):
    api = get_api(request)
    if format not in {"csv", "xlsx"}:
        raise HTTPException(status_code=400, detail="Formato inválido")
    content = await api.export_productos(fmt=format)
    media = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"productos.{format}"
    return StreamingResponse(iter([content]), media_type=media, headers={"Content-Disposition": f'attachment; filename="{filename}"'})

@router.get("/productos/form/new")
async def productos_form_new(request: Request):
    user = request.session.get("user", "—")
    features = {"productos": True}
    producto = {"id": None, "nombre": "", "precio": 0, "stock": 0, "is_active": True}
    return templates.TemplateResponse(
        "products/_form.html",
        {
            "request": request,
            "features": features,
            "user": user,
            "producto": producto,
            "title": "Nuevo producto",
        },
    )

@router.get("/productos/form/{pid}")
async def productos_form_edit(request: Request, pid: int):
    user = request.session.get("user", "—")
    features = {"productos": True}
    api = get_api(request)
    try:
        p = await api.get_producto(pid)
    except Exception:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto = {
        "id": p.get("id"),
        "nombre": p.get("nombre") or p.get("name") or "",
        "precio": p.get("precio", p.get("price", 0)) or 0,
        "stock": p.get("stock", 0),
        "is_active": p.get("is_active", True),
    }
    return templates.TemplateResponse(
        "products/_form.html",
        {
            "request": request,
            "features": features,
            "user": user,
            "producto": producto,
            "title": f"Editar {producto['nombre']}",
        },
    )

@router.post("/productos/create")
async def productos_create(
    request: Request,
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
):
    api = get_api(request)
    data = {"nombre": nombre, "precio": precio, "stock": stock, "is_active": True}
    try:
        await api.create_producto(data)
    except Exception:
        producto = {"id": None, "nombre": nombre, "precio": precio, "stock": stock, "is_active": True}
        return templates.TemplateResponse(
            "products/_form.html",
            {
                "request": request,
                "features": {"productos": True},
                "user": request.session.get("user", "—"),
                "producto": producto,
                "title": "Nuevo producto",
                "error": "No se pudo crear. Verifica datos.",
            },
        )
    return await productos_table(request, q="", page=1, size=20)

@router.post("/productos/update/{pid}")
async def productos_update(
    request: Request,
    pid: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    is_active: str = Form("true"),
):
    api = get_api(request)
    active = is_active.lower() == "true"
    data = {"nombre": nombre, "precio": precio, "stock": stock, "is_active": active}
    try:
        await api.update_producto(pid, data)
    except Exception:
        producto = {"id": pid, "nombre": nombre, "precio": precio, "stock": stock, "is_active": active}
        return templates.TemplateResponse(
            "products/_form.html",
            {
                "request": request,
                "features": {"productos": True},
                "user": request.session.get("user", "—"),
                "producto": producto,
                "title": f"Editar {nombre}",
                "error": "No se pudo actualizar.",
            },
        )
    return await productos_table(request, q="", page=1, size=20)

@router.post("/productos/toggle/{pid}")
async def productos_toggle(request: Request, pid: int, current_active: str = Form("false")):
    api = get_api(request)
    active = current_active.lower() == "true"
    try:
        await api.toggle_producto(pid, is_active=active)
    except Exception:
        pass
    return await productos_table(request, q="", page=1, size=20)
