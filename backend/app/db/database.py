from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Opción A: SQLite (desarrollo/local) ---
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# --- Opción B: PostgreSQL (producción) ---
# DATABASE_URL = "postgresql+psycopg2://usuario:password@localhost:5432/sistema"
# engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependencia para inyectar la sesión en los endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
