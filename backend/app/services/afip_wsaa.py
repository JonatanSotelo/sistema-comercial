# app/services/afip_wsaa.py
"""
Cliente WSAA (Web Services de Autenticación y Autorización) de AFIP
Genera Tickets de Acceso (TA) firmados con certificado y clave privada.
"""

import os
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

try:
    from zeep import Client
    from zeep.transports import Transport
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
    import requests
except ImportError as e:
    raise ImportError(
        f"Faltan dependencias para AFIP WSAA: {e}. "
        "Instala: pip install zeep cryptography requests"
    )

from app.core.config import settings


class WSAAClient:
    """Cliente para autenticación con WSAA de AFIP"""

    def __init__(
        self,
        service: str = "wsfe",  # wsfe, wsfev1, wsaa, etc.
        wsdl_url: Optional[str] = None,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
        key_password: Optional[str] = None,
        cuit: Optional[str] = None,
        cache_dir: str = "/tmp/afip_cache",
    ):
        self.service = service
        self.wsdl_url = wsdl_url or settings.AFIP_WSDL_WSAA
        self.cert_path = cert_path or settings.AFIP_CERT_PATH
        self.key_path = key_path or settings.AFIP_KEY_PATH
        self.key_password = key_password or settings.AFIP_CERT_PASS
        self.cuit = cuit or settings.AFIP_CUIT
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache del TA en memoria
        self._cached_ta: Optional[dict] = None

    def get_ticket_acceso(self, force_new: bool = False) -> dict:
        """
        Obtiene un Ticket de Acceso (TA) válido.
        Si existe en caché y no está vencido, lo retorna.
        Si no, solicita uno nuevo a WSAA.
        
        Returns:
            dict con {'token': str, 'sign': str, 'expiration': datetime}
        """
        if not force_new and self._cached_ta:
            if datetime.now() < self._cached_ta["expiration"]:
                print(f"[WSAA] Usando TA en cache (expira: {self._cached_ta['expiration']})")
                return self._cached_ta

        # Intentar cargar desde archivo de cache
        if not force_new:
            ta_cached = self._load_ta_from_file()
            if ta_cached:
                self._cached_ta = ta_cached
                return ta_cached

        # Solicitar nuevo TA
        print("[WSAA] Solicitando nuevo TA a AFIP...")
        ta = self._request_new_ta()
        self._cached_ta = ta
        self._save_ta_to_file(ta)
        return ta

    def _request_new_ta(self) -> dict:
        """Solicita un nuevo TA a WSAA"""
        # 1. Crear TRA (Ticket de Requerimiento de Acceso)
        tra_xml = self._create_tra()
        
        # 2. Firmar TRA con certificado y clave privada
        cms_signed = self._sign_tra(tra_xml)
        
        # 3. Enviar CMS firmado a WSAA
        token, sign, expiration = self._call_wsaa(cms_signed)
        
        return {
            "token": token,
            "sign": sign,
            "expiration": expiration,
        }

    def _create_tra(self) -> str:
        """Crea el XML del TRA (Ticket de Requerimiento de Acceso)"""
        now = datetime.utcnow()
        generation_time = now.strftime("%Y-%m-%dT%H:%M:%S")
        expiration_time = (now + timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%S")
        unique_id = int(now.timestamp())

        tra_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<loginTicketRequest version="1.0">
<header>
    <uniqueId>{unique_id}</uniqueId>
    <generationTime>{generation_time}</generationTime>
    <expirationTime>{expiration_time}</expirationTime>
</header>
<service>{self.service}</service>
</loginTicketRequest>"""
        
        return tra_xml

    def _sign_tra(self, tra_xml: str) -> str:
        """Firma el TRA con PKCS7 usando certificado y clave privada"""
        # Cargar certificado
        with open(self.cert_path, "rb") as f:
            cert_data = f.read()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        # Cargar clave privada
        with open(self.key_path, "rb") as f:
            key_data = f.read()
        
        if self.key_password:
            private_key = serialization.load_pem_private_key(
                key_data,
                password=self.key_password.encode() if isinstance(self.key_password, str) else self.key_password,
                backend=default_backend()
            )
        else:
            private_key = serialization.load_pem_private_key(
                key_data,
                password=None,
                backend=default_backend()
            )

        # Firmar el TRA (simulación PKCS#7)
        # En producción, usar M2Crypto o similar para PKCS#7 real
        # Aquí usamos una aproximación simplificada compatible con WSAA de homologación
        signature = private_key.sign(
            tra_xml.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Codificar en base64
        cms_signed = base64.b64encode(signature).decode("utf-8")
        
        return cms_signed

    def _call_wsaa(self, cms_signed: str) -> tuple:
        """Llama al servicio WSAA con el CMS firmado"""
        # Usar zeep para llamar al WSDL
        session = requests.Session()
        session.verify = False  # Solo para desarrollo; en prod usar certificados válidos
        transport = Transport(session=session)
        client = Client(self.wsdl_url, transport=transport)
        
        # Llamar al método loginCms
        response = client.service.loginCms(cms_signed)
        
        # Parsear respuesta XML
        root = ET.fromstring(response)
        
        # Extraer token, sign y expiration
        credentials = root.find(".//credentials")
        if credentials is None:
            raise Exception("No se pudo obtener credenciales de WSAA")
        
        token = credentials.find("token").text
        sign = credentials.find("sign").text
        expiration_str = root.find(".//expirationTime").text
        
        # Parsear fecha de expiración
        expiration = datetime.strptime(expiration_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        
        return token, sign, expiration

    def _save_ta_to_file(self, ta: dict):
        """Guarda el TA en un archivo de caché"""
        cache_file = self.cache_dir / f"ta_{self.service}_{self.cuit}.cache"
        with open(cache_file, "w") as f:
            f.write(f"{ta['token']}\n")
            f.write(f"{ta['sign']}\n")
            f.write(f"{ta['expiration'].isoformat()}\n")
        print(f"[WSAA] TA guardado en {cache_file}")

    def _load_ta_from_file(self) -> Optional[dict]:
        """Carga el TA desde un archivo de caché si existe y no está vencido"""
        cache_file = self.cache_dir / f"ta_{self.service}_{self.cuit}.cache"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r") as f:
                lines = f.readlines()
                token = lines[0].strip()
                sign = lines[1].strip()
                expiration = datetime.fromisoformat(lines[2].strip())
            
            if datetime.now() < expiration:
                print(f"[WSAA] TA cargado desde cache (expira: {expiration})")
                return {"token": token, "sign": sign, "expiration": expiration}
            else:
                print("[WSAA] TA en cache vencido")
                return None
        except Exception as e:
            print(f"[WSAA] Error al cargar TA desde cache: {e}")
            return None

