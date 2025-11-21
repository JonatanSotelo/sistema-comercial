import re
from typing import Any, Dict, List
import httpx
from fastapi import APIRouter, Request, Query, HTTPException, Form
from fastapi.templating import Jinja2Templates

from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


def _to_float(value: str | None) -> float | None:
    if not value:
        return None
    try:
        cleaned = value.replace(",", ".").replace(" ", "")
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def _to_int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        cleaned = re.sub(r"[^\d]", "", str(value))
        return int(cleaned) if cleaned else None
    except (ValueError, AttributeError):
        return None


@router.get("/ventas")
async def ventas_index(request: Request):
    user = request.session.get("user", "—")
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"ventas": True}
    return templates.TemplateResponse(
        "sales/index.html",
        {
            "request": request,
            "features": features,
            "user": user,
            "title": "Ventas",
        },
    )


@router.get("/ventas/table")
async def ventas_table(
    request: Request,
    q: str = Query("", alias="q"),
    page: int = 1,
    size: int = 20,
    oob_clear: bool = False,
):
    api = get_api(request)
    try:
        data = await api.list_ventas(q=q, page=page, size=size)
    except Exception:
        data = {"items": [], "total": 0, "page": page, "size": size}

    if isinstance(data, dict):
        items = data.get("items", [])
        total = data.get("total", len(items))
        page = data.get("page", page)
        size = data.get("size", size)
    elif isinstance(data, list):
        items = data
        total = len(items)
    else:
        items, total = [], 0

    return templates.TemplateResponse(
        "sales/_table.html",
        {
            "request": request,
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "q": q,
            "oob_clear": oob_clear,
        },
    )


@router.get("/ventas/form/new")
async def ventas_form_new(request: Request):
    return templates.TemplateResponse(
        "sales/_form.html",
        {
            "request": request,
            "venta": {"id": None, "cliente_id": None, "items": []},
            "error": None,
        },
    )


@router.get("/ventas/lookup/cliente")
async def ventas_lookup_cliente(request: Request, q: str = Query("")):
    api = get_api(request)
    try:
        items = await api.search_clientes(q=q, size=5)
    except Exception:
        items = []

    return templates.TemplateResponse(
        "sales/_lookup_cliente.html",
        {"request": request, "items": items},
    )


@router.get("/ventas/lookup/producto")
async def ventas_lookup_producto(request: Request, q: str = Query("")):
    api = get_api(request)
    try:
        items = await api.search_productos(q=q, size=5)
    except Exception:
        items = []

    return templates.TemplateResponse(
        "sales/_lookup_producto.html",
        {"request": request, "items": items},
    )


@router.post("/ventas/create")
async def ventas_create(
    request: Request,
    cliente_id: str = Form(""),
    producto_id: List[str] = Form([]),
    cantidad: List[str] = Form([]),
    precio_unitario: List[str] = Form([]),
):
    api = get_api(request)

    cliente_id_int = _to_int(cliente_id) if cliente_id else None

    items = []
    for pid_str, cant_str, precio_str in zip(producto_id, cantidad, precio_unitario):
        pid = _to_int(pid_str)
        cant = _to_float(cant_str) or _to_int(cant_str)
        precio = _to_float(precio_str)

        if pid is None or cant is None or cant <= 0:
            continue
        if precio is None or precio <= 0:
            continue

        items.append(
            {
                "producto_id": pid,
                "cantidad": int(cant),
                "precio_unitario": float(precio),
            }
        )

    if not items:
        return templates.TemplateResponse(
            "sales/_form.html",
            {
                "request": request,
                "venta": {"id": None, "cliente_id": cliente_id, "items": []},
                "error": "Debe haber al menos un ítem válido.",
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    payload = {
        "cliente_id": cliente_id_int,
        "items": items,
    }

    try:
        await api.create_venta(payload)
    except httpx.HTTPStatusError as ex:
        error_msg = "No se pudo crear la venta. Verifica los datos."
        if ex.response.status_code == 409:
            try:
                detail = ex.response.json().get("detail", "")
                error_msg = f"Stock insuficiente: {detail}"
            except Exception:
                error_msg = "Stock insuficiente para uno o más productos."
        elif ex.response.status_code == 400:
            try:
                detail = ex.response.json().get("detail", "")
                error_msg = detail
            except Exception:
                pass

        return templates.TemplateResponse(
            "sales/_form.html",
            {
                "request": request,
                "venta": {"id": None, "cliente_id": cliente_id, "items": items},
                "error": error_msg,
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )
    except Exception as ex:
        error_msg = f"No se pudo crear la venta: {str(ex)}"
        return templates.TemplateResponse(
            "sales/_form.html",
            {
                "request": request,
                "venta": {"id": None, "cliente_id": cliente_id, "items": items},
                "error": error_msg,
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    return await ventas_table(request, q="", page=1, size=20, oob_clear=True)

