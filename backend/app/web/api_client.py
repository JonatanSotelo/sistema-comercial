# app/web/api_client.py
"""
Cliente API mejorado que evita problemas de conectividad HTTP cuando
el frontend y backend están en el mismo proceso.
"""
import os
from typing import Optional
import httpx
from fastapi.testclient import TestClient

from app.web.core import web_settings


def get_smart_api_client():
    """
    Retorna un cliente API inteligente:
    - Si USE_TEST_CLIENT=true, usa TestClient (sin HTTP, más rápido)
    - Si no, usa httpx (para llamadas HTTP reales)
    """
    use_test_client = os.getenv("USE_TEST_CLIENT", "true").lower() == "true"
    
    if use_test_client:
        # Usar TestClient para llamadas internas (sin HTTP)
        from app.main import app
        return TestClient(app, base_url="http://testserver")
    else:
        # Usar httpx para llamadas HTTP reales
        return httpx.Client(
            base_url=web_settings.API_BASE_URL,
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
        )


class APIClient:
    """Wrapper unificado que funciona con httpx.Client y TestClient"""
    
    def __init__(self):
        self.client = get_smart_api_client()
    
    def post(self, url: str, **kwargs):
        return self.client.post(url, **kwargs)
    
    def get(self, url: str, **kwargs):
        return self.client.get(url, **kwargs)
    
    def put(self, url: str, **kwargs):
        return self.client.put(url, **kwargs)
    
    def delete(self, url: str, **kwargs):
        return self.client.delete(url, **kwargs)
    
    def patch(self, url: str, **kwargs):
        return self.client.patch(url, **kwargs)
    
    def close(self):
        if hasattr(self.client, 'close'):
            self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


