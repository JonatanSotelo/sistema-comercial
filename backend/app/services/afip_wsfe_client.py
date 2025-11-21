# app/services/afip_wsfe_client.py
"""
Cliente WSFEv1 (Web Services de Facturación Electrónica v1) de AFIP
Emite comprobantes electrónicos tipo A, B, C con CAE.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from zeep import Client
    from zeep.transports import Transport
    import requests
except ImportError as e:
    raise ImportError(
        f"Faltan dependencias para AFIP WSFEv1: {e}. "
        "Instala: pip install zeep requests"
    )

from app.core.config import settings
from app.services.afip_wsaa import WSAAClient


class WSFEv1Client:
    """Cliente para el servicio de Facturación Electrónica v1 de AFIP"""

    def __init__(
        self,
        wsdl_url: Optional[str] = None,
        cuit: Optional[str] = None,
    ):
        self.wsdl_url = wsdl_url or settings.AFIP_WSDL_WSFEV1
        self.cuit = cuit or settings.AFIP_CUIT
        
        # Cliente WSAA para autenticación
        self.wsaa = WSAAClient(service="wsfe")
        
        # Cliente zeep para WSFEv1
        session = requests.Session()
        session.verify = False  # Solo para desarrollo; en prod usar certificados válidos
        transport = Transport(session=session)
        self.client = Client(self.wsdl_url, transport=transport)

    def _get_auth_credentials(self) -> Dict[str, str]:
        """Obtiene las credenciales de autenticación (token y sign) desde WSAA"""
        ta = self.wsaa.get_ticket_acceso()
        return {
            "Token": ta["token"],
            "Sign": ta["sign"],
            "Cuit": self.cuit,
        }

    def fe_comp_ultimo_autorizado(self, pto_vta: int, tipo_cbte: int) -> int:
        """
        Obtiene el último comprobante autorizado para un punto de venta y tipo de comprobante.
        
        Args:
            pto_vta: Punto de venta
            tipo_cbte: Tipo de comprobante (1=A, 6=B, 11=C)
        
        Returns:
            Número del último comprobante autorizado (0 si no hay ninguno)
        """
        try:
            auth = self._get_auth_credentials()
            response = self.client.service.FECompUltimoAutorizado(
                Auth=auth,
                PtoVta=pto_vta,
                CbteTipo=tipo_cbte
            )
            
            if hasattr(response, 'CbteNro'):
                return int(response.CbteNro)
            return 0
        except Exception as e:
            print(f"[WSFEv1] Error al obtener último comprobante: {e}")
            raise Exception(f"Error AFIP FECompUltimoAutorizado: {str(e)}")

    def fe_cae_solicitar(
        self,
        pto_vta: int,
        tipo_cbte: int,
        concepto: int,
        doc_tipo: int,
        doc_nro: str,
        fecha_cbte: str,
        imp_total: float,
        imp_tot_conc: float,
        imp_neto: float,
        imp_op_ex: float,
        imp_trib: float,
        imp_iva: float,
        moneda_id: str,
        moneda_ctz: float,
        iva_alics: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Solicita la autorización de un comprobante (CAE).
        
        Args:
            pto_vta: Punto de venta
            tipo_cbte: Tipo de comprobante (1=A, 6=B, 11=C)
            concepto: Concepto (1=Productos, 2=Servicios, 3=Mixto)
            doc_tipo: Tipo de documento del receptor (80=CUIT, 96=DNI, 99=CF)
            doc_nro: Número de documento del receptor
            fecha_cbte: Fecha del comprobante (YYYYMMDD)
            imp_total: Importe total
            imp_tot_conc: Importe total no gravado
            imp_neto: Importe neto gravado
            imp_op_ex: Importe exento
            imp_trib: Importe tributos
            imp_iva: Importe IVA
            moneda_id: ID de moneda (PES para pesos argentinos)
            moneda_ctz: Cotización de moneda
            iva_alics: Lista de alícuotas de IVA aplicadas
        
        Returns:
            Dict con los datos del CAE autorizado o error
        """
        try:
            # Obtener último comprobante
            ultimo_cbte = self.fe_comp_ultimo_autorizado(pto_vta, tipo_cbte)
            proximo_cbte = ultimo_cbte + 1
            
            # Construir el comprobante
            fecae_det = {
                "Concepto": concepto,
                "DocTipo": doc_tipo,
                "DocNro": int(doc_nro) if doc_nro.isdigit() else 0,
                "CbteDesde": proximo_cbte,
                "CbteHasta": proximo_cbte,
                "CbteFch": fecha_cbte,
                "ImpTotal": round(imp_total, 2),
                "ImpTotConc": round(imp_tot_conc, 2),
                "ImpNeto": round(imp_neto, 2),
                "ImpOpEx": round(imp_op_ex, 2),
                "ImpTrib": round(imp_trib, 2),
                "ImpIVA": round(imp_iva, 2),
                "MonId": moneda_id,
                "MonCotiz": moneda_ctz,
            }
            
            # Agregar alícuotas de IVA si existen
            if iva_alics:
                iva_list = []
                for alic in iva_alics:
                    iva_list.append({
                        "Id": alic["id"],  # 3=0%, 4=10.5%, 5=21%, 6=27%
                        "BaseImp": round(alic["base_imponible"], 2),
                        "Importe": round(alic["importe"], 2),
                    })
                fecae_det["Iva"] = {"AlicIva": iva_list}
            
            # Obtener credenciales de autenticación
            auth = self._get_auth_credentials()
            
            # Construir solicitud
            fecae_request = {
                "FeCabReq": {
                    "CantReg": 1,
                    "PtoVta": pto_vta,
                    "CbteTipo": tipo_cbte,
                },
                "FeDetReq": {
                    "FECAEDetRequest": [fecae_det]
                }
            }
            
            # Llamar al servicio
            print(f"[WSFEv1] Solicitando CAE para comprobante {pto_vta}-{tipo_cbte}-{proximo_cbte}")
            response = self.client.service.FECAESolicitar(
                Auth=auth,
                FeCAEReq=fecae_request
            )
            
            # Procesar respuesta
            if hasattr(response, 'FeDetResp') and response.FeDetResp:
                det_resp = response.FeDetResp.FECAEDetResponse[0]
                
                # Verificar resultado
                resultado = det_resp.Resultado  # A=Aprobado, R=Rechazado
                
                if resultado == "A":
                    return {
                        "success": True,
                        "resultado": resultado,
                        "cae": det_resp.CAE,
                        "cae_vto": det_resp.CAEFchVto,
                        "nro_cbte": proximo_cbte,
                        "obs": self._extract_observations(det_resp) if hasattr(det_resp, 'Observaciones') else None,
                    }
                else:
                    # Rechazado
                    obs = self._extract_observations(det_resp) if hasattr(det_resp, 'Observaciones') else "Sin observaciones"
                    return {
                        "success": False,
                        "resultado": resultado,
                        "obs": obs,
                        "nro_cbte": proximo_cbte,
                    }
            else:
                # Error en la respuesta
                errors = self._extract_errors(response)
                return {
                    "success": False,
                    "resultado": "R",
                    "obs": errors,
                }
        
        except Exception as e:
            print(f"[WSFEv1] Error al solicitar CAE: {e}")
            return {
                "success": False,
                "resultado": "R",
                "obs": f"Error de comunicación: {str(e)}",
            }

    def _extract_observations(self, det_resp: Any) -> str:
        """Extrae observaciones del detalle de respuesta"""
        if not hasattr(det_resp, 'Observaciones'):
            return ""
        
        obs_list = []
        if hasattr(det_resp.Observaciones, 'Obs'):
            for obs in det_resp.Observaciones.Obs:
                msg = f"[{obs.Code}] {obs.Msg}"
                obs_list.append(msg)
        
        return " | ".join(obs_list) if obs_list else ""

    def _extract_errors(self, response: Any) -> str:
        """Extrae errores de la respuesta"""
        errors = []
        if hasattr(response, 'Errors') and response.Errors:
            if hasattr(response.Errors, 'Err'):
                for err in response.Errors.Err:
                    msg = f"[{err.Code}] {err.Msg}"
                    errors.append(msg)
        
        return " | ".join(errors) if errors else "Error desconocido"

    def dummy_test(self) -> Dict[str, Any]:
        """Ejecuta una prueba de conexión con el servicio (FEDummy)"""
        try:
            response = self.client.service.FEDummy()
            return {
                "success": True,
                "app_server": response.AppServer,
                "db_server": response.DbServer,
                "auth_server": response.AuthServer,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

