# app/schemas/factura_schema.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class FacturaItemOut(BaseModel):
    """Schema de salida para ítem de factura"""
    id: int
    factura_id: int
    producto_id: Optional[int] = None
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    alic_iva: Decimal
    subtotal: Decimal
    iva_monto: Decimal

    class Config:
        from_attributes = True


class FacturaOut(BaseModel):
    """Schema de salida para factura"""
    id: int
    created_at: datetime
    venta_id: Optional[int] = None
    pedido_id: Optional[int] = None
    tipo_cbte: int
    pto_vta: int
    nro_cbte: int
    concepto: int
    doc_tipo: int
    doc_nro: str
    imp_neto: Decimal
    imp_iva: Decimal
    imp_total: Decimal
    imp_exento: Decimal
    moneda: str
    cotiz: Decimal
    cae: Optional[str] = None
    cae_vto: Optional[str] = None
    resultado: Optional[str] = None
    obs: Optional[str] = None
    qr_json: Optional[Dict[str, Any]] = None
    items: List[FacturaItemOut] = []

    class Config:
        from_attributes = True


class FacturaEmitirRequest(BaseModel):
    """Schema de entrada para emitir factura"""
    venta_id: Optional[int] = None
    pedido_id: Optional[int] = None
    tipo_cbte: int = Field(..., description="Tipo de comprobante: 1=A, 6=B, 11=C")
    pto_vta: Optional[int] = Field(None, description="Punto de venta (default: config)")

    class Config:
        json_schema_extra = {
            "example": {
                "venta_id": 123,
                "tipo_cbte": 6,
                "pto_vta": 1
            }
        }


class FacturaListFilter(BaseModel):
    """Schema para filtros de listado de facturas"""
    fecha_desde: Optional[str] = None  # YYYY-MM-DD
    fecha_hasta: Optional[str] = None  # YYYY-MM-DD
    cliente_id: Optional[int] = None
    tipo_cbte: Optional[int] = None
    pto_vta: Optional[int] = None
    page: int = 1
    size: int = 20

