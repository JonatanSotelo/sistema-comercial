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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajustá en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers de auth/usuarios
app.include_router(auth_router.router, tags=["Auth"])
app.include_router(user_router.router, tags=["Usuarios"])

# Estos routers ya traen su propio prefix interno ("/productos", "/clientes", etc.)
app.include_router(producto_router.router, tags=["Productos"])
app.include_router(cliente_router.router, tags=["Clientes"])
app.include_router(proveedor_router.router, tags=["Proveedores"])
app.include_router(compra_router.router, tags=["Compras"])
app.include_router(venta_router.router, tags=["Ventas"])
app.include_router(stock_router.router, tags=["Stock"])
app.include_router(auditoria_router.router, tags=["Auditoría"])

# Health: sólo incluir el router (no definir otra función /health acá)
app.include_router(health_router.router)
