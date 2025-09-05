# tests/test_dashboard.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.venta_model import Venta, VentaItem
from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.models.compra_model import StockMovimiento

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Obtiene headers de autenticación para las pruebas"""
    # Login para obtener token
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_dashboard_ventas_resumen(auth_headers):
    """Test del endpoint de resumen de ventas"""
    response = client.get("/dashboard/ventas/resumen", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "total_ventas" in data
    assert "total_monto" in data
    assert "promedio_venta" in data
    assert "venta_mayor" in data
    assert "venta_menor" in data
    assert "ventas_hoy" in data
    assert "monto_hoy" in data

def test_dashboard_ventas_periodo(auth_headers):
    """Test del endpoint de ventas por período"""
    response = client.get("/dashboard/ventas/periodo?periodo=dia&limite=7", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Si hay datos, verificar estructura
    if data:
        item = data[0]
        assert "periodo" in item
        assert "cantidad_ventas" in item
        assert "monto_total" in item
        assert "promedio" in item

def test_dashboard_productos_mas_vendidos(auth_headers):
    """Test del endpoint de productos más vendidos"""
    response = client.get("/dashboard/productos/mas-vendidos?limite=5", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Si hay datos, verificar estructura
    if data:
        item = data[0]
        assert "producto_id" in item
        assert "producto_nombre" in item
        assert "cantidad_vendida" in item
        assert "monto_total" in item
        assert "ventas_count" in item

def test_dashboard_clientes_top(auth_headers):
    """Test del endpoint de clientes top"""
    response = client.get("/dashboard/clientes/top?limite=5", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Si hay datos, verificar estructura
    if data:
        item = data[0]
        assert "cliente_id" in item
        assert "cliente_nombre" in item
        assert "cantidad_ventas" in item
        assert "monto_total" in item
        assert "promedio_compra" in item

def test_dashboard_stock_bajo(auth_headers):
    """Test del endpoint de stock bajo"""
    response = client.get("/dashboard/stock/bajo?stock_minimo=5.0", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Si hay datos, verificar estructura
    if data:
        item = data[0]
        assert "producto_id" in item
        assert "producto_nombre" in item
        assert "stock_actual" in item
        assert "stock_minimo" in item
        assert "diferencia" in item
        assert "porcentaje" in item

def test_dashboard_metricas(auth_headers):
    """Test del endpoint de métricas de rendimiento"""
    response = client.get("/dashboard/metricas", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "ventas_ultimo_mes" in data
    assert "crecimiento_ventas" in data
    assert "productos_activos" in data
    assert "clientes_activos" in data
    assert "ticket_promedio" in data
    assert "conversion_rate" in data

def test_dashboard_tendencias(auth_headers):
    """Test del endpoint de tendencias de ventas"""
    response = client.get("/dashboard/tendencias?dias=14", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Si hay datos, verificar estructura
    if data:
        item = data[0]
        assert "fecha" in item
        assert "ventas" in item
        assert "monto" in item
        assert "crecimiento_diario" in item

def test_dashboard_completo(auth_headers):
    """Test del endpoint de dashboard completo"""
    response = client.get("/dashboard/completo", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "resumen_ventas" in data
    assert "ventas_por_periodo" in data
    assert "productos_mas_vendidos" in data
    assert "clientes_top" in data
    assert "stock_bajo" in data
    assert "metricas" in data
    assert "tendencias" in data
    assert "ultima_actualizacion" in data

def test_dashboard_ventas_estadisticas(auth_headers):
    """Test del endpoint de estadísticas detalladas"""
    response = client.get("/dashboard/ventas/estadisticas", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "resumen" in data
    assert "productos_destacados" in data
    assert "clientes_destacados" in data
    assert "tendencias" in data
    assert "filtros_aplicados" in data

def test_dashboard_sin_autenticacion():
    """Test que los endpoints requieren autenticación"""
    response = client.get("/dashboard/ventas/resumen")
    assert response.status_code == 401

def test_dashboard_periodo_invalido(auth_headers):
    """Test de período inválido"""
    response = client.get("/dashboard/ventas/periodo?periodo=invalido", headers=auth_headers)
    assert response.status_code == 400
    assert "Período debe ser" in response.json()["detail"]

def test_dashboard_filtros_fecha(auth_headers):
    """Test con filtros de fecha"""
    fecha_inicio = (date.today() - timedelta(days=30)).isoformat()
    fecha_fin = date.today().isoformat()
    
    response = client.get(
        f"/dashboard/ventas/resumen?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "total_ventas" in data
    assert "total_monto" in data
