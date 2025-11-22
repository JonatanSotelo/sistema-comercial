# app/services/label_service.py
from io import BytesIO
import json
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from app.models.pedido_model import Pedido


def generate_label_pdf(pedido: Pedido) -> bytes:
    """Genera etiqueta PDF con QR para pedido (tamaño A6: ~105x148mm)"""
    
    # 1. Preparar datos para QR
    qr_data = {
        "type": "pedido",
        "id": pedido.id,
        "cliente": pedido.cliente.nombre if pedido.cliente else "Sin cliente",
        "telefono": pedido.telefono or (pedido.cliente.telefono if pedido.cliente else None),
        "total": float(pedido.total),
        "estado": pedido.estado.value,
        "items_count": len(pedido.items)
    }
    
    # 2. Generar QR code
    qr = qrcode.QRCode(
        version=1,  # Auto-ajusta el tamaño
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # 3. Convertir QR a formato compatible con ReportLab
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    # 4. Crear PDF (tamaño A6)
    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A6)
    width, height = A6  # ~105mm x 148mm = ~297 x 420 puntos
    
    # 5. Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 1.5*cm, f"PEDIDO #{pedido.id:06d}")
    
    # 6. QR Code (centrado)
    qr_size = 4*cm
    qr_x = (width - qr_size) / 2
    qr_y = height - 6.5*cm
    
    try:
        c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)
    except Exception as e:
        print(f"[label] Error drawing QR: {e}")
        # Fallback: mostrar texto
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, qr_y + 2*cm, "[QR CODE]")
    
    # 7. Información del pedido
    y = qr_y - 0.8*cm
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*cm, y, "Cliente:")
    c.setFont("Helvetica", 10)
    cliente_nombre = pedido.cliente.nombre if pedido.cliente else "Sin cliente"
    c.drawString(3*cm, y, cliente_nombre[:20])
    
    y -= 0.7*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*cm, y, "Teléfono:")
    c.setFont("Helvetica", 10)
    telefono = pedido.telefono or (pedido.cliente.telefono if pedido.cliente else "-")
    c.drawString(3*cm, y, str(telefono)[:15])
    
    y -= 0.7*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*cm, y, "Items:")
    c.setFont("Helvetica", 10)
    c.drawString(3*cm, y, f"{len(pedido.items)} producto(s)")
    
    y -= 0.7*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*cm, y, "Estado:")
    c.setFont("Helvetica", 10)
    c.drawString(3*cm, y, pedido.estado.value)
    
    # 8. Total destacado
    y -= 1.2*cm
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, f"TOTAL: ${pedido.total:.2f}")
    
    # 9. Footer con fecha
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 0.8*cm, f"Generado: {pedido.created_at.strftime('%d/%m/%Y %H:%M')}")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer.getvalue()

