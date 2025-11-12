
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from fastapi.templating import Jinja2Templates
from .deps import get_api

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/login")
async def login_form(request: Request):
    # Si ya estás logueado, redirige
    if request.session.get("access_token"):
        return RedirectResponse("/app/dashboard", status_code=HTTP_302_FOUND)
    features = {}
    return templates.TemplateResponse("login.html", {"request": request, "features": features, "error": None})

@router.post("/login")
async def do_login(request: Request, username: str = Form(...), password: str = Form(...)):
    api = get_api(request)
    try:
        token = await api.login(username, password)
    except Exception as e:
        features = {}
        return templates.TemplateResponse("login.html", {"request": request, "features": features, "error": "Credenciales inválidas o backend no disponible"})
    request.session["access_token"] = token
    request.session["user"] = username
    return RedirectResponse("/app/dashboard", status_code=HTTP_302_FOUND)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/app/login", status_code=HTTP_302_FOUND)
