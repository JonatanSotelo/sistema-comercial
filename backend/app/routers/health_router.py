from fastapi import APIRouter
from sqlalchemy import text
from app.db.database import SessionLocal

router = APIRouter(tags=["Health"])

@router.get("/health")
def health():
    # Ping rápido a la DB para validar conexión
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        return {"status": "degraded", "db": f"error: {e.__class__.__name__}"}
