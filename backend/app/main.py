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

# 👉 auth_router NO tiene prefix interno => acá SÍ usamos prefix
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])

# 👉 user_router define internamente /usuarios => acá usamos /users para agrupar
app.include_router(user_router.router, prefix="/users", tags=["Usuarios"])

# ❗️Estos routers YA tienen prefix interno (/productos, /clientes, etc.)
#    Por eso acá VAN SIN prefix para evitar /productos/productos, etc.
app.include_router(producto_router.router, tags=["Productos"])
app.include_router(cliente_router.router, tags=["Clientes"])
app.include_router(proveedor_router.router, tags=["Proveedores"])
app.include_router(compra_router.router, tags=["Compras"])
app.include_router(venta_router.router, tags=["Ventas"])
app.include_router(stock_router.router, tags=["Stock"])
app.include_router(auditoria_router.router, tags=["Auditoría"])

# Health ya viene bien (1 sola vez)
app.include_router(health_router.router, tags=["Health"])
