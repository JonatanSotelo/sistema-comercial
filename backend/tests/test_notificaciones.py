# tests/test_notificaciones.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.notificacion_model import Notificacion, TipoNotificacion, EstadoNotificacion

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Obtiene headers de autenticación para las pruebas"""
    # Login para obtener token
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_crear_notificacion(auth_headers):
    """Test de creación de notificación"""
    notificacion_data = {
        "titulo": "Test de notificación",
        "mensaje": "Esta es una notificación de prueba",
        "tipo": "info",
        "es_urgente": False,
        "requiere_accion": False
    }
    
    response = client.post("/notificaciones", json=notificacion_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["titulo"] == "Test de notificación"
    assert data["mensaje"] == "Esta es una notificación de prueba"
    assert data["tipo"] == "info"
    assert data["estado"] == "pendiente"

def test_listar_notificaciones(auth_headers):
    """Test de listado de notificaciones"""
    response = client.get("/notificaciones", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

def test_obtener_resumen_notificaciones(auth_headers):
    """Test de resumen de notificaciones"""
    response = client.get("/notificaciones/resumen", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "pendientes" in data
    assert "leidas" in data
    assert "urgentes" in data
    assert "por_tipo" in data

def test_obtener_estadisticas_notificaciones(auth_headers):
    """Test de estadísticas de notificaciones"""
    response = client.get("/notificaciones/estadisticas", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "total_notificaciones" in data
    assert "notificaciones_hoy" in data
    assert "notificaciones_semana" in data
    assert "notificaciones_mes" in data
    assert "tasa_lectura" in data

def test_obtener_pendientes(auth_headers):
    """Test de notificaciones pendientes"""
    response = client.get("/notificaciones/pendientes", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

def test_obtener_urgentes(auth_headers):
    """Test de notificaciones urgentes"""
    response = client.get("/notificaciones/urgentes", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

def test_crear_notificacion_stock_bajo(auth_headers):
    """Test de creación de notificación de stock bajo"""
    response = client.post(
        "/notificaciones/stock-bajo",
        params={
            "producto_id": 1,
            "producto_nombre": "Producto Test",
            "stock_actual": 5.0,
            "stock_minimo": 10.0
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["tipo"] == "stock_bajo"
    assert data["es_urgente"] == True
    assert data["requiere_accion"] == True

def test_crear_notificacion_venta_importante(auth_headers):
    """Test de creación de notificación de venta importante"""
    response = client.post(
        "/notificaciones/venta-importante",
        params={
            "venta_id": 1,
            "monto": 15000.0,
            "cliente_nombre": "Cliente Test"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["tipo"] == "venta_importante"
    assert data["es_urgente"] == True  # > 10000

def test_crear_notificacion_sistema(auth_headers):
    """Test de creación de notificación del sistema"""
    response = client.post(
        "/notificaciones/sistema",
        params={
            "titulo": "Mantenimiento programado",
            "mensaje": "El sistema estará en mantenimiento mañana",
            "es_urgente": False
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["tipo"] == "sistema"
    assert data["titulo"] == "Mantenimiento programado"

def test_marcar_como_leida(auth_headers):
    """Test de marcar notificación como leída"""
    # Primero crear una notificación
    notificacion_data = {
        "titulo": "Test para marcar como leída",
        "mensaje": "Esta notificación será marcada como leída",
        "tipo": "info"
    }
    
    response = client.post("/notificaciones", json=notificacion_data, headers=auth_headers)
    assert response.status_code == 200
    notificacion_id = response.json()["id"]
    
    # Marcar como leída
    response = client.patch(f"/notificaciones/{notificacion_id}/leer", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data

def test_filtros_notificaciones(auth_headers):
    """Test de filtros en notificaciones"""
    # Crear notificaciones de diferentes tipos
    tipos = ["info", "warning", "error"]
    for tipo in tipos:
        notificacion_data = {
            "titulo": f"Test {tipo}",
            "mensaje": f"Notificación de tipo {tipo}",
            "tipo": tipo
        }
        client.post("/notificaciones", json=notificacion_data, headers=auth_headers)
    
    # Filtrar por tipo
    response = client.get("/notificaciones?tipo=info", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    for notif in data:
        assert notif["tipo"] == "info"

def test_sin_autenticacion():
    """Test que los endpoints requieren autenticación"""
    response = client.get("/notificaciones")
    assert response.status_code == 401

def test_crear_notificacion_sin_permisos():
    """Test que crear notificaciones requiere permisos de admin"""
    # Crear usuario normal (esto requeriría implementar registro de usuarios)
    # Por ahora solo verificamos que el endpoint existe
    response = client.post("/notificaciones", json={
        "titulo": "Test",
        "mensaje": "Test",
        "tipo": "info"
    })
    assert response.status_code == 401
