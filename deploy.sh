#!/bin/bash
# deploy.sh
# Script de deployment para producción

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    error "No se encontró docker-compose.prod.yml. Ejecutar desde el directorio raíz del proyecto."
fi

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    error "No se encontró archivo .env. Crear uno basado en env.example"
fi

# Cargar variables de entorno
source .env

# Verificar variables requeridas
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "cambia-esto-por-uno-seguro-en-produccion" ]; then
    error "SECRET_KEY debe ser configurado en .env"
fi

if [ -z "$POSTGRES_PASSWORD" ]; then
    error "POSTGRES_PASSWORD debe ser configurado en .env"
fi

log "Iniciando deployment..."

# Crear directorios necesarios
log "Creando directorios..."
mkdir -p backups logs ssl

# Generar certificados SSL autofirmados si no existen
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    warn "Generando certificados SSL autofirmados..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=AR/ST=BA/L=BA/O=SistemaComercial/CN=localhost"
fi

# Parar servicios existentes
log "Parando servicios existentes..."
docker-compose -f docker-compose.prod.yml down || true

# Limpiar imágenes huérfanas
log "Limpiando imágenes huérfanas..."
docker image prune -f || true

# Construir y levantar servicios
log "Construyendo y levantando servicios..."
docker-compose -f docker-compose.prod.yml up -d --build

# Esperar a que los servicios estén listos
log "Esperando a que los servicios estén listos..."
sleep 30

# Verificar salud de los servicios
log "Verificando salud de los servicios..."

# Verificar PostgreSQL
if ! docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres}; then
    error "PostgreSQL no está listo"
fi

# Verificar Redis
if ! docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping | grep -q PONG; then
    error "Redis no está listo"
fi

# Verificar Backend
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    error "Backend no está respondiendo"
fi

# Ejecutar migraciones
log "Ejecutando migraciones de base de datos..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# Crear usuario admin si no existe
log "Verificando usuario admin..."
docker-compose -f docker-compose.prod.yml exec -T backend python -c "
from app.db.database import SessionLocal
from app.models.user_model import User
from app.core.security import hash_password

db = SessionLocal()
admin_user = db.query(User).filter(User.username == 'admin').first()
if not admin_user:
    admin_user = User(
        username='admin',
        hashed_password=hash_password('admin123'),
        role='admin'
    )
    db.add(admin_user)
    db.commit()
    print('Usuario admin creado')
else:
    print('Usuario admin ya existe')
db.close()
"

# Ejecutar seed de datos
log "Ejecutando seed de datos..."
docker-compose -f docker-compose.prod.yml exec -T backend python -c "
from app.seed import run
run()
"

# Verificar que todo funciona
log "Verificando funcionamiento del sistema..."

# Test de autenticación
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' | \
    python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    error "No se pudo obtener token de autenticación"
fi

# Test de endpoint protegido
if ! curl -f -H "Authorization: Bearer $TOKEN" http://localhost:8000/users/usuarios/me > /dev/null 2>&1; then
    error "No se pudo acceder a endpoint protegido"
fi

log "Deployment completado exitosamente!"
log "Sistema disponible en: http://localhost:8000"
log "Documentación API: http://localhost:8000/docs"
log "Usuario admin: admin / admin123"

# Mostrar logs de los servicios
log "Mostrando logs de los servicios (Ctrl+C para salir):"
docker-compose -f docker-compose.prod.yml logs -f
