# app/services/factura_pdf_service.py
"""
Servicio para generar PDF de facturas electrónicas AFIP
Incluye QR AFIP, datos fiscales y formatos A/B/C
"""

import base64
import json
from io import BytesIO
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    import qrcode
except ImportError as e:
    raise ImportError(
        f"Faltan dependencias para PDF de facturas: {e}. "
        "Instala: pip install reportlab qrcode[pil] Pillow"
    )

from app.models.factura_model import Factura
from app.core.config import settings


def generate_factura_pdf(db: Session, factura_id: int) -> bytes:
    """
    Genera el PDF de una factura electrónica con QR AFIP.
    
    Args:
        db: Sesión de base de datos
        factura_id: ID de la factura
    
    Returns:
        Bytes del PDF generado
    """
    # Obtener factura con relaciones
    factura = db.query(Factura).options(
        joinedload(Factura.venta).joinedload("cliente"),
        joinedload(Factura.pedido).joinedload("cliente"),
        joinedload(Factura.items).joinedload("producto")
    ).filter(Factura.id == factura_id).first()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Determinar cliente
    cliente = None
    if factura.venta and factura.venta.cliente:
        cliente = factura.venta.cliente
    elif factura.pedido and factura.pedido.cliente:
        cliente = factura.pedido.cliente
    
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
        fontSize=16,
        textColor=colors.HexColor('#1976D2'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Determinar tipo de factura para título
    tipo_nombre = _get_tipo_nombre(factura.tipo_cbte)
    
    # ========== ENCABEZADO ==========
    story.append(Paragraph(f"<b>FACTURA {tipo_nombre}</b>", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Datos del emisor (2 columnas: info + QR)
    emisor_data = [
        ['<b>Razón Social:</b> TU EMPRESA S.A.', ''],  # TODO: Parametrizar
        [f'<b>CUIT:</b> {settings.AFIP_CUIT}', ''],
        [f'<b>Punto de Venta:</b> {factura.pto_vta:04d}', f'<b>Nº Comprobante:</b> {factura.nro_cbte:08d}'],
        [f'<b>Fecha:</b> {factura.created_at.strftime("%d/%m/%Y")}', ''],
    ]
    
    # Agregar QR si existe
    qr_image = None
    if factura.qr_json and factura.cae:
        try:
            qr_image = _generate_qr_image(factura.qr_json)
        except Exception as e:
            print(f"[PDF] Error al generar QR: {e}")
    
    if qr_image:
        # Tabla con QR a la derecha
        emisor_table = Table([
            [Paragraph('<b>DATOS DEL EMISOR</b>', styles['Heading3']), qr_image],
            [Paragraph('<br/>'.join([d[0] for d in emisor_data]), styles['Normal']), '']
        ], colWidths=[doc.width * 0.65, doc.width * 0.35])
        emisor_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ]))
    else:
        emisor_table = Table([[Paragraph('<br/>'.join([f"{d[0]} {d[1]}" for d in emisor_data]), styles['Normal'])]], colWidths=[doc.width])
    
    story.append(emisor_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ========== DATOS DEL RECEPTOR ==========
    story.append(Paragraph('<b>DATOS DEL CLIENTE</b>', styles['Heading3']))
    story.append(Spacer(1, 0.2*cm))
    
    cliente_nombre = cliente.nombre if cliente else "Consumidor Final"
    cliente_direccion = cliente.direccion if cliente and cliente.direccion else ""
    cliente_doc = _format_documento(factura.doc_tipo, factura.doc_nro)
    
    receptor_data = [
        ['<b>Nombre / Razón Social:</b>', cliente_nombre],
        ['<b>Documento:</b>', cliente_doc],
        ['<b>Dirección:</b>', cliente_direccion or "—"],
    ]
    
    receptor_table = Table(receptor_data, colWidths=[doc.width * 0.3, doc.width * 0.7])
    receptor_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(receptor_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ========== DETALLE DE ÍTEMS ==========
    story.append(Paragraph('<b>DETALLE DE PRODUCTOS / SERVICIOS</b>', styles['Heading3']))
    story.append(Spacer(1, 0.2*cm))
    
    # Encabezado de tabla según tipo de factura
    if factura.tipo_cbte == 11:  # C (sin IVA discriminado)
        items_header = ['Descripción', 'Cant.', 'P. Unit.', 'Subtotal']
        col_widths = [doc.width * 0.5, doc.width * 0.15, doc.width * 0.15, doc.width * 0.2]
    else:  # A o B (con IVA discriminado)
        items_header = ['Descripción', 'Cant.', 'P. Unit.', 'IVA', 'Subtotal']
        col_widths = [doc.width * 0.4, doc.width * 0.12, doc.width * 0.15, doc.width * 0.13, doc.width * 0.2]
    
    items_data = [items_header]
    
    for item in factura.items:
        desc = item.descripcion or "Sin descripción"
        cant = f"{float(item.cantidad):.2f}"
        pu = f"${float(item.precio_unitario):.2f}"
        subtotal = f"${float(item.subtotal):.2f}"
        
        if factura.tipo_cbte == 11:  # C
            items_data.append([desc, cant, pu, subtotal])
        else:  # A o B
            iva_porc = f"{float(item.alic_iva):.1f}%"
            items_data.append([desc, cant, pu, iva_porc, subtotal])
    
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ========== TOTALES ==========
    totales_data = []
    
    if factura.tipo_cbte in [1, 6]:  # A o B
        totales_data.append(['Subtotal (Neto):', f"${float(factura.imp_neto):.2f}"])
        if float(factura.imp_exento) > 0:
            totales_data.append(['Exento:', f"${float(factura.imp_exento):.2f}"])
        totales_data.append(['IVA:', f"${float(factura.imp_iva):.2f}"])
    
    totales_data.append(['<b>TOTAL:</b>', f"<b>${float(factura.imp_total):.2f}</b>"])
    
    totales_table = Table(totales_data, colWidths=[doc.width * 0.7, doc.width * 0.3])
    totales_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ]))
    story.append(totales_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ========== DATOS AFIP ==========
    if factura.cae:
        story.append(Paragraph('<b>DATOS DE AUTORIZACIÓN AFIP</b>', styles['Heading3']))
        story.append(Spacer(1, 0.2*cm))
        
        cae_data = [
            ['<b>CAE:</b>', factura.cae],
            ['<b>Vencimiento CAE:</b>', _format_cae_vto(factura.cae_vto)],
            ['<b>Comprobante Autorizado:</b>', f"{factura.pto_vta:04d}-{factura.nro_cbte:08d}"],
        ]
        
        cae_table = Table(cae_data, colWidths=[doc.width * 0.4, doc.width * 0.6])
        cae_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(cae_table)
        story.append(Spacer(1, 0.3*cm))
        
        # URL del QR
        if factura.qr_json:
            qr_url = _generate_qr_url(factura.qr_json)
            story.append(Paragraph(f'<font size="8">Validar en AFIP: {qr_url}</font>', styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _get_tipo_nombre(tipo_cbte: int) -> str:
    """Convierte tipo de comprobante numérico a letra"""
    mapping = {
        1: "A",
        6: "B",
        11: "C",
        3: "NC A",
        8: "NC B",
        13: "NC C",
        2: "ND A",
        7: "ND B",
        12: "ND C",
    }
    return mapping.get(tipo_cbte, "DESCONOCIDA")


def _format_documento(doc_tipo: int, doc_nro: str) -> str:
    """Formatea documento según tipo"""
    tipo_map = {
        80: "CUIT",
        96: "DNI",
        99: "Consumidor Final",
        86: "CUIL",
    }
    tipo_str = tipo_map.get(doc_tipo, f"Tipo {doc_tipo}")
    return f"{tipo_str}: {doc_nro}" if doc_nro != "0" else tipo_str


def _format_cae_vto(cae_vto: str) -> str:
    """Formatea fecha de vencimiento CAE (YYYYMMDD -> DD/MM/YYYY)"""
    if not cae_vto or len(cae_vto) != 8:
        return cae_vto
    return f"{cae_vto[6:8]}/{cae_vto[4:6]}/{cae_vto[0:4]}"


def _generate_qr_image(qr_json: dict) -> Image:
    """Genera imagen del QR AFIP para incluir en PDF"""
    qr_url = _generate_qr_url(qr_json)
    
    # Generar QR con qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar en buffer
    qr_buffer = BytesIO()
    img_qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    # Crear Image de ReportLab
    qr_image = Image(qr_buffer, width=3*cm, height=3*cm)
    
    return qr_image


def _generate_qr_url(qr_json: dict) -> str:
    """Genera la URL del QR AFIP según especificación oficial"""
    # Codificar JSON en base64url
    json_str = json.dumps(qr_json, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    base64_bytes = base64.urlsafe_b64encode(json_bytes)
    base64_str = base64_bytes.decode('utf-8').rstrip('=')  # Remover padding
    
    return f"https://www.afip.gob.ar/fe/qr/?p={base64_str}"

