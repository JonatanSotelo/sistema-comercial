# app/core/error_handlers.py
"""
Manejadores de errores centralizados para mejor UX.
"""
from fastapi import Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
import os


# Templates para páginas de error
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=template_dir)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Maneja excepciones HTTP de forma elegante.
    Retorna HTML para rutas web, JSON para rutas API.
    """
    # Determinar si es una ruta web o API
    is_web = request.url.path.startswith("/app")
    
    if is_web:
        # Páginas de error para el frontend web
        if exc.status_code == 404:
            return templates.TemplateResponse(
                "error_404.html",
                {"request": request, "detail": exc.detail},
                status_code=404
            )
        elif exc.status_code == 403:
            return templates.TemplateResponse(
                "error_403.html",
                {"request": request, "detail": exc.detail},
                status_code=403
            )
        elif exc.status_code == 500:
            return templates.TemplateResponse(
                "error_500.html",
                {"request": request, "detail": exc.detail},
                status_code=500
            )
        else:
            # Error genérico
            return templates.TemplateResponse(
                "error_generic.html",
                {"request": request, "status_code": exc.status_code, "detail": exc.detail},
                status_code=exc.status_code
            )
    else:
        # Respuesta JSON para API
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )


async def validation_exception_handler(request: Request, exc: Exception):
    """Maneja errores de validación de Pydantic."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Error de validación", "errors": str(exc)}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones no controladas."""
    print(f"❌ Error no controlado: {exc}")
    
    is_web = request.url.path.startswith("/app")
    
    if is_web:
        return templates.TemplateResponse(
            "error_500.html",
            {"request": request, "detail": "Error interno del servidor"},
            status_code=500
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor"}
        )


