import os
import uuid
import pytest
import httpx

@pytest.fixture(scope="session")
def base_url() -> str:
    # Permite sobreescribir con API_BASE_URL si lo necesitás
    return os.environ.get("API_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def admin_user() -> str:
    return os.environ.get("ADMIN_USERNAME", "admin")

@pytest.fixture(scope="session")
def admin_pass() -> str:
    return os.environ.get("ADMIN_PASSWORD", "admin123")

@pytest.fixture(scope="session")
def client(base_url: str):
    # follow_redirects=True para evitar problemas con rutas con/sin barra final
    with httpx.Client(base_url=base_url, timeout=15, follow_redirects=True) as c:
        yield c

@pytest.fixture(scope="session")
def admin_token(client: httpx.Client, admin_user: str, admin_pass: str) -> str:
    r = client.post("/auth/login", data={"username": admin_user, "password": admin_pass})
    if r.status_code != 200:
        pytest.skip(f"No pude loguear admin ({admin_user}). Respuesta: {r.status_code} {r.text}")
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def auth_headers(admin_token: str):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def unique_username() -> str:
    # Usuario único por test
    return f"vend_{uuid.uuid4().hex[:8]}"
