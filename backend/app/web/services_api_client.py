# app/web/services_api_client.py
import httpx
from typing import Optional, Dict, Any, List


class ApiClient:
    """Cliente HTTP para llamar a la propia API desde el web UI."""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        
    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h
    
    # ========== PRODUCTOS ==========
    async def list_productos(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/productos", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    async def search_productos(self, q: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/productos/search?q={q}", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    # ========== CLIENTES ==========
    async def list_clientes(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/clientes", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    async def get_cliente(self, cliente_id: int) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/clientes/{cliente_id}", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    async def get_saldo_cliente(self, cliente_id: int) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/clientes/{cliente_id}/saldo", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    # ========== VENTAS ==========
    async def list_ventas(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/ventas", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    async def get_venta(self, venta_id: int) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/ventas/{venta_id}", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    async def get_saldo_venta(self, venta_id: int) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/cobros/venta/{venta_id}/saldo", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    # ========== PEDIDOS ==========
    async def list_pedidos(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/pedidos", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    # ========== FACTURAS ==========
    async def list_facturas(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/facturas", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    async def emitir_factura_afip(self, venta_id: int, tipo_cbte: int, pto_vta: int) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            payload = {"venta_id": venta_id, "tipo_cbte": tipo_cbte, "pto_vta": pto_vta}
            r = await client.post(f"{self.base_url}/facturacion/emitir", json=payload, headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    # ========== COBROS ==========
    async def list_cobros(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/cobros", headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    async def create_cobro(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.base_url}/cobros", json=data, headers=self._headers())
            r.raise_for_status()
            return r.json()
    
    # ========== IVA COMPRAS ==========
    async def list_iva_compras(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/iva-compras", headers=self._headers())
            r.raise_for_status()
            return r.json()
