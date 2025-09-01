# app/routers/health_router.py
from fastapi import APIRouter
from sqlalchemy import text
from app.db.database import SessionLocal

router = APIRouter()

@router.get("/health", tags=["Health"], operation_id="health")
def health():
    """
    Check de salud de la app.
    - Devuelve {"status":"ok","db":"ok"} si la DB responde.
    - En caso de problema con la DB, informa estado "degraded".
    """
    try:
        # Usamos el context manager para garantizar el cierre de la sesión
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        return {"status": "degraded", "db": f"error: {e.__class__.__name__}"}
