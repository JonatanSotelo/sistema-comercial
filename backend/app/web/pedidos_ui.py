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


@router.get("/pedidos")
async def pedidos_index(request: Request):
    user = request.session.get("user", "—")
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"pedidos": True}
    return templates.TemplateResponse(
        "pedidos/index.html",
        {
            "request": request,
            "features": features,
            "user": user,
            "title": "Pedidos",
        },
    )


@router.get("/pedidos/table")
async def pedidos_table(
    request: Request,
    q: str = Query("", alias="q"),
    estado: str = Query("", alias="estado"),
    page: int = 1,
    size: int = 20,
    oob_clear: bool = False,
):
    api = get_api(request)
    try:
        params = {"q": q, "page": page, "size": size}
        if estado:
            params["estado"] = estado
        data = await api.list_pedidos(**params)
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
        "pedidos/_table.html",
        {
            "request": request,
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "q": q,
            "estado": estado,
            "oob_clear": oob_clear,
        },
    )


@router.get("/pedidos/form/new")
async def pedidos_form_new(request: Request):
    return templates.TemplateResponse(
        "pedidos/_form.html",
        {
            "request": request,
            "pedido": {"id": None, "cliente_id": None, "items": [], "nota": ""},
            "error": None,
        },
    )


@router.get("/pedidos/form/{pedido_id}")
async def pedidos_form_edit(request: Request, pedido_id: int):
    api = get_api(request)
    try:
        pedido = await api.get_pedido(pedido_id)
    except Exception:
        return templates.TemplateResponse(
            "pedidos/_form.html",
            {
                "request": request,
                "pedido": {"id": None, "cliente_id": None, "items": [], "nota": ""},
                "error": "No se pudo cargar el pedido",
            },
            status_code=400,
        )

    # Verificar si el pedido puede editarse
    if pedido.get("estado") not in ["NUEVO", "EN_PREPARACION"]:
        return templates.TemplateResponse(
            "pedidos/_form.html",
            {
                "request": request,
                "pedido": pedido,
                "error": f"No se puede editar un pedido en estado {pedido.get('estado')}",
            },
            status_code=400,
        )

    return templates.TemplateResponse(
        "pedidos/_form.html",
        {
            "request": request,
            "pedido": pedido,
            "error": None,
        },
    )


@router.get("/pedidos/lookup/cliente")
async def pedidos_lookup_cliente(request: Request, q: str = Query("")):
    api = get_api(request)
    try:
        items = await api.search_clientes(q=q, size=5)
    except Exception:
        items = []

    return templates.TemplateResponse(
        "pedidos/_lookup_cliente.html",
        {"request": request, "items": items},
    )


@router.get("/pedidos/lookup/producto")
async def pedidos_lookup_producto(request: Request, q: str = Query("")):
    api = get_api(request)
    try:
        items = await api.search_productos(q=q, size=5)
    except Exception:
        items = []

    return templates.TemplateResponse(
        "pedidos/_lookup_producto.html",
        {"request": request, "items": items},
    )


@router.post("/pedidos/create")
async def pedidos_create(
    request: Request,
    cliente_id: str = Form(""),
    producto_id: List[str] = Form([]),
    cantidad: List[str] = Form([]),
    precio_unitario: List[str] = Form([]),
    nota: str = Form(""),
):
    api = get_api(request)

    cliente_id_int = _to_int(cliente_id) if cliente_id else None

    items = []
    for pid_str, cant_str, precio_str in zip(producto_id, cantidad, precio_unitario):
        pid = _to_int(pid_str)
        cant = _to_int(cant_str)
        precio = _to_float(precio_str)

        if pid is None or cant is None or cant <= 0:
            continue
        if precio is None or precio < 0:
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
            "pedidos/_form.html",
            {
                "request": request,
                "pedido": {"id": None, "cliente_id": cliente_id, "items": [], "nota": nota},
                "error": "Debe haber al menos un ítem válido.",
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    payload = {
        "cliente_id": cliente_id_int,
        "items": items,
        "nota": nota if nota else None,
    }

    try:
        await api.create_pedido(payload)
    except httpx.HTTPStatusError as ex:
        error_msg = "No se pudo crear el pedido. Verifica los datos."
        if ex.response.status_code == 400:
            try:
                detail = ex.response.json().get("detail", "")
                error_msg = detail
            except Exception:
                pass

        return templates.TemplateResponse(
            "pedidos/_form.html",
            {
                "request": request,
                "pedido": {"id": None, "cliente_id": cliente_id, "items": items, "nota": nota},
                "error": error_msg,
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )
    except Exception as ex:
        error_msg = f"No se pudo crear el pedido: {str(ex)}"
        return templates.TemplateResponse(
            "pedidos/_form.html",
            {
                "request": request,
                "pedido": {"id": None, "cliente_id": cliente_id, "items": items, "nota": nota},
                "error": error_msg,
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    return await pedidos_table(request, q="", estado="", page=1, size=20, oob_clear=True)


@router.post("/pedidos/update/{pedido_id}")
async def pedidos_update(
    request: Request,
    pedido_id: int,
    producto_id: List[str] = Form([]),
    cantidad: List[str] = Form([]),
    precio_unitario: List[str] = Form([]),
    nota: str = Form(""),
):
    api = get_api(request)

    items = []
    for pid_str, cant_str, precio_str in zip(producto_id, cantidad, precio_unitario):
        pid = _to_int(pid_str)
        cant = _to_int(cant_str)
        precio = _to_float(precio_str)

        if pid is None or cant is None or cant <= 0:
            continue
        if precio is None or precio < 0:
            continue

        items.append(
            {
                "producto_id": pid,
                "cantidad": int(cant),
                "precio_unitario": float(precio),
            }
        )

    if not items:
        pedido = await api.get_pedido(pedido_id)
        return templates.TemplateResponse(
            "pedidos/_form.html",
            {
                "request": request,
                "pedido": pedido,
                "error": "Debe haber al menos un ítem válido.",
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    payload = {
        "items": items,
        "nota": nota if nota else None,
    }

    try:
        await api.update_pedido(pedido_id, payload)
    except httpx.HTTPStatusError as ex:
        error_msg = "No se pudo actualizar el pedido."
        if ex.response.status_code == 400:
            try:
                detail = ex.response.json().get("detail", "")
                error_msg = detail
            except Exception:
                pass

        pedido = await api.get_pedido(pedido_id)
        return templates.TemplateResponse(
            "pedidos/_form.html",
            {
                "request": request,
                "pedido": pedido,
                "error": error_msg,
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )
    except Exception as ex:
        pedido = await api.get_pedido(pedido_id)
        error_msg = f"No se pudo actualizar el pedido: {str(ex)}"
        return templates.TemplateResponse(
            "pedidos/_form.html",
            {
                "request": request,
                "pedido": pedido,
                "error": error_msg,
            },
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    return await pedidos_table(request, q="", estado="", page=1, size=20, oob_clear=True)


@router.post("/pedidos/{pedido_id}/estado")
async def pedidos_change_estado(
    request: Request,
    pedido_id: int,
    estado: str = Form(...),
):
    api = get_api(request)
    try:
        await api.change_pedido_estado(pedido_id, {"estado": estado})
    except Exception as ex:
        print(f"Error al cambiar estado: {ex}")

    return await pedidos_table(request, q="", estado="", page=1, size=20, oob_clear=False)


@router.post("/pedidos/{pedido_id}/facturar")
async def pedidos_facturar(request: Request, pedido_id: int):
    api = get_api(request)
    try:
        await api.facturar_pedido(pedido_id)
    except httpx.HTTPStatusError as ex:
        error_msg = "No se pudo facturar el pedido."
        if ex.response.status_code == 409:
            try:
                detail = ex.response.json().get("detail", "")
                error_msg = f"Stock insuficiente: {detail}"
            except Exception:
                error_msg = "Stock insuficiente para uno o más productos."
        print(f"Error al facturar: {error_msg}")
    except Exception as ex:
        print(f"Error al facturar: {ex}")

    return await pedidos_table(request, q="", estado="", page=1, size=20, oob_clear=False)


@router.post("/pedidos/bulk_estado")
async def pedidos_bulk_estado(
    request: Request,
    pedido_ids: str = Form(...),
    nuevo_estado: str = Form(...),
):
    """Cambiar estado de múltiples pedidos"""
    api = get_api(request)
    
    # Parsear IDs
    ids = [int(id.strip()) for id in pedido_ids.split(",") if id.strip()]
    
    if not ids:
        return await pedidos_table(request, q="", estado="", page=1, size=20, oob_clear=False)
    
    try:
        # Llamar al endpoint de bulk change estado
        # Como no existe en el API client, lo hacemos directo
        result = await api._call_bulk_change_estado(ids, nuevo_estado)
        print(f"Bulk change result: {result}")
    except Exception as ex:
        print(f"Error en bulk change estado: {ex}")
    
    return await pedidos_table(request, q="", estado="", page=1, size=20, oob_clear=False)

