# app/services/notifications_service.py
import asyncio
import httpx
from typing import Optional
from sqlalchemy.orm import Session
from app.models.pedido_model import Pedido
from app.models.auditoria import AuditAction
from app.core.config import settings


async def notify_order_ready(db: Session, pedido_id: int):
    """
    Envía notificación WhatsApp (y opcionalmente email) cuando un pedido está LISTO
    No bloqueante, ejecuta en BackgroundTasks
    """
    try:
        # 1. Obtener pedido
        pedido = db.get(Pedido, pedido_id)
        if not pedido:
            print(f"[notify] Pedido {pedido_id} not found")
            return
        
        # 2. Verificar si está habilitado
        if not settings.NOTIFY_ON_READY:
            print(f"[notify] Notifications disabled (NOTIFY_ON_READY=false)")
            return
        
        # 3. Armar payload
        telefono = pedido.telefono or (pedido.cliente.telefono if pedido.cliente else None)
        if not telefono:
            print(f"[notify] Pedido {pedido_id} sin teléfono, skip notification")
            _audit_notification(db, pedido_id, success=False, details={"error": "sin_telefono"})
            return
        
        payload = {
            "phone": telefono,
            "customer_name": pedido.cliente.nombre if pedido.cliente else "Cliente",
            "order_id": pedido.id,
            "items": [
                {
                    "producto": item.producto.nombre,
                    "cantidad": item.cantidad,
                    "precio": float(item.precio_unitario)
                }
                for item in pedido.items
            ],
            "total": float(pedido.total),
            "external_ref": pedido.external_ref,
            "message": f"¡Tu pedido #{pedido.id} está listo para retirar! Total: ${pedido.total:.2f}"
        }
        
        # 4. Enviar WhatsApp con retries
        success = await _send_whatsapp_notification(payload)
        
        # 5. Opcional: Email
        if settings.SMTP_HOST:
            try:
                await _send_email_notification(payload)
            except Exception as e:
                print(f"[notify] Email notification failed: {e}")
        
        # 6. Auditoría
        _audit_notification(db, pedido_id, success=success, details={
            "type": "order_ready",
            "phone": telefono,
            "items_count": len(pedido.items)
        })
        
        print(f"[notify] Pedido {pedido_id} notification sent: {success}")
        
    except Exception as e:
        print(f"[notify] Error processing notification for pedido {pedido_id}: {e}")
        _audit_notification(db, pedido_id, success=False, details={"error": str(e)})


async def _send_whatsapp_notification(payload: dict) -> bool:
    """Envía notificación WhatsApp con retries y backoff exponencial"""
    if not settings.NOTIFY_WHATS_ENDPOINT:
        print("[notify] NOTIFY_WHATS_ENDPOINT not configured")
        return False
    
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    settings.NOTIFY_WHATS_ENDPOINT,
                    json=payload,
                    headers={"Authorization": f"Bearer {settings.NOTIFY_WHATS_TOKEN}"}
                )
                
                if response.status_code == 200:
                    print(f"[notify] WhatsApp notification sent successfully (attempt {attempt + 1})")
                    return True
                else:
                    print(f"[notify] WhatsApp notification failed with status {response.status_code} (attempt {attempt + 1})")
                    
        except Exception as e:
            print(f"[notify] WhatsApp notification attempt {attempt + 1} failed: {e}")
        
        # Backoff exponencial: 0.5s, 1s, 2s
        if attempt < 2:
            await asyncio.sleep(0.5 * (2 ** attempt))
    
    print("[notify] WhatsApp notification failed after 3 attempts")
    return False


async def _send_email_notification(payload: dict):
    """Envía notificación por email (opcional, simple)"""
    # TODO: Implementar con aiosmtplib o similar
    # Por ahora solo logging
    print(f"[notify] Email notification would be sent to {payload.get('customer_name')}")
    pass


def _audit_notification(db: Session, pedido_id: int, success: bool, details: dict):
    """Registra la notificación en auditoría (sin tokens sensibles)"""
    try:
        from app.services.auditoria_service import create_audit_log
        
        create_audit_log(
            db=db,
            user_id=None,
            username="system",
            table_name="notificaciones",
            action=AuditAction.CREATE if success else AuditAction.UPDATE,
            record_id=str(pedido_id),
            details={
                **details,
                "success": success,
                "timestamp": None  # Se agrega automáticamente
            },
            path=None,
            method=None,
            ip=None
        )
        db.commit()
    except Exception as e:
        print(f"[notify] Error creating audit log: {e}")

