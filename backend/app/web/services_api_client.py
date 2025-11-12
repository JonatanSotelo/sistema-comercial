
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

    async def _map_producto_payload(self, base: Dict[str, Any], schema_hint: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        nombre = base.get("nombre")
        precio = base.get("precio")
        stock = base.get("stock")
        is_active = base.get("is_active")

        payload_es: Dict[str, Any] = {}
        payload_en: Dict[str, Any] = {}

        if nombre is not None:
            payload_es["nombre"] = nombre
            payload_en["name"] = nombre
        if precio is not None:
            payload_es["precio"] = precio
            payload_en["price"] = precio
        if stock is not None:
            payload_es["stock"] = stock
            payload_en["stock"] = stock
        if is_active is not None:
            payload_es["is_active"] = is_active
            payload_es.setdefault("activo", is_active)
            payload_en["is_active"] = is_active

        if schema_hint:
            keys = set(schema_hint.keys())
            if {"nombre", "precio", "stock"} & keys:
                return payload_es or payload_en
            if {"name", "price", "stock"} & keys:
                return payload_en or payload_es

        merged = payload_es.copy()
        for k, v in payload_en.items():
            merged.setdefault(k, v)
        return merged

    async def get_producto(self, pid: int) -> Dict[str, Any]:
        url = f"{self.base_url}/productos/{pid}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def create_producto(self, data: Dict[str, Any]) -> Dict[str, Any]:
        schema_hint: Optional[Dict[str, Any]] = None
        try:
            sample = await self.list_productos(page=1, size=1)
            items = sample.get("items") or []
            if items:
                schema_hint = items[0]
        except Exception:
            pass

        payload = await self._map_producto_payload(data, schema_hint)
        url = f"{self.base_url}/productos"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, headers=self._headers(), timeout=30)
            if r.status_code >= 400:
                alt = await self._map_producto_payload(data, {"name": ""})
                r = await client.post(url, json=alt, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def update_producto(self, pid: int, data: Dict[str, Any]) -> Dict[str, Any]:
        schema_hint: Optional[Dict[str, Any]] = None
        try:
            schema_hint = await self.get_producto(pid)
        except Exception:
            pass

        payload = await self._map_producto_payload(data, schema_hint)
        url = f"{self.base_url}/productos/{pid}"
        async with httpx.AsyncClient() as client:
            r = await client.put(url, json=payload, headers=self._headers(), timeout=30)
            if r.status_code in (400, 405, 415, 422):
                r = await client.patch(url, json=payload, headers=self._headers(), timeout=30)
            if r.status_code >= 400:
                alt = await self._map_producto_payload(data, {"name": "" if "nombre" in payload else "nombre"})
                r = await client.put(url, json=alt, headers=self._headers(), timeout=30)
                if r.status_code in (400, 405, 415, 422):
                    r = await client.patch(url, json=alt, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def toggle_producto(self, pid: int, is_active: bool) -> Dict[str, Any]:
        url = f"{self.base_url}/productos/{pid}"
        payload = {"is_active": (not is_active)}
        async with httpx.AsyncClient() as client:
            r = await client.patch(url, json=payload, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    # --- Clientes ---

    async def list_clientes(self, q: str = "", page: int = 1, size: int = 20) -> Dict[str, Any]:
        params: Dict[str, Any] = {"page": page, "size": size}
        if q:
            params["q"] = q
        url = f"{self.base_url}/clientes"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, headers=self._headers(), timeout=30)
            r.raise_for_status()
            data = r.json()

            if isinstance(data, list):
                total = len(data)
                start = max((page - 1) * size, 0)
                end = start + size
                items = data[start:end]
                return {"items": items, "total": total, "page": page, "size": size}

            if isinstance(data, dict):
                if "items" in data:
                    return data
                items = data.get("results") or data.get("data") or []
                if isinstance(items, list):
                    total = data.get("total", len(items))
                    return {
                        "items": items,
                        "total": total,
                        "page": data.get("page", page),
                        "size": data.get("size", size),
                    }

        return {"items": [], "total": 0, "page": page, "size": size}

    async def get_cliente(self, cid: int) -> Dict[str, Any]:
        url = f"{self.base_url}/clientes/{cid}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def _map_cliente_payload(self, base: Dict[str, Any], schema_hint: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        nombre = base.get("nombre")
        email = base.get("email")
        telefono = base.get("telefono")
        cuit = base.get("cuit")

        es: Dict[str, Any] = {}
        en: Dict[str, Any] = {}

        if nombre is not None:
            es["nombre"] = nombre
            en["name"] = nombre
        if email is not None:
            es["email"] = email
            en["email"] = email
        if telefono is not None:
            es["telefono"] = telefono
            en["phone"] = telefono
        if cuit is not None:
            es["cuit"] = cuit
            en["tax_id"] = cuit

        if schema_hint:
            keys = set(schema_hint.keys())
            if {"nombre", "telefono", "email"} & keys:
                return es or en
            if {"name", "phone", "email"} & keys:
                return en or es

        merged = es.copy()
        for k, v in en.items():
            merged.setdefault(k, v)
        return merged

    async def create_cliente(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hint: Optional[Dict[str, Any]] = None
        try:
            sample = await self.list_clientes(page=1, size=1)
            items = sample.get("items") or []
            if items:
                hint = items[0]
        except Exception:
            pass

        payload = await self._map_cliente_payload(data, hint)
        url = f"{self.base_url}/clientes"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, headers=self._headers(), timeout=30)
            if r.status_code >= 400:
                alt = await self._map_cliente_payload(data, {"name": ""})
                r = await client.post(url, json=alt, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def update_cliente(self, cid: int, data: Dict[str, Any]) -> Dict[str, Any]:
        hint: Optional[Dict[str, Any]] = None
        try:
            hint = await self.get_cliente(cid)
        except Exception:
            pass

        payload = await self._map_cliente_payload(data, hint)
        url = f"{self.base_url}/clientes/{cid}"
        async with httpx.AsyncClient() as client:
            r = await client.put(url, json=payload, headers=self._headers(), timeout=30)
            if r.status_code in (400, 405, 415, 422):
                r = await client.patch(url, json=payload, headers=self._headers(), timeout=30)
            if r.status_code >= 400:
                alt = await self._map_cliente_payload(data, {"name": "" if "nombre" in payload else "nombre"})
                r = await client.put(url, json=alt, headers=self._headers(), timeout=30)
                if r.status_code in (400, 405, 415, 422):
                    r = await client.patch(url, json=alt, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()
