
from fastapi import APIRouter
from .auth_ui import router as auth_router
from .app_ui import router as app_router
from .products_ui import router as products_router
from .clients_ui import router as clients_router
from .suppliers_ui import router as suppliers_router
from .sales_ui import router as sales_router
from .purchases_ui import router as purchases_router
from .audit_ui import router as audit_router
from .reports_ui import router as reports_router
from .backups_ui import router as backups_router
from .integrations_whatsapp_ui import router as integrations_whatsapp_router
from .pedidos_ui import router as pedidos_router
from .facturacion_ui import router as facturacion_router  # v0.9.0
from .cobros_ui import router as cobros_router  # v0.9.1
from .iva_compras_ui import router as iva_compras_router  # v0.9.1

router = APIRouter()
router.include_router(auth_router, prefix="/app", tags=["ui-auth"])
router.include_router(app_router, prefix="/app", tags=["ui-app"])
router.include_router(products_router, prefix="/app", tags=["ui-productos"])
router.include_router(clients_router, prefix="/app", tags=["ui-clientes"])
router.include_router(suppliers_router, prefix="/app", tags=["ui-proveedores"])
router.include_router(sales_router, prefix="/app", tags=["ui-ventas"])
router.include_router(purchases_router, prefix="/app", tags=["ui-compras"])
router.include_router(audit_router, prefix="", tags=["ui-auditoria"])
router.include_router(reports_router, prefix="", tags=["ui-reportes"])
router.include_router(backups_router, prefix="", tags=["ui-backups"])
router.include_router(integrations_whatsapp_router, prefix="", tags=["ui-integraciones"])
router.include_router(pedidos_router, prefix="/app", tags=["ui-pedidos"])
router.include_router(facturacion_router, prefix="", tags=["ui-facturacion"])  # v0.9.0
router.include_router(cobros_router, prefix="", tags=["ui-cobros"])  # v0.9.1
router.include_router(iva_compras_router, prefix="", tags=["ui-iva-compras"])  # v0.9.1
