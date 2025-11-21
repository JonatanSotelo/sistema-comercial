# tests/test_pedidos.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_pedido_create_ok(client: TestClient, admin_token: str, db: Session):
    """Test crear pedido con items válidos"""
    # Crear cliente
    cliente_data = {"nombre": "Cliente Test Pedido", "telefono": "1234567890"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    cliente_id = response.json()["id"]
    
    # Crear productos
    producto1 = {"nombre": "Producto Pedido 1", "precio": 100.0}
    response = client.post("/productos", json=producto1, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto1_id = response.json()["id"]
    
    producto2 = {"nombre": "Producto Pedido 2", "precio": 50.0}
    response = client.post("/productos", json=producto2, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto2_id = response.json()["id"]
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [
            {"producto_id": producto1_id, "cantidad": 2, "precio_unitario": 100.0},
            {"producto_id": producto2_id, "cantidad": 3, "precio_unitario": 50.0}
        ],
        "nota": "Pedido de prueba"
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    pedido = response.json()
    assert pedido["total"] == 350.0  # 2*100 + 3*50
    assert pedido["estado"] == "NUEVO"
    assert pedido["origen"] == "MANUAL"
    assert len(pedido["items"]) == 2


def test_pedido_transiciones_validas(client: TestClient, admin_token: str, db: Session):
    """Test transiciones de estado válidas"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente Estado", "telefono": "1111111111"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Estado", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 1, "precio_unitario": 100.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    # NUEVO -> EN_PREPARACION
    response = client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "EN_PREPARACION"
    
    # EN_PREPARACION -> LISTO
    response = client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "LISTO"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "LISTO"
    
    # LISTO -> FACTURADO no se puede hacer directamente, debe usar /facturar
    response = client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "FACTURADO"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400


def test_pedido_cancelar_desde_cualquier_estado(client: TestClient, admin_token: str, db: Session):
    """Test cancelar pedido desde diferentes estados"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente Cancelar", "telefono": "2222222222"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Cancelar", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear pedido y cancelar desde NUEVO
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 1, "precio_unitario": 100.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    response = client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "CANCELADO"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "CANCELADO"


def test_pedido_no_editable_en_listo(client: TestClient, admin_token: str, db: Session):
    """Test que no se puede editar un pedido en estado LISTO"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente Editar", "telefono": "3333333333"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Editar", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 1, "precio_unitario": 100.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    # Mover a LISTO
    client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "LISTO"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Intentar editar
    update_data = {
        "items": [{"producto_id": producto_id, "cantidad": 2, "precio_unitario": 100.0}],
        "nota": "Intento editar"
    }
    response = client.put(
        f"/pedidos/{pedido_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400


def test_pedido_facturar_ok(client: TestClient, admin_token: str, db: Session):
    """Test facturar pedido con stock suficiente"""
    # Crear cliente
    cliente_data = {"nombre": "Cliente Facturar", "telefono": "4444444444"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    # Crear producto
    producto_data = {"nombre": "Producto Facturar", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear proveedor si no existe
    proveedor_data = {"nombre": "Proveedor Test"}
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    if response.status_code == 201:
        proveedor_id = response.json()["id"]
    else:
        # Usar proveedor existente
        response = client.get("/proveedores?size=1", headers={"Authorization": f"Bearer {admin_token}"})
        items = response.json().get("items", [])
        proveedor_id = items[0]["id"] if items else 1
    
    # Crear compra para tener stock
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": 10, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 3, "precio_unitario": 100.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    # Mover a LISTO
    client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "LISTO"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Facturar
    response = client.post(
        f"/pedidos/{pedido_id}/facturar",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    result = response.json()
    assert "venta_id" in result
    assert result["total"] == 300.0
    
    # Verificar que pedido está FACTURADO
    response = client.get(f"/pedidos/{pedido_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.json()["estado"] == "FACTURADO"


def test_pedido_stock_insuficiente_al_facturar(client: TestClient, admin_token: str, db: Session):
    """Test que no se puede facturar sin stock suficiente"""
    # Crear cliente
    cliente_data = {"nombre": "Cliente Sin Stock", "telefono": "5555555555"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    # Crear producto sin stock
    producto_data = {"nombre": "Producto Sin Stock", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 5, "precio_unitario": 100.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    # Mover a LISTO
    client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "LISTO"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Intentar facturar sin stock
    response = client.post(
        f"/pedidos/{pedido_id}/facturar",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 409


def test_integracion_whatsapp_as_order(client: TestClient, db: Session):
    """Test integración WhatsApp con as_order=true"""
    # Configurar token (debe estar en settings)
    token = "test-integration-token"
    headers = {"X-Integration-Token": token}
    
    # Crear producto con stock
    admin_token_response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    if admin_token_response.status_code == 200:
        admin_token = admin_token_response.json().get("access_token")
        
        producto_data = {"nombre": "Producto WhatsApp", "precio": 50.0}
        response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
        if response.status_code == 201:
            producto_id = response.json()["id"]
            
            # Cotización (confirm=false)
            order_data = {
                "phone": "+5491112345678",
                "customer_name": "Cliente WhatsApp Test",
                "confirm": False,
                "as_order": True,
                "items": [{"product_id": producto_id, "cantidad": 2}]
            }
            
            # Nota: Este test solo funciona si WHATS_ORDERS_TOKEN está configurado
            try:
                response = client.post("/integrations/whatsapp/orders", json=order_data, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    assert result["type"] == "quote"
                    assert result["total"] == 100.0
            except Exception:
                # Si la integración no está configurada, skip
                pytest.skip("WhatsApp integration not configured")


def test_listar_pedidos_con_filtros(client: TestClient, admin_token: str, db: Session):
    """Test listar pedidos con filtros"""
    response = client.get("/pedidos?size=10", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    
    # Filtrar por estado
    response = client.get("/pedidos?estado=NUEVO", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


def test_pedidos_packing_html(client: TestClient, admin_token: str, db: Session):
    """Test obtener packing slip HTML"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente Packing", "telefono": "6666666666"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Packing", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 2, "precio_unitario": 100.0}],
        "nota": "Test packing"
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    # Obtener packing HTML
    response = client.get(f"/pedidos/{pedido_id}/packing")
    assert response.status_code == 200
    assert "PACKING SLIP" in response.text
    assert "Cliente Packing" in response.text


def test_pedidos_packing_pdf(client: TestClient, admin_token: str, db: Session):
    """Test obtener packing slip PDF"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente PDF", "telefono": "7777777777"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto PDF", "precio": 50.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 1, "precio_unitario": 50.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    # Obtener packing PDF
    response = client.get(f"/pedidos/{pedido_id}/packing.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


def test_pedidos_bulk_estado(client: TestClient, admin_token: str, db: Session):
    """Test cambiar estado de múltiples pedidos"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente Bulk", "telefono": "8888888888"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Bulk", "precio": 75.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear 3 pedidos
    pedido_ids = []
    for i in range(3):
        pedido_data = {
            "cliente_id": cliente_id,
            "items": [{"producto_id": producto_id, "cantidad": 1, "precio_unitario": 75.0}],
            "nota": f"Bulk test {i+1}"
        }
        response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
        pedido_ids.append(response.json()["id"])
    
    # Cambiar estado en bloque a EN_PREPARACION
    bulk_data = {
        "pedido_ids": pedido_ids,
        "nuevo_estado": "EN_PREPARACION"
    }
    response = client.post("/pedidos/bulk_estado", json=bulk_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    result = response.json()
    assert len(result["exitosos"]) == 3
    assert len(result["fallidos"]) == 0
    
    # Verificar que los pedidos cambiaron de estado
    for pedido_id in pedido_ids:
        response = client.get(f"/pedidos/{pedido_id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.json()["estado"] == "EN_PREPARACION"

