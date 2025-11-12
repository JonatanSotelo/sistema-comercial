
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
        # Intento 1: /auth/login con payload JSON
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{self.base_url}/auth/login",
                    json={"username": username, "password": password},
                    headers={"Accept": "application/json"},
                    timeout=30,
                )
                if r.status_code < 400:
                    data = r.json()
                    token = data.get("access_token") or data.get("token") or data.get("access")
                    if token:
                        return token
        except Exception:
            pass

        # Intento 2: OAuth2 password flow (/auth/oauth2/token)
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{self.base_url}/auth/oauth2/token",
                    data={"username": username, "password": password, "grant_type": "password"},
                    headers={"Accept": "application/json"},
                    timeout=30,
                )
                if r.status_code < 400:
                    data = r.json()
                    token = data.get("access_token") or data.get("token") or data.get("access")
                    if token:
                        return token
        except Exception:
            pass

        return None

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

    async def get_producto(self, pid: int) -> Dict[str, Any]:
        url = f"{self.base_url}/productos/{pid}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def create_producto(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/productos"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=data, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def update_producto(self, pid: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/productos/{pid}"
        async with httpx.AsyncClient() as client:
            r = await client.put(url, json=data, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def toggle_producto(self, pid: int, is_active: bool) -> Dict[str, Any]:
        url = f"{self.base_url}/productos/{pid}"
        payload = {"is_active": (not is_active)}
        async with httpx.AsyncClient() as client:
            r = await client.patch(url, json=payload, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()
