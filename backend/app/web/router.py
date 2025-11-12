
from fastapi import APIRouter
from .auth_ui import router as auth_router
from .app_ui import router as app_router
from .products_ui import router as products_router
from .clients_ui import router as clients_router

router = APIRouter()
router.include_router(auth_router, prefix="/app", tags=["ui-auth"])
router.include_router(app_router, prefix="/app", tags=["ui-app"])
router.include_router(products_router, prefix="/app", tags=["ui-productos"])
router.include_router(clients_router, prefix="/app", tags=["ui-clientes"])
