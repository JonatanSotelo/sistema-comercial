# app/db/base.py
from app.db.database import Base  # 👈 TU Base (no uses base_class aquí)

# Importá TODOS los modelos que quieras que Alembic “vea”
from app.models.user_model import User  # 'Usuario' es alias dentro del archivo
from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.models.venta_model import Venta
from app.models.proveedor_model import Proveedor
from app.models.compra_model import Compra, CompraItem, StockMovimiento
from app.models.auditoria import AuditLog

__all__ = [
    "Base",
    "User",
    "Producto",
    "Cliente",
    "Venta",
    "Proveedor",
    "Compra",
    "CompraItem",
    "StockMovimiento",
    "AuditLog",
]
