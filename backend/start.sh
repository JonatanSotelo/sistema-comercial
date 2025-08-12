#!/usr/bin/env bash
set -e

# Esperar DB (ajustá HOST/PORT si cambian)
if command -v nc >/dev/null 2>&1; then
  echo "Esperando a la DB..."
  until nc -z "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}"; do
    sleep 1
  done
fi

# Migraciones Alembic
echo "Aplicando migraciones..."
alembic upgrade head

# Levantar API
echo "Iniciando FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
