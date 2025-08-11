#!/usr/bin/env bash
set -e

echo "Esperando a Postgres en $DATABASE_HOST:$DATABASE_PORT..."
# Espera simple a TCP abierto
until nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
  sleep 1
done
echo "Postgres listo!"

echo "Aplicando migraciones..."
alembic upgrade head

echo "Iniciando Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
