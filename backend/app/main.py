# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth_router,
    user_router,
    producto_router,
    cliente_router,
    proveedor_router,
    compra_router,
    venta_router,
    stock_router,
    auditoria_router,
    health_router,
)

app = FastAPI(title="Sistema Comercial", version="0.1.0")

# CORS (ajustar orígenes en prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Incluí cada router UNA sola vez, con su prefix
app.include_router(auth_router.router,      prefix="/auth",      tags=["Auth"])
app.include_router(user_router.router,      prefix="/users",     tags=["Users"])
app.include_router(producto_router.router,  prefix="/productos", tags=["Productos"])
app.include_router(cliente_router.router,   prefix="/clientes",  tags=["Clientes"])
app.include_router(proveedor_router.router, prefix="/proveedores", tags=["Proveedores"])
app.include_router(compra_router.router,    prefix="/compras",   tags=["Compras"])
app.include_router(venta_router.router,     prefix="/ventas",    tags=["Ventas"])
app.include_router(stock_router.router,     prefix="/stock",     tags=["Stock"])
app.include_router(auditoria_router.router, prefix="/auditoria", tags=["Auditoría"])
app.include_router(health_router.router)  # si tu router define /health

# fallback por si no tuvieras health_router
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
