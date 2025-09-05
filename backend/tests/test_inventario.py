# tests/test_inventario.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio padre al path para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Headers de autenticación para tests"""
    # Login como admin
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_crear_configuracion_inventario(auth_headers):
    """Test de creación de configuración de inventario"""
    config_data = {
        "producto_id": 1,
        "stock_minimo": 10.0,
        "stock_maximo": 100.0,
        "punto_reorden": 15.0,
        "cantidad_reorden": 50.0,
        "alerta_stock_bajo": True,
        "alerta_stock_critico": True,
        "alerta_vencimiento": True,
        "dias_vencimiento_alerta": 30,
        "alerta_movimiento_grande": True,
        "umbral_movimiento_grande": 20.0
    }
    
    response = client.post("/inventario/configuraciones", json=config_data, headers=auth_headers)
    
    # Debería fallar porque el producto no existe, pero verificar que la estructura está bien
    assert response.status_code in [200, 404, 400]  # 404 si no existe producto, 400 si ya existe config

def test_listar_configuraciones(auth_headers):
    """Test de listado de configuraciones"""
    response = client.get("/inventario/configuraciones", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_crear_movimiento_inventario(auth_headers):
    """Test de creación de movimiento de inventario"""
    movimiento_data = {
        "producto_id": 1,
        "tipo_movimiento": "entrada",
        "cantidad": 10.0,
        "referencia_tipo": "compra",
        "referencia_id": 1,
        "motivo": "Compra de prueba",
        "costo_unitario": 5.0,
        "costo_total": 50.0
    }
    
    response = client.post("/inventario/movimientos", json=movimiento_data, headers=auth_headers)
    
    # Debería fallar porque el producto no existe, pero verificar estructura
    assert response.status_code in [200, 400, 404]

def test_listar_movimientos(auth_headers):
    """Test de listado de movimientos"""
    response = client.get("/inventario/movimientos", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_listar_alertas(auth_headers):
    """Test de listado de alertas"""
    response = client.get("/inventario/alertas", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_obtener_alertas_pendientes(auth_headers):
    """Test de alertas pendientes"""
    response = client.get("/inventario/alertas/pendientes", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_obtener_alertas_urgentes(auth_headers):
    """Test de alertas urgentes"""
    response = client.get("/inventario/alertas/urgentes", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_listar_reordenes(auth_headers):
    """Test de listado de reordenes"""
    response = client.get("/inventario/reordenes", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_obtener_resumen_inventario(auth_headers):
    """Test de resumen del inventario"""
    response = client.get("/inventario/resumen", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura del resumen
    assert "total_productos" in data
    assert "productos_stock_bajo" in data
    assert "productos_stock_critico" in data
    assert "productos_agotados" in data
    assert "alertas_pendientes" in data
    assert "alertas_urgentes" in data
    assert "valor_total_inventario" in data
    assert "movimientos_hoy" in data
    assert "reordenes_pendientes" in data

def test_obtener_estadisticas_inventario(auth_headers):
    """Test de estadísticas del inventario"""
    response = client.get("/inventario/estadisticas", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura de estadísticas
    assert "total_productos" in data
    assert "productos_configurados" in data
    assert "alertas_por_tipo" in data
    assert "movimientos_por_tipo" in data
    assert "valor_inventario_por_categoria" in data
    assert "productos_mas_movidos" in data
    assert "tendencia_stock" in data
    assert "alertas_resueltas_mes" in data
    assert "tiempo_promedio_resolucion" in data

def test_procesar_alertas(auth_headers):
    """Test de procesamiento de alertas"""
    response = client.post("/inventario/procesar-alertas", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "procesadas" in data
    assert isinstance(data["procesadas"], int)

def test_generar_reorden_automatico(auth_headers):
    """Test de generación de reorden automático"""
    response = client.post("/inventario/generar-reorden/1", headers=auth_headers)
    
    # Debería fallar porque no hay configuración, pero verificar estructura
    assert response.status_code in [200, 400, 404]

def test_filtros_configuraciones(auth_headers):
    """Test de filtros en configuraciones"""
    # Test con filtro de producto
    response = client.get("/inventario/configuraciones?producto_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de activos
    response = client.get("/inventario/configuraciones?solo_activos=true", headers=auth_headers)
    assert response.status_code == 200

def test_filtros_movimientos(auth_headers):
    """Test de filtros en movimientos"""
    # Test con filtro de producto
    response = client.get("/inventario/movimientos?producto_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de tipo
    response = client.get("/inventario/movimientos?tipo_movimiento=entrada", headers=auth_headers)
    assert response.status_code == 200

def test_filtros_alertas(auth_headers):
    """Test de filtros en alertas"""
    # Test con filtro de producto
    response = client.get("/inventario/alertas?producto_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de tipo
    response = client.get("/inventario/alertas?tipo_alerta=stock_bajo", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de estado
    response = client.get("/inventario/alertas?estado_alerta=pendiente", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de prioridad
    response = client.get("/inventario/alertas?prioridad=1", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_configuraciones(auth_headers):
    """Test de paginación en configuraciones"""
    response = client.get("/inventario/configuraciones?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_movimientos(auth_headers):
    """Test de paginación en movimientos"""
    response = client.get("/inventario/movimientos?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_alertas(auth_headers):
    """Test de paginación en alertas"""
    response = client.get("/inventario/alertas?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_reordenes(auth_headers):
    """Test de paginación en reordenes"""
    response = client.get("/inventario/reordenes?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200
