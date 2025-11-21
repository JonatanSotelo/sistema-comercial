#!/usr/bin/env bash
# Check Foreign Keys to users table
# Usage: bash scripts/check_db_fks.sh

set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.dev.yml}"
USER="${POSTGRES_USER:-appuser}"
DATABASE="${POSTGRES_DB:-appdb}"

echo ""
echo "=== Checking Foreign Keys to users table ==="

# Verificar que el contenedor esté corriendo
if ! docker ps --filter "name=sc_postgres" --format "{{.Names}}" | grep -q "sc_postgres"; then
    echo "ERROR: Container sc_postgres is not running"
    echo "Run: docker compose -f $COMPOSE_FILE up -d"
    exit 1
fi

# Verificar que el archivo SQL existe
if [ ! -f "scripts/sql/check_fks_users.sql" ]; then
    echo "ERROR: scripts/sql/check_fks_users.sql not found"
    exit 1
fi

# Ejecutar el check (con pager deshabilitado)
docker compose -f "$COMPOSE_FILE" exec -T sc_postgres \
    psql -U "$USER" -d "$DATABASE" -P pager=off -f /app/scripts/sql/check_fks_users.sql

echo ""
echo "=== Check completed ==="
echo "If you see FKs pointing to 'usuarios', run the fix migration:"
echo "  docker compose -f $COMPOSE_FILE exec -T sc_backend alembic upgrade head"

