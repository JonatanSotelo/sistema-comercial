# app/services/recibo_pdf_service.py
"""
Servicio para generar PDF de recibos de cobro
"""

from io import BytesIO
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
except ImportError as e:
    raise ImportError(f"Faltan dependencias para PDF de recibos: {e}")

from app.models.cobro_model import Cobro
from app.core.config import settings
from app.services.cobros_service import get_saldo_venta


def generate_recibo_pdf(db: Session, cobro_id: int) -> bytes:
    """
    Genera el PDF de un recibo de cobro.
    
    Args:
        db: Sesión de base de datos
        cobro_id: ID del cobro
    
    Returns:
        Bytes del PDF generado
    """
    # Obtener cobro (sin joinedload para evitar error con columna direccion faltante)
    cobro = db.query(Cobro).filter(Cobro.id == cobro_id).first()
    
    if not cobro:
        raise HTTPException(status_code=404, detail="Cobro no encontrado")
    
    # Cargar venta y cliente manualmente para evitar lazy loading issues
    try:
        venta = cobro.venta
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cargando venta: {str(e)}")
    
    cliente = None
    if venta and venta.cliente_id:
        try:
            from app.models.cliente_model import Cliente
            cliente = db.query(Cliente).filter(Cliente.id == venta.cliente_id).first()
        except Exception as e:
            db.rollback()
            # Si falla obtener cliente, continuamos sin cliente
            cliente = None
    
    # Crear buffer para PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Estilo personalizado para encabezado
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1976D2'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # ========== ENCABEZADO ==========
    recibo_numero = f"{settings.RECIBO_SERIE}-{cobro.id:06d}"
    story.append(Paragraph(f"<b>RECIBO {recibo_numero}</b>", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Datos del emisor
    story.append(Paragraph("<b>DATOS DE LA EMPRESA</b>", styles['Heading3']))
    story.append(Paragraph("TU EMPRESA S.A.", styles['Normal']))  # TODO: Parametrizar
    story.append(Paragraph(f"CUIT: {settings.AFIP_CUIT}", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # ========== DATOS DEL CLIENTE ==========
    story.append(Paragraph("<b>RECIBIMOS DE</b>", styles['Heading3']))
    story.append(Spacer(1, 0.2*cm))
    
    cliente_nombre = cliente.nombre if cliente else "Consumidor Final"
    cliente_cuit = getattr(cliente, 'cuit', None) if cliente else None
    cliente_doc_nro = getattr(cliente, 'doc_nro', None) if cliente else None
    cliente_doc = f"CUIT/DNI: {cliente_cuit or cliente_doc_nro}" if (cliente_cuit or cliente_doc_nro) else ""
    
    receptor_data = [
        ['<b>Cliente:</b>', cliente_nombre],
        ['<b>Documento:</b>', cliente_doc or "—"],
        ['<b>Fecha:</b>', cobro.created_at.strftime("%d/%m/%Y %H:%M") if cobro.created_at else "—"],
    ]
    
    receptor_table = Table(receptor_data, colWidths=[doc.width * 0.3, doc.width * 0.7])
    receptor_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(receptor_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ========== DETALLE DEL COBRO ==========
    story.append(Paragraph("<b>DETALLE DEL PAGO</b>", styles['Heading3']))
    story.append(Spacer(1, 0.2*cm))
    
    detalle_data = [
        ['Concepto', 'Valor'],
        [f'Pago de Venta #{venta.id}', f"${float(venta.total):.2f}"],
        [f'<b>Cobrado por {cobro.medio.value}</b>', f"<b>${float(cobro.importe):.2f}</b>"],
    ]
    
    if cobro.referencia:
        detalle_data.append([f'Referencia: {cobro.referencia}', ''])
    
    # Calcular saldo post-cobro
    saldo_actual = get_saldo_venta(db, venta.id)
    detalle_data.append(['Saldo Pendiente', f"${saldo_actual:.2f}"])
    
    detalle_table = Table(detalle_data, colWidths=[doc.width * 0.6, doc.width * 0.4])
    detalle_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(detalle_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ========== OBSERVACIONES ==========
    if cobro.observaciones:
        story.append(Paragraph("<b>Observaciones:</b>", styles['Heading3']))
        story.append(Paragraph(cobro.observaciones, styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
    
    # ========== FOOTER ==========
    if settings.RECIBO_PDF_FOOTER:
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(settings.RECIBO_PDF_FOOTER, styles['Normal']))
    
    # Espacio para firma
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("_________________________", styles['Normal']))
    story.append(Paragraph("Firma y Aclaración", styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

