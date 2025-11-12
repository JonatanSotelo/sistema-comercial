# app/main.py
from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.settings import settings
from app.routers import register_routers
from app.web.router import router as web_router
from app.db.database import SessionLocal
from app.db.database import engine
from app.db.base import Base  # asegura que todos los modelos estén importados
from app.services import user_service
from app.schemas.user_schema import UserCreate

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

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "dev-secret"),
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(web_router)

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
    # 1) Crear tablas si no existen (dev/entornos limpios)
    try:
        Base.metadata.create_all(bind=engine)
        print("[startup] Tablas verificadas/creadas")
    except Exception as e:
        print(f"[startup] Error creando/verificando tablas: {e}")

    # 2) Scheduler
    schedule_jobs()

    # 3) Crear usuario(s) inicial(es)
    try:
        db = SessionLocal()
        try:
            # Admin por variables de entorno
            admin_user = os.environ.get("ADMIN_USERNAME") or None
            admin_pass = os.environ.get("ADMIN_PASSWORD") or None
            if admin_user and admin_pass:
                existing = user_service.get_by_username(db, admin_user)
                if not existing:
                    # Email por env o valor seguro por defecto
                    data = UserCreate(
                        username=admin_user,
                        password=admin_pass,
                        role="admin",
                        is_active=True,
                    )
                    user_service.create_user(db, data)
                    print(f"[startup] Usuario admin '{admin_user}' creado")
                else:
                    # Opcional: forzar actualización de password/rol en dev o si ADMIN_FORCE_UPDATE=true
                    force = (os.environ.get("ADMIN_FORCE_UPDATE", "false").lower() == "true") or settings.ENV.lower().startswith("dev")
                    if force:
                        from app.schemas.user_schema import UserUpdate
                        user_service.update_user(db, existing.id, UserUpdate(password=admin_pass, role="admin"))  # type: ignore
                        print(f"[startup] Usuario admin '{admin_user}' actualizado (dev/force)")
                    else:
                        print(f"[startup] Usuario admin '{admin_user}' ya existe")
            
            # Inicializar permisos y roles por defecto
            try:
                from app.services.permiso_service import permiso_service
                permiso_service.initialize_default_permissions(db)
                permiso_service.initialize_default_roles(db)
                print("[startup] Permisos y roles inicializados correctamente")
            except Exception as e:
                print(f"[startup] Error al inicializar permisos: {e}")

            # Usuario estándar opcional por env
            user_user = os.environ.get("USER_USERNAME") or None
            user_pass = os.environ.get("USER_PASSWORD") or None
            if user_user and user_pass:
                existing_u = user_service.get_by_username(db, user_user)
                if not existing_u:
                    data = UserCreate(
                        username=user_user,
                        password=user_pass,
                        role="consulta",
                        is_active=True,
                    )
                    user_service.create_user(db, data)
                    print(f"[startup] Usuario estándar '{user_user}' creado")
                else:
                    force_user = (os.environ.get("USER_FORCE_UPDATE", "false").lower() == "true") or settings.ENV.lower().startswith("dev")
                    if force_user:
                        from app.schemas.user_schema import UserUpdate
                        user_service.update_user(db, existing_u.id, UserUpdate(password=user_pass, role="consulta"))  # type: ignore
                        print(f"[startup] Usuario estándar '{user_user}' actualizado (dev/force)")
                    else:
                        print(f"[startup] Usuario estándar '{user_user}' ya existe")

            # En entornos de desarrollo, si no hay usuarios en absoluto, sembrar admin y user por defecto
            if settings.ENV.lower().startswith("dev"):
                try:
                    from app.models.user_model import User  # type: ignore
                    total = db.query(User).count()
                except Exception:
                    total = 0
                if total == 0:
                    # admin
                    if not admin_user:
                        data = UserCreate(
                            username="admin",
                            password="admin123",
                            role="admin",
                            is_active=True,
                        )
                        user_service.create_user(db, data)
                        print("[startup] Usuario admin por defecto 'admin' creado (dev)")
                    # user
                    if not user_user:
                        data = UserCreate(
                            username="user",
                            password="user123",
                            role="consulta",
                            is_active=True,
                        )
                        user_service.create_user(db, data)
                        print("[startup] Usuario estándar por defecto 'user' creado (dev)")
        finally:
            db.close()
    except Exception as e:
        print(f"[startup] No se pudo asegurar admin: {e}")

@app.on_event("shutdown")
def on_shutdown():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None

@app.get("/", tags=["Health"])
def root():
    return {"ok": True, "app": settings.APP_NAME}
