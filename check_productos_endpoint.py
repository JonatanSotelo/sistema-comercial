#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

print("=== 1. Verificar métodos registrados para /productos ===")
try:
    resp = requests.options(f"{BASE_URL}/productos")
    print(f"OPTIONS status: {resp.status_code}")
    print(f"Allow header: {resp.headers.get('Allow', 'NOT FOUND')}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== 2. Verificar OpenAPI para /productos ===")
try:
    resp = requests.get(f"{BASE_URL}/openapi.json")
    openapi = resp.json()
    
    # Buscar rutas de productos
    paths = openapi.get("paths", {})
    productos_paths = {k: v for k in paths.keys() if "/productos" in k}
    
    print(f"Rutas encontradas con '/productos':")
    for path, methods in productos_paths.items():
        print(f"\n  {path}:")
        for method in methods.keys():
            if method.lower() != "options":
                print(f"    - {method.upper()}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== 3. Verificar si POST /productos existe ===")
try:
    if "/productos" in paths:
        productos_methods = paths["/productos"]
        if "post" in productos_methods:
            print("✓ POST /productos existe en OpenAPI")
            print(f"  Detalles: {json.dumps(productos_methods['post'], indent=2)}")
        else:
            print("✗ POST /productos NO existe en OpenAPI")
            print(f"  Métodos disponibles: {list(productos_methods.keys())}")
    else:
        print("✗ /productos no existe en paths")
        print(f"  Rutas disponibles con 'productos': {list(productos_paths.keys())}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== 4. Intentar POST /productos con autenticación ===")
try:
    # Login
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if login_resp.status_code == 200:
        token = login_resp.json().get("access_token") or login_resp.json().get("token") or login_resp.json().get("access")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Intentar POST con código único
        import time
        codigo_unico = f"TEST-{int(time.time())}"
        post_resp = requests.post(
            f"{BASE_URL}/productos",
            headers=headers,
            json={
                "nombre": "Test Product",
                "codigo": codigo_unico,
                "categoria": "Test",
                "precio": 1000,
                "costo": 500,
                "stock": 1
            }
        )
        print(f"POST /productos status: {post_resp.status_code}")
        print(f"  Response headers: {dict(post_resp.headers)}")
        if post_resp.status_code == 201:
            print(f"  ✓ Producto creado: {post_resp.json().get('id')}")
        elif post_resp.status_code == 405:
            print(f"  ✗ 405 Method Not Allowed - El POST no está disponible")
        else:
            print(f"  Error: {post_resp.text}")
    else:
        print(f"Login failed: {login_resp.status_code} - {login_resp.text}")
except Exception as e:
    print(f"Error: {e}")
