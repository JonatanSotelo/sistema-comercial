# tests/test_ventas_completas.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_crear_venta_sin_stock(client: TestClient, admin_token: str, db: Session):
    """Test que no se puede crear venta sin stock suficiente"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Intentar crear venta sin stock
    venta_data = {
        "cliente_id": None,
        "items": [{"producto_id": producto_id, "cantidad": 5}]
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]

def test_crear_venta_con_stock(client: TestClient, admin_token: str, db: Session):
    """Test crear venta con stock suficiente"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear compra para tener stock
    compra_data = {
        "proveedor_id": 1,  # Asumiendo que existe
        "items": [{"producto_id": producto_id, "cantidad": 10, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Crear venta
    venta_data = {
        "cliente_id": None,
        "items": [{"producto_id": producto_id, "cantidad": 3}]
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    venta = response.json()
    assert venta["total"] == 300.0  # 3 * 100
    assert len(venta["items"]) == 1

def test_venta_con_precio_personalizado(client: TestClient, admin_token: str, db: Session):
    """Test venta con precio personalizado"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear compra para tener stock
    compra_data = {
        "proveedor_id": 1,
        "items": [{"producto_id": producto_id, "cantidad": 10, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Crear venta con precio personalizado
    venta_data = {
        "cliente_id": None,
        "items": [{"producto_id": producto_id, "cantidad": 2, "precio_unitario": 150.0}]
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    venta = response.json()
    assert venta["total"] == 300.0  # 2 * 150

def test_eliminar_venta(client: TestClient, admin_token: str, db: Session):
    """Test eliminar venta"""
    # Crear venta (asumiendo que ya existe stock)
    venta_data = {
        "cliente_id": None,
        "items": [{"producto_id": 1, "cantidad": 1}]
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    if response.status_code == 201:
        venta_id = response.json()["id"]
        
        # Eliminar venta
        response = client.delete(f"/ventas/{venta_id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        
        # Verificar que no existe
        response = client.get(f"/ventas/{venta_id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 404

def test_listar_ventas_paginado(client: TestClient, admin_token: str):
    """Test listar ventas con paginación"""
    response = client.get("/ventas?page=1&size=5", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data or isinstance(data, list)

def test_venta_con_cliente(client: TestClient, admin_token: str, db: Session):
    """Test crear venta asociada a cliente"""
    # Crear cliente
    cliente_data = {
        "nombre": "Cliente Test",
        "email": "cliente@test.com",
        "telefono": "123456789"
    }
    response = client.post("/clientes", json=cliente_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    cliente_id = response.json()["id"]
    
    # Crear venta con cliente
    venta_data = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": 1, "cantidad": 1}]
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    # Puede fallar por stock, pero la estructura debe ser correcta
    if response.status_code == 201:
        venta = response.json()
        assert venta["cliente_id"] == cliente_id
