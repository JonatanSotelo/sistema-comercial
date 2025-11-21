# tests/test_integrations_whatsapp.py
import pytest
import os
import sys
import uuid

# Agregar el directorio backend al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.core.settings import settings

# Crear cliente de test
test_client = TestClient(app)


@pytest.fixture
def whatsapp_token():
    """Token de integración para tests"""
    token = os.environ.get("WHATS_ORDERS_TOKEN", "test-token-123")
    # Configurar en settings si no está
    settings.WHATS_ORDERS_TOKEN = token
    return token


@pytest.fixture
def whatsapp_headers(whatsapp_token):
    """Headers con token de integración"""
    return {"X-Integration-Token": whatsapp_token}


def test_whats_orders_structured_ok_crea_venta(
    admin_token: str,
    whatsapp_headers
):
    """Test: cliente no existe → se crea → venta ok → stock baja → auditoría"""
    # Crear producto con stock (código único)
    unique_code = f"WHTEST{uuid.uuid4().hex[:6].upper()}"
    producto_data = {
        "nombre": "Producto WhatsApp Test",
        "codigo": unique_code,
        "categoria": "Test",
        "precio": 100.0,
        "costo": 50.0,
        "stock": 10
    }
    response = test_client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Pedido con cliente nuevo
    payload = {
        "phone": "5491100000000",
        "customer_name": "Cliente WhatsApp Test",
        "confirm": True,
        "items": [
            {
                "product_id": producto_id,
                "cantidad": 2
            }
        ]
    }
    
    response = test_client.post(
        "/integrations/whatsapp/orders",
        json=payload,
        headers=whatsapp_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "sale"
    assert "venta_id" in data
    assert data["total"] > 0
    
    # Verificar que el stock bajó
    response = test_client.get(f"/productos/{producto_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    producto = response.json()
    assert producto["stock"] == 8  # 10 - 2
    
    # Verificar auditoría (verificar que existe el log)
    # Nota: La auditoría se registra en la base de datos, pero no podemos acceder directamente
    # desde el test sin db session. Verificamos que la respuesta fue exitosa.


def test_whats_orders_quote_only(
    admin_token: str,
    whatsapp_headers
):
    """Test: confirm=false → no altera stock"""
    # Crear producto con stock (código único)
    unique_code = f"QUOTE{uuid.uuid4().hex[:6].upper()}"
    producto_data = {
        "nombre": "Producto Quote Test",
        "codigo": unique_code,
        "categoria": "Test",
        "precio": 100.0,
        "costo": 50.0,
        "stock": 10
    }
    response = test_client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear cliente
    cliente_data = {
        "nombre": "Cliente Quote",
        "telefono": "5491100000001"
    }
    response = test_client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    payload = {
        "phone": "5491100000001",
        "confirm": False,
        "items": [
            {
                "product_id": producto_id,
                "cantidad": 5
            }
        ]
    }
    
    response = test_client.post(
        "/integrations/whatsapp/orders",
        json=payload,
        headers=whatsapp_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "quote"
    assert "total" in data
    assert "items" in data
    
    # Verificar que el stock NO cambió
    response = test_client.get(f"/productos/{producto_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    producto = response.json()
    assert producto["stock"] == 10


def test_whats_orders_ambiguous(
    admin_token: str,
    whatsapp_headers
):
    """Test: query devuelve múltiples productos → 400 con sugerencias"""
    # Crear productos con nombres similares (códigos únicos)
    unique_code1 = f"BAT65{uuid.uuid4().hex[:4].upper()}"
    unique_code2 = f"BAT100{uuid.uuid4().hex[:4].upper()}"
    producto1_data = {
        "nombre": "Batería 12V 65Ah",
        "codigo": unique_code1,
        "categoria": "Baterías",
        "precio": 150000,
        "costo": 100000,
        "stock": 5
    }
    producto2_data = {
        "nombre": "Batería 12V 100Ah",
        "codigo": unique_code2,
        "categoria": "Baterías",
        "precio": 200000,
        "costo": 150000,
        "stock": 3
    }
    response = test_client.post("/productos", json=producto1_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    response = test_client.post("/productos", json=producto2_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    payload = {
        "phone": "5491100000000",
        "customer_name": "Cliente Ambiguo",
        "confirm": False,
        "items": [
            {
                "query": "bateria 12v",
                "cantidad": 1
            }
        ]
    }
    
    response = test_client.post(
        "/integrations/whatsapp/orders",
        json=payload,
        headers=whatsapp_headers
    )
    
    # Debería fallar con ambigüedad
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    # El detalle debería mencionar múltiples productos


def test_whats_orders_stock_409(
    admin_token: str,
    whatsapp_headers
):
    """Test: stock insuficiente → 409"""
    # Crear producto con stock limitado (código único)
    unique_code = f"STOCK{uuid.uuid4().hex[:6].upper()}"
    producto_data = {
        "nombre": "Producto Stock Limitado",
        "codigo": unique_code,
        "categoria": "Test",
        "precio": 100.0,
        "costo": 50.0,
        "stock": 2
    }
    response = test_client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    payload = {
        "phone": "5491100000000",
        "customer_name": "Cliente Stock",
        "confirm": True,
        "items": [
            {
                "product_id": producto_id,
                "cantidad": 5  # Más que el stock disponible
            }
        ]
    }
    
    response = test_client.post(
        "/integrations/whatsapp/orders",
        json=payload,
        headers=whatsapp_headers
    )
    
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert "Stock insuficiente" in str(data["detail"])


def test_whats_orders_auth_401(
    admin_token: str
):
    """Test: token inválido → 401"""
    # Crear producto (código único)
    unique_code = f"AUTH{uuid.uuid4().hex[:6].upper()}"
    producto_data = {
        "nombre": "Producto Auth Test",
        "codigo": unique_code,
        "categoria": "Test",
        "precio": 100.0,
        "costo": 50.0,
        "stock": 10
    }
    response = test_client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    payload = {
        "phone": "5491100000000",
        "customer_name": "Cliente Auth",
        "confirm": False,
        "items": [
            {
                "product_id": producto_id,
                "cantidad": 1
            }
        ]
    }
    
    # Sin token
    response = test_client.post(
        "/integrations/whatsapp/orders",
        json=payload
    )
    assert response.status_code == 401
    
    # Token incorrecto
    response = test_client.post(
        "/integrations/whatsapp/orders",
        json=payload,
        headers={"X-Integration-Token": "token-incorrecto"}
    )
    assert response.status_code == 401


def test_whats_orders_by_codigo(
    admin_token: str,
    whatsapp_headers
):
    """Test: resolver producto por código"""
    # Crear producto con código específico (código único)
    unique_code = f"TEST{uuid.uuid4().hex[:6].upper()}"
    producto_data = {
        "nombre": "Producto Código Test",
        "codigo": unique_code,
        "categoria": "Test",
        "precio": 100.0,
        "costo": 50.0,
        "stock": 10
    }
    response = test_client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_nombre = producto_data["nombre"]
    
    payload = {
        "phone": "5491100000000",
        "customer_name": "Cliente Código",
        "confirm": False,
        "items": [
            {
                "codigo": unique_code,
                "cantidad": 1
            }
        ]
    }
    
    response = test_client.post(
        "/integrations/whatsapp/orders",
        json=payload,
        headers=whatsapp_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "quote"
    assert len(data["items"]) == 1
    assert data["items"][0]["producto_nombre"] == producto_nombre

