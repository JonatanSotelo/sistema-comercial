
#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000}"

echo "[1/12] GET /app/login"
curl -sSf -o /dev/null "$BASE/app/login"

echo "[2/12] GET /app/dashboard (sin sesión redirige a login)"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/dashboard")
test "$code" = "200" -o "$code" = "302"

echo "[3/12] GET /app/productos (puede requerir login según backend)"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/productos")
test "$code" = "200" -o "$code" = "302"

echo "[4/12] GET /app/productos/table (HTMX partial)"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/productos/table")
test "$code" = "200" -o "$code" = "302"

echo "[5/12] GET /app/clientes"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/clientes")
test "$code" = "200" -o "$code" = "302"

echo "[6/12] GET /app/clientes/table"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/clientes/table")
test "$code" = "200" -o "$code" = "302"

echo "[7/12] GET /app/proveedores"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/proveedores")
test "$code" = "200" -o "$code" = "302"

echo "[8/12] GET /app/proveedores/table"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/proveedores/table")
test "$code" = "200" -o "$code" = "302"

echo "[9/12] GET /app/ventas"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/ventas")
test "$code" = "200" -o "$code" = "302"

echo "[10/12] GET /app/ventas/table"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/ventas/table")
test "$code" = "200" -o "$code" = "302"

echo "[11/12] GET /app/compras"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/compras")
test "$code" = "200" -o "$code" = "302"

echo "[12/14] GET /app/compras/table"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/compras/table")
test "$code" = "200" -o "$code" = "302"

echo "[13/14] GET /app/auditoria"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/auditoria")
test "$code" = "200" -o "$code" = "302"

echo "[14/16] GET /app/auditoria/table"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/auditoria/table")
test "$code" = "200" -o "$code" = "302"

echo "[15/16] GET /app/reportes"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/reportes")
test "$code" = "200" -o "$code" = "302"

echo "[16/18] GET /app/reportes/ventas/table"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/reportes/ventas/table")
test "$code" = "200" -o "$code" = "302"

echo "[17/18] GET /app/backups"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/backups")
test "$code" = "200" -o "$code" = "302"

echo "[18/18] GET /backups/list"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/backups/list")
test "$code" = "200" -o "$code" = "302" -o "$code" = "401"

echo "[W1] POST /integrations/whatsapp/orders (quote)"
WHATS_ORDERS_TOKEN="${WHATS_ORDERS_TOKEN:-test-token-123}"
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/integrations/whatsapp/orders" \
  -H "X-Integration-Token: $WHATS_ORDERS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone":"5491100000000","customer_name":"QA Whats","confirm":false,"items":[{"query":"bateria 12v","cantidad":1}]}')
test "$code" = "200" -o "$code" = "400" -o "$code" = "409"

echo "[W2] GET /app/integraciones/whatsapp"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/integraciones/whatsapp")
test "$code" = "200" -o "$code" = "302"

echo "[P1] GET /app/pedidos"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/pedidos")
test "$code" = "200" -o "$code" = "302"

echo "[P2] GET /app/pedidos/table"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/pedidos/table")
test "$code" = "200" -o "$code" = "302"

echo "[P3] API create pedido (requiere auth)"
# Intentar login para obtener token
TOKEN_RESPONSE=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}')
TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
  TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
fi
if [ -z "$TOKEN" ]; then
  TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access":"[^"]*' | cut -d'"' -f4)
fi

if [ -n "$TOKEN" ]; then
  echo "[P4] API create pedido con token"
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/pedidos" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"cliente_id":null,"items":[{"producto_id":1,"cantidad":1,"precio_unitario":100.0}],"nota":"QA smoke"}')
  test "$code" = "201" -o "$code" = "404" -o "$code" = "400"
  
  echo "[P5] API list pedidos"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/pedidos?size=5" \
    -H "Authorization: Bearer $TOKEN")
  test "$code" = "200"
  
  # Intentar obtener packing HTML del primer pedido (puede no existir)
  echo "[P6] GET /pedidos/1/packing (HTML)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/pedidos/1/packing")
  test "$code" = "200" -o "$code" = "404"
  
  echo "[P7] GET /pedidos/1/packing.pdf"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/pedidos/1/packing.pdf")
  test "$code" = "200" -o "$code" = "404"
  
  echo "[P8] GET /reportes/pedidos"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/reportes/pedidos?group_by=estado" \
    -H "Authorization: Bearer $TOKEN")
  test "$code" = "200"
  
  # Tests de RESERVAS
  echo "[R1] Lookup producto devuelve disponible"
  code=$(curl -s "$BASE/app/pedidos/lookup/producto?q=bateria" | grep -q "Disponible" && echo "200" || echo "500")
  test "$code" = "200"
  
  echo "[R2] API productos incluye disponible"
  response=$(curl -s "$BASE/productos?size=1" -H "Authorization: Bearer $TOKEN")
  echo "$response" | grep -q "disponible" || echo "[WARN] No se encontró campo disponible en productos"
  
  # Crear producto para test de reservas
  echo "[R3] Crear producto con stock limitado para test"
  PRODUCTO_RESPONSE=$(curl -s -X POST "$BASE/productos" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"nombre":"Producto Reserva Test","codigo":"PRESTEST","categoria":"TEST","precio":100.0,"costo":50.0,"stock":5,"stock_minimo":0}')
  PRODUCTO_ID=$(echo "$PRODUCTO_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  
  if [ -n "$PRODUCTO_ID" ] && [ "$PRODUCTO_ID" != "0" ]; then
    echo "[R4] Crear pedido 1 con producto de stock limitado"
    PEDIDO1_RESPONSE=$(curl -s -X POST "$BASE/pedidos" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"cliente_id\":null,\"items\":[{\"producto_id\":$PRODUCTO_ID,\"cantidad\":3,\"precio_unitario\":100.0}],\"nota\":\"Pedido 1 reservas\"}")
    PEDIDO1_ID=$(echo "$PEDIDO1_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    
    if [ -n "$PEDIDO1_ID" ] && [ "$PEDIDO1_ID" != "0" ]; then
      echo "[R5] Cambiar pedido 1 a EN_PREPARACION (crea reservas)"
      code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/pedidos/$PEDIDO1_ID/estado" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"estado":"EN_PREPARACION"}')
      test "$code" = "200"
      
      echo "[R6] Crear pedido 2 con mismo producto"
      PEDIDO2_RESPONSE=$(curl -s -X POST "$BASE/pedidos" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"cliente_id\":null,\"items\":[{\"producto_id\":$PRODUCTO_ID,\"cantidad\":3,\"precio_unitario\":100.0}],\"nota\":\"Pedido 2 reservas\"}")
      PEDIDO2_ID=$(echo "$PEDIDO2_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
      
      if [ -n "$PEDIDO2_ID" ] && [ "$PEDIDO2_ID" != "0" ]; then
        echo "[R7] Intentar cambiar pedido 2 a EN_PREPARACION (debe fallar por falta de disponible)"
        code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/pedidos/$PEDIDO2_ID/estado" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"estado":"EN_PREPARACION"}')
        # Debe ser 400 o 409 (conflicto de stock)
        test "$code" = "400" -o "$code" = "409"
        
        echo "[R8] Cancelar pedido 1 (libera reservas)"
        code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/pedidos/$PEDIDO1_ID/estado" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"estado":"CANCELADO"}')
        test "$code" = "200"
        
        echo "[R9] Ahora pedido 2 puede pasar a EN_PREPARACION"
        code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/pedidos/$PEDIDO2_ID/estado" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"estado":"EN_PREPARACION"}')
        test "$code" = "200"
      else
        echo "[R7-R9] SKIP: No se pudo crear pedido 2"
      fi
    else
      echo "[R5-R9] SKIP: No se pudo crear pedido 1"
    fi
  else
    echo "[R4-R9] SKIP: No se pudo crear producto de test"
  fi
  # Tests de NOTIFICACIONES + PDFS (v0.8.0)
  echo "[N1] Auditoría de notificaciones (verificar tabla exists)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/auditoria?q=notificaciones")
  test "$code" = "200" -o "$code" = "302"
  
  echo "[PDF1] Remito PDF de última venta (puede no existir)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/ventas/1/remito.pdf" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "404" -o "$code" = "401"
  
  echo "[PDF2] Etiqueta PDF de último pedido (puede no existir)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/pedidos/1/label.pdf" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "404" -o "$code" = "401"
  
  # Si tenemos pedidos creados en tests anteriores, probar con ellos
  if [ -n "$PEDIDO1_ID" ] && [ "$PEDIDO1_ID" != "0" ]; then
    echo "[PDF3] Etiqueta PDF del pedido creado en test"
    code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/pedidos/$PEDIDO1_ID/label.pdf" -H "Authorization: Bearer $TOKEN")
    test "$code" = "200" -o "$code" = "404"
  fi
  
  # Facturación AFIP (v0.9.0)
  echo "[FAC1] GET /app/facturacion"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/facturacion")
  test "$code" = "200" -o "$code" = "302"
  
  echo "[FAC2] GET /app/facturacion/table (HTMX partial)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/facturacion/table" -H "Cookie: access_token=$TOKEN")
  test "$code" = "200" -o "$code" = "401"
  
  echo "[FAC3] GET /facturacion (API list facturas)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/facturacion" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "401"
  
  echo "[FAC4] GET /reportes/libro-iva-ventas?desde=2025-01-01&hasta=2025-12-31&format=csv"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/reportes/libro-iva-ventas?desde=2025-01-01&hasta=2025-12-31&format=csv" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "401" -o "$code" = "400"
  
  echo "[FAC5] GET /facturas/1/pdf (puede no existir)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/facturacion/1/pdf" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "404" -o "$code" = "401"
  
  # Cobros & Caja (v0.9.1)
  echo "[COB1] GET /app/cobros"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/cobros")
  test "$code" = "200" -o "$code" = "302"
  
  echo "[COB2] GET /app/cobros/table (HTMX partial)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/cobros/table" -H "Cookie: access_token=$TOKEN")
  test "$code" = "200" -o "$code" = "401"
  
  echo "[COB3] GET /cobros (API list cobros)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/cobros" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "401"
  
  echo "[COB4] GET /clientes/1/saldo (puede no existir)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/clientes/1/saldo" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "404" -o "$code" = "401"
  
  echo "[COB5] GET /cobros/1/pdf (puede no existir)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/cobros/1/pdf" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "404" -o "$code" = "401"
  
  # IVA Compras (v0.9.1)
  echo "[IVC1] GET /app/iva-compras"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/iva-compras")
  test "$code" = "200" -o "$code" = "302"
  
  echo "[IVC2] GET /app/iva-compras/table (HTMX partial)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/iva-compras/table" -H "Cookie: access_token=$TOKEN")
  test "$code" = "200" -o "$code" = "401"
  
  echo "[IVC3] GET /iva-compras (API list)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/iva-compras" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "401"
  
  echo "[IVC4] GET /reportes/libro-iva-compras?desde=2025-01-01&hasta=2025-12-31&format=csv"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/reportes/libro-iva-compras?desde=2025-01-01&hasta=2025-12-31&format=csv" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "401" -o "$code" = "400"
  
  # Reportes adicionales (v0.9.1)
  echo "[REP1] GET /reportes/cuentas-corrientes (JSON)"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/reportes/cuentas-corrientes" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "401"
  
  echo "[REP2] GET /reportes/cuentas-corrientes?format=csv"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/reportes/cuentas-corrientes?format=csv" -H "Authorization: Bearer $TOKEN")
  test "$code" = "200" -o "$code" = "401"

else
  echo "[P4-R9+N+PDF+FAC+COB+IVC+REP] SKIP: No se pudo obtener token de autenticación"
fi

echo "OK smoke"
