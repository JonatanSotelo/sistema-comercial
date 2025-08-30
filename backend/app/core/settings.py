# app/core/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema Comercial"

    # JWT
    SECRET_KEY: str = "cambia-esto-por-uno-seguro"  # en producción generá uno fuerte
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"

    # DB (solo string, SessionLocal está en app/db/database.py)
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/postgres"

    class Config:
        env_file = ".env"

settings = Settings()
