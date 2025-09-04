# tests/test_stock_completo.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_stock_inicial_vacio(client: TestClient, admin_token: str, db: Session):
    """Test que el stock inicial de un producto es 0"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Verificar stock inicial
    response = client.get(f"/stock/{producto_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    stock = response.json()
    assert stock["stock"] == 0.0

def test_stock_despues_compra(client: TestClient, admin_token: str, db: Session):
    """Test que el stock se incrementa después de una compra"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear proveedor
    proveedor_data = {
        "nombre": "Proveedor Test",
        "email": "proveedor@test.com"
    }
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    proveedor_id = response.json()["id"]
    
    # Crear compra
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": 10, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Verificar stock después de compra
    response = client.get(f"/stock/{producto_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    stock = response.json()
    assert stock["stock"] == 10.0

def test_stock_despues_venta(client: TestClient, admin_token: str, db: Session):
    """Test que el stock se decrementa después de una venta"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear proveedor y compra para tener stock
    proveedor_data = {"nombre": "Proveedor Test", "email": "proveedor@test.com"}
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    proveedor_id = response.json()["id"]
    
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": 10, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Verificar stock después de compra
    response = client.get(f"/stock/{producto_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    stock_inicial = response.json()["stock"]
    assert stock_inicial == 10.0
    
    # Crear venta
    venta_data = {
        "cliente_id": None,
        "items": [{"producto_id": producto_id, "cantidad": 3}]
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Verificar stock después de venta
    response = client.get(f"/stock/{producto_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    stock_final = response.json()["stock"]
    assert stock_final == 7.0  # 10 - 3

def test_stock_insuficiente_para_venta(client: TestClient, admin_token: str, db: Session):
    """Test que no se puede vender más stock del disponible"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear proveedor y compra para tener stock limitado
    proveedor_data = {"nombre": "Proveedor Test", "email": "proveedor@test.com"}
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    proveedor_id = response.json()["id"]
    
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": 5, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Intentar vender más stock del disponible
    venta_data = {
        "cliente_id": None,
        "items": [{"producto_id": producto_id, "cantidad": 10}]  # Más del disponible
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]

def test_stock_multiples_movimientos(client: TestClient, admin_token: str, db: Session):
    """Test stock con múltiples compras y ventas"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear proveedor
    proveedor_data = {"nombre": "Proveedor Test", "email": "proveedor@test.com"}
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    proveedor_id = response.json()["id"]
    
    # Primera compra: +10
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": 10, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Primera venta: -3
    venta_data = {
        "cliente_id": None,
        "items": [{"producto_id": producto_id, "cantidad": 3}]
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Segunda compra: +5
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": 5, "costo_unitario": 60.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Segunda venta: -2
    venta_data = {
        "cliente_id": None,
        "items": [{"producto_id": producto_id, "cantidad": 2}]
    }
    response = client.post("/ventas", json=venta_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    
    # Verificar stock final: 10 - 3 + 5 - 2 = 10
    response = client.get(f"/stock/{producto_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    stock_final = response.json()["stock"]
    assert stock_final == 10.0

def test_stock_producto_inexistente(client: TestClient, admin_token: str):
    """Test obtener stock de producto inexistente"""
    response = client.get("/stock/99999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404
