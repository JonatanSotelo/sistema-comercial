#!/usr/bin/env python3
"""
Script para probar los endpoints de reportes financieros:
- GET /reportes-financieros/ultimo - Obtener último reporte
- GET /reportes-financieros/historial - Obtener historial de reportes
"""

import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime

BASE_URL = "http://localhost:8000"

def hacer_request(url, method="GET", data=None, headers=None):
    """Hace una petición HTTP"""
    if headers is None:
        headers = {}
    
    req = urllib.request.Request(url, headers=headers)
    req.get_method = lambda: method
    
    if data:
        data = urllib.parse.urlencode(data).encode('utf-8')
        req.data = data
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8')
            return e.code, json.loads(body) if body else None
        except:
            return e.code, None
    except Exception as e:
        raise Exception(f"Error de conexión: {e}")

def obtener_token():
    """Obtiene un token de autenticación"""
    try:
        # Intentar login con admin por defecto
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        status, response = hacer_request(
            f"{BASE_URL}/auth/login",
            method="POST",
            data=login_data
        )
        if status == 200 and response:
            return response.get("access_token")
        else:
            print(f"Error al obtener token: {status}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def obtener_ultimo_reporte(token):
    """Obtiene el último reporte financiero"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        status, response = hacer_request(
            f"{BASE_URL}/reportes-financieros/ultimo",
            headers=headers
        )
        if status == 200:
            return response
        elif status == 404:
            print("No se encontraron reportes financieros")
            return None
        else:
            print(f"Error: {status}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def obtener_historial(token, limit=10):
    """Obtiene el historial de reportes financieros"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/reportes-financieros/historial?limit={limit}"
    try:
        status, response = hacer_request(url, headers=headers)
        if status == 200:
            return response
        else:
            print(f"Error: {status}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def formatear_reporte(reporte):
    """Formatea un reporte para mostrar"""
    if not reporte:
        return "No hay reporte"
    
    fecha_gen = reporte.get("fecha_generacion", "N/A")
    if fecha_gen and fecha_gen != "N/A":
        try:
            fecha_gen = datetime.fromisoformat(fecha_gen.replace("Z", "+00:00"))
            fecha_gen = fecha_gen.strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
    
    return f"""
═══════════════════════════════════════════════════════════
REPORTE FINANCIERO
═══════════════════════════════════════════════════════════
ID: {reporte.get('id', 'N/A')}
Nombre: {reporte.get('nombre', 'N/A')}
Tipo: {reporte.get('tipo', 'N/A')}
Período: {reporte.get('periodo', 'N/A')}
Estado: {reporte.get('estado', 'N/A')}
Fecha Generación: {fecha_gen}
Fecha Inicio: {reporte.get('fecha_inicio', 'N/A')}
Fecha Fin: {reporte.get('fecha_fin', 'N/A')}
───────────────────────────────────────────────────────────
RESULTADOS:
  Total Ingresos: ${reporte.get('total_ingresos', 0):,.2f}
  Total Costos: ${reporte.get('total_costos', 0):,.2f}
  Total Gastos: ${reporte.get('total_gastos', 0):,.2f}
  Ganancia Neta: ${reporte.get('ganancia_neta', 0):,.2f}
  Margen Bruto: {reporte.get('margen_bruto', 0):.2f}%
  Margen Neto: {reporte.get('margen_neto', 0):.2f}%
═══════════════════════════════════════════════════════════
"""

def main():
    print("=" * 60)
    print("PRUEBA DE ENDPOINTS DE REPORTES FINANCIEROS")
    print("=" * 60)
    print()
    
    # Verificar conexión
    try:
        status, _ = hacer_request(f"{BASE_URL}/health")
        if status != 200:
            print(f"⚠️  El servidor no está respondiendo correctamente (Status: {status})")
            sys.exit(1)
    except Exception as e:
        print("❌ Error: No se puede conectar al servidor")
        print(f"   Asegúrate de que el servidor esté corriendo en {BASE_URL}")
        print(f"   Error: {e}")
        sys.exit(1)
    
    print("✅ Servidor disponible")
    print()
    
    # Obtener token
    print("🔐 Obteniendo token de autenticación...")
    token = obtener_token()
    if not token:
        print("❌ No se pudo obtener el token de autenticación")
        sys.exit(1)
    print("✅ Token obtenido")
    print()
    
    # Obtener último reporte
    print("📊 Obteniendo último reporte financiero...")
    print("-" * 60)
    ultimo_reporte = obtener_ultimo_reporte(token)
    if ultimo_reporte:
        print(formatear_reporte(ultimo_reporte))
    else:
        print("No se encontró ningún reporte")
    print()
    
    # Obtener historial
    print("📋 Obteniendo historial de reportes (últimos 10)...")
    print("-" * 60)
    historial = obtener_historial(token, limit=10)
    if historial and len(historial) > 0:
        print(f"Total de reportes en historial: {len(historial)}")
        print()
        print("ÚLTIMO REPORTE DEL HISTORIAL:")
        print(formatear_reporte(historial[0]))
        
        if len(historial) > 1:
            print(f"\n... y {len(historial) - 1} reporte(s) más en el historial")
    else:
        print("No se encontraron reportes en el historial")
    print()
    
    print("=" * 60)
    print("✅ Prueba completada")
    print("=" * 60)

if __name__ == "__main__":
    main()

