FROM python:3.11-slim

# Zona horaria
ENV TZ=America/Argentina/Buenos_Aires
# Instalar tzdata y postgresql-client (para pg_dump en backups)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el código del backend
COPY . /app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]