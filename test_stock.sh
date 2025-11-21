#!/bin/bash
set -e

TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('access_token') or d.get('token') or d.get('access') or '')")
auth="Authorization: Bearer $TOKEN"

echo "=== Creando Proveedor ==="
PROVEEDOR_ID=$(curl -s -X POST http://localhost:8000/proveedores -H "$auth" -H "Content-Type: application/json" -d '{"nombre":"Proveedor A","cuit":"20123456780","telefono":"1144442222","direccion":"Av. Siempreviva 742"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
echo "Proveedor ID: $PROVEEDOR_ID"

echo "=== Creando Producto (stock=5) ==="
PRODUCTO_ID=$(curl -s -X POST http://localhost:8000/productos -H "$auth" -H "Content-Type: application/json" -d "{\"nombre\":\"Batería 12V\",\"precio\":150000,\"stock\":5,\"proveedor_id\":1}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
echo "Producto ID: $PRODUCTO_ID"

echo "=== Creando Cliente ==="
CLIENTE_ID=$(curl -s -X POST http://localhost:8000/clientes -H "$auth" -H "Content-Type: application/json" -d '{"nombre":"Cliente Demo","cuit":"20333444559","telefono":"1166663333"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
echo "Cliente ID: $CLIENTE_ID"

echo "=== Stock Inicial ==="
STOCK_INICIAL=$(curl -s http://localhost:8000/productos/1 -H "$auth" | python3 -c "import sys, json; print(json.load(sys.stdin).get('stock', 0))")
echo "Stock inicial: $STOCK_INICIAL"

echo "=== Creando Venta (3 unidades) ==="
VENTA_RESPONSE=$(curl -s -X POST http://localhost:8000/ventas -H "$auth" -H "Content-Type: application/json" -d '{"cliente_id":1,"items":[{"producto_id":1,"cantidad":3,"precio_unitario":150000}]}')
echo "Venta creada: $VENTA_RESPONSE"

echo "=== Stock Post Venta (debería ser 2) ==="
STOCK_POST_VENTA=$(curl -s http://localhost:8000/productos/1 -H "$auth" | python3 -c "import sys, json; print(json.load(sys.stdin).get('stock', 0))")
echo "Stock post venta: $STOCK_POST_VENTA"

echo "=== Intentando Venta Insuficiente (4 unidades, debería dar 409) ==="
VENTA_ERROR=$(curl -i -s -X POST http://localhost:8000/ventas -H "$auth" -H "Content-Type: application/json" -d '{"cliente_id":1,"items":[{"producto_id":1,"cantidad":4,"precio_unitario":150000}]}' | head -n 1)
echo "Respuesta: $VENTA_ERROR"

echo "=== Creando Compra (10 unidades) ==="
COMPRA_RESPONSE=$(curl -s -X POST http://localhost:8000/compras -H "$auth" -H "Content-Type: application/json" -d '{"proveedor_id":1,"items":[{"producto_id":1,"cantidad":10,"costo_unitario":120000}]}')
echo "Compra creada: $COMPRA_RESPONSE"

echo "=== Stock Post Compra (debería ser 12) ==="
STOCK_POST_COMPRA=$(curl -s http://localhost:8000/productos/1 -H "$auth" | python3 -c "import sys, json; print(json.load(sys.stdin).get('stock', 0))")
echo "Stock post compra: $STOCK_POST_COMPRA"

echo "=== Resumen ==="
echo "Stock inicial: $STOCK_INICIAL"
echo "Stock post venta (3u): $STOCK_POST_VENTA (debería ser 2)"
echo "Stock post compra (10u): $STOCK_POST_COMPRA (debería ser 12)"

