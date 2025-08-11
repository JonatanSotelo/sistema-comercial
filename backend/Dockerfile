FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:/root/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev netcat-traditional curl \
 && rm -rf /var/lib/apt/lists/*

# Mejora: aseguramos herramientas de build actualizadas
RUN python -m pip install --upgrade pip setuptools wheel

# Copiamos deps primero (cache)
COPY pyproject.toml poetry.lock* /app/

# Instalamos Poetry y deps del proyecto (sin venv)
RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root \
 && pip install --no-cache-dir "uvicorn[standard]==0.35.0"

# Copiamos código y migraciones
COPY app /app/app
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000
CMD ["/app/start.sh"]
