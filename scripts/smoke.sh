
#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000}"

echo "[1/4] GET /app/login"
curl -sSf -o /dev/null "$BASE/app/login"

echo "[2/4] GET /app/dashboard (sin sesión redirige a login)"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/dashboard")
test "$code" = "200" -o "$code" = "302"

echo "[3/4] GET /app/productos (puede requerir login según backend)"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/productos")
test "$code" = "200" -o "$code" = "302"

echo "[4/4] GET /app/productos/table (HTMX partial)"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/app/productos/table")
test "$code" = "200" -o "$code" = "302"

echo "OK smoke"
