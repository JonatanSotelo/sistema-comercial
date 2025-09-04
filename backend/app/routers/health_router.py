# app/routers/health_router.py
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Healthcheck")
def health():
    return {"ok": True}
