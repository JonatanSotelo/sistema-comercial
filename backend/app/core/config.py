# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://appuser:apppass@localhost:5432/appdb"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API
    API_BASE_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Backups
    BACKUP_DIR: str = "/data/backups"
    
    # WhatsApp Integration
    WHATS_ORDERS_TOKEN: str = "test-token-123"
    WHATS_CREATE_ORDERS: bool = True
    
    # Notifications (v0.8.0+)
    NOTIFY_ON_READY: bool = False
    NOTIFY_WHATS_ENDPOINT: Optional[str] = None
    NOTIFY_WHATS_TOKEN: Optional[str] = None
    
    # SMTP (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SMTP_FROM: str = "noreply@sistema-comercial.com"
    
    # AFIP Facturación (v0.9.0+)
    AFIP_ENV: str = "homologacion"  # homologacion | produccion
    AFIP_CUIT: str = "20123456789"
    AFIP_CERT_PATH: str = "/secrets/afip.crt"
    AFIP_KEY_PATH: str = "/secrets/afip.key"
    AFIP_CERT_PASS: Optional[str] = None
    AFIP_WSDL_WSAA: str = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
    AFIP_WSDL_WSFEV1: str = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
    FACTURA_PTO_VTA: int = 1
    FACTURA_MONEDA: str = "ARS"
    FACTURA_COTIZACION: float = 1.000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

