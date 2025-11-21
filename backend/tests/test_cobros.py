# tests/test_cobros.py
import pytest
from fastapi import status
from decimal import Decimal


def test_crear_cobro(client, db_session, create_test_user, create_test_cliente, create_test_producto):
    """Test crear cobro para una venta"""
    user = create_test_user()
    cliente = create_test_cliente()
    producto = create_test_producto()
    
    # Login
    response = client.post(
        "/token",
        data={"username": user.username, "password": "testpass"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear venta primero
    venta_data = {
        "cliente_id": cliente.id,
        "items": [
            {
                "producto_id": producto.id,
                "cantidad": 2,
                "precio_unitario": 100.0,
            }
        ],
        "total": 200.0,
    }
    response = client.post("/ventas", json=venta_data, headers=headers)
    assert response.status_code == 201
    venta_id = response.json()["id"]
    
    # Crear cobro
    cobro_data = {
        "venta_id": venta_id,
        "medio": "EFECTIVO",
        "importe": 100.0,
        "referencia": "Cobro de prueba",
        "observaciones": "Test",
    }
    response = client.post("/cobros", json=cobro_data, headers=headers)
    assert response.status_code == 201
    
    cobro = response.json()
    assert cobro["venta_id"] == venta_id
    assert cobro["medio"] == "EFECTIVO"
    assert float(cobro["importe"]) == 100.0
    assert cobro["estado"] == "CONFIRMADO"
    
    # Verificar saldo de venta
    response = client.get(f"/cobros/venta/{venta_id}/saldo", headers=headers)
    assert response.status_code == 200
    saldo_data = response.json()
    assert float(saldo_data["saldo"]) == 100.0  # 200 - 100


def test_multiples_cobros(client, db_session, create_test_user, create_test_cliente, create_test_producto):
    """Test múltiples cobros para una misma venta"""
    user = create_test_user()
    cliente = create_test_cliente()
    producto = create_test_producto()
    
    # Login
    response = client.post(
        "/token",
        data={"username": user.username, "password": "testpass"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear venta
    venta_data = {
        "cliente_id": cliente.id,
        "items": [{"producto_id": producto.id, "cantidad": 1, "precio_unitario": 500.0}],
        "total": 500.0,
    }
    response = client.post("/ventas", json=venta_data, headers=headers)
    venta_id = response.json()["id"]
    
    # Primer cobro
    response = client.post("/cobros", json={"venta_id": venta_id, "medio": "EFECTIVO", "importe": 200.0}, headers=headers)
    assert response.status_code == 201
    
    # Segundo cobro
    response = client.post("/cobros", json={"venta_id": venta_id, "medio": "TRANSFERENCIA", "importe": 150.0}, headers=headers)
    assert response.status_code == 201
    
    # Verificar saldo
    response = client.get(f"/cobros/venta/{venta_id}/saldo", headers=headers)
    saldo = float(response.json()["saldo"])
    assert saldo == 150.0  # 500 - 200 - 150


def test_anular_cobro(client, db_session, create_test_user, create_test_cliente, create_test_producto):
    """Test anular cobro y recalcular saldo"""
    user = create_test_user()
    cliente = create_test_cliente()
    producto = create_test_producto()
    
    # Login
    response = client.post(
        "/token",
        data={"username": user.username, "password": "testpass"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear venta
    venta_data = {
        "cliente_id": cliente.id,
        "items": [{"producto_id": producto.id, "cantidad": 1, "precio_unitario": 300.0}],
        "total": 300.0,
    }
    response = client.post("/ventas", json=venta_data, headers=headers)
    venta_id = response.json()["id"]
    
    # Crear cobro
    response = client.post("/cobros", json={"venta_id": venta_id, "medio": "EFECTIVO", "importe": 300.0}, headers=headers)
    cobro_id = response.json()["id"]
    
    # Verificar saldo antes de anular
    response = client.get(f"/cobros/venta/{venta_id}/saldo", headers=headers)
    assert float(response.json()["saldo"]) == 0.0
    
    # Anular cobro
    response = client.post(f"/cobros/{cobro_id}/anular", headers=headers)
    assert response.status_code == 200
    
    # Verificar saldo después de anular
    response = client.get(f"/cobros/venta/{venta_id}/saldo", headers=headers)
    assert float(response.json()["saldo"]) == 300.0


def test_recibo_pdf(client, db_session, create_test_user, create_test_cliente, create_test_producto):
    """Test generar PDF de recibo"""
    user = create_test_user()
    cliente = create_test_cliente()
    producto = create_test_producto()
    
    # Login
    response = client.post(
        "/token",
        data={"username": user.username, "password": "testpass"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear venta
    venta_data = {
        "cliente_id": cliente.id,
        "items": [{"producto_id": producto.id, "cantidad": 1, "precio_unitario": 100.0}],
        "total": 100.0,
    }
    response = client.post("/ventas", json=venta_data, headers=headers)
    venta_id = response.json()["id"]
    
    # Crear cobro
    response = client.post("/cobros", json={"venta_id": venta_id, "medio": "EFECTIVO", "importe": 100.0}, headers=headers)
    cobro_id = response.json()["id"]
    
    # Descargar PDF
    response = client.get(f"/cobros/{cobro_id}/pdf", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0  # PDF no vacío


def test_saldo_cliente(client, db_session, create_test_user, create_test_cliente, create_test_producto):
    """Test saldo total de un cliente"""
    user = create_test_user()
    cliente = create_test_cliente()
    producto = create_test_producto()
    
    # Login
    response = client.post(
        "/token",
        data={"username": user.username, "password": "testpass"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear 2 ventas
    venta_data = {
        "cliente_id": cliente.id,
        "items": [{"producto_id": producto.id, "cantidad": 1, "precio_unitario": 100.0}],
        "total": 100.0,
    }
    response1 = client.post("/ventas", json=venta_data, headers=headers)
    venta1_id = response1.json()["id"]
    
    response2 = client.post("/ventas", json={**venta_data, "total": 200.0}, headers=headers)
    venta2_id = response2.json()["id"]
    
    # Crear 1 cobro para la primera venta
    client.post("/cobros", json={"venta_id": venta1_id, "medio": "EFECTIVO", "importe": 50.0}, headers=headers)
    
    # Verificar saldo del cliente
    response = client.get(f"/clientes/{cliente.id}/saldo", headers=headers)
    assert response.status_code == 200
    saldo = float(response.json()["saldo"])
    assert saldo == 250.0  # (100 - 50) + 200


def test_libro_iva_compras_crud(client, db_session, create_test_user):
    """Test CRUD de Libro IVA Compras"""
    user = create_test_user()
    
    # Login
    response = client.post(
        "/token",
        data={"username": user.username, "password": "testpass"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear registro
    data = {
        "proveedor_nombre": "Proveedor Test",
        "fecha": "2025-01-15",
        "tipo_cbte": 6,  # B
        "pto_vta": 1,
        "nro_cbte": 123,
        "doc_tipo": 80,
        "doc_nro": "20123456789",
        "imp_neto": 100.0,
        "imp_iva": 21.0,
        "imp_exento": 0.0,
        "imp_total": 121.0,
        "alicuota_principal": 21.0,
        "moneda": "ARS",
        "cotiz": 1.0,
    }
    
    response = client.post("/iva-compras", json=data, headers=headers)
    assert response.status_code == 201
    registro_id = response.json()["id"]
    
    # Leer
    response = client.get("/iva-compras", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Actualizar
    data_update = {**data, "imp_neto": 150.0, "imp_iva": 31.5, "imp_total": 181.5}
    response = client.put(f"/iva-compras/{registro_id}", json=data_update, headers=headers)
    assert response.status_code == 200
    
    # Eliminar
    response = client.delete(f"/iva-compras/{registro_id}", headers=headers)
    assert response.status_code == 204


def test_libro_iva_compras_export(client, db_session, create_test_user):
    """Test exportación Libro IVA Compras"""
    user = create_test_user()
    
    # Login
    response = client.post(
        "/token",
        data={"username": user.username, "password": "testpass"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear registro
    data = {
        "proveedor_nombre": "Proveedor Test",
        "fecha": "2025-01-15",
        "tipo_cbte": 6,
        "pto_vta": 1,
        "nro_cbte": 456,
        "doc_tipo": 80,
        "doc_nro": "20987654321",
        "imp_neto": 200.0,
        "imp_iva": 42.0,
        "imp_exento": 0.0,
        "imp_total": 242.0,
        "alicuota_principal": 21.0,
        "moneda": "ARS",
        "cotiz": 1.0,
    }
    client.post("/iva-compras", json=data, headers=headers)
    
    # Export CSV
    response = client.get("/reportes/libro-iva-compras?desde=2025-01-01&hasta=2025-12-31&format=csv", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    assert len(response.content) > 0

