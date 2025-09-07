# backend/tests/test_reportes_financieros.py
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
from app.models.reporte_financiero_model import ReporteFinanciero, EstadoResultados, FlujoCaja, AnalisisRentabilidad

client = TestClient(app)

# Datos de prueba
test_user_data = {
    "username": "test_admin",
    "email": "admin@test.com",
    "password": "testpassword123",
    "role": "admin"
}

test_reporte_data = {
    "nombre": "Reporte Financiero Test",
    "tipo": "estado_resultados",
    "periodo": "mensual",
    "fecha_inicio": "2025-01-01",
    "fecha_fin": "2025-01-31",
    "incluir_detalles": True,
    "incluir_proyecciones": False,
    "incluir_comparaciones": False,
    "formato_salida": "json",
    "descripcion": "Reporte de prueba para testing"
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

class TestReportesFinancieros:
    
    def test_crear_reporte_financiero(self):
        """Test crear un reporte financiero"""
        headers = get_auth_headers()
        response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == test_reporte_data["nombre"]
        assert data["tipo"] == test_reporte_data["tipo"]
        assert data["periodo"] == test_reporte_data["periodo"]
        assert data["estado"] == "generando"
        assert "id" in data
    
    def test_listar_reportes_financieros(self):
        """Test listar reportes financieros"""
        headers = get_auth_headers()
        response = client.get("/reportes-financieros/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_obtener_reporte_financiero(self):
        """Test obtener un reporte financiero específico"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Obtener el reporte
        response = client.get(f"/reportes-financieros/{reporte_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == reporte_id
        assert data["nombre"] == test_reporte_data["nombre"]
    
    def test_actualizar_reporte_financiero(self):
        """Test actualizar un reporte financiero"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Actualizar el reporte
        update_data = {
            "nombre": "Reporte Actualizado",
            "descripcion": "Descripción actualizada"
        }
        response = client.put(f"/reportes-financieros/{reporte_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Reporte Actualizado"
        assert data["descripcion"] == "Descripción actualizada"
    
    def test_eliminar_reporte_financiero(self):
        """Test eliminar un reporte financiero"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Eliminar el reporte
        response = client.delete(f"/reportes-financieros/{reporte_id}", headers=headers)
        
        assert response.status_code == 200
        assert "eliminado" in response.json()["message"]
    
    def test_generar_estado_resultados(self):
        """Test generar estado de resultados"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Generar estado de resultados
        response = client.post(
            "/reportes-financieros/estado-resultados",
            params={
                "reporte_id": reporte_id,
                "periodo_desde": "2025-01-01",
                "periodo_hasta": "2025-01-31"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "ventas_brutas" in data
        assert "ventas_netas" in data
        assert "utilidad_bruta" in data
        assert "utilidad_neta" in data
        assert "margen_bruto_porcentaje" in data
        assert "margen_neto_porcentaje" in data
    
    def test_generar_flujo_caja(self):
        """Test generar flujo de caja"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Generar flujo de caja
        response = client.post(
            "/reportes-financieros/flujo-caja",
            params={
                "reporte_id": reporte_id,
                "periodo_desde": "2025-01-01",
                "periodo_hasta": "2025-01-31"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "ingresos_operativos" in data
        assert "flujo_operativo" in data
        assert "flujo_caja_neto" in data
        assert "saldo_caja_inicial" in data
        assert "saldo_caja_final" in data
    
    def test_generar_analisis_rentabilidad(self):
        """Test generar análisis de rentabilidad"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Generar análisis de rentabilidad
        response = client.post(
            "/reportes-financieros/analisis-rentabilidad",
            params={
                "reporte_id": reporte_id,
                "tipo_entidad": "producto",
                "periodo_desde": "2025-01-01",
                "periodo_hasta": "2025-01-31"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # Si hay datos
            assert "tipo_entidad" in data[0]
            assert "entidad_id" in data[0]
            assert "entidad_nombre" in data[0]
            assert "ingresos_totales" in data[0]
            assert "costos_totales" in data[0]
            assert "utilidad_bruta" in data[0]
            assert "margen_bruto_porcentaje" in data[0]
    
    def test_generar_proyeccion_financiera(self):
        """Test generar proyección financiera"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Generar proyección financiera
        proyeccion_data = {
            "reporte_id": reporte_id,
            "tipo_proyeccion": "ventas",
            "horizonte_meses": 12,
            "metodo_calculo": "tendencia",
            "periodo_historico_desde": "2024-01-01",
            "periodo_historico_hasta": "2024-12-31",
            "factor_estacional": 1.0,
            "factor_crecimiento": 1.1,
            "factor_inflacion": 1.05,
            "confianza_porcentaje": 80.0
        }
        
        response = client.post("/reportes-financieros/proyecciones", json=proyeccion_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["tipo_proyeccion"] == "ventas"
        assert data["horizonte_meses"] == 12
        assert data["metodo_calculo"] == "tendencia"
        assert "valor_historico_promedio" in data
    
    def test_crear_metrica_financiera(self):
        """Test crear métrica financiera"""
        headers = get_auth_headers()
        
        metrica_data = {
            "nombre": "Margen Bruto Promedio",
            "categoria": "rentabilidad",
            "tipo_valor": "porcentaje",
            "valor_actual": 25.5,
            "valor_objetivo": 30.0,
            "descripcion": "Margen bruto promedio del negocio",
            "formula": "(Utilidad Bruta / Ventas Netas) * 100",
            "fuente_datos": "Estado de Resultados",
            "periodo_desde": "2025-01-01",
            "periodo_hasta": "2025-01-31"
        }
        
        response = client.post("/reportes-financieros/metricas", json=metrica_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == metrica_data["nombre"]
        assert data["categoria"] == metrica_data["categoria"]
        assert data["tipo_valor"] == metrica_data["tipo_valor"]
        assert data["valor_actual"] == metrica_data["valor_actual"]
    
    def test_listar_metricas_financieras(self):
        """Test listar métricas financieras"""
        headers = get_auth_headers()
        response = client.get("/reportes-financieros/metricas", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_obtener_dashboard_financiero(self):
        """Test obtener dashboard financiero"""
        headers = get_auth_headers()
        response = client.get("/reportes-financieros/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "ingresos_mes_actual" in data
        assert "costos_mes_actual" in data
        assert "utilidad_neta_mes" in data
        assert "margen_bruto" in data
        assert "margen_neto" in data
        assert "crecimiento_ingresos" in data
        assert "crecimiento_costos" in data
        assert "crecimiento_utilidad" in data
        assert "tendencia_crecimiento" in data
        assert "alertas" in data
        assert "top_productos_rentables" in data
        assert "top_clientes_rentables" in data
        assert "categorias_mas_rentables" in data
    
    def test_obtener_resumen_reportes(self):
        """Test obtener resumen de reportes"""
        headers = get_auth_headers()
        response = client.get("/reportes-financieros/resumen", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_reportes" in data
        assert "reportes_por_tipo" in data
        assert "reportes_por_estado" in data
        assert "reportes_por_periodo" in data
        assert "total_ingresos_mes" in data
        assert "total_costos_mes" in data
        assert "ganancia_neta_mes" in data
        assert "margen_bruto_promedio" in data
    
    def test_exportar_reporte(self):
        """Test exportar reporte"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Exportar reporte
        export_data = {
            "formato": "pdf",
            "incluir_graficos": True,
            "incluir_detalles": True,
            "incluir_comparaciones": False,
            "idioma": "es",
            "moneda": "ARS"
        }
        
        response = client.post(f"/reportes-financieros/{reporte_id}/exportar", json=export_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "mensaje" in data
        assert "archivo_ruta" in data
        assert "formato" in data
        assert data["formato"] == "pdf"
    
    def test_comparar_reportes(self):
        """Test comparar reportes"""
        headers = get_auth_headers()
        
        # Crear dos reportes
        reporte1_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte1_id = reporte1_response.json()["id"]
        
        reporte2_data = test_reporte_data.copy()
        reporte2_data["nombre"] = "Reporte Comparación"
        reporte2_response = client.post("/reportes-financieros/", json=reporte2_data, headers=headers)
        reporte2_id = reporte2_response.json()["id"]
        
        # Generar estados de resultados para ambos reportes
        client.post(
            "/reportes-financieros/estado-resultados",
            params={
                "reporte_id": reporte1_id,
                "periodo_desde": "2025-01-01",
                "periodo_hasta": "2025-01-31"
            },
            headers=headers
        )
        
        client.post(
            "/reportes-financieros/estado-resultados",
            params={
                "reporte_id": reporte2_id,
                "periodo_desde": "2025-01-01",
                "periodo_hasta": "2025-01-31"
            },
            headers=headers
        )
        
        # Comparar reportes
        response = client.get(
            f"/reportes-financieros/{reporte1_id}/comparar",
            params={"reporte_comparar_id": reporte2_id},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "periodo_actual" in data
        assert "periodo_anterior" in data
        assert "variaciones" in data
        assert "tendencias" in data
        assert "recomendaciones" in data
    
    def test_regenerar_reporte(self):
        """Test regenerar reporte"""
        headers = get_auth_headers()
        
        # Crear un reporte primero
        create_response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        reporte_id = create_response.json()["id"]
        
        # Regenerar reporte
        response = client.post(f"/reportes-financieros/{reporte_id}/regenerar", headers=headers)
        
        assert response.status_code == 200
        assert "regeneración" in response.json()["message"]
    
    def test_obtener_tipos_disponibles(self):
        """Test obtener tipos disponibles"""
        headers = get_auth_headers()
        response = client.get("/reportes-financieros/tipos-disponibles", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tipos_reporte" in data
        assert "periodos" in data
        assert "estados" in data
        assert "formatos_exportacion" in data
        assert "tipos_entidad_rentabilidad" in data
        assert "tipos_proyeccion" in data
        assert "metodos_calculo" in data
        assert "categorias_metricas" in data
        assert "tipos_valor" in data
    
    def test_filtros_reportes(self):
        """Test filtros en listado de reportes"""
        headers = get_auth_headers()
        
        # Crear un reporte con tipo específico
        reporte_data = test_reporte_data.copy()
        reporte_data["tipo"] = "flujo_caja"
        client.post("/reportes-financieros/", json=reporte_data, headers=headers)
        
        # Filtrar por tipo
        response = client.get(
            "/reportes-financieros/",
            params={"tipo": "flujo_caja"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verificar que todos los reportes devueltos sean del tipo filtrado
        for reporte in data:
            assert reporte["tipo"] == "flujo_caja"
    
    def test_paginacion_reportes(self):
        """Test paginación en listado de reportes"""
        headers = get_auth_headers()
        
        # Crear varios reportes
        for i in range(5):
            reporte_data = test_reporte_data.copy()
            reporte_data["nombre"] = f"Reporte {i+1}"
            client.post("/reportes-financieros/", json=reporte_data, headers=headers)
        
        # Probar paginación
        response = client.get(
            "/reportes-financieros/",
            params={"skip": 0, "limit": 3},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3  # Máximo 3 reportes por página
    
    def test_validaciones_esquemas(self):
        """Test validaciones de esquemas Pydantic"""
        headers = get_auth_headers()
        
        # Test con datos inválidos
        invalid_data = {
            "nombre": "",  # Nombre vacío
            "tipo": "tipo_invalido",  # Tipo inválido
            "periodo": "periodo_invalido",  # Período inválido
            "fecha_inicio": "2025-01-31",  # Fecha inicio posterior a fin
            "fecha_fin": "2025-01-01",
            "formato_salida": "formato_invalido"  # Formato inválido
        }
        
        response = client.post("/reportes-financieros/", json=invalid_data, headers=headers)
        
        assert response.status_code == 422  # Error de validación
        errors = response.json()["detail"]
        assert len(errors) > 0  # Debe haber errores de validación
    
    def test_acceso_no_autorizado(self):
        """Test acceso no autorizado"""
        # Test sin headers de autenticación
        response = client.get("/reportes-financieros/")
        assert response.status_code == 401
        
        # Test con token inválido
        headers = {"Authorization": "Bearer token_invalido"}
        response = client.get("/reportes-financieros/", headers=headers)
        assert response.status_code == 401
    
    def test_permisos_administrador(self):
        """Test que solo administradores pueden crear/actualizar/eliminar reportes"""
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
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Intentar crear reporte (debe fallar)
        response = client.post("/reportes-financieros/", json=test_reporte_data, headers=headers)
        assert response.status_code == 403  # Prohibido para usuarios no admin
