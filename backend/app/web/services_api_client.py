
import os
from typing import Optional, Dict, Any
import httpx

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

class ApiClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.base_url = API_BASE_URL.rstrip("/")
        self.token = token

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def login(self, username: str, password: str) -> Optional[str]:
        # Ajustá la ruta si tu backend usa /auth/oauth2/token
        url = f"{self.base_url}/auth/login"
        data = {"username": username, "password": password}
        async with httpx.AsyncClient() as client:
            r = await client.post(url, data=data, headers={"Accept": "application/json"})
            r.raise_for_status()
            payload = r.json()
            return payload.get("access_token")

    async def get_features(self) -> Dict[str, Any]:
        url = f"{self.base_url}/features"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def list_productos(self, q: str = "", page: int = 1, size: int = 20) -> Dict[str, Any]:
        params = {"page": page, "size": size}
        if q:
            params["q"] = q
        url = f"{self.base_url}/productos"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def export_productos(self, fmt: str = "csv") -> bytes:
        url = f"{self.base_url}/productos/export"
        params = {"format": fmt}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, headers=self._headers(), timeout=None)
            r.raise_for_status()
            return r.content
