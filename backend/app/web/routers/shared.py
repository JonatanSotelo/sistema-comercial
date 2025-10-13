# app/web/routers/shared.py
"""
Utilidades compartidas entre routers: triggers HTMX, helpers, etc.
"""
from typing import Optional


def build_hx_trigger(event: str, data: Optional[dict] = None) -> str:
    """
    Construye un header HX-Trigger para HTMX.
    
    Ejemplo:
        build_hx_trigger("refreshTable") -> "refreshTable"
        build_hx_trigger("showToast", {"message": "Guardado"}) -> '{"showToast": {"message": "Guardado"}}'
    """
    if data:
        import json
        return json.dumps({event: data})
    return event


def parse_pagination_params(page: Optional[int], size: Optional[int]) -> tuple[int, int]:
    """
    Parsea y valida parámetros de paginación.
    Retorna (page, size) con valores por defecto.
    """
    from app.web.core import web_settings
    
    page = max(1, page or 1)
    size = max(1, min(200, size or web_settings.DEFAULT_PAGE_SIZE))
    return page, size


def format_currency(value: Optional[float]) -> str:
    """Formatea un valor numérico como moneda."""
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"


def format_bool(value: bool) -> str:
    """Formatea un booleano para mostrar en UI."""
    return "Sí" if value else "No"


