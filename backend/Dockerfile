FROM python:3.10-slim

WORKDIR /app

# SO deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev netcat-traditional curl \
 && rm -rf /var/lib/apt/lists/*

# Mejorar pip
RUN python -m pip install --upgrade pip setuptools wheel

# Copiamos definiciones de dependencias primero para aprovechar cache
COPY pyproject.toml poetry.lock* /app/

# Instalar Poetry y dependencias del proyecto (sin venv)
RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry lock --no-interaction \
 && poetry install --no-interaction --no-ansi --no-root --with dev \
 && pip install --no-cache-dir "uvicorn[standard]==0.35.0"

# Copiar el resto del código
COPY . /app

# Asegurar permisos de ejecución
RUN chmod +x /app/start.sh || true

EXPOSE 8000

# Comando por defecto (lo sobreescribe docker-compose con /app/start.sh, pero dejamos algo sensato)
CMD ["/app/start.sh"]
