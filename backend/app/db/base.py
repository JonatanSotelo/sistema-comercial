# app/db/base.py
from app.db.database import Base

from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.models.venta_model import Venta
from app.models.user_model import Usuario
from app.models.proveedor_model import Proveedor
from app.models.compra_model import Compra, CompraItem, StockMovimiento
from app.models.auditoria import AuditLog  # 👈 importante
