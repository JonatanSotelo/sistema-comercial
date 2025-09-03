# backend/Dockerfile
FROM python:3.11-slim

# Evitar buffers y bytecode
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Carpeta de trabajo (coincide con docker-compose)
WORKDIR /app

# Paquetes de sistema necesarios (psycopg2 y build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Copiamos requirements e instalamos deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el código (igualmente luego montás volumen ./backend:/app)
COPY . /app

# Exponemos el puerto que mapea docker-compose
EXPOSE 8000

# El comando real lo define docker-compose:
# command: ["bash", "/app/start.sh"]
