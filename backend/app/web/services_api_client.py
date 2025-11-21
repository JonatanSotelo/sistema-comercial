
import os
from typing import Optional, Dict, Any, List
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

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        message = response.reason_phrase
        try:
            payload = response.json()
            detail = payload.get("detail") if isinstance(payload, dict) else None
            if detail:
                message = detail
        except Exception:
            pass
        raise httpx.HTTPStatusError(message, request=response.request, response=response)

    @staticmethod
    def _normalize_page(data: Any, page: int, size: int) -> Dict[str, Any]:
        if isinstance(data, dict) and "items" in data:
            return data
        if isinstance(data, list):
            return {
                "items": data,
                "total": len(data),
                "page": page,
                "size": size,
            }
        return {"items": [], "total": 0, "page": page, "size": size}

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

    _CUIT_KEYS: tuple[str, ...] = ("cuit", "tax_id", "dni", "documento", "id_number", "national_id", "cuil")
    _PHONE_KEYS: tuple[str, ...] = ("telefono", "phone", "phone_number", "telefono_movil")
    _ADDRESS_KEYS: tuple[str, ...] = ("direccion", "address", "direccion_fiscal", "domicilio")

    async def _map_cliente_payload(self, base: Dict[str, Any], schema_hint: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        nombre = base.get("nombre")
        email = base.get("email")
        telefono = base.get("telefono")
        cuit = base.get("cuit")

        payload: Dict[str, Any] = {}
        hint_keys = set(schema_hint.keys()) if schema_hint else set()

        if nombre is not None:
            if "nombre" in hint_keys:
                payload["nombre"] = nombre
            elif "name" in hint_keys:
                payload["name"] = nombre
            else:
                payload["nombre"] = nombre

        if email is not None:
            payload["email"] = email

        if telefono is not None:
            tel_key = next((k for k in self._PHONE_KEYS if k in hint_keys), None)
            payload[tel_key or "telefono"] = telefono

        if cuit is not None:
            cuit_key = next((k for k in self._CUIT_KEYS if k in hint_keys), None)
            payload[cuit_key or "cuit"] = cuit

        return payload

    def _cuit_alias_variants(self, value: str) -> List[Dict[str, Any]]:
        return [{k: value} for k in self._CUIT_KEYS]

    async def _get_cliente_cuit_value(self, cid: int) -> Optional[str]:
        try:
            obj = await self.get_cliente(cid)
        except Exception:
            return None

        for key in self._CUIT_KEYS:
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return val
        return None

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
            response = await client.post(url, json=payload, headers=self._headers(), timeout=30)

            if response.status_code >= 400 and data.get("cuit"):
                for variant in self._cuit_alias_variants(data["cuit"]):
                    alt = payload.copy()
                    for key in self._CUIT_KEYS:
                        alt.pop(key, None)
                    alt.update(variant)
                    response = await client.post(url, json=alt, headers=self._headers(), timeout=30)
                    if response.status_code < 400:
                        break

            response.raise_for_status()
            created = response.json()

            cid = created.get("id")
            if cid and data.get("cuit"):
                saved_value = await self._get_cliente_cuit_value(cid)
                if saved_value != data["cuit"]:
                    for variant in self._cuit_alias_variants(data["cuit"]):
                        alt = payload.copy()
                        for key in self._CUIT_KEYS:
                            alt.pop(key, None)
                        alt.update(variant)
                        follow = await client.put(f"{url}/{cid}", json=alt, headers=self._headers(), timeout=30)
                        if follow.status_code in (400, 405, 415, 422):
                            follow = await client.patch(f"{url}/{cid}", json=alt, headers=self._headers(), timeout=30)
                        if follow.status_code < 400:
                            saved_value = await self._get_cliente_cuit_value(cid)
                            if saved_value == data["cuit"]:
                                break

            return created

    async def update_cliente(self, cid: int, data: Dict[str, Any]) -> Dict[str, Any]:
        hint: Optional[Dict[str, Any]] = None
        try:
            hint = await self.get_cliente(cid)
        except Exception:
            pass

        payload = await self._map_cliente_payload(data, hint)
        url = f"{self.base_url}/clientes/{cid}"

        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=payload, headers=self._headers(), timeout=30)
            if response.status_code in (400, 405, 415, 422):
                response = await client.patch(url, json=payload, headers=self._headers(), timeout=30)

            if data.get("cuit"):
                saved_value = await self._get_cliente_cuit_value(cid)
                if saved_value != data["cuit"]:
                    for variant in self._cuit_alias_variants(data["cuit"]):
                        alt = payload.copy()
                        for key in self._CUIT_KEYS:
                            alt.pop(key, None)
                        alt.update(variant)

                        response = await client.put(url, json=alt, headers=self._headers(), timeout=30)
                        if response.status_code in (400, 405, 415, 422):
                            response = await client.patch(url, json=alt, headers=self._headers(), timeout=30)

                        if response.status_code < 400:
                            saved_value = await self._get_cliente_cuit_value(cid)
                            if saved_value == data["cuit"]:
                                break

            response.raise_for_status()
            return response.json()

    # --- Proveedores ---

    async def list_proveedores(self, q: str = "", page: int = 1, size: int = 20) -> Dict[str, Any]:
        params: Dict[str, Any] = {"page": page, "size": size}
        if q:
            params["q"] = q
        url = f"{self.base_url}/proveedores"
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

    async def get_proveedor(self, pid: int) -> Dict[str, Any]:
        url = f"{self.base_url}/proveedores/{pid}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def _map_proveedor_payload(self, base: Dict[str, Any], schema_hint: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        nombre = base.get("nombre")
        email = base.get("email")
        telefono = base.get("telefono")
        cuit = base.get("cuit")
        direccion = base.get("direccion")

        payload: Dict[str, Any] = {}
        hint_keys = set(schema_hint.keys()) if schema_hint else set()

        if nombre is not None:
            if "nombre" in hint_keys:
                payload["nombre"] = nombre
            elif "name" in hint_keys:
                payload["name"] = nombre
            else:
                payload["nombre"] = nombre

        if email is not None:
            payload["email"] = email

        if telefono is not None:
            tel_key = next((k for k in self._PHONE_KEYS if k in hint_keys), None)
            payload[tel_key or "telefono"] = telefono

        if cuit is not None:
            cuit_key = next((k for k in self._CUIT_KEYS if k in hint_keys), None)
            payload[cuit_key or "cuit"] = cuit

        if direccion is not None:
            addr_key = next((k for k in self._ADDRESS_KEYS if k in hint_keys), None)
            payload[addr_key or "direccion"] = direccion

        return payload

    def _address_alias_variants(self, value: str) -> List[Dict[str, Any]]:
        return [{k: value} for k in self._ADDRESS_KEYS]

    async def _get_proveedor_value(self, pid: int, keys: tuple[str, ...]) -> Optional[str]:
        try:
            obj = await self.get_proveedor(pid)
        except Exception:
            return None

        for key in keys:
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return val
        return None

    async def create_proveedor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hint: Optional[Dict[str, Any]] = None
        try:
            sample = await self.list_proveedores(page=1, size=1)
            items = sample.get("items") or []
            if items:
                hint = items[0]
        except Exception:
            pass

        payload = await self._map_proveedor_payload(data, hint)
        url = f"{self.base_url}/proveedores"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers(), timeout=30)

            if response.status_code >= 400 and (data.get("cuit") or data.get("direccion")):
                cuit_variants = self._cuit_alias_variants(data.get("cuit", "")) if data.get("cuit") else [None]
                addr_variants = self._address_alias_variants(data.get("direccion", "")) if data.get("direccion") else [None]

                for cuit_variant in cuit_variants:
                    for addr_variant in addr_variants:
                        alt = payload.copy()
                        for key in self._CUIT_KEYS:
                            alt.pop(key, None)
                        for key in self._ADDRESS_KEYS:
                            alt.pop(key, None)
                        if cuit_variant:
                            alt.update(cuit_variant)
                        if addr_variant:
                            alt.update(addr_variant)
                        response = await client.post(url, json=alt, headers=self._headers(), timeout=30)
                        if response.status_code < 400:
                            break
                    if response.status_code < 400:
                        break

            response.raise_for_status()
            created = response.json()

            pid = created.get("id")
            if pid and data.get("cuit"):
                saved_cuit = await self._get_proveedor_value(pid, self._CUIT_KEYS)
                if saved_cuit != data["cuit"]:
                    for variant in self._cuit_alias_variants(data["cuit"]):
                        alt = payload.copy()
                        for key in self._CUIT_KEYS:
                            alt.pop(key, None)
                        alt.update(variant)
                        follow = await client.put(f"{url}/{pid}", json=alt, headers=self._headers(), timeout=30)
                        if follow.status_code in (400, 405, 415, 422):
                            follow = await client.patch(f"{url}/{pid}", json=alt, headers=self._headers(), timeout=30)
                        if follow.status_code < 400:
                            saved_cuit = await self._get_proveedor_value(pid, self._CUIT_KEYS)
                            if saved_cuit == data["cuit"]:
                                break

            return created

    async def update_proveedor(self, pid: int, data: Dict[str, Any]) -> Dict[str, Any]:
        hint: Optional[Dict[str, Any]] = None
        try:
            hint = await self.get_proveedor(pid)
        except Exception:
            pass

        payload = await self._map_proveedor_payload(data, hint)
        url = f"{self.base_url}/proveedores/{pid}"

        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=payload, headers=self._headers(), timeout=30)
            if response.status_code in (400, 405, 415, 422):
                response = await client.patch(url, json=payload, headers=self._headers(), timeout=30)

            if (data.get("cuit") or data.get("direccion")):
                saved_cuit = await self._get_proveedor_value(pid, self._CUIT_KEYS) if data.get("cuit") else None
                needs_cuit_retry = data.get("cuit") and saved_cuit != data["cuit"]

                if needs_cuit_retry or response.status_code >= 400:
                    cuit_variants = self._cuit_alias_variants(data.get("cuit", "")) if data.get("cuit") else [None]
                    addr_variants = self._address_alias_variants(data.get("direccion", "")) if data.get("direccion") else [None]

                    for cuit_variant in cuit_variants:
                        for addr_variant in addr_variants:
                            alt = payload.copy()
                            for key in self._CUIT_KEYS:
                                alt.pop(key, None)
                            for key in self._ADDRESS_KEYS:
                                alt.pop(key, None)
                            if cuit_variant:
                                alt.update(cuit_variant)
                            if addr_variant:
                                alt.update(addr_variant)

                            response = await client.put(url, json=alt, headers=self._headers(), timeout=30)
                            if response.status_code in (400, 405, 415, 422):
                                response = await client.patch(url, json=alt, headers=self._headers(), timeout=30)

                            if response.status_code < 400:
                                if data.get("cuit"):
                                    saved_cuit = await self._get_proveedor_value(pid, self._CUIT_KEYS)
                                    if saved_cuit != data["cuit"]:
                                        continue
                                break
                        if response.status_code < 400:
                            break

            response.raise_for_status()
            return response.json()

    # --- Ventas / Compras ---

    async def list_ventas(self, q: str = "", page: int = 1, size: int = 20) -> Dict[str, Any]:
        params: Dict[str, Any] = {"page": page, "per_page": size}
        if q:
            params["search"] = q
        url = f"{self.base_url}/ventas"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            data = response.json()
            return self._normalize_page(data, page, size)

    async def create_venta(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/ventas"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            return response.json()

    async def list_compras(self, q: str = "", page: int = 1, size: int = 20) -> Dict[str, Any]:
        params: Dict[str, Any] = {"page": page, "per_page": size}
        if q:
            params["search"] = q
        url = f"{self.base_url}/compras"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            data = response.json()
            return self._normalize_page(data, page, size)

    async def create_compra(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/compras"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            return response.json()

    async def search_clientes(self, q: str = "", size: int = 5) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"page": 1, "size": size}
        if q:
            params["search"] = q
        url = f"{self.base_url}/clientes"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            data = response.json()
            page_data = self._normalize_page(data, 1, size)
            return page_data.get("items", [])

    async def search_proveedores(self, q: str = "", size: int = 5) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"page": 1, "size": size}
        if q:
            params["search"] = q
        url = f"{self.base_url}/proveedores"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            data = response.json()
            page_data = self._normalize_page(data, 1, size)
            return page_data.get("items", [])

    async def search_productos(self, q: str = "", size: int = 5) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"page": 1, "size": size}
        if q:
            params["search"] = q
        url = f"{self.base_url}/productos"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            data = response.json()
            page_data = self._normalize_page(data, 1, size)
            return page_data.get("items", [])

    async def list_audit_logs(
        self,
        q: str = "",
        page: int = 1,
        size: int = 20,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        table_name: Optional[str] = None,
        action: Optional[str] = None,
        username: Optional[str] = None,
        record_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"page": page, "size": size}
        if q:
            params["search"] = q
        if fecha_desde:
            params["fecha_desde"] = fecha_desde
        if fecha_hasta:
            params["fecha_hasta"] = fecha_hasta
        if table_name:
            params["table_name"] = table_name
        if action:
            params["action"] = action
        if username:
            params["username"] = username
        if record_id:
            params["record_id"] = record_id
        
        url = f"{self.base_url}/audit-logs"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            data = response.json()
            return self._normalize_page(data, page, size)

    async def get_reporte_ventas(
        self,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
        group_by: str = "dia",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"group_by": group_by}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        
        url = f"{self.base_url}/reportes/ventas"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            return response.json()

    async def get_reporte_compras(
        self,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
        group_by: str = "dia",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"group_by": group_by}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        
        url = f"{self.base_url}/reportes/compras"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            return response.json()

    async def list_backups(self) -> Dict[str, Any]:
        url = f"{self.base_url}/backups/list"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers(), timeout=30)
            self._raise_for_status(response)
            return response.json()

    async def create_backup(self) -> Dict[str, Any]:
        url = f"{self.base_url}/backups/create"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._headers(), timeout=300)  # 5 min timeout
            self._raise_for_status(response)
            return response.json()

    async def export_clientes(self, fmt: str = "csv") -> bytes:
        url = f"{self.base_url}/clientes/export"
        params = {"format": fmt}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=None)
            self._raise_for_status(response)
            return response.content

    async def export_proveedores(self, fmt: str = "csv") -> bytes:
        url = f"{self.base_url}/proveedores/export"
        params = {"format": fmt}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self._headers(), timeout=None)
            self._raise_for_status(response)
            return response.content

    async def import_clientes(self, file_content: bytes, filename: str, dry_run: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}/clientes/import?dry_run={'true' if dry_run else 'false'}"
        files = {"file": (filename, file_content, "text/csv" if filename.endswith(".csv") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, headers={k: v for k, v in self._headers().items() if k.lower() != "content-type"}, timeout=60)
            self._raise_for_status(response)
            return response.json()

    async def import_proveedores(self, file_content: bytes, filename: str, dry_run: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}/proveedores/import?dry_run={'true' if dry_run else 'false'}"
        files = {"file": (filename, file_content, "text/csv" if filename.endswith(".csv") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, headers={k: v for k, v in self._headers().items() if k.lower() != "content-type"}, timeout=60)
            self._raise_for_status(response)
            return response.json()

    async def import_productos(self, file_content: bytes, filename: str, dry_run: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}/productos/import?dry_run={'true' if dry_run else 'false'}"
        files = {"file": (filename, file_content, "text/csv" if filename.endswith(".csv") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, headers={k: v for k, v in self._headers().items() if k.lower() != "content-type"}, timeout=60)
            self._raise_for_status(response)
            return response.json()

    # --- Pedidos ---

    async def list_pedidos(
        self,
        q: str = "",
        page: int = 1,
        size: int = 20,
        estado: Optional[str] = None,
        cliente_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"page": page, "size": size}
        if q:
            params["q"] = q
        if estado:
            params["estado"] = estado
        if cliente_id:
            params["cliente_id"] = cliente_id
        
        url = f"{self.base_url}/pedidos"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, headers=self._headers(), timeout=30)
            r.raise_for_status()
            data = r.json()
            return self._normalize_page(data, page, size)

    async def get_pedido(self, pedido_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/pedidos/{pedido_id}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def create_pedido(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/pedidos"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=data, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def update_pedido(self, pedido_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/pedidos/{pedido_id}"
        async with httpx.AsyncClient() as client:
            r = await client.put(url, json=data, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def change_pedido_estado(self, pedido_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/pedidos/{pedido_id}/estado"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=data, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def facturar_pedido(self, pedido_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/pedidos/{pedido_id}/facturar"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def _call_bulk_change_estado(self, pedido_ids: list[int], nuevo_estado: str) -> Dict[str, Any]:
        url = f"{self.base_url}/pedidos/bulk_estado"
        payload = {"pedido_ids": pedido_ids, "nuevo_estado": nuevo_estado}
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    # Facturación (v0.9.0+)
    async def list_facturas(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/facturacion"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params or {}, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()

    async def emitir_factura_afip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/facturacion/emitir"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=data, headers=self._headers(), timeout=60)
            r.raise_for_status()
            return r.json()


# Helper functions for UI (cookie-based auth via forwarded requests)
def _get_token_from_request(request: Any) -> Optional[str]:
    """Extract auth token from request cookies or headers"""
    if hasattr(request, "cookies"):
        return request.cookies.get("access_token")
    return None


def listar_facturas(request: Any, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Lista facturas desde la API (sync wrapper)"""
    import asyncio
    token = _get_token_from_request(request)
    client = ApiClient(token=token)
    return asyncio.run(client.list_facturas(params))


def emitir_factura(request: Any, data: Dict[str, Any]) -> Dict[str, Any]:
    """Emite una factura AFIP desde la API (sync wrapper)"""
    import asyncio
    token = _get_token_from_request(request)
    client = ApiClient(token=token)
    return asyncio.run(client.emitir_factura_afip(data))
