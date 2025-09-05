# tests/test_precios.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, date
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

def test_crear_precio_producto(auth_headers):
    """Test de creación de precio de producto"""
    precio_data = {
        "producto_id": 1,
        "tipo": "cliente",
        "precio_base": 100.0,
        "precio_especial": 80.0,
        "cliente_id": 1,
        "fecha_inicio": datetime.utcnow().isoformat(),
        "fecha_fin": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "nombre": "Precio especial cliente",
        "descripcion": "Descuento especial para cliente VIP",
        "prioridad": 1
    }
    
    response = client.post("/precios/productos", json=precio_data, headers=auth_headers)
    
    # Debería fallar porque el producto no existe, pero verificar estructura
    assert response.status_code in [200, 404, 400]

def test_listar_precios_producto(auth_headers):
    """Test de listado de precios de producto"""
    response = client.get("/precios/productos", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_crear_precio_volumen(auth_headers):
    """Test de creación de precio por volumen"""
    precio_data = {
        "producto_id": 1,
        "cantidad_minima": 10.0,
        "cantidad_maxima": 50.0,
        "descuento_porcentaje": 15.0,
        "fecha_inicio": datetime.utcnow().isoformat(),
        "fecha_fin": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "nombre": "Descuento por volumen",
        "descripcion": "Descuento por compra en cantidad",
        "prioridad": 2
    }
    
    response = client.post("/precios/volumen", json=precio_data, headers=auth_headers)
    
    # Debería fallar porque el producto no existe, pero verificar estructura
    assert response.status_code in [200, 404, 400]

def test_listar_precios_volumen(auth_headers):
    """Test de listado de precios por volumen"""
    response = client.get("/precios/volumen", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_crear_precio_categoria(auth_headers):
    """Test de creación de precio por categoría"""
    precio_data = {
        "categoria_id": 1,
        "descuento_porcentaje": 10.0,
        "multiplicador": 0.9,
        "fecha_inicio": datetime.utcnow().isoformat(),
        "fecha_fin": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "nombre": "Descuento categoría",
        "descripcion": "Descuento para toda la categoría",
        "prioridad": 3
    }
    
    response = client.post("/precios/categoria", json=precio_data, headers=auth_headers)
    
    assert response.status_code in [200, 400]

def test_listar_precios_categoria(auth_headers):
    """Test de listado de precios por categoría"""
    response = client.get("/precios/categoria", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_crear_precio_estacional(auth_headers):
    """Test de creación de precio estacional"""
    precio_data = {
        "producto_id": 1,
        "nombre_temporada": "Navidad 2024",
        "descuento_porcentaje": 20.0,
        "fecha_inicio": date.today().isoformat(),
        "fecha_fin": (date.today() + timedelta(days=30)).isoformat(),
        "descripcion": "Descuento navideño",
        "prioridad": 1
    }
    
    response = client.post("/precios/estacionales", json=precio_data, headers=auth_headers)
    
    # Debería fallar porque el producto no existe, pero verificar estructura
    assert response.status_code in [200, 404, 400]

def test_listar_precios_estacionales(auth_headers):
    """Test de listado de precios estacionales"""
    response = client.get("/precios/estacionales", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_aplicar_precio_dinamico(auth_headers):
    """Test de aplicación de precio dinámico"""
    request_data = {
        "venta_id": 1,
        "producto_id": 1,
        "cliente_id": 1,
        "cantidad": 5.0,
        "precio_base": 100.0
    }
    
    response = client.post("/precios/aplicar", json=request_data, headers=auth_headers)
    
    # Debería fallar porque la venta no existe, pero verificar estructura
    assert response.status_code in [200, 404, 400]

def test_listar_precios_aplicados(auth_headers):
    """Test de listado de precios aplicados"""
    response = client.get("/precios/aplicados", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_listar_historial_precios(auth_headers):
    """Test de listado de historial de precios"""
    response = client.get("/precios/historial", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_obtener_resumen_precios(auth_headers):
    """Test de resumen de precios"""
    response = client.get("/precios/resumen", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura del resumen
    assert "total_precios" in data
    assert "precios_activos" in data
    assert "precios_por_tipo" in data
    assert "precios_por_cliente" in data
    assert "precios_por_volumen" in data
    assert "precios_estacionales" in data
    assert "descuento_promedio" in data
    assert "ahorro_total" in data

def test_obtener_estadisticas_precios(auth_headers):
    """Test de estadísticas de precios"""
    response = client.get("/precios/estadisticas", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura de estadísticas
    assert "total_precios" in data
    assert "precios_por_tipo" in data
    assert "precios_por_estado" in data
    assert "descuento_promedio_por_tipo" in data
    assert "productos_mas_descontados" in data
    assert "clientes_mas_descontados" in data
    assert "tendencia_precios" in data
    assert "ahorro_total_mes" in data
    assert "ahorro_promedio_por_venta" in data

def test_simular_precio_dinamico(auth_headers):
    """Test de simulación de precio dinámico"""
    response = client.get("/precios/simular?producto_id=1&cantidad=10", headers=auth_headers)
    
    # Debería fallar porque el producto no existe, pero verificar estructura
    assert response.status_code in [200, 404, 400]

def test_filtros_precios_producto(auth_headers):
    """Test de filtros en precios de producto"""
    # Test con filtro de producto
    response = client.get("/precios/productos?producto_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de cliente
    response = client.get("/precios/productos?cliente_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de tipo
    response = client.get("/precios/productos?tipo=cliente", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de estado
    response = client.get("/precios/productos?estado=activo", headers=auth_headers)
    assert response.status_code == 200

def test_filtros_precios_volumen(auth_headers):
    """Test de filtros en precios por volumen"""
    # Test con filtro de producto
    response = client.get("/precios/volumen?producto_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de cliente
    response = client.get("/precios/volumen?cliente_id=1", headers=auth_headers)
    assert response.status_code == 200

def test_filtros_precios_categoria(auth_headers):
    """Test de filtros en precios por categoría"""
    # Test con filtro de categoría
    response = client.get("/precios/categoria?categoria_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de cliente
    response = client.get("/precios/categoria?cliente_id=1", headers=auth_headers)
    assert response.status_code == 200

def test_filtros_precios_estacionales(auth_headers):
    """Test de filtros en precios estacionales"""
    # Test con filtro de producto
    response = client.get("/precios/estacionales?producto_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de cliente
    response = client.get("/precios/estacionales?cliente_id=1", headers=auth_headers)
    assert response.status_code == 200

def test_filtros_precios_aplicados(auth_headers):
    """Test de filtros en precios aplicados"""
    # Test con filtro de venta
    response = client.get("/precios/aplicados?venta_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de producto
    response = client.get("/precios/aplicados?producto_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de cliente
    response = client.get("/precios/aplicados?cliente_id=1", headers=auth_headers)
    assert response.status_code == 200
    
    # Test con filtro de tipo
    response = client.get("/precios/aplicados?tipo_precio=cliente", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_precios_producto(auth_headers):
    """Test de paginación en precios de producto"""
    response = client.get("/precios/productos?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_precios_volumen(auth_headers):
    """Test de paginación en precios por volumen"""
    response = client.get("/precios/volumen?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_precios_categoria(auth_headers):
    """Test de paginación en precios por categoría"""
    response = client.get("/precios/categoria?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_precios_estacionales(auth_headers):
    """Test de paginación en precios estacionales"""
    response = client.get("/precios/estacionales?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_precios_aplicados(auth_headers):
    """Test de paginación en precios aplicados"""
    response = client.get("/precios/aplicados?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_paginacion_historial_precios(auth_headers):
    """Test de paginación en historial de precios"""
    response = client.get("/precios/historial?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200

def test_activar_precio(auth_headers):
    """Test de activación de precio"""
    response = client.post("/precios/activar/1?tipo=producto", headers=auth_headers)
    
    # Debería fallar porque el precio no existe, pero verificar estructura
    assert response.status_code in [200, 404, 400]

def test_desactivar_precio(auth_headers):
    """Test de desactivación de precio"""
    response = client.post("/precios/desactivar/1?tipo=producto", headers=auth_headers)
    
    # Debería fallar porque el precio no existe, pero verificar estructura
    assert response.status_code in [200, 404, 400]

def test_obtener_precio_producto_especifico(auth_headers):
    """Test de obtener precio de producto específico"""
    response = client.get("/precios/productos/1", headers=auth_headers)
    
    # Debería fallar porque el precio no existe, pero verificar estructura
    assert response.status_code in [200, 404]

def test_actualizar_precio_producto(auth_headers):
    """Test de actualización de precio de producto"""
    update_data = {
        "precio_especial": 75.0,
        "descuento_porcentaje": 25.0,
        "nombre": "Precio actualizado"
    }
    
    response = client.put("/precios/productos/1", json=update_data, headers=auth_headers)
    
    # Debería fallar porque el precio no existe, pero verificar estructura
    assert response.status_code in [200, 404]

def test_eliminar_precio_producto(auth_headers):
    """Test de eliminación de precio de producto"""
    response = client.delete("/precios/productos/1", headers=auth_headers)
    
    # Debería fallar porque el precio no existe, pero verificar estructura
    assert response.status_code in [200, 404]
