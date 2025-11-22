# app/services/facturacion_service.py
"""
Servicio de facturación electrónica AFIP
Emite facturas A/B/C desde ventas/pedidos
"""

import base64
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.models.factura_model import Factura, FacturaItem, TipoComprobante, TipoDocumento, ConceptoFactura
from app.models.venta_model import Venta
from app.models.pedido_model import Pedido
from app.models.cliente_model import Cliente
from app.models.auditoria import AuditAction
from app.services.auditoria_service import create_audit_log, get_client_ip
from app.services.afip_wsfe_client import WSFEv1Client
from app.core.config import settings


def emitir_factura(
    db: Session,
    venta_id: Optional[int] = None,
    pedido_id: Optional[int] = None,
    tipo_cbte: int = 6,  # Default: B
    pto_vta: Optional[int] = None,
    user: Optional[Any] = None,
    request: Optional[Request] = None,
) -> Factura:
    """
    Emite una factura electrónica AFIP desde una venta o pedido.
    
    Args:
        db: Sesión de base de datos
        venta_id: ID de la venta (al menos uno de venta_id o pedido_id requerido)
        pedido_id: ID del pedido
        tipo_cbte: Tipo de comprobante (1=A, 6=B, 11=C)
        pto_vta: Punto de venta (default: config)
        user: Usuario que emite
        request: Request object para auditoría
    
    Returns:
        Factura creada con CAE
    """
    if not venta_id and not pedido_id:
        raise HTTPException(status_code=400, detail="Debe especificar venta_id o pedido_id")
    
    if not pto_vta:
        pto_vta = settings.FACTURA_PTO_VTA
    
    # Obtener la venta o pedido
    venta = None
    pedido = None
    if venta_id:
        venta = db.query(Venta).options(
            joinedload(Venta.cliente),
            joinedload(Venta.items)
        ).filter(Venta.id == venta_id).first()
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    if pedido_id:
        pedido = db.query(Pedido).options(
            joinedload(Pedido.cliente),
            joinedload(Pedido.items)
        ).filter(Pedido.id == pedido_id).first()
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Determinar origen de datos (priorizar venta)
    origen = venta if venta else pedido
    cliente = origen.cliente
    items = origen.items
    total = float(origen.total)
    
    # Validar cliente
    if not cliente:
        raise HTTPException(status_code=400, detail="La venta/pedido debe tener un cliente asociado")
    
    # Determinar tipo de documento del cliente
    doc_tipo, doc_nro = _determinar_documento_cliente(cliente, tipo_cbte)
    
    # Calcular importes según tipo de factura
    imp_neto, imp_iva, imp_exento, iva_alics = _calcular_importes(items, tipo_cbte)
    imp_total = imp_neto + imp_iva + imp_exento
    
    # Validar que el total coincida (permitir diferencia de redondeo)
    if abs(imp_total - total) > 0.01:
        print(f"[FACTURACION] Advertencia: Total calculado ({imp_total}) difiere del total de origen ({total})")
    
    try:
        # Solicitar CAE a AFIP
        afip_client = WSFEv1Client()
        fecha_cbte = datetime.now().strftime("%Y%m%d")
        
        response = afip_client.fe_cae_solicitar(
            pto_vta=pto_vta,
            tipo_cbte=tipo_cbte,
            concepto=ConceptoFactura.PRODUCTOS.value,
            doc_tipo=doc_tipo,
            doc_nro=doc_nro,
            fecha_cbte=fecha_cbte,
            imp_total=imp_total,
            imp_tot_conc=0.0,  # No gravado
            imp_neto=imp_neto,
            imp_op_ex=imp_exento,
            imp_trib=0.0,  # Tributos
            imp_iva=imp_iva,
            moneda_id="PES",
            moneda_ctz=1.0,
            iva_alics=iva_alics if tipo_cbte in [1, 6] else None,  # Solo A/B tienen IVA discriminado
        )
        
        if not response.get("success"):
            # Error al solicitar CAE
            obs = response.get("obs", "Error desconocido")
            _log_factura_error(db, venta_id, pedido_id, tipo_cbte, obs, user, request)
            raise HTTPException(status_code=500, detail=f"Error AFIP: {obs}")
        
        # CAE obtenido exitosamente
        cae = response["cae"]
        cae_vto = response["cae_vto"]
        nro_cbte = response["nro_cbte"]
        resultado = response["resultado"]
        obs = response.get("obs")
        
        # Crear registro de factura
        factura = Factura(
            venta_id=venta_id,
            pedido_id=pedido_id,
            tipo_cbte=tipo_cbte,
            pto_vta=pto_vta,
            nro_cbte=nro_cbte,
            concepto=ConceptoFactura.PRODUCTOS.value,
            doc_tipo=doc_tipo,
            doc_nro=doc_nro,
            imp_neto=Decimal(str(imp_neto)),
            imp_iva=Decimal(str(imp_iva)),
            imp_total=Decimal(str(imp_total)),
            imp_exento=Decimal(str(imp_exento)),
            moneda=settings.FACTURA_MONEDA,
            cotiz=Decimal(str(settings.FACTURA_COTIZACION)),
            cae=cae,
            cae_vto=cae_vto,
            resultado=resultado,
            obs=obs,
            qr_json=None,  # Se genera después
        )
        db.add(factura)
        db.flush()  # Para obtener factura.id
        
        # Crear ítems de factura
        for item in items:
            producto = item.producto if hasattr(item, 'producto') else None
            descripcion = producto.nombre if producto else f"Ítem #{item.id}"
            cantidad = float(item.cantidad)
            precio_unit = float(item.precio_unitario)
            
            # Determinar alícuota de IVA (default 21%)
            # En producción, esto debería venir del producto
            alic_iva = 21.0 if tipo_cbte in [1, 6] else 0.0  # C no discrimina IVA
            
            subtotal = cantidad * precio_unit
            if tipo_cbte in [1, 6]:  # A o B
                # Subtotal es neto, calcular IVA
                iva_monto = subtotal * (alic_iva / 100)
            else:  # C
                # Subtotal ya incluye IVA
                iva_monto = 0.0
            
            factura_item = FacturaItem(
                factura_id=factura.id,
                producto_id=producto.id if producto else None,
                descripcion=descripcion,
                cantidad=Decimal(str(cantidad)),
                precio_unitario=Decimal(str(precio_unit)),
                alic_iva=Decimal(str(alic_iva)),
                subtotal=Decimal(str(subtotal)),
                iva_monto=Decimal(str(iva_monto)),
            )
            db.add(factura_item)
        
        # Generar QR AFIP
        qr_json = generar_qr_json(factura)
        factura.qr_json = qr_json
        
        # Auditoría
        try:
            create_audit_log(
                db,
                user_id=getattr(user, "id", None) if user else None,
                username=getattr(user, "username", None) if user else None,
                table_name="facturacion",
                action=AuditAction.CREATE,
                record_id=str(factura.id),
                details={
                    "tipo_cbte": tipo_cbte,
                    "pto_vta": pto_vta,
                    "nro_cbte": nro_cbte,
                    "cae": cae,
                    "cae_vto": cae_vto,
                    "imp_total": float(imp_total),
                    "venta_id": venta_id,
                    "pedido_id": pedido_id,
                },
                path=request.url.path if request else None,
                method=request.method if request else None,
                ip=get_client_ip(request) if request else None,
            )
        except Exception as e:
            print(f"[auditoria] Error al registrar factura: {e}")
        
        db.commit()
        db.refresh(factura)
        return factura
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"[FACTURACION] Error al emitir factura: {e}")
        raise HTTPException(status_code=500, detail=f"Error al emitir factura: {str(e)}")


def _determinar_documento_cliente(cliente: Cliente, tipo_cbte: int) -> tuple:
    """
    Determina el tipo y número de documento del cliente según el tipo de factura.
    
    Args:
        cliente: Cliente de la factura
        tipo_cbte: Tipo de comprobante (1=A, 6=B, 11=C)
    
    Returns:
        Tupla (doc_tipo, doc_nro)
    """
    # Para Factura C a Consumidor Final
    if tipo_cbte == 11:  # C
        return TipoDocumento.CONSUMIDOR_FINAL.value, "0"
    
    # Para Factura A/B, intentar usar datos del cliente
    if cliente.doc_tipo and cliente.doc_nro:
        return cliente.doc_tipo, cliente.doc_nro
    
    # Si tiene CUIT, usar CUIT
    if cliente.cuit:
        return TipoDocumento.CUIT.value, cliente.cuit.replace("-", "")
    
    # Default: Consumidor Final
    return TipoDocumento.CONSUMIDOR_FINAL.value, "0"


def _calcular_importes(items: list, tipo_cbte: int) -> tuple:
    """
    Calcula los importes de la factura según el tipo de comprobante.
    
    Args:
        items: Lista de ítems de venta/pedido
        tipo_cbte: Tipo de comprobante (1=A, 6=B, 11=C)
    
    Returns:
        Tupla (imp_neto, imp_iva, imp_exento, iva_alics)
    """
    imp_neto = 0.0
    imp_iva = 0.0
    imp_exento = 0.0
    iva_alics_dict = {}  # {alic_id: {"base": 0, "importe": 0}}
    
    for item in items:
        cantidad = float(item.cantidad)
        precio_unit = float(item.precio_unitario)
        subtotal = cantidad * precio_unit
        
        # Determinar alícuota de IVA
        # En producción, esto debería venir del producto
        alic_iva = 21.0  # Default 21%
        alic_id = _get_alic_id(alic_iva)
        
        if tipo_cbte == 11:  # C
            # Factura C: el precio ya incluye IVA, no se discrimina
            imp_neto += subtotal
            imp_iva += 0.0
        else:  # A o B
            # Facturas A/B: IVA discriminado
            imp_neto += subtotal
            iva_monto = subtotal * (alic_iva / 100)
            imp_iva += iva_monto
            
            # Acumular por alícuota
            if alic_id not in iva_alics_dict:
                iva_alics_dict[alic_id] = {"base": 0.0, "importe": 0.0}
            iva_alics_dict[alic_id]["base"] += subtotal
            iva_alics_dict[alic_id]["importe"] += iva_monto
    
    # Convertir iva_alics_dict a lista para AFIP
    iva_alics = []
    for alic_id, data in iva_alics_dict.items():
        iva_alics.append({
            "id": alic_id,
            "base_imponible": data["base"],
            "importe": data["importe"],
        })
    
    return imp_neto, imp_iva, imp_exento, iva_alics


def _get_alic_id(alic_iva: float) -> int:
    """Convierte alícuota de IVA a ID de AFIP"""
    mapping = {
        0.0: 3,
        10.5: 4,
        21.0: 5,
        27.0: 6,
    }
    return mapping.get(alic_iva, 5)  # Default: 21%


def generar_qr_json(factura: Factura) -> dict:
    """
    Genera el JSON del QR AFIP según especificación oficial.
    
    URL: https://www.afip.gob.ar/fe/qr/?p=<base64url(json)>
    
    Args:
        factura: Factura a generar QR
    
    Returns:
        Dict con los datos del QR
    """
    qr_data = {
        "ver": 1,
        "fecha": factura.created_at.strftime("%Y-%m-%d"),
        "cuit": int(settings.AFIP_CUIT),
        "ptoVta": factura.pto_vta,
        "tipoCmp": factura.tipo_cbte,
        "nroCmp": factura.nro_cbte,
        "importe": float(factura.imp_total),
        "moneda": "PES",
        "ctz": 1,
        "tipoDocRec": factura.doc_tipo,
        "nroDocRec": int(factura.doc_nro) if (factura.doc_nro and factura.doc_nro.isdigit()) else 0,
        "tipoCodAut": "E",
        "codAut": factura.cae,
    }
    return qr_data


def _log_factura_error(
    db: Session,
    venta_id: Optional[int],
    pedido_id: Optional[int],
    tipo_cbte: int,
    error_msg: str,
    user: Optional[Any],
    request: Optional[Request],
):
    """Registra error de facturación en auditoría"""
    try:
        from app.services.auditoria_service import create_audit_log, get_client_ip
        create_audit_log(
            db,
            user_id=getattr(user, "id", None) if user else None,
            username=getattr(user, "username", None) if user else None,
            table_name="facturacion",
            action=AuditAction.ERROR,
            record_id=str(venta_id or pedido_id),
            details={
                "tipo_cbte": tipo_cbte,
                "error": error_msg,
                "venta_id": venta_id,
                "pedido_id": pedido_id,
            },
            path=request.url.path if request else None,
            method=request.method if request else None,
            ip=get_client_ip(request) if request else None,
        )
        db.commit()
    except Exception as e:
        print(f"[auditoria] Error al registrar error de factura: {e}")

