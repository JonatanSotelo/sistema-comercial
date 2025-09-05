# tests/test_descuentos.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.descuento_model import Descuento, TipoDescuento, EstadoDescuento

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Obtiene headers de autenticación para las pruebas"""
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_crear_descuento_porcentaje(auth_headers):
    """Test de creación de descuento por porcentaje"""
    descuento_data = {
        "codigo": "DESCUENTO10",
        "nombre": "Descuento del 10%",
        "descripcion": "Descuento del 10% en toda la compra",
        "tipo": "porcentaje",
        "valor": 10.0,
        "valor_minimo": 100.0,
        "fecha_inicio": datetime.utcnow().isoformat(),
        "fecha_fin": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "aplica_envio": False,
        "aplica_impuestos": True
    }
    
    response = client.post("/descuentos", json=descuento_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["codigo"] == "DESCUENTO10"
    assert data["tipo"] == "porcentaje"
    assert data["valor"] == 10.0
    assert data["estado"] == "activo"

def test_crear_descuento_monto_fijo(auth_headers):
    """Test de creación de descuento de monto fijo"""
    descuento_data = {
        "codigo": "DESCUENTO50",
        "nombre": "Descuento de $50",
        "descripcion": "Descuento fijo de $50",
        "tipo": "monto_fijo",
        "valor": 50.0,
        "valor_minimo": 200.0,
        "fecha_inicio": datetime.utcnow().isoformat(),
        "aplica_envio": False,
        "aplica_impuestos": True
    }
    
    response = client.post("/descuentos", json=descuento_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["codigo"] == "DESCUENTO50"
    assert data["tipo"] == "monto_fijo"
    assert data["valor"] == 50.0

def test_listar_descuentos(auth_headers):
    """Test de listado de descuentos"""
    response = client.get("/descuentos", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

def test_obtener_descuento_por_codigo(auth_headers):
    """Test de obtener descuento por código"""
    # Primero crear un descuento
    descuento_data = {
        "codigo": "TESTCODE",
        "nombre": "Test Descuento",
        "tipo": "porcentaje",
        "valor": 5.0,
        "fecha_inicio": datetime.utcnow().isoformat()
    }
    client.post("/descuentos", json=descuento_data, headers=auth_headers)
    
    # Luego obtenerlo por código
    response = client.get("/descuentos/codigo/TESTCODE", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["codigo"] == "TESTCODE"

def test_aplicar_descuento_valido(auth_headers):
    """Test de aplicación de descuento válido"""
    # Crear descuento
    descuento_data = {
        "codigo": "APLICAR10",
        "nombre": "Descuento Aplicable",
        "tipo": "porcentaje",
        "valor": 10.0,
        "valor_minimo": 50.0,
        "fecha_inicio": datetime.utcnow().isoformat()
    }
    client.post("/descuentos", json=descuento_data, headers=auth_headers)
    
    # Aplicar descuento
    aplicacion_data = {
        "codigo": "APLICAR10",
        "monto_total": 100.0,
        "productos_ids": [1, 2, 3],
        "cliente_id": 1
    }
    
    response = client.post("/descuentos/aplicar", json=aplicacion_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["aplicable"] == True
    assert data["monto_descuento"] == 10.0
    assert data["monto_final"] == 90.0

def test_aplicar_descuento_monto_insuficiente(auth_headers):
    """Test de aplicación de descuento con monto insuficiente"""
    # Crear descuento con monto mínimo
    descuento_data = {
        "codigo": "MINIMO100",
        "nombre": "Descuento Mínimo",
        "tipo": "porcentaje",
        "valor": 10.0,
        "valor_minimo": 100.0,
        "fecha_inicio": datetime.utcnow().isoformat()
    }
    client.post("/descuentos", json=descuento_data, headers=auth_headers)
    
    # Intentar aplicar con monto insuficiente
    aplicacion_data = {
        "codigo": "MINIMO100",
        "monto_total": 50.0,
        "productos_ids": [1, 2]
    }
    
    response = client.post("/descuentos/aplicar", json=aplicacion_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["aplicable"] == False
    assert "mínima" in data["mensaje"].lower()

def test_aplicar_descuento_expirado(auth_headers):
    """Test de aplicación de descuento expirado"""
    # Crear descuento expirado
    descuento_data = {
        "codigo": "EXPIRADO",
        "nombre": "Descuento Expirado",
        "tipo": "porcentaje",
        "valor": 10.0,
        "fecha_inicio": (datetime.utcnow() - timedelta(days=10)).isoformat(),
        "fecha_fin": (datetime.utcnow() - timedelta(days=1)).isoformat()
    }
    client.post("/descuentos", json=descuento_data, headers=auth_headers)
    
    # Intentar aplicar descuento expirado
    aplicacion_data = {
        "codigo": "EXPIRADO",
        "monto_total": 100.0,
        "productos_ids": [1, 2]
    }
    
    response = client.post("/descuentos/aplicar", json=aplicacion_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["aplicable"] == False
    assert "expirado" in data["mensaje"].lower()

def test_obtener_estadisticas_descuentos(auth_headers):
    """Test de estadísticas de descuentos"""
    response = client.get("/descuentos/estadisticas", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "total_descuentos" in data
    assert "descuentos_activos" in data
    assert "total_usos" in data
    assert "monto_total_descuentado" in data
    assert "descuentos_por_tipo" in data

def test_obtener_descuentos_disponibles(auth_headers):
    """Test de descuentos disponibles"""
    response = client.get("/descuentos/disponibles", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

def test_activar_descuento(auth_headers):
    """Test de activación de descuento"""
    # Crear descuento inactivo
    descuento_data = {
        "codigo": "INACTIVO",
        "nombre": "Descuento Inactivo",
        "tipo": "porcentaje",
        "valor": 10.0,
        "fecha_inicio": datetime.utcnow().isoformat(),
        "estado": "inactivo"
    }
    response = client.post("/descuentos", json=descuento_data, headers=auth_headers)
    descuento_id = response.json()["id"]
    
    # Activar descuento
    response = client.patch(f"/descuentos/{descuento_id}/activar", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["estado"] == "activo"
    assert data["es_activo"] == True

def test_desactivar_descuento(auth_headers):
    """Test de desactivación de descuento"""
    # Crear descuento activo
    descuento_data = {
        "codigo": "ACTIVO",
        "nombre": "Descuento Activo",
        "tipo": "porcentaje",
        "valor": 10.0,
        "fecha_inicio": datetime.utcnow().isoformat()
    }
    response = client.post("/descuentos", json=descuento_data, headers=auth_headers)
    descuento_id = response.json()["id"]
    
    # Desactivar descuento
    response = client.patch(f"/descuentos/{descuento_id}/desactivar", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["estado"] == "inactivo"
    assert data["es_activo"] == False

def test_actualizar_estados_descuentos(auth_headers):
    """Test de actualización de estados de descuentos"""
    response = client.post("/descuentos/actualizar-estados", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "actualizados" in data

def test_codigo_descuento_duplicado(auth_headers):
    """Test de código de descuento duplicado"""
    descuento_data = {
        "codigo": "DUPLICADO",
        "nombre": "Primer Descuento",
        "tipo": "porcentaje",
        "valor": 10.0,
        "fecha_inicio": datetime.utcnow().isoformat()
    }
    
    # Crear primer descuento
    response = client.post("/descuentos", json=descuento_data, headers=auth_headers)
    assert response.status_code == 200
    
    # Intentar crear segundo descuento con mismo código
    descuento_data["nombre"] = "Segundo Descuento"
    response = client.post("/descuentos", json=descuento_data, headers=auth_headers)
    assert response.status_code == 400
    assert "Ya existe" in response.json()["detail"]

def test_sin_autenticacion():
    """Test que los endpoints requieren autenticación"""
    response = client.get("/descuentos")
    assert response.status_code == 401

def test_crear_descuento_sin_permisos():
    """Test que crear descuentos requiere permisos de admin"""
    response = client.post("/descuentos", json={
        "codigo": "TEST",
        "nombre": "Test",
        "tipo": "porcentaje",
        "valor": 10.0,
        "fecha_inicio": datetime.utcnow().isoformat()
    })
    assert response.status_code == 401
