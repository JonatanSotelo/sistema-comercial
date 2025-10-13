# backend/tests/test_metricas_rendimiento.py
import sys
import os
import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.database import get_db
from app.models.user_model import User
from app.models.metricas_rendimiento_model import MetricaRendimiento, MedicionMetrica, AlertaMetrica

client = TestClient(app)

# Datos de prueba
test_user_data = {
    "username": "test_admin",
    "email": "admin@test.com",
    "password": "testpassword123",
    "role": "admin"
}

test_metrica_data = {
    "nombre": "Ventas Mensuales",
    "codigo": "VENTAS_MENSUALES",
    "descripcion": "Métrica de ventas mensuales",
    "tipo_metrica": "ventas",
    "categoria": "crecimiento",
    "subcategoria": "ingresos",
    "tipo_calculo": "suma",
    "formula": "SUM(ventas.total)",
    "unidad_medida": "pesos",
    "decimales": 2,
    "frecuencia_medicion": "mensual",
    "fuente_datos": "tabla_ventas",
    "valor_objetivo": 200000.0,
    "valor_minimo": 100000.0,
    "valor_maximo": 500000.0,
    "rango_optimo_inicio": 150000.0,
    "rango_optimo_fin": 300000.0
}

def get_auth_headers():
    """Obtiene headers de autenticación para las pruebas"""
    # Crear usuario de prueba
    response = client.post("/auth/register", json=test_user_data)
    if response.status_code != 201:
        # Si el usuario ya existe, hacer login
        response = client.post("/auth/login", data={"username": test_user_data["username"], "password": test_user_data["password"]})
    
    # Verificar que la respuesta sea exitosa
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Si falla, usar un token de prueba
        return {"Authorization": "Bearer test_token"}

class TestMetricasRendimiento:
    
    def test_crear_metrica(self):
        """Test crear una métrica de rendimiento"""
        headers = get_auth_headers()
        response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == test_metrica_data["nombre"]
        assert data["codigo"] == test_metrica_data["codigo"].upper()
        assert data["tipo_metrica"] == test_metrica_data["tipo_metrica"]
        assert data["categoria"] == test_metrica_data["categoria"]
        assert "id" in data
    
    def test_listar_metricas(self):
        """Test listar métricas de rendimiento"""
        headers = get_auth_headers()
        response = client.get("/metricas-rendimiento/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_obtener_metrica(self):
        """Test obtener una métrica específica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Obtener la métrica
        response = client.get(f"/metricas-rendimiento/{metrica_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == metrica_id
        assert data["nombre"] == test_metrica_data["nombre"]
    
    def test_actualizar_metrica(self):
        """Test actualizar una métrica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Actualizar la métrica
        update_data = {
            "nombre": "Ventas Mensuales Actualizadas",
            "descripcion": "Descripción actualizada"
        }
        response = client.put(f"/metricas-rendimiento/{metrica_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Ventas Mensuales Actualizadas"
        assert data["descripcion"] == "Descripción actualizada"
    
    def test_eliminar_metrica(self):
        """Test eliminar una métrica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Eliminar la métrica
        response = client.delete(f"/metricas-rendimiento/{metrica_id}", headers=headers)
        
        assert response.status_code == 200
        assert "eliminada" in response.json()["message"]
    
    def test_calcular_medicion(self):
        """Test calcular una medición de métrica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Calcular medición
        response = client.post(
            f"/metricas-rendimiento/{metrica_id}/mediciones",
            params={
                "fecha_medicion": datetime.utcnow().isoformat(),
                "periodo_desde": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "periodo_hasta": datetime.utcnow().isoformat()
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "valor_actual" in data
        assert "fecha_medicion" in data
        assert "tendencia" in data
        assert "variacion_porcentual" in data
    
    def test_listar_mediciones(self):
        """Test listar mediciones de una métrica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Calcular una medición
        client.post(f"/metricas-rendimiento/{metrica_id}/mediciones", headers=headers)
        
        # Listar mediciones
        response = client.get(f"/metricas-rendimiento/{metrica_id}/mediciones", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_crear_alerta(self):
        """Test crear una alerta para una métrica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Crear alerta
        alerta_data = {
            "nombre": "Alerta Ventas Bajas",
            "descripcion": "Alerta cuando las ventas están por debajo del objetivo",
            "tipo_alerta": "umbral",
            "condicion": "valor < umbral_minimo",
            "umbral_minimo": 150000.0,
            "notificar_email": True,
            "notificar_dashboard": True,
            "frecuencia_verificacion": "diaria"
        }
        
        response = client.post(f"/metricas-rendimiento/{metrica_id}/alertas", json=alerta_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == alerta_data["nombre"]
        assert data["tipo_alerta"] == alerta_data["tipo_alerta"]
        assert data["umbral_minimo"] == alerta_data["umbral_minimo"]
    
    def test_listar_alertas(self):
        """Test listar alertas de una métrica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Crear una alerta
        alerta_data = {
            "nombre": "Alerta Test",
            "tipo_alerta": "umbral",
            "condicion": "valor < umbral_minimo",
            "umbral_minimo": 100000.0
        }
        client.post(f"/metricas-rendimiento/{metrica_id}/alertas", json=alerta_data, headers=headers)
        
        # Listar alertas
        response = client.get(f"/metricas-rendimiento/{metrica_id}/alertas", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_obtener_dashboard_ejecutivo(self):
        """Test obtener dashboard ejecutivo"""
        headers = get_auth_headers()
        response = client.get("/metricas-rendimiento/dashboard-ejecutivo", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "ingresos_mes" in data
        assert "ingresos_anio" in data
        assert "crecimiento_ingresos" in data
        assert "margen_bruto" in data
        assert "margen_neto" in data
        assert "ventas_mes" in data
        assert "clientes_activos" in data
        assert "tendencia_ingresos" in data
        assert "tendencia_ventas" in data
        assert "recomendaciones" in data
        assert "fecha_actualizacion" in data
    
    def test_obtener_resumen_metricas(self):
        """Test obtener resumen de métricas"""
        headers = get_auth_headers()
        response = client.get("/metricas-rendimiento/resumen", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_metricas" in data
        assert "metricas_activas" in data
        assert "metricas_inactivas" in data
        assert "total_mediciones" in data
        assert "mediciones_mes_actual" in data
        assert "total_alertas" in data
        assert "alertas_activas" in data
        assert "total_dashboards" in data
        assert "total_reportes" in data
    
    def test_obtener_estadisticas_metrica(self):
        """Test obtener estadísticas de una métrica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Obtener estadísticas
        response = client.get(f"/metricas-rendimiento/{metrica_id}/estadisticas", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["metrica_id"] == metrica_id
        assert "nombre_metrica" in data
        assert "codigo_metrica" in data
        assert "total_mediciones" in data
        assert "valor_promedio" in data
        assert "tendencia_actual" in data
        assert "total_alertas" in data
    
    def test_calcular_todas_metricas(self):
        """Test calcular todas las métricas"""
        headers = get_auth_headers()
        response = client.post("/metricas-rendimiento/calcular-todas", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "metricas_procesadas" in data
        assert data["metricas_procesadas"] >= 0
    
    def test_obtener_tipos_disponibles(self):
        """Test obtener tipos disponibles"""
        headers = get_auth_headers()
        response = client.get("/metricas-rendimiento/tipos-disponibles", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tipos_metrica" in data
        assert "categorias" in data
        assert "tipos_calculo" in data
        assert "frecuencias_medicion" in data
        assert "tipos_alerta" in data
        assert "estados_alerta" in data
        assert "severidades" in data
        assert "tendencias" in data
        assert "tipos_dashboard" in data
        assert "tipos_reporte" in data
        assert "formatos_entrega" in data
        assert "tipos_grafico" in data
    
    def test_probar_metrica(self):
        """Test probar una métrica"""
        headers = get_auth_headers()
        
        # Crear una métrica primero
        create_response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
        metrica_id = create_response.json()["id"]
        
        # Probar métrica
        response = client.post(f"/metricas-rendimiento/{metrica_id}/test", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "exito" in data
        assert "mensaje" in data
        if data["exito"]:
            assert "valor_calculado" in data
            assert "tendencia" in data
            assert "fecha_calculo" in data
        else:
            assert "fecha_error" in data
    
    def test_filtros_metricas(self):
        """Test filtros en listado de métricas"""
        headers = get_auth_headers()
        
        # Crear una métrica con tipo específico
        metrica_data = test_metrica_data.copy()
        metrica_data["tipo_metrica"] = "rentabilidad"
        client.post("/metricas-rendimiento/", json=metrica_data, headers=headers)
        
        # Filtrar por tipo
        response = client.get(
            "/metricas-rendimiento/",
            params={"tipo_metrica": "rentabilidad"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verificar que todas las métricas devueltas sean del tipo filtrado
        for metrica in data:
            assert metrica["tipo_metrica"] == "rentabilidad"
    
    def test_paginacion_metricas(self):
        """Test paginación en listado de métricas"""
        headers = get_auth_headers()
        
        # Crear varias métricas
        for i in range(5):
            metrica_data = test_metrica_data.copy()
            metrica_data["nombre"] = f"Métrica {i+1}"
            metrica_data["codigo"] = f"METRICA_{i+1}"
            client.post("/metricas-rendimiento/", json=metrica_data, headers=headers)
        
        # Probar paginación
        response = client.get(
            "/metricas-rendimiento/",
            params={"skip": 0, "limit": 3},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3  # Máximo 3 métricas por página
    
    def test_validaciones_esquemas(self):
        """Test validaciones de esquemas Pydantic"""
        headers = get_auth_headers()
        
        # Test con datos inválidos
        invalid_data = {
            "nombre": "",  # Nombre vacío
            "codigo": "codigo invalido!",  # Código con caracteres inválidos
            "tipo_metrica": "tipo_invalido",  # Tipo inválido
            "categoria": "categoria_invalida",  # Categoría inválida
            "rango_optimo_inicio": 300000.0,  # Rango inválido
            "rango_optimo_fin": 200000.0,  # Inicio mayor que fin
            "color_positivo": "color_invalido"  # Color inválido
        }
        
        response = client.post("/metricas-rendimiento/", json=invalid_data, headers=headers)
        
        assert response.status_code == 422  # Error de validación
        errors = response.json()["detail"]
        assert len(errors) > 0  # Debe haber errores de validación
    
    def test_acceso_no_autorizado(self):
        """Test acceso no autorizado"""
        # Test sin headers de autenticación
        response = client.get("/metricas-rendimiento/")
        assert response.status_code == 401
        
        # Test con token inválido
        headers = {"Authorization": "Bearer token_invalido"}
        response = client.get("/metricas-rendimiento/", headers=headers)
        assert response.status_code == 401
    
    def test_permisos_administrador(self):
        """Test que solo administradores pueden crear/actualizar/eliminar métricas"""
        # Crear usuario no administrador
        user_data = {
            "username": "test_user",
            "email": "user@test.com",
            "password": "testpassword123",
            "role": "user"
        }
        
        # Registrar usuario
        client.post("/auth/register", json=user_data)
        
        # Login
        login_response = client.post("/auth/login", data={"username": user_data["username"], "password": user_data["password"]})
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Intentar crear métrica (debe fallar)
            response = client.post("/metricas-rendimiento/", json=test_metrica_data, headers=headers)
            assert response.status_code == 403  # Prohibido para usuarios no admin




























