# app/routers/__init__.py
from fastapi import FastAPI

# importá aquí TODOS tus routers
from app.routers.health_router import router as health_router
from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router
from app.routers.cliente_router import router as cliente_router
from app.routers.proveedor_router import router as proveedor_router
from app.routers.producto_router import router as producto_router
from app.routers.stock_router import router as stock_router
from app.routers.compra_router import router as compra_router
from app.routers.venta_router import router as venta_router
from app.routers.backup_router import router as backup_router
from app.routers.auditoria_router import router as auditoria_router  # 👈 nuevo

def register_routers(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(cliente_router)
    app.include_router(proveedor_router)
    app.include_router(producto_router)
    app.include_router(stock_router)
    app.include_router(compra_router)
    app.include_router(venta_router)
    app.include_router(backup_router)
    app.include_router(auditoria_router)
