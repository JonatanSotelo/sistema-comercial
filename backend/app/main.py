from fastapi import FastAPI
from app.core.settings import settings
from app.core.logger import logger
from app.routers import producto_router
from app.routers import cliente_router
from app.routers import venta_router
from app.routers import producto_router, cliente_router, venta_router, user_router
from app.routers import proveedor_router, compra_router, venta_router, stock_router
from app.db.database import Base, engine

app = FastAPI(title="Sistema Comercial", version="0.1.0")

app.include_router(producto_router.router)
app.include_router(cliente_router.router)
app.include_router(venta_router.router)
app.include_router(user_router.router)
app.include_router(proveedor_router.router)
app.include_router(compra_router.router)
app.include_router(stock_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}

