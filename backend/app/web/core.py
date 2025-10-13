# app/web/core.py
"""
Configuración y settings para el módulo web.
"""
import os
from pydantic_settings import BaseSettings


class WebSettings(BaseSettings):
    """Settings específicos para el módulo web"""
    
    # URL base del API (para llamadas desde el servidor)
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    # Secret key para SessionMiddleware (debe ser la misma que la del backend)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tu-secret-key-muy-segura-cambiala-en-produccion")
    
    # Modo de uso (para desarrollo se puede usar una DB falsa)
    USE_FAKE_DB: bool = os.getenv("USE_FAKE_DB", "false").lower() == "true"
    
    # Configuración de paginación por defecto
    DEFAULT_PAGE_SIZE: int = 20
    
    # Directorio de templates
    TEMPLATE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


web_settings = WebSettings()


