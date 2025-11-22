# app/services/libro_iva_ventas_service.py
"""
Servicio para generar Libro IVA Ventas
Reporte de facturas emitidas para AFIP
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from io import BytesIO
import csv

from app.models.factura_model import Factura, FacturaItem


def generar_libro_iva_ventas(
    db: Session,
    fecha_desde: str,
    fecha_hasta: str,
    formato: str = "csv"
) -> bytes:
    """
    Genera el Libro IVA Ventas en formato CSV o XLSX.
    
    Args:
        db: Sesión de base de datos
        fecha_desde: Fecha desde (YYYY-MM-DD)
        fecha_hasta: Fecha hasta (YYYY-MM-DD)
        formato: Formato de salida ("csv" o "xlsx")
    
    Returns:
        Bytes del archivo generado
    """
    # Parsear fechas
    try:
        dt_desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
        dt_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")
        dt_hasta = dt_hasta.replace(hour=23, minute=59, second=59)
    except ValueError:
        raise ValueError("Formato de fecha inválido (YYYY-MM-DD)")
    
    # Consultar facturas
    facturas = db.query(Factura).options(
        joinedload(Factura.venta).joinedload("cliente"),
        joinedload(Factura.pedido).joinedload("cliente"),
        joinedload(Factura.items)
    ).filter(
        and_(
            Factura.created_at >= dt_desde,
            Factura.created_at <= dt_hasta,
            Factura.resultado == "A"  # Solo facturas aprobadas
        )
    ).order_by(Factura.created_at).all()
    
    # Generar datos para el reporte
    rows = []
    for factura in facturas:
        # Determinar cliente
        cliente = None
        if factura.venta and factura.venta.cliente:
            cliente = factura.venta.cliente
        elif factura.pedido and factura.pedido.cliente:
            cliente = factura.pedido.cliente
        
        cliente_nombre = cliente.nombre if cliente else "Consumidor Final"
        cliente_doc = factura.doc_nro if factura.doc_nro != "0" else "—"
        
        # Determinar alícuota principal (la de mayor importe)
        alic_principal = _get_alicuota_principal(factura.items)
        
        row = {
            "Fecha": factura.created_at.strftime("%d/%m/%Y"),
            "Tipo": _get_tipo_nombre(factura.tipo_cbte),
            "Pto. Vta.": f"{factura.pto_vta:04d}",
            "Nro. Cbte.": f"{factura.nro_cbte:08d}",
            "Doc. Tipo": _get_doc_tipo_nombre(factura.doc_tipo),
            "Doc. Nro.": cliente_doc,
            "Cliente": cliente_nombre,
            "Neto Gravado": f"{float(factura.imp_neto):.2f}",
            "Exento": f"{float(factura.imp_exento):.2f}",
            "IVA": f"{float(factura.imp_iva):.2f}",
            "Total": f"{float(factura.imp_total):.2f}",
            "Alíc. Principal": alic_principal,
            "CAE": factura.cae or "—",
        }
        rows.append(row)
    
    # Generar archivo según formato
    if formato == "xlsx":
        return _generate_xlsx(rows)
    else:  # csv
        return _generate_csv(rows)


def _get_tipo_nombre(tipo_cbte: int) -> str:
    """Convierte tipo de comprobante numérico a letra"""
    mapping = {
        1: "FA-A",
        6: "FA-B",
        11: "FA-C",
        3: "NC-A",
        8: "NC-B",
        13: "NC-C",
        2: "ND-A",
        7: "ND-B",
        12: "ND-C",
    }
    return mapping.get(tipo_cbte, f"T{tipo_cbte}")


def _get_doc_tipo_nombre(doc_tipo: int) -> str:
    """Convierte tipo de documento numérico a nombre"""
    mapping = {
        80: "CUIT",
        96: "DNI",
        99: "CF",
        86: "CUIL",
    }
    return mapping.get(doc_tipo, f"T{doc_tipo}")


def _get_alicuota_principal(items: List[FacturaItem]) -> str:
    """Determina la alícuota principal (la de mayor monto de IVA)"""
    if not items:
        return "—"
    
    # Agrupar por alícuota
    alic_dict = {}
    for item in items:
        alic = float(item.alic_iva)
        iva_monto = float(item.iva_monto)
        if alic not in alic_dict:
            alic_dict[alic] = 0.0
        alic_dict[alic] += iva_monto
    
    if not alic_dict:
        return "—"
    
    # Obtener la alícuota con mayor monto
    max_alic = max(alic_dict.items(), key=lambda x: x[1])[0]
    
    if max_alic == 0.0:
        return "0%"
    elif max_alic == 10.5:
        return "10.5%"
    elif max_alic == 21.0:
        return "21%"
    elif max_alic == 27.0:
        return "27%"
    else:
        return f"{max_alic}%"


def _generate_csv(rows: List[Dict[str, Any]]) -> bytes:
    """Genera archivo CSV"""
    if not rows:
        return b""
    
    buffer = BytesIO()
    fieldnames = list(rows[0].keys())
    
    # Usar StringIO para CSV y luego convertir a bytes
    from io import StringIO
    string_buffer = StringIO()
    writer = csv.DictWriter(string_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    
    # Convertir a bytes
    csv_content = string_buffer.getvalue()
    buffer.write(csv_content.encode('utf-8-sig'))  # UTF-8 con BOM para Excel
    buffer.seek(0)
    
    return buffer.getvalue()


def _generate_xlsx(rows: List[Dict[str, Any]]) -> bytes:
    """Genera archivo XLSX"""
    if not rows:
        return b""
    
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
    except ImportError:
        raise ImportError("openpyxl no está instalado. Instalar con: pip install openpyxl")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Libro IVA Ventas"
    
    # Encabezado
    headers = list(rows[0].keys())
    ws.append(headers)
    
    # Aplicar estilo al encabezado
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Datos
    for row in rows:
        ws.append(list(row.values()))
    
    # Ajustar ancho de columnas
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Guardar en buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer.getvalue()

