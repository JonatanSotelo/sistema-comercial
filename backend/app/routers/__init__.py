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
from app.routers.auditoria_router import router as auditoria_router
from app.routers.audit_log_router import router as audit_log_router
from app.routers.reportes_router import router as reportes_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.notificacion_router import router as notificacion_router
from app.routers.descuento_router import router as descuento_router  # 👈 nuevo
from app.routers.inventario_router import router as inventario_router  # 👈 nuevo
from app.routers.precio_router import router as precio_router  # 👈 nuevo
from app.routers.reporte_financiero_router import router as reporte_financiero_router  # 👈 nuevo
from app.routers.proveedor_integracion_router import router as proveedor_integracion_router  # 👈 nuevo
from app.routers.metricas_rendimiento_router import router as metricas_rendimiento_router  # 👈 nuevo
from app.routers.permiso_router import router as permiso_router  # 👈 nuevo
from app.routers.integrations_whatsapp_router import router as integrations_whatsapp_router  # 👈 nuevo
from app.routers.pedidos_router import router as pedidos_router  # 👈 nuevo

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
    app.include_router(audit_log_router)
    app.include_router(reportes_router)
    app.include_router(dashboard_router)
    app.include_router(notificacion_router)
    app.include_router(descuento_router)
    app.include_router(inventario_router)
    app.include_router(precio_router)
    app.include_router(reporte_financiero_router)
    app.include_router(proveedor_integracion_router)  # 👈 nuevo
    app.include_router(metricas_rendimiento_router)  # 👈 nuevo
    app.include_router(permiso_router)  # 👈 nuevo
    app.include_router(integrations_whatsapp_router)  # 👈 nuevo
    app.include_router(pedidos_router)  # 👈 nuevo
