from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.settings import settings

# Engine y SessionLocal (SQLAlchemy 2.0+)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI: yield una sesión y luego cierra."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
