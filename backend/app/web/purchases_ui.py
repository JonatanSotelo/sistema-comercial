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


@router.get("/compras")
async def compras_index(request: Request):
    user = request.session.get("user", "—")
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"compras": True}
    return templates.TemplateResponse(
        "purchases/index.html",
        {
            "request": request,
            "features": features,
            "user": user,
            "title": "Compras",
        },
    )


@router.get("/compras/table")
async def compras_table(
    request: Request,
    q: str = Query("", alias="q"),
    page: int = 1,
    size: int = 20,
    oob_clear: bool = False,
):
    api = get_api(request)
    try:
        data = await api.list_compras(q=q, page=page, size=size)
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
        "purchases/_table.html",
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


@router.get("/compras/form/new")
async def compras_form_new(request: Request):
    return templates.TemplateResponse(
        "purchases/_form.html",
        {
            "request": request,
            "compra": {"id": None, "proveedor_id": None, "items": []},
            "error": None,
        },
    )


@router.get("/compras/lookup/proveedor")
async def compras_lookup_proveedor(request: Request, q: str = Query("")):
    api = get_api(request)
    try:
        items = await api.search_proveedores(q=q, size=5)
    except Exception:
        items = []

    return templates.TemplateResponse(
        "purchases/_lookup_proveedor.html",
        {"request": request, "items": items},
    )


@router.get("/compras/lookup/producto")
async def compras_lookup_producto(request: Request, q: str = Query("")):
    api = get_api(request)
    try:
        items = await api.search_productos(q=q, size=5)
    except Exception:
        items = []

    return templates.TemplateResponse(
        "purchases/_lookup_producto.html",
        {"request": request, "items": items},
    )


@router.post("/compras/create")
async def compras_create(
    request: Request,
    proveedor_id: str = Form(...),
    producto_id: List[str] = Form([]),
    cantidad: List[str] = Form([]),
    costo_unitario: List[str] = Form([]),
):
    api = get_api(request)

    proveedor_id_int = _to_int(proveedor_id)
    if proveedor_id_int is None:
        return templates.TemplateResponse(
            "purchases/_form.html",
            {
                "request": request,
                "compra": {"id": None, "proveedor_id": proveedor_id, "items": []},
                "error": "Proveedor es obligatorio.",
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    items = []
    for pid_str, cant_str, costo_str in zip(producto_id, cantidad, costo_unitario):
        pid = _to_int(pid_str)
        cant = _to_float(cant_str) or _to_int(cant_str)
        costo = _to_float(costo_str)

        if pid is None or cant is None or cant <= 0:
            continue
        if costo is None or costo < 0:
            continue

        items.append(
            {
                "producto_id": pid,
                "cantidad": int(cant),
                "costo_unitario": float(costo),
            }
        )

    if not items:
        return templates.TemplateResponse(
            "purchases/_form.html",
            {
                "request": request,
                "compra": {"id": None, "proveedor_id": proveedor_id_int, "items": []},
                "error": "Debe haber al menos un ítem válido.",
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    payload = {
        "proveedor_id": proveedor_id_int,
        "items": items,
    }

    try:
        await api.create_compra(payload)
    except httpx.HTTPStatusError as ex:
        error_msg = "No se pudo crear la compra. Verifica los datos."
        if ex.response.status_code == 400:
            try:
                detail = ex.response.json().get("detail", "")
                error_msg = detail
            except Exception:
                pass

        return templates.TemplateResponse(
            "purchases/_form.html",
            {
                "request": request,
                "compra": {"id": None, "proveedor_id": proveedor_id_int, "items": items},
                "error": error_msg,
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )
    except Exception as ex:
        error_msg = f"No se pudo crear la compra: {str(ex)}"
        return templates.TemplateResponse(
            "purchases/_form.html",
            {
                "request": request,
                "compra": {"id": None, "proveedor_id": proveedor_id_int, "items": items},
                "error": error_msg,
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    return await compras_table(request, q="", page=1, size=20, oob_clear=True)

