FROM python:3.11-slim

# Zona horaria (útil para backups)
ENV TZ=America/Argentina/Buenos_Aires
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos requirements desde el contexto raiz (../) apuntando al path real
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el código del backend
COPY backend/ /app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
