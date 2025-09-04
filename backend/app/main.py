# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.settings import settings
from app.routers import register_routers

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (ajustá orígenes si hace falta)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Routers
register_routers(app)

scheduler: BackgroundScheduler | None = None

def schedule_jobs():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler(timezone="America/Argentina/Buenos_Aires")
        # Import adentro para evitar ciclos
        from app.services.backup_service import create_backup_zip
        scheduler.add_job(
            create_backup_zip,
            "cron",
            hour=2,
            minute=30,
            id="daily_backup",
            replace_existing=True,
        )
        scheduler.start()
        print("[scheduler] iniciado con job daily_backup a las 02:30")

@app.on_event("startup")
def on_startup():
    schedule_jobs()

@app.on_event("shutdown")
def on_shutdown():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None

@app.get("/", tags=["Health"])
def root():
    return {"ok": True, "app": settings.APP_NAME}
