from typing import Any, Dict
import re

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates

from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

_PHONE_KEYS = ("telefono", "phone", "phone_number", "telefono_movil")
_CUIT_KEYS = ("cuit", "tax_id", "dni", "documento", "id_number", "national_id", "cuil")
_ADDRESS_KEYS = ("direccion", "address", "direccion_fiscal", "domicilio")


def _digits(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\D+", "", value)
    return cleaned or None


def _normalize_cuit(value: str | None) -> str | None:
    digits = _digits(value)
    if not digits:
        return None
    return digits[:11]


def _hydrate_proveedor(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    raw = raw or {}
    telefono = next((raw.get(k) for k in _PHONE_KEYS if raw.get(k)), "")
    cuit = next((raw.get(k) for k in _CUIT_KEYS if raw.get(k)), "")
    direccion = next((raw.get(k) for k in _ADDRESS_KEYS if raw.get(k)), "")
    return {
        "id": raw.get("id"),
        "nombre": raw.get("nombre") or raw.get("name") or "",
        "email": raw.get("email") or raw.get("correo") or "",
        "telefono": telefono or "",
        "cuit": cuit or "",
        "direccion": direccion or "",
    }


def _validate_email(value: str | None) -> bool:
    if not value:
        return True
    return "@" in value


@router.get("/proveedores")
async def proveedores_index(request: Request):
    user = request.session.get("user", "—")
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"proveedores": True}
    return templates.TemplateResponse(
        "suppliers/index.html",
        {
            "request": request,
            "features": features,
            "user": user,
            "title": "Proveedores",
        },
    )


@router.get("/proveedores/table")
async def proveedores_table(
    request: Request,
    q: str = Query("", alias="q"),
    page: int = 1,
    size: int = 20,
    oob_clear: bool = False,
):
    api = get_api(request)
    try:
        data = await api.list_proveedores(q=q, page=page, size=size)
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
        "suppliers/_table.html",
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


@router.get("/proveedores/form/new")
async def proveedores_form_new(request: Request):
    proveedor = _hydrate_proveedor({"id": None})
    return templates.TemplateResponse(
        "suppliers/_form.html",
        {
            "request": request,
            "proveedor": proveedor,
            "title": "Nuevo proveedor",
        },
    )


@router.get("/proveedores/form/{pid}")
async def proveedores_form_edit(request: Request, pid: int):
    api = get_api(request)
    try:
        data = await api.get_proveedor(pid)
    except Exception:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    proveedor = _hydrate_proveedor(data)
    return templates.TemplateResponse(
        "suppliers/_form.html",
        {
            "request": request,
            "proveedor": proveedor,
            "title": f"Editar {proveedor['nombre']}",
        },
    )


@router.post("/proveedores/create")
async def proveedores_create(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(""),
    telefono: str = Form(""),
    cuit: str = Form(""),
    direccion: str = Form(""),
):
    nombre_ok = nombre.strip()
    email_ok = email.strip() or None
    tel_ok = _digits(telefono)
    cuit_ok = _normalize_cuit(cuit)
    direccion_ok = direccion.strip() or None

    if not nombre_ok:
        proveedor = _hydrate_proveedor(
            {
                "id": None,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "cuit": cuit,
                "direccion": direccion,
            }
        )
        return templates.TemplateResponse(
            "suppliers/_form.html",
            {"request": request, "proveedor": proveedor, "error": "Nombre es obligatorio."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )
    if not _validate_email(email_ok):
        proveedor = _hydrate_proveedor(
            {
                "id": None,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "cuit": cuit,
                "direccion": direccion,
            }
        )
        return templates.TemplateResponse(
            "suppliers/_form.html",
            {"request": request, "proveedor": proveedor, "error": "Email inválido."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    data = {"nombre": nombre_ok}
    if email_ok:
        data["email"] = email_ok
    if tel_ok:
        data["telefono"] = tel_ok
    if cuit_ok:
        data["cuit"] = cuit_ok
    if direccion_ok:
        data["direccion"] = direccion_ok

    api = get_api(request)
    try:
        await api.create_proveedor(data)
    except Exception:
        proveedor = _hydrate_proveedor(
            {
                "id": None,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "cuit": cuit,
                "direccion": direccion,
            }
        )
        return templates.TemplateResponse(
            "suppliers/_form.html",
            {"request": request, "proveedor": proveedor, "error": "No se pudo crear. Verifica los datos."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    return await proveedores_table(request, q="", page=1, size=20, oob_clear=True)


@router.post("/proveedores/update/{pid}")
async def proveedores_update(
    request: Request,
    pid: int,
    nombre: str = Form(...),
    email: str = Form(""),
    telefono: str = Form(""),
    cuit: str = Form(""),
    direccion: str = Form(""),
):
    nombre_ok = nombre.strip()
    email_ok = email.strip() or None
    tel_ok = _digits(telefono)
    cuit_ok = _normalize_cuit(cuit)
    direccion_ok = direccion.strip() or None

    if not nombre_ok:
        proveedor = _hydrate_proveedor(
            {
                "id": pid,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "cuit": cuit,
                "direccion": direccion,
            }
        )
        return templates.TemplateResponse(
            "suppliers/_form.html",
            {"request": request, "proveedor": proveedor, "error": "Nombre es obligatorio."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )
    if not _validate_email(email_ok):
        proveedor = _hydrate_proveedor(
            {
                "id": pid,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "cuit": cuit,
                "direccion": direccion,
            }
        )
        return templates.TemplateResponse(
            "suppliers/_form.html",
            {"request": request, "proveedor": proveedor, "error": "Email inválido."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    data = {"nombre": nombre_ok}
    if email_ok:
        data["email"] = email_ok
    if tel_ok:
        data["telefono"] = tel_ok
    if cuit_ok:
        data["cuit"] = cuit_ok
    if direccion_ok:
        data["direccion"] = direccion_ok

    api = get_api(request)
    try:
        await api.update_proveedor(pid, data)
    except Exception:
        proveedor = _hydrate_proveedor(
            {
                "id": pid,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "cuit": cuit,
                "direccion": direccion,
            }
        )
        return templates.TemplateResponse(
            "suppliers/_form.html",
            {"request": request, "proveedor": proveedor, "error": "No se pudo actualizar."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    return await proveedores_table(request, q="", page=1, size=20, oob_clear=True)
