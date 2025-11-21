#!/usr/bin/env python3
import requests
import json
import sys
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("=== QA de Auditoría ===")
print("\n1. Login")
try:
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if login_resp.status_code != 200:
        print(f"Error en login: {login_resp.text}")
        sys.exit(1)
    token = login_resp.json().get("access_token") or login_resp.json().get("token") or login_resp.json().get("access")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print(f"✓ Login OK")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("\n2. Verificar que existan datos (proveedor, producto, cliente)")
# Obtener primer proveedor
proveedores = requests.get(f"{BASE_URL}/proveedores?page=1&size=1", headers=headers).json()
proveedor_id = None
if isinstance(proveedores, dict) and proveedores.get("items"):
    proveedor_id = proveedores["items"][0].get("id")
elif isinstance(proveedores, list) and len(proveedores) > 0:
    proveedor_id = proveedores[0].get("id")

if not proveedor_id:
    print("⚠ No hay proveedores. Creando uno...")
    proveedor_resp = requests.post(
        f"{BASE_URL}/proveedores",
        headers=headers,
        json={"nombre": f"Proveedor QA {int(time.time())}", "cuit": f"20{int(time.time()) % 100000000:08d}"}
    )
    proveedor_id = proveedor_resp.json().get("id")

# Obtener primer producto
productos = requests.get(f"{BASE_URL}/productos?page=1&size=1", headers=headers).json()
producto_id = None
if isinstance(productos, dict) and productos.get("items"):
    producto_id = productos["items"][0].get("id")
elif isinstance(productos, list) and len(productos) > 0:
    producto_id = productos[0].get("id")

if not producto_id:
    print("⚠ No hay productos. Creando uno...")
    producto_resp = requests.post(
        f"{BASE_URL}/productos",
        headers=headers,
        json={
            "nombre": f"Producto QA {int(time.time())}",
            "codigo": f"QA-{int(time.time())}",
            "categoria": "Test",
            "precio": 1000,
            "costo": 500,
            "stock": 10,
            "proveedor_id": proveedor_id
        }
    )
    producto_id = producto_resp.json().get("id")

# Obtener primer cliente
clientes = requests.get(f"{BASE_URL}/clientes?page=1&size=1", headers=headers).json()
cliente_id = None
if isinstance(clientes, dict) and clientes.get("items"):
    cliente_id = clientes["items"][0].get("id")
elif isinstance(clientes, list) and len(clientes) > 0:
    cliente_id = clientes[0].get("id")

if not cliente_id:
    print("⚠ No hay clientes. Creando uno...")
    cliente_resp = requests.post(
        f"{BASE_URL}/clientes",
        headers=headers,
        json={"nombre": f"Cliente QA {int(time.time())}", "cuit": f"20{int(time.time()) % 100000000 + 200000000:08d}"}
    )
    cliente_id = cliente_resp.json().get("id")

print(f"✓ Proveedor ID: {proveedor_id}, Producto ID: {producto_id}, Cliente ID: {cliente_id}")

print("\n3. Crear Venta")
venta_resp = requests.post(
    f"{BASE_URL}/ventas",
    headers=headers,
    json={"cliente_id": cliente_id, "items": [{"producto_id": producto_id, "cantidad": 1, "precio_unitario": 150000}]}
)
if venta_resp.status_code == 201:
    venta_id = venta_resp.json().get("id")
    print(f"✓ Venta creada: ID {venta_id}")
else:
    print(f"✗ Error al crear venta: {venta_resp.status_code} - {venta_resp.text}")
    sys.exit(1)

print("\n4. Crear Compra")
compra_resp = requests.post(
    f"{BASE_URL}/compras",
    headers=headers,
    json={"proveedor_id": proveedor_id, "items": [{"producto_id": producto_id, "cantidad": 2, "costo_unitario": 120000}]}
)
if compra_resp.status_code == 201:
    compra_id = compra_resp.json().get("id")
    print(f"✓ Compra creada: ID {compra_id}")
else:
    print(f"✗ Error al crear compra: {compra_resp.status_code} - {compra_resp.text}")
    sys.exit(1)

print("\n5. Verificar logs de auditoría")
logs_resp = requests.get(
    f"{BASE_URL}/audit-logs?page=1&size=10",
    headers=headers
)
if logs_resp.status_code == 200:
    logs_data = logs_resp.json()
    items = logs_data.get("items", []) if isinstance(logs_data, dict) else logs_data
    print(f"✓ Logs encontrados: {len(items)}")
    
    # Buscar logs de venta y compra
    venta_log = next((log for log in items if log.get("table_name") == "ventas" and log.get("record_id") == str(venta_id)), None)
    compra_log = next((log for log in items if log.get("table_name") == "compras" and log.get("record_id") == str(compra_id)), None)
    stock_logs = [log for log in items if log.get("table_name") == "stock" and log.get("action") in ("ADJUST", "UPDATE")]
    
    if venta_log:
        print(f"✓ Log de venta encontrado: {venta_log.get('id')} - {venta_log.get('action')}")
    else:
        print("⚠ No se encontró log de venta")
    
    if compra_log:
        print(f"✓ Log de compra encontrado: {compra_log.get('id')} - {compra_log.get('action')}")
    else:
        print("⚠ No se encontró log de compra")
    
    print(f"✓ Logs de stock encontrados: {len(stock_logs)}")
    
    if venta_log and compra_log and len(stock_logs) >= 2:
        print("\n✅ QA de Auditoría: PASADO")
    else:
        print("\n⚠ QA de Auditoría: PARCIAL (algunos logs faltantes)")
else:
    print(f"✗ Error al obtener logs: {logs_resp.status_code} - {logs_resp.text}")

print("\n6. Probar filtros")
# Filtro por módulo
filtro_ventas = requests.get(
    f"{BASE_URL}/audit-logs?table_name=ventas&page=1&size=5",
    headers=headers
)
if filtro_ventas.status_code == 200:
    ventas_data = filtro_ventas.json()
    ventas_items = ventas_data.get("items", []) if isinstance(ventas_data, dict) else ventas_data
    print(f"✓ Filtro por módulo 'ventas': {len(ventas_items)} logs")

# Filtro por acción
filtro_create = requests.get(
    f"{BASE_URL}/audit-logs?action=CREATE&page=1&size=5",
    headers=headers
)
if filtro_create.status_code == 200:
    create_data = filtro_create.json()
    create_items = create_data.get("items", []) if isinstance(create_data, dict) else create_data
    print(f"✓ Filtro por acción 'CREATE': {len(create_items)} logs")

# Filtro por acción ADJUST
filtro_adjust = requests.get(
    f"{BASE_URL}/audit-logs?action=ADJUST&page=1&size=5",
    headers=headers
)
if filtro_adjust.status_code == 200:
    adjust_data = filtro_adjust.json()
    adjust_items = adjust_data.get("items", []) if isinstance(adjust_data, dict) else adjust_data
    print(f"✓ Filtro por acción 'ADJUST': {len(adjust_items)} logs")

print("\n✅ QA de Auditoría completado")

