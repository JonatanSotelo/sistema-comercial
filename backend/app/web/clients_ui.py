import re

from fastapi import APIRouter, Request, Query, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


def _digits(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\D+", "", value)
    return cleaned or None


def _validate_email(value: str | None) -> bool:
    if not value:
        return True
    return "@" in value


@router.get("/clientes")
async def clientes_index(request: Request):
    user = request.session.get("user", "—")
    try:
        features = await get_api(request).get_features()
    except Exception:
        features = {"clientes": True}
    return templates.TemplateResponse(
        "clients/index.html",
        {
            "request": request,
            "features": features,
            "user": user,
            "title": "Clientes",
        },
    )


@router.get("/clientes/table")
async def clientes_table(
    request: Request,
    q: str = Query("", alias="q"),
    page: int = 1,
    size: int = 20,
    oob_clear: bool = False,
):
    api = get_api(request)
    try:
        data = await api.list_clientes(q=q, page=page, size=size)
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
        "clients/_table.html",
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


@router.get("/clientes/form/new")
async def clientes_form_new(request: Request):
    cliente = {"id": None, "nombre": "", "email": "", "telefono": "", "cuit": ""}
    return templates.TemplateResponse(
        "clients/_form.html",
        {
            "request": request,
            "cliente": cliente,
            "title": "Nuevo cliente",
        },
    )


@router.get("/clientes/form/{cid}")
async def clientes_form_edit(request: Request, cid: int):
    api = get_api(request)
    try:
        data = await api.get_cliente(cid)
    except Exception:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente = {
        "id": data.get("id"),
        "nombre": data.get("nombre") or data.get("name") or "",
        "email": data.get("email") or data.get("correo") or "",
        "telefono": data.get("telefono") or data.get("phone") or "",
        "cuit": data.get("cuit") or data.get("tax_id") or "",
    }
    return templates.TemplateResponse(
        "clients/_form.html",
        {
            "request": request,
            "cliente": cliente,
            "title": f"Editar {cliente['nombre']}",
        },
    )


@router.post("/clientes/create")
async def clientes_create(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(""),
    telefono: str = Form(""),
    cuit: str = Form(""),
):
    nombre_ok = nombre.strip()
    email_ok = email.strip() or None
    tel_ok = _digits(telefono)
    cuit_ok = _digits(cuit)

    if not nombre_ok:
        cliente = {"id": None, "nombre": nombre, "email": email, "telefono": telefono, "cuit": cuit}
        return templates.TemplateResponse(
            "clients/_form.html",
            {"request": request, "cliente": cliente, "error": "Nombre es obligatorio."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )
    if not _validate_email(email_ok):
        cliente = {"id": None, "nombre": nombre, "email": email, "telefono": telefono, "cuit": cuit}
        return templates.TemplateResponse(
            "clients/_form.html",
            {"request": request, "cliente": cliente, "error": "Email inválido."},
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

    api = get_api(request)
    try:
        await api.create_cliente(data)
    except Exception:
        cliente = {"id": None, "nombre": nombre, "email": email, "telefono": telefono, "cuit": cuit}
        return templates.TemplateResponse(
            "clients/_form.html",
            {"request": request, "cliente": cliente, "error": "No se pudo crear. Verifica los datos."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    return await clientes_table(request, q="", page=1, size=20, oob_clear=True)


@router.post("/clientes/update/{cid}")
async def clientes_update(
    request: Request,
    cid: int,
    nombre: str = Form(...),
    email: str = Form(""),
    telefono: str = Form(""),
    cuit: str = Form(""),
):
    nombre_ok = nombre.strip()
    email_ok = email.strip() or None
    tel_ok = _digits(telefono)
    cuit_ok = _digits(cuit)

    if not nombre_ok:
        cliente = {"id": cid, "nombre": nombre, "email": email, "telefono": telefono, "cuit": cuit}
        return templates.TemplateResponse(
            "clients/_form.html",
            {"request": request, "cliente": cliente, "error": "Nombre es obligatorio."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )
    if not _validate_email(email_ok):
        cliente = {"id": cid, "nombre": nombre, "email": email, "telefono": telefono, "cuit": cuit}
        return templates.TemplateResponse(
            "clients/_form.html",
            {"request": request, "cliente": cliente, "error": "Email inválido."},
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

    api = get_api(request)
    try:
        await api.update_cliente(cid, data)
    except Exception:
        cliente = {"id": cid, "nombre": nombre, "email": email, "telefono": telefono, "cuit": cuit}
        return templates.TemplateResponse(
            "clients/_form.html",
            {"request": request, "cliente": cliente, "error": "No se pudo actualizar."},
            headers={"HX-Retarget": "#form-container", "HX-Reswap": "innerHTML"},
            status_code=400,
        )

    return await clientes_table(request, q="", page=1, size=20, oob_clear=True)
