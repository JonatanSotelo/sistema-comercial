# app/services/remito_service.py
from io import BytesIO
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import cm
from app.models.venta_model import Venta


def generate_remito_html(venta: Venta) -> str:
    """Genera HTML imprimible de remito"""
    cliente_nombre = venta.cliente.nombre if venta.cliente else 'Consumidor Final'
    cliente_tel = venta.cliente.telefono if venta.cliente else '-'
    fecha_str = venta.fecha.strftime('%d/%m/%Y %H:%M')
    
    items_html = "".join([
        f"""
        <tr>
            <td>{item.producto.nombre[:40]}</td>
            <td style="text-align:center">{item.cantidad}</td>
            <td style="text-align:right">${item.precio_unitario:.2f}</td>
            <td style="text-align:right">${item.subtotal:.2f}</td>
        </tr>
        """
        for item in venta.items
    ])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Remito #{venta.id}</title>
        <style>
            @media print {{
                @page {{ margin: 1cm; }}
                body {{ margin: 0; }}
            }}
            body {{
                font-family: Arial, sans-serif;
                margin: 2cm;
                font-size: 12px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 2cm;
                border-bottom: 2px solid #333;
                padding-bottom: 1cm;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .info {{
                margin-bottom: 1cm;
            }}
            .info p {{
                margin: 0.3em 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 1cm;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .total {{
                font-weight: bold;
                font-size: 1.3em;
                text-align: right;
                margin: 1cm 0;
            }}
            .footer {{
                margin-top: 3cm;
                padding-top: 1cm;
                border-top: 1px solid #ccc;
            }}
            .signature {{
                margin-top: 2cm;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>REMITO</h1>
            <p>Nro: {venta.id:06d}</p>
        </div>
        
        <div class="info">
            <p><strong>Fecha:</strong> {fecha_str}</p>
            <p><strong>Cliente:</strong> {cliente_nombre}</p>
            <p><strong>Teléfono:</strong> {cliente_tel}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width:50%">Producto</th>
                    <th style="width:15%;text-align:center">Cantidad</th>
                    <th style="width:15%;text-align:right">P.Unit</th>
                    <th style="width:20%;text-align:right">Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>
        
        <div class="total">
            TOTAL: ${venta.total:.2f}
        </div>
        
        <div class="footer">
            <div class="signature">
                <p>Firma del receptor: _______________________________________</p>
                <p>Aclaración: _______________________________________________</p>
                <p>DNI: ______________________________________________________</p>
            </div>
            
            <div style="margin-top:2cm">
                <p><strong>Observaciones:</strong></p>
                <p>_____________________________________________________________</p>
                <p>_____________________________________________________________</p>
            </div>
        </div>
        
        <script>
            // Auto-print on load (optional)
            // window.onload = function() {{ window.print(); }}
        </script>
    </body>
    </html>
    """
    return html


def generate_remito_pdf(venta: Venta) -> bytes:
    """Genera PDF de remito con ReportLab"""
    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 2*cm, "REMITO")
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 2.8*cm, f"Nro: {venta.id:06d}")
    
    # Cliente y fecha
    y = height - 4.5*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "Fecha:")
    c.setFont("Helvetica", 11)
    c.drawString(4*cm, y, venta.fecha.strftime('%d/%m/%Y %H:%M'))
    
    y -= 0.8*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "Cliente:")
    c.setFont("Helvetica", 11)
    cliente_nombre = venta.cliente.nombre if venta.cliente else 'Consumidor Final'
    c.drawString(4*cm, y, cliente_nombre[:50])
    
    y -= 0.8*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "Teléfono:")
    c.setFont("Helvetica", 11)
    cliente_tel = venta.cliente.telefono if venta.cliente else '-'
    c.drawString(4*cm, y, cliente_tel)
    
    # Tabla de items
    y -= 1.5*cm
    
    # Header de tabla
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Producto")
    c.drawString(12*cm, y, "Cant")
    c.drawString(14.5*cm, y, "P.Unit")
    c.drawString(17*cm, y, "Subtotal")
    
    # Línea separadora
    y -= 0.3*cm
    c.line(2*cm, y, width - 2*cm, y)
    
    # Items
    y -= 0.6*cm
    c.setFont("Helvetica", 9)
    
    for item in venta.items:
        if y < 5*cm:  # Nueva página si no hay espacio
            c.showPage()
            y = height - 3*cm
            c.setFont("Helvetica", 9)
        
        producto_nombre = item.producto.nombre[:45] if len(item.producto.nombre) > 45 else item.producto.nombre
        c.drawString(2*cm, y, producto_nombre)
        c.drawString(12.2*cm, y, str(item.cantidad))
        c.drawRightString(16*cm, y, f"${item.precio_unitario:.2f}")
        c.drawRightString(19*cm, y, f"${item.subtotal:.2f}")
        y -= 0.6*cm
    
    # Línea separadora
    y -= 0.2*cm
    c.line(2*cm, y, width - 2*cm, y)
    
    # Total
    y -= 1*cm
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(19*cm, y, f"TOTAL: ${venta.total:.2f}")
    
    # Footer - Firma y observaciones
    y -= 3*cm
    if y < 8*cm:
        c.showPage()
        y = height - 3*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, "Firma del receptor: ____________________________________________")
    y -= 0.8*cm
    c.drawString(2*cm, y, "Aclaración: ___________________________________________________")
    y -= 0.8*cm
    c.drawString(2*cm, y, "DNI: __________________________________________________________")
    
    y -= 1.5*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "Observaciones:")
    y -= 0.6*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, "_________________________________________________________________")
    y -= 0.6*cm
    c.drawString(2*cm, y, "_________________________________________________________________")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer.getvalue()

