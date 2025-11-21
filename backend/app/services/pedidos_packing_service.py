# app/services/pedidos_packing_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from io import BytesIO
from datetime import datetime
from typing import Optional

from app.models.pedido_model import Pedido
from app.models.cliente_model import Cliente
from app.models.producto_model import Producto

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def get_pedido_with_details(db: Session, pedido_id: int) -> Optional[Pedido]:
    """Obtener pedido con cliente y productos cargados"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        return None
    
    # Eager load relationships
    if pedido.cliente_id:
        pedido.cliente = db.query(Cliente).filter(Cliente.id == pedido.cliente_id).first()
    
    for item in pedido.items:
        item.producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
    
    return pedido


def generate_packing_html(db: Session, pedido_id: int) -> str:
    """Genera HTML imprimible para picking/packing"""
    pedido = get_pedido_with_details(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Cliente info
    cliente_nombre = "—"
    cliente_telefono = ""
    if pedido.cliente:
        cliente_nombre = pedido.cliente.nombre
        cliente_telefono = pedido.cliente.telefono or ""
    elif pedido.telefono:
        cliente_nombre = f"Tel: {pedido.telefono}"
    
    # Items table rows
    items_html = ""
    for item in pedido.items:
        producto_nombre = f"Producto #{item.producto_id}"
        if item.producto:
            producto_nombre = item.producto.nombre
        
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{producto_nombre}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{item.cantidad}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item.precio_unitario:.2f}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item.subtotal:.2f}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; width: 100px;"></td>
        </tr>
        """
    
    # Nota
    nota_html = ""
    if pedido.nota:
        nota_html = f"""
        <div style="margin-top: 20px; padding: 10px; background: #f9f9f9; border-left: 3px solid #333;">
            <strong>Observaciones:</strong> {pedido.nota}
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Packing Slip - Pedido #{pedido.id}</title>
        <style>
            @media print {{
                body {{ margin: 0; }}
                .no-print {{ display: none; }}
            }}
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }}
            .header {{
                border-bottom: 3px solid #333;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .info-section {{
                margin-bottom: 20px;
            }}
            .info-section div {{
                margin: 5px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th {{
                background: #333;
                color: white;
                padding: 10px;
                text-align: left;
            }}
            .total-row {{
                font-weight: bold;
                background: #f0f0f0;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="no-print" style="margin-bottom: 20px;">
            <button onclick="window.print()" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
                🖨️ Imprimir
            </button>
            <button onclick="window.close()" style="padding: 10px 20px; font-size: 16px; cursor: pointer; margin-left: 10px;">
                ✖ Cerrar
            </button>
        </div>
        
        <div class="header">
            <h1>PACKING SLIP / PICKING LIST</h1>
            <div style="font-size: 14px; color: #666;">Sistema Comercial</div>
        </div>
        
        <div class="info-section">
            <div><strong>Pedido N°:</strong> {pedido.id}</div>
            <div><strong>Fecha:</strong> {pedido.created_at.strftime('%d/%m/%Y %H:%M')}</div>
            <div><strong>Estado:</strong> {pedido.estado.value}</div>
            <div><strong>Cliente:</strong> {cliente_nombre}</div>
            {f'<div><strong>Teléfono:</strong> {cliente_telefono}</div>' if cliente_telefono else ''}
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Producto</th>
                    <th style="text-align: center; width: 100px;">Cantidad</th>
                    <th style="text-align: right; width: 120px;">Precio Unit.</th>
                    <th style="text-align: right; width: 120px;">Subtotal</th>
                    <th style="text-align: center; width: 100px;">✓ Verificado</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
                <tr class="total-row">
                    <td colspan="3" style="padding: 10px; text-align: right;">TOTAL:</td>
                    <td style="padding: 10px; text-align: right;">${pedido.total:.2f}</td>
                    <td></td>
                </tr>
            </tbody>
        </table>
        
        {nota_html}
        
        <div class="footer">
            <div>Preparado por: _____________________________ Fecha: ___/___/___</div>
            <div style="margin-top: 10px;">Firma: _____________________________</div>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_packing_pdf(db: Session, pedido_id: int) -> bytes:
    """Genera PDF para picking/packing usando ReportLab"""
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="ReportLab no está instalado. Ejecute: pip install reportlab"
        )
    
    pedido = get_pedido_with_details(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Crear buffer
    buffer = BytesIO()
    
    # Crear documento
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.black,
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Título
    story.append(Paragraph("PACKING SLIP / PICKING LIST", title_style))
    story.append(Paragraph("Sistema Comercial", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Info del pedido
    cliente_nombre = "—"
    cliente_telefono = ""
    if pedido.cliente:
        cliente_nombre = pedido.cliente.nombre
        cliente_telefono = pedido.cliente.telefono or ""
    elif pedido.telefono:
        cliente_nombre = f"Tel: {pedido.telefono}"
    
    info_data = [
        ["Pedido N°:", str(pedido.id), "Fecha:", pedido.created_at.strftime('%d/%m/%Y %H:%M')],
        ["Cliente:", cliente_nombre, "Estado:", pedido.estado.value],
    ]
    if cliente_telefono:
        info_data.append(["Teléfono:", cliente_telefono, "", ""])
    
    info_table = Table(info_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 2.5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de items
    items_data = [["Producto", "Cantidad", "Precio Unit.", "Subtotal", "✓"]]
    for item in pedido.items:
        producto_nombre = f"Producto #{item.producto_id}"
        if item.producto:
            producto_nombre = item.producto.nombre
        
        items_data.append([
            producto_nombre,
            str(item.cantidad),
            f"${item.precio_unitario:.2f}",
            f"${item.subtotal:.2f}",
            ""
        ])
    
    # Fila de total
    items_data.append(["", "", "TOTAL:", f"${pedido.total:.2f}", ""])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.2*inch, 1.2*inch, 0.6*inch])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Body
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
        ('TOPPADDING', (0, 1), (-1, -2), 6),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        
        # Alignment
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        
        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
    ]))
    story.append(items_table)
    
    # Nota
    if pedido.nota:
        story.append(Spacer(1, 0.2*inch))
        nota_style = ParagraphStyle(
            'Nota',
            parent=styles['Normal'],
            fontSize=9,
            leftIndent=10,
            spaceBefore=6,
            spaceAfter=6,
        )
        story.append(Paragraph(f"<b>Observaciones:</b> {pedido.nota}", nota_style))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_data = [
        ["Preparado por: _____________________________", "Fecha: ___/___/___"],
        ["Firma: _____________________________", ""],
    ]
    footer_table = Table(footer_data, colWidths=[4*inch, 3*inch])
    footer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(footer_table)
    
    # Construir PDF
    doc.build(story)
    
    # Obtener bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

