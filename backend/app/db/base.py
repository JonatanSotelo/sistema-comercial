from app.db.database import Base  # 👈 TU Base

# Importá TODOS los modelos que quieras que Alembic "vea"
from app.models.user_model import User
from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.models.venta_model import Venta
from app.models.proveedor_model import Proveedor
from app.models.compra_model import Compra, CompraItem, StockMovimiento
from app.models.auditoria import AuditLog
from app.models.notificacion_model import Notificacion
from app.models.permiso_model import Role, Permission
from app.models.pedido_model import Pedido, PedidoItem
from app.models.stock_reservation_model import StockReservation
from app.models.factura_model import Factura, FacturaItem  # v0.9.0+
from app.models.cobro_model import Cobro  # v0.9.1+
from app.models.purchase_invoice_model import PurchaseInvoice  # v0.9.1+

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
    "Notificacion",
    "Role",
    "Permission",
    "Pedido",
    "PedidoItem",
    "StockReservation",
    "Factura",  # v0.9.0+
    "FacturaItem",  # v0.9.0+
    "Cobro",  # v0.9.1+
    "PurchaseInvoice",  # v0.9.1+
]
