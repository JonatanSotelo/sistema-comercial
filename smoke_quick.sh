#!/bin/bash
set -e

BASE="${1:-http://localhost:8000}"
echo "🚀 SMOKE TEST QUICK - Sistema Comercial HTMX"
echo "Base URL: $BASE"
echo "=========================================="

# 0) Login OAuth2
echo ""
echo "== 0) Login OAuth2 =="
TOKEN_RESP=$(curl -s -X POST "$BASE/auth/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123&grant_type=password")

TOKEN=$(echo "$TOKEN_RESP" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login falló"
  echo "Response: $TOKEN_RESP"
  exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:20}..."
AUTH_HEADER="Authorization: Bearer $TOKEN"

# 1) Ventas (ping)
echo ""
echo "== 1) Ventas API =="
VENTAS=$(curl -s -H "$AUTH_HEADER" "$BASE/ventas/?page=1&size=1")
VENTA_ID=$(echo "$VENTAS" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$VENTA_ID" ]; then
  echo "⚠️  No hay ventas, creando una..."
  # Obtener cliente y producto
  CLIENTES=$(curl -s -H "$AUTH_HEADER" "$BASE/clientes/?page=1&size=1")
  CLIENTE_ID=$(echo "$CLIENTES" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  
  PRODUCTOS=$(curl -s -H "$AUTH_HEADER" "$BASE/productos/?page=1&size=1")
  PRODUCTO_ID=$(echo "$PRODUCTOS" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  
  if [ -z "$CLIENTE_ID" ] || [ -z "$PRODUCTO_ID" ]; then
    echo "❌ No hay clientes o productos para crear venta"
    exit 1
  fi
  
  NUEVA_VENTA=$(curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
    "$BASE/ventas/" -d "{
      \"cliente_id\": $CLIENTE_ID,
      \"total\": 100.0,
      \"items\": [{
        \"producto_id\": $PRODUCTO_ID,
        \"cantidad\": 1,
        \"precio_unitario\": 100.0
      }]
    }")
  VENTA_ID=$(echo "$NUEVA_VENTA" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
fi

echo "✅ Venta ID: $VENTA_ID"

# 2) Cobro simple
echo ""
echo "== 2) Crear Cobro =="
COBRO=$(curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  "$BASE/cobros/" -d "{
    \"venta_id\": $VENTA_ID,
    \"medio\": \"EFECTIVO\",
    \"importe\": 50.0,
    \"referencia\": \"QA-SMOKE\"
  }")

COBRO_ID=$(echo "$COBRO" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$COBRO_ID" ]; then
  echo "❌ Cobro falló"
  echo "Response: $COBRO"
  exit 1
fi

echo "✅ Cobro ID: $COBRO_ID"

# 3) PDF Recibo
echo ""
echo "== 3) Descargar PDF Recibo =="
PDF_FILE="recibo_${COBRO_ID}.pdf"
curl -s -H "$AUTH_HEADER" "$BASE/cobros/$COBRO_ID/pdf" -o "$PDF_FILE"

PDF_SIZE=$(wc -c < "$PDF_FILE" 2>/dev/null || echo "0")

if [ "$PDF_SIZE" -gt 1500 ]; then
  echo "✅ PDF generado: $PDF_FILE ($PDF_SIZE bytes)"
else
  echo "❌ PDF muy pequeño o vacío ($PDF_SIZE bytes)"
  exit 1
fi

# 4) IVA Compras Export
echo ""
echo "== 4) Export IVA Compras CSV =="
CSV_FILE="iva_compras.csv"
curl -s -H "$AUTH_HEADER" "$BASE/reportes/libro-iva-compras?desde=2025-01-01&hasta=2025-12-31&format=csv" -o "$CSV_FILE"

CSV_SIZE=$(wc -c < "$CSV_FILE" 2>/dev/null || echo "0")

if [ "$CSV_SIZE" -gt 200 ]; then
  echo "✅ CSV generado: $CSV_FILE ($CSV_SIZE bytes)"
else
  echo "❌ CSV muy pequeño o vacío ($CSV_SIZE bytes)"
  exit 1
fi

# 5) Backups
echo ""
echo "== 5) Backups =="
BACKUP_CREATE=$(curl -s -X POST -H "$AUTH_HEADER" "$BASE/backups/create")
echo "Backup create response: $(echo $BACKUP_CREATE | head -c 100)..."

BACKUPS_LIST=$(curl -s -H "$AUTH_HEADER" "$BASE/backups/list")
BACKUP_COUNT=$(echo "$BACKUPS_LIST" | grep -o '"filename"' | wc -l)

if [ "$BACKUP_COUNT" -ge 1 ]; then
  echo "✅ Backups OK (count: $BACKUP_COUNT)"
else
  echo "❌ No hay backups disponibles"
  exit 1
fi

# Resumen
echo ""
echo "=========================================="
echo "✅ SMOKE TEST COMPLETADO"
echo ""
echo "Archivos generados:"
echo "  - $PDF_FILE ($PDF_SIZE bytes)"
echo "  - $CSV_FILE ($CSV_SIZE bytes)"
echo ""
echo "Verificaciones:"
echo "  ✅ Login OAuth2"
echo "  ✅ Ventas API"
echo "  ✅ Cobro creado"
echo "  ✅ PDF Recibo"
echo "  ✅ CSV IVA Compras"
echo "  ✅ Backups"

