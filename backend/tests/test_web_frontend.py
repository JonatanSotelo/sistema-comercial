# tests/test_web_frontend.py
"""
Tests para el frontend web Python (Jinja2 + HTMX).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_web_root_redirect():
    """Test que / redirige a /app."""
    response = client.get("/app", follow_redirects=False)
    assert response.status_code in [303, 307]


def test_login_page_loads():
    """Test que la página de login carga correctamente."""
    response = client.get("/app/login")
    assert response.status_code == 200
    assert b"Sistema Comercial" in response.content
    assert b"usuario" in response.content.lower()


def test_login_success():
    """Test de login exitoso."""
    response = client.post(
        "/app/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=False
    )
    assert response.status_code == 303
    assert "dashboard" in response.headers.get("location", "")


def test_login_invalid():
    """Test de login con credenciales inválidas."""
    response = client.post(
        "/app/login",
        data={"username": "invalid", "password": "wrong"},
        follow_redirects=False
    )
    assert response.status_code == 303
    assert "error" in response.headers.get("location", "")


def test_dashboard_requires_auth():
    """Test que dashboard requiere autenticación."""
    response = client.get("/app/dashboard", follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers.get("location", "")


def test_productos_page_requires_auth():
    """Test que productos requiere autenticación."""
    response = client.get("/app/productos", follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers.get("location", "")


def test_logout():
    """Test de logout."""
    # Primero login
    response = client.post(
        "/app/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=False
    )
    
    # Luego logout
    response = client.get("/app/logout", follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers.get("location", "")


class TestProductosWeb:
    """Tests del módulo de productos web."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login antes de cada test."""
        self.client = TestClient(app)
        response = self.client.post(
            "/app/login",
            data={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 303
    
    def test_productos_index_loads(self):
        """Test que la página de productos carga."""
        response = self.client.get("/app/productos")
        assert response.status_code == 200
        assert b"Productos" in response.content
    
    def test_productos_table_loads(self):
        """Test que la tabla de productos carga vía HTMX."""
        response = self.client.get("/app/productos/table?page=1&size=20")
        assert response.status_code == 200
    
    def test_productos_form_loads(self):
        """Test que el formulario de productos carga."""
        response = self.client.get("/app/productos/form")
        assert response.status_code == 200
        assert b"Nombre" in response.content


class TestClientesWeb:
    """Tests del módulo de clientes web."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login antes de cada test."""
        self.client = TestClient(app)
        response = self.client.post(
            "/app/login",
            data={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 303
    
    def test_clientes_index_loads(self):
        """Test que la página de clientes carga."""
        response = self.client.get("/app/clientes")
        assert response.status_code == 200
        assert b"Clientes" in response.content


class TestProveedoresWeb:
    """Tests del módulo de proveedores web."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login antes de cada test."""
        self.client = TestClient(app)
        response = self.client.post(
            "/app/login",
            data={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 303
    
    def test_proveedores_index_loads(self):
        """Test que la página de proveedores carga."""
        response = self.client.get("/app/proveedores")
        assert response.status_code == 200
        assert b"Proveedores" in response.content


class TestVentasWeb:
    """Tests del módulo de ventas web."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login antes de cada test."""
        self.client = TestClient(app)
        response = self.client.post(
            "/app/login",
            data={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 303
    
    def test_ventas_index_loads(self):
        """Test que la página de ventas carga."""
        response = self.client.get("/app/ventas")
        assert response.status_code == 200
        assert b"Ventas" in response.content


class TestComprasWeb:
    """Tests del módulo de compras web."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login antes de cada test."""
        self.client = TestClient(app)
        response = self.client.post(
            "/app/login",
            data={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 303
    
    def test_compras_index_loads(self):
        """Test que la página de compras carga."""
        response = self.client.get("/app/compras")
        assert response.status_code == 200
        assert b"Compras" in response.content


