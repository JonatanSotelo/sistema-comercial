# app/web/routers/auth.py
"""
Router para autenticación: login, logout.
"""
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx

from app.web.core import web_settings
from app.web.api_client import APIClient

router = APIRouter(tags=["Auth Web"])

# Configurar templates
templates = Jinja2Templates(directory=web_settings.TEMPLATE_DIR)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login."""
    # Si ya está autenticado, redirigir al dashboard
    if request.session.get("access_token"):
        return RedirectResponse(url="/app/dashboard", status_code=303)
    
    error = request.query_params.get("error")
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
    })


@router.post("/login", response_class=RedirectResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Procesa el formulario de login.
    Llama a /auth/oauth2/token del backend y guarda el token en la sesión.
    """
    with APIClient() as client:
        try:
            # Llamar al endpoint OAuth2 del backend
            response = client.post(
                "/auth/oauth2/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                
                # Obtener info del usuario
                user_response = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            
                user_data = {}
                if user_response.status_code == 200:
                    user_data = user_response.json()
                
                # Guardar en sesión
                request.session["access_token"] = access_token
                request.session["user"] = user_data
                
                return RedirectResponse(url="/app/dashboard", status_code=status.HTTP_303_SEE_OTHER)
            else:
                # Error de autenticación
                return RedirectResponse(
                    url="/app/login?error=Usuario o contraseña inválidos",
                    status_code=status.HTTP_303_SEE_OTHER,
                )
        except Exception as e:
            print(f"Error en login: {e}")
            return RedirectResponse(
                url="/app/login?error=Error de conexión con el servidor",
                status_code=status.HTTP_303_SEE_OTHER,
            )


@router.get("/logout", response_class=RedirectResponse)
@router.post("/logout", response_class=RedirectResponse)
async def logout(request: Request):
    """Cierra la sesión del usuario."""
    request.session.clear()
    return RedirectResponse(url="/app/login", status_code=status.HTTP_303_SEE_OTHER)

