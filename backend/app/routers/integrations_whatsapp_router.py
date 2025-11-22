# app/routers/integrations_whatsapp_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.core.settings import settings
from app.services.integrations.whatsapp_orders_service import (
    resolve_or_create_cliente_by_phone,
    quote_or_create_sale
)
from app.services.auditoria_service import create_audit_log, get_client_ip
from app.models.auditoria import AuditAction

router = APIRouter(prefix="/integrations/whatsapp", tags=["Integraciones WhatsApp"])


# Schemas
class WhatsAppOrderItem(BaseModel):
    """Item de pedido WhatsApp (estructurado)"""
    product_id: Optional[int] = None
    codigo: Optional[str] = None
    query: Optional[str] = None
    cantidad: int = Field(1, ge=1)
    precio_unitario: Optional[float] = Field(None, ge=0)


class WhatsAppOrderStructured(BaseModel):
    """Pedido estructurado (preferido)"""
    phone: str
    customer_name: Optional[str] = None
    confirm: bool = False
    as_order: bool = False  # True para crear pedido, False para crear venta
    external_ref: Optional[str] = None  # ID mensaje/hilo del bot
    items: List[WhatsAppOrderItem]


class WhatsAppOrderText(BaseModel):
    """Pedido en texto libre (opcional, MVP simple)"""
    phone: str
    message: str


def verify_integration_token(x_integration_token: Optional[str] = Header(None)) -> bool:
    """Verifica el token de integración"""
    expected_token = getattr(settings, "WHATS_ORDERS_TOKEN", None)
    
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="Integración WhatsApp no configurada (WHATS_ORDERS_TOKEN no definido)"
        )
    
    if not x_integration_token or x_integration_token != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Token de integración inválido"
        )
    
    return True


@router.post("/orders", summary="Crear pedido/cotización desde WhatsApp")
async def create_whatsapp_order(
    order: WhatsAppOrderStructured,
    request: Request,
    db: Session = Depends(get_db),
    _token_verified: bool = Depends(verify_integration_token)
):
    """
    Endpoint para recibir pedidos desde Bot WhatsApp.
    
    - Si confirm=false: devuelve cotización sin tocar stock
    - Si confirm=true + as_order=false: crea venta y ajusta stock
    - Si confirm=true + as_order=true: crea pedido (no ajusta stock)
    
    Variable de entorno WHATS_CREATE_ORDERS=true fuerza as_order=true.
    
    Autenticación: Header X-Integration-Token
    """
    client_ip = get_client_ip(request)
    
    # Sanitizar payload para auditoría (sin token)
    sanitized_payload = {
        "phone": order.phone,
        "customer_name": order.customer_name,
        "confirm": order.confirm,
        "items_count": len(order.items)
    }
    
    try:
        # Resolver o crear cliente
        cliente = resolve_or_create_cliente_by_phone(
            db,
            order.phone,
            order.customer_name
        )
        
        # Convertir items a formato dict
        items_dict = [
            {
                "product_id": item.product_id,
                "codigo": item.codigo,
                "query": item.query,
                "cantidad": item.cantidad,
                "precio_unitario": item.precio_unitario
            }
            for item in order.items
        ]
        
        # Cotizar o crear venta/pedido
        result = quote_or_create_sale(
            db,
            cliente.id,
            items_dict,
            confirm=order.confirm,
            request=request,
            as_order=order.as_order,
            telefono=order.phone,
            external_ref=order.external_ref,
        )
        
        # Registrar en auditoría
        try:
            create_audit_log(
                db,
                user_id=None,
                username="whatsapp_bot",
                table_name="integraciones",
                action=AuditAction.CREATE,
                record_id=str(result.get("venta_id") or result.get("pedido_id") or "quote"),
                details={
                    **sanitized_payload,
                    "cliente_id": cliente.id,
                    "result": result,
                    "status": "success"
                },
                path=request.url.path,
                method=request.method,
                ip=client_ip
            )
        except Exception as e:
            # No fallar si el log falla
            print(f"[auditoria] Error al registrar log de integración WhatsApp: {e}")
        
        return result
    
    except HTTPException:
        # Re-lanzar HTTPException
        raise
    except Exception as e:
        # Registrar error en auditoría
        try:
            create_audit_log(
                db,
                user_id=None,
                username="whatsapp_bot",
                table_name="integraciones",
                action=AuditAction.CREATE,
                record_id="error",
                details={
                    **sanitized_payload,
                    "error": str(e),
                    "status": "error"
                },
                path=request.url.path,
                method=request.method,
                ip=client_ip
            )
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar pedido: {str(e)}"
        )

