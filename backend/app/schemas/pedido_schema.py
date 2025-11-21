from pydantic import BaseModel
from typing import List, Optional
from pydantic.config import ConfigDict
from datetime import datetime
from app.models.pedido_model import EstadoPedido, OrigenPedido


class PedidoItemIn(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: Optional[float] = None


class PedidoCreate(BaseModel):
    cliente_id: Optional[int] = None
    items: List[PedidoItemIn]
    nota: Optional[str] = None
    origen: OrigenPedido = OrigenPedido.MANUAL
    telefono: Optional[str] = None
    external_ref: Optional[str] = None


class PedidoUpdate(BaseModel):
    items: List[PedidoItemIn]
    nota: Optional[str] = None


class PedidoEstadoChange(BaseModel):
    estado: EstadoPedido


class PedidoItemOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class PedidoOut(BaseModel):
    id: int
    created_at: datetime
    cliente_id: Optional[int] = None
    estado: EstadoPedido
    origen: OrigenPedido
    telefono: Optional[str] = None
    nota: Optional[str] = None
    total: float
    created_by: Optional[int] = None
    external_ref: Optional[str] = None
    items: List[PedidoItemOut]
    model_config = ConfigDict(from_attributes=True)


class PedidoFacturarResponse(BaseModel):
    venta_id: int
    total: float

