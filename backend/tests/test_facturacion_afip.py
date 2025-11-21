# tests/test_facturacion_afip.py
"""
Tests para facturación electrónica AFIP
Mockea las llamadas a WSAA y WSFEv1
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.venta_model import Venta, VentaItem
from app.models.cliente_model import Cliente
from app.models.producto_model import Producto
from app.models.factura_model import Factura
from app.services.facturacion_service import emitir_factura, generar_qr_json


# Fixtures
@pytest.fixture
def cliente_ri(db: Session):
    """Cliente Responsable Inscripto"""
    cliente = Cliente(
        nombre="Empresa Test SA",
        cuit="20123456789",
        condicion_iva="RI",
        doc_tipo=80,
        doc_nro="20123456789",
        direccion="Calle Falsa 123"
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@pytest.fixture
def cliente_cf(db: Session):
    """Cliente Consumidor Final"""
    cliente = Cliente(
        nombre="Juan Pérez",
        condicion_iva="CF",
        doc_tipo=96,
        doc_nro="12345678"
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@pytest.fixture
def producto_test(db: Session):
    """Producto de prueba"""
    producto = Producto(
        nombre="Producto Test",
        precio=100.0,
        costo=50.0,
        stock=100,
        codigo="TEST001",
        categoria="Test"
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@pytest.fixture
def venta_ri(db: Session, cliente_ri, producto_test):
    """Venta a Responsable Inscripto"""
    venta = Venta(
        cliente_id=cliente_ri.id,
        total=121.0  # $100 + 21% IVA
    )
    db.add(venta)
    db.flush()
    
    item = VentaItem(
        venta_id=venta.id,
        producto_id=producto_test.id,
        cantidad=1.0,
        precio_unitario=100.0,
        subtotal=100.0
    )
    db.add(item)
    db.commit()
    db.refresh(venta)
    return venta


@pytest.fixture
def venta_cf(db: Session, cliente_cf, producto_test):
    """Venta a Consumidor Final"""
    venta = Venta(
        cliente_id=cliente_cf.id,
        total=121.0
    )
    db.add(venta)
    db.flush()
    
    item = VentaItem(
        venta_id=venta.id,
        producto_id=producto_test.id,
        cantidad=1.0,
        precio_unitario=121.0,  # Precio final con IVA
        subtotal=121.0
    )
    db.add(item)
    db.commit()
    db.refresh(venta)
    return venta


# Tests
def test_emitir_factura_b_consumidor_final_ok(db: Session, venta_cf):
    """Test: Emitir Factura B a Consumidor Final exitosamente"""
    with patch('app.services.facturacion_service.WSFEv1Client') as mock_wsfev1:
        # Mock del cliente AFIP
        mock_client = MagicMock()
        mock_wsfev1.return_value = mock_client
        
        # Mock de la respuesta exitosa de AFIP
        mock_client.fe_cae_solicitar.return_value = {
            "success": True,
            "resultado": "A",
            "cae": "12345678901234",
            "cae_vto": "20251231",
            "nro_cbte": 1,
            "obs": None
        }
        
        # Emitir factura B (6)
        factura = emitir_factura(
            db=db,
            venta_id=venta_cf.id,
            tipo_cbte=6,  # B
            pto_vta=1
        )
        
        # Verificaciones
        assert factura is not None
        assert factura.venta_id == venta_cf.id
        assert factura.tipo_cbte == 6
        assert factura.cae == "12345678901234"
        assert factura.resultado == "A"
        assert factura.nro_cbte == 1
        
        # Verificar que se llamó al servicio AFIP
        mock_client.fe_cae_solicitar.assert_called_once()


def test_emitir_factura_a_ri_ok(db: Session, venta_ri):
    """Test: Emitir Factura A a Responsable Inscripto exitosamente"""
    with patch('app.services.facturacion_service.WSFEv1Client') as mock_wsfev1:
        mock_client = MagicMock()
        mock_wsfev1.return_value = mock_client
        
        mock_client.fe_cae_solicitar.return_value = {
            "success": True,
            "resultado": "A",
            "cae": "98765432109876",
            "cae_vto": "20251231",
            "nro_cbte": 2,
            "obs": None
        }
        
        # Emitir factura A (1)
        factura = emitir_factura(
            db=db,
            venta_id=venta_ri.id,
            tipo_cbte=1,  # A
            pto_vta=1
        )
        
        # Verificaciones
        assert factura is not None
        assert factura.tipo_cbte == 1
        assert factura.doc_tipo == 80  # CUIT
        assert factura.cae == "98765432109876"
        assert float(factura.imp_neto) > 0
        assert float(factura.imp_iva) > 0


def test_qr_payload_ok(db: Session, venta_cf):
    """Test: Generar payload QR AFIP con campos obligatorios"""
    with patch('app.services.facturacion_service.WSFEv1Client') as mock_wsfev1:
        mock_client = MagicMock()
        mock_wsfev1.return_value = mock_client
        
        mock_client.fe_cae_solicitar.return_value = {
            "success": True,
            "resultado": "A",
            "cae": "11111111111111",
            "cae_vto": "20251231",
            "nro_cbte": 3,
            "obs": None
        }
        
        factura = emitir_factura(db=db, venta_id=venta_cf.id, tipo_cbte=6)
        
        # Verificar que se generó el QR JSON
        assert factura.qr_json is not None
        qr = factura.qr_json
        
        # Verificar campos obligatorios del QR AFIP
        assert qr["ver"] == 1
        assert "fecha" in qr
        assert "cuit" in qr
        assert qr["ptoVta"] == 1
        assert qr["tipoCmp"] == 6
        assert "nroCmp" in qr
        assert "importe" in qr
        assert qr["moneda"] == "PES"
        assert "tipoDocRec" in qr
        assert "nroDocRec" in qr
        assert qr["tipoCodAut"] == "E"
        assert qr["codAut"] == "11111111111111"


def test_pdf_nonempty(db: Session, venta_cf):
    """Test: PDF de factura genera bytes no vacíos"""
    with patch('app.services.facturacion_service.WSFEv1Client') as mock_wsfev1:
        mock_client = MagicMock()
        mock_wsfev1.return_value = mock_client
        
        mock_client.fe_cae_solicitar.return_value = {
            "success": True,
            "resultado": "A",
            "cae": "44444444444444",
            "cae_vto": "20251231",
            "nro_cbte": 4,
            "obs": None
        }
        
        factura = emitir_factura(db=db, venta_id=venta_cf.id, tipo_cbte=6)
        
        # Generar PDF
        from app.services.factura_pdf_service import generate_factura_pdf
        pdf_bytes = generate_factura_pdf(db, factura.id)
        
        # Verificar que el PDF no está vacío
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000  # Un PDF válido debería tener al menos 1KB


def test_error_afip_auditoria(db: Session, venta_cf):
    """Test: Errores de AFIP se registran en auditoría"""
    with patch('app.services.facturacion_service.WSFEv1Client') as mock_wsfev1:
        mock_client = MagicMock()
        mock_wsfev1.return_value = mock_client
        
        # Mock de respuesta rechazada por AFIP
        mock_client.fe_cae_solicitar.return_value = {
            "success": False,
            "resultado": "R",
            "obs": "Error: Datos inválidos"
        }
        
        # Intentar emitir factura (debería fallar)
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            emitir_factura(db=db, venta_id=venta_cf.id, tipo_cbte=6)
        
        # Verificar que se registró el error
        assert "Error AFIP" in str(exc_info.value.detail)


def test_sin_venta_ni_pedido_error(db: Session):
    """Test: Error si no se especifica venta_id ni pedido_id"""
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        emitir_factura(db=db, venta_id=None, pedido_id=None, tipo_cbte=6)
    
    assert exc_info.value.status_code == 400
    assert "venta_id o pedido_id" in str(exc_info.value.detail).lower()

