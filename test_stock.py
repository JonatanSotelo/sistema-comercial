#!/usr/bin/env python3
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"
TIMESTAMP = int(time.time())

# Login
print("=== Login ===")
try:
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    print(f"Login status: {login_resp.status_code}")
    if login_resp.status_code != 200:
        print(f"Login error: {login_resp.text}")
        # Intentar con OAuth2
        print("Intentando con OAuth2...")
        login_resp = requests.post(
            f"{BASE_URL}/auth/oauth2/token",
            data={"username": "admin", "password": "admin123", "grant_type": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"OAuth2 status: {login_resp.status_code}")
        if login_resp.status_code != 200:
            print(f"OAuth2 error: {login_resp.text}")
            sys.exit(1)
except Exception as e:
    print(f"Error en login: {e}")
    sys.exit(1)

login_resp.raise_for_status()
token_data = login_resp.json()
token = token_data.get("access_token") or token_data.get("token") or token_data.get("access")
if not token:
    print(f"Error: No se obtuvo token. Respuesta: {token_data}")
    sys.exit(1)
print(f"Token obtenido: {token[:20]}...")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Crear Proveedor
print("\n=== Creando Proveedor ===")
proveedor_cuit = f"20{TIMESTAMP % 100000000:08d}"
proveedor_resp = requests.post(
    f"{BASE_URL}/proveedores",
    headers=headers,
    json={"nombre": f"Proveedor A {TIMESTAMP}", "cuit": proveedor_cuit, "telefono": "1144442222", "direccion": "Av. Siempreviva 742"}
)
proveedor_resp.raise_for_status()
proveedor_id = proveedor_resp.json().get("id")
print(f"Proveedor ID: {proveedor_id}")

# Crear Producto
print("\n=== Creando Producto (stock=5) ===")
producto_codigo = f"BAT-12V-{TIMESTAMP}"
producto_resp = requests.post(
    f"{BASE_URL}/productos",
    headers=headers,
    json={
        "nombre": "Batería 12V",
        "codigo": producto_codigo,
        "categoria": "Baterías",
        "precio": 150000,
        "costo": 120000,
        "stock": 5,
        "proveedor_id": proveedor_id
    }
)
print(f"Producto status: {producto_resp.status_code}")
if producto_resp.status_code != 201:
    print(f"Producto error: {producto_resp.text}")
    sys.exit(1)
producto_resp.raise_for_status()
producto_id = producto_resp.json().get("id")
print(f"Producto ID: {producto_id}")

# Crear Cliente
print("\n=== Creando Cliente ===")
cliente_cuit = f"20{TIMESTAMP % 100000000 + 100000000:08d}"
cliente_resp = requests.post(
    f"{BASE_URL}/clientes",
    headers=headers,
    json={"nombre": "Cliente Demo", "cuit": cliente_cuit, "telefono": "1166663333"}
)
cliente_resp.raise_for_status()
cliente_id = cliente_resp.json().get("id")
print(f"Cliente ID: {cliente_id}")

# Stock Inicial
print("\n=== Stock Inicial ===")
producto_get = requests.get(f"{BASE_URL}/productos/{producto_id}", headers=headers)
producto_get.raise_for_status()
stock_inicial = producto_get.json().get("stock", 0)
print(f"Stock inicial: {stock_inicial}")

# Crear Venta (3 unidades)
print("\n=== Creando Venta (3 unidades) ===")
venta_resp = requests.post(
    f"{BASE_URL}/ventas",
    headers=headers,
    json={"cliente_id": cliente_id, "items": [{"producto_id": producto_id, "cantidad": 3, "precio_unitario": 150000}]}
)
venta_resp.raise_for_status()
print(f"Venta creada: {venta_resp.json()}")

# Stock Post Venta
print("\n=== Stock Post Venta (debería ser 2) ===")
producto_get = requests.get(f"{BASE_URL}/productos/{producto_id}", headers=headers)
producto_get.raise_for_status()
stock_post_venta = producto_get.json().get("stock", 0)
print(f"Stock post venta: {stock_post_venta}")

# Intentar Venta Insuficiente (4 unidades, debería dar 409)
print("\n=== Intentando Venta Insuficiente (4 unidades, debería dar 409) ===")
venta_error_resp = requests.post(
    f"{BASE_URL}/ventas",
    headers=headers,
    json={"cliente_id": cliente_id, "items": [{"producto_id": producto_id, "cantidad": 4, "precio_unitario": 150000}]}
)
print(f"Status code: {venta_error_resp.status_code}")
if venta_error_resp.status_code == 409:
    print("✓ Correcto: Se rechazó la venta por stock insuficiente (409)")
else:
    print(f"⚠ Error: Se esperaba 409, se obtuvo {venta_error_resp.status_code}")
    print(f"Respuesta: {venta_error_resp.text}")

# Crear Compra (10 unidades)
print("\n=== Creando Compra (10 unidades) ===")
compra_resp = requests.post(
    f"{BASE_URL}/compras",
    headers=headers,
    json={"proveedor_id": proveedor_id, "items": [{"producto_id": producto_id, "cantidad": 10, "costo_unitario": 120000}]}
)
compra_resp.raise_for_status()
print(f"Compra creada: {compra_resp.json()}")

# Stock Post Compra
print("\n=== Stock Post Compra (debería ser 12) ===")
producto_get = requests.get(f"{BASE_URL}/productos/{producto_id}", headers=headers)
producto_get.raise_for_status()
stock_post_compra = producto_get.json().get("stock", 0)
print(f"Stock post compra: {stock_post_compra}")

# Resumen
print("\n=== Resumen ===")
print(f"Stock inicial: {stock_inicial} (esperado: 5)")
print(f"Stock post venta (3u): {stock_post_venta} (esperado: 2)")
print(f"Stock post compra (10u): {stock_post_compra} (esperado: 12)")

# Verificación
if stock_inicial == 5 and stock_post_venta == 2 and stock_post_compra == 12:
    print("\n✓ Todas las pruebas de stock pasaron correctamente!")
    sys.exit(0)
else:
    print("\n✗ Algunas pruebas de stock fallaron")
    sys.exit(1)

