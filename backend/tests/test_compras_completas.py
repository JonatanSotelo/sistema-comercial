# tests/test_compras_completas.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_crear_compra_basica(client: TestClient, admin_token: str, db: Session):
    """Test crear compra básica"""
    # Crear proveedor
    proveedor_data = {
        "nombre": "Proveedor Test",
        "email": "proveedor@test.com"
    }
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    proveedor_id = response.json()["id"]
    
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Crear compra
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [
            {"producto_id": producto_id, "cantidad": 5, "costo_unitario": 50.0},
            {"producto_id": producto_id, "cantidad": 3, "costo_unitario": 60.0}
        ]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    compra = response.json()
    assert compra["total"] == 430.0  # (5*50) + (3*60)
    assert len(compra["items"]) == 2

def test_compra_con_producto_inexistente(client: TestClient, admin_token: str, db: Session):
    """Test que no se puede crear compra con producto inexistente"""
    # Crear proveedor
    proveedor_data = {
        "nombre": "Proveedor Test",
        "email": "proveedor@test.com"
    }
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    proveedor_id = response.json()["id"]
    
    # Intentar crear compra con producto inexistente
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": 99999, "cantidad": 5, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400
    assert "Producto 99999 no existe" in response.json()["detail"]

def test_compra_con_proveedor_inexistente(client: TestClient, admin_token: str, db: Session):
    """Test que no se puede crear compra con proveedor inexistente"""
    # Crear producto
    producto_data = {
        "nombre": "Producto Test",
        "descripcion": "Producto para test",
        "precio": 100.0
    }
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    producto_id = response.json()["id"]
    
    # Intentar crear compra con proveedor inexistente
    compra_data = {
        "proveedor_id": 99999,
        "items": [{"producto_id": producto_id, "cantidad": 5, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400
    assert "Proveedor no existe" in response.json()["detail"]

def test_compra_con_cantidad_negativa(client: TestClient, admin_token: str, db: Session):
    """Test que no se puede crear compra con cantidad negativa"""
    # Crear proveedor y producto
    proveedor_data = {"nombre": "Proveedor Test", "email": "proveedor@test.com"}
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    proveedor_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Test", "descripcion": "Test", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Intentar crear compra con cantidad negativa
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": -5, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400
    assert "Cantidad/costo inválidos" in response.json()["detail"]

def test_compra_con_costo_negativo(client: TestClient, admin_token: str, db: Session):
    """Test que no se puede crear compra con costo negativo"""
    # Crear proveedor y producto
    proveedor_data = {"nombre": "Proveedor Test", "email": "proveedor@test.com"}
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    proveedor_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Test", "descripcion": "Test", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    # Intentar crear compra con costo negativo
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": 5, "costo_unitario": -50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400
    assert "Cantidad/costo inválidos" in response.json()["detail"]

def test_obtener_compra(client: TestClient, admin_token: str, db: Session):
    """Test obtener compra por ID"""
    # Crear compra
    proveedor_data = {"nombre": "Proveedor Test", "email": "proveedor@test.com"}
    response = client.post("/proveedores", json=proveedor_data, headers={"Authorization": f"Bearer {admin_token}"})
    proveedor_id = response.json()["id"]
    
    producto_data = {"nombre": "Producto Test", "descripcion": "Test", "precio": 100.0}
    response = client.post("/productos", json=producto_data, headers={"Authorization": f"Bearer {admin_token}"})
    producto_id = response.json()["id"]
    
    compra_data = {
        "proveedor_id": proveedor_id,
        "items": [{"producto_id": producto_id, "cantidad": 5, "costo_unitario": 50.0}]
    }
    response = client.post("/compras", json=compra_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    compra_id = response.json()["id"]
    
    # Obtener compra
    response = client.get(f"/compras/{compra_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    compra = response.json()
    assert compra["id"] == compra_id
    assert compra["total"] == 250.0

def test_compra_inexistente(client: TestClient, admin_token: str):
    """Test obtener compra inexistente"""
    response = client.get("/compras/99999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404
