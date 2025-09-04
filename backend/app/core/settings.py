# app/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "Sistema Comercial"
    API_PREFIX: str = ""
    ENV: str = "development"
    
    # Base de datos
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@sc_postgres:5432/postgres"
    BACKUP_DATABASE_URL: str | None = None
    
    # JWT Configuration
    SECRET_KEY: str = "cambia-esto-por-uno-seguro-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Backup
    BACKUP_DIR: str = "/app/backups"
    
    # Email (futuro)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    
    # Redis (futuro)
    REDIS_URL: str | None = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str | None = None
    
    # CORS
    ALLOWED_ORIGINS: str = "*"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Monitoreo
    SENTRY_DSN: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
