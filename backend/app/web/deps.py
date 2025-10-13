# app/web/deps.py
"""
Dependencias compartidas para el módulo web: SessionMiddleware, httpx client, etc.
"""
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import httpx

from app.web.core import web_settings


def add_session_middleware(app):
    """
    Agrega SessionMiddleware a la aplicación FastAPI.
    Esto permite usar request.session para guardar datos de sesión (ej: access_token).
    """
    app.add_middleware(
        SessionMiddleware,
        secret_key=web_settings.SECRET_KEY,
        max_age=3600 * 24,  # 24 horas
        same_site="lax",
    )


def get_api_client() -> httpx.Client:
    """
    Retorna un cliente httpx configurado para llamar al API backend.
    """
    return httpx.Client(
        base_url=web_settings.API_BASE_URL,
        timeout=httpx.Timeout(30.0, connect=10.0),
        follow_redirects=True,
    )


def get_current_token(request: Request) -> Optional[str]:
    """
    Obtiene el access_token desde la sesión.
    Retorna None si no hay token.
    """
    return request.session.get("access_token")


def require_auth(request: Request) -> str:
    """
    Dependency que requiere que el usuario esté autenticado.
    Retorna el access_token o redirige al login.
    """
    token = get_current_token(request)
    if not token:
        # Redirigir al login si no hay token
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="No autenticado",
            headers={"Location": "/app/login"},
        )
    return token


def get_auth_header(request: Request) -> dict:
    """
    Retorna headers de autorización para usar con httpx.
    """
    token = get_current_token(request)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def get_current_user_data(request: Request) -> Optional[dict]:
    """
    Obtiene los datos del usuario actual desde la sesión.
    """
    return request.session.get("user")

