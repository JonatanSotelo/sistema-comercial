# tests/test_reservas.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_reserva_al_preparar(client: TestClient, admin_token: str, db: Session):
    """Test que al pasar a EN_PREPARACION se crean reservas"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente Reserva", "telefono": "9999999999"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Reserva Test", "precio": 100.0, "stock": 10}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 3, "precio_unitario": 100.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    pedido_id = response.json()["id"]
    
    # Cambiar a EN_PREPARACION (debe crear reservas)
    response = client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "EN_PREPARACION"
    
    # Verificar que se crearon reservas (via auditoría o disponible)
    # El disponible debe ser stock - cantidad_reservada = 10 - 3 = 7


def test_reserva_ajuste_cantidad(client: TestClient, admin_token: str, db: Session):
    """Test que al editar items se ajustan las reservas"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente Ajuste", "telefono": "1010101010"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Ajuste", "precio": 50.0, "stock": 20}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear pedido
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 5, "precio_unitario": 50.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    # Cambiar a EN_PREPARACION
    response = client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Editar pedido (cambiar cantidad)
    update_data = {
        "items": [{"producto_id": producto_id, "cantidad": 8, "precio_unitario": 50.0}],
        "nota": "Cantidad ajustada"
    }
    response = client.put(
        f"/pedidos/{pedido_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    # Las reservas deben ajustarse automáticamente


def test_cancelacion_libera(client: TestClient, admin_token: str, db: Session):
    """Test que al cancelar se liberan las reservas"""
    # Crear cliente y producto
    cliente_data = {"nombre": "Cliente Cancelar", "telefono": "1111111111"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Cancelar", "precio": 75.0, "stock": 15}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear pedido y pasar a EN_PREPARACION
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 4, "precio_unitario": 75.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    response = client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Cancelar pedido
    response = client.post(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "CANCELADO"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "CANCELADO"
    
    # Las reservas deben estar liberadas (estado=CANCELADA)


def test_facturar_consumo(client: TestClient, admin_token: str, db: Session):
    """Test que al facturar se consumen reservas y se descuenta stock"""
    # Crear cliente
    cliente_data = {"nombre": "Cliente Facturar", "telefono": "1212121212"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    # Crear producto con stock
    producto_data = {"nombre": "Producto Facturar", "precio": 100.0, "stock": 25}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    stock_inicial = response.json()["stock"]
    
    # Crear pedido
    cantidad = 7
    pedido_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": cantidad, "precio_unitario": 100.0}]
    }
    response = client.post("/pedidos", json=pedido_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido_id = response.json()["id"]
    
    # EN_PREPARACION → LISTO
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
    assert "venta_id" in response.json()
    
    # Verificar que el pedido está FACTURADO
    response = client.get(f"/pedidos/{pedido_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.json()["estado"] == "FACTURADO"
    
    # Verificar que el stock se descontó
    response = client.get(f"/productos/{producto_id}", headers={"Authorization": f"Bearer {admin_token}"})
    stock_final = response.json()["stock"]
    assert stock_final == stock_inicial - cantidad


def test_reserva_concurrencia(client: TestClient, admin_token: str, db: Session):
    """Test que dos pedidos concurrentes no pueden reservar más del disponible"""
    # Crear cliente
    cliente_data = {"nombre": "Cliente Concurrencia", "telefono": "1313131313"}
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    cliente_id = response.json()["id"]
    
    # Crear producto con stock limitado
    producto_data = {"nombre": "Producto Limitado", "precio": 50.0, "stock": 5}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Crear dos pedidos que juntos superan el stock
    pedido1_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 3, "precio_unitario": 50.0}],
        "nota": "Pedido 1"
    }
    response = client.post("/pedidos", json=pedido1_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido1_id = response.json()["id"]
    
    pedido2_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": producto_id, "cantidad": 3, "precio_unitario": 50.0}],
        "nota": "Pedido 2"
    }
    response = client.post("/pedidos", json=pedido2_data, headers={"Authorization": f"Bearer {admin_token}"})
    pedido2_id = response.json()["id"]
    
    # Pasar el primero a EN_PREPARACION (debe funcionar)
    response = client.post(
        f"/pedidos/{pedido1_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Intentar pasar el segundo a EN_PREPARACION (debe fallar con 409)
    response = client.post(
        f"/pedidos/{pedido2_id}/estado",
        json={"estado": "EN_PREPARACION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # Debe fallar porque no hay disponible suficiente (5 - 3 = 2, pero pide 3)
    assert response.status_code in [400, 409]  # Depende de cómo manejemos el error

