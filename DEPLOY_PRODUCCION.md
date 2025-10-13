# 🚀 Guía de Deploy a Producción

## ✅ Pre-requisitos

Antes de deployar a producción, verificar:

- [x] Todos los tests pasan
- [x] CI/CD configurado
- [x] Variables de entorno configuradas
- [x] Base de datos lista
- [x] Dominio configurado (opcional)
- [x] SSL/TLS certificado (recomendado)

---

## 🔧 Configuración

### 1. Variables de Entorno

Crear archivo `.env.production`:

```bash
# Base de datos
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname

# Seguridad
SECRET_KEY=<genera-una-key-muy-segura-de-32-chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<password-segura>
ADMIN_EMAIL=admin@tudominio.com

# API Web
API_BASE_URL=http://127.0.0.1:8000
USE_TEST_CLIENT=true

# Redis
REDIS_URL=redis://redis:6379

# Entorno
ENV=production
APP_NAME="Sistema Comercial"

# Backup
BACKUP_DIR=/app/backups

# CORS (ajustar según tu dominio)
ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

### 2. Docker Compose Production

Usar archivo `docker-compose.prod.yml` (crear si no existe):

```yaml
version: '3.8'

services:
  backend:
    image: sistema-comercial-backend:latest
    container_name: sc_backend_prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_URL=redis://redis:6379
      - ENV=production
      - USE_TEST_CLIENT=true
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    restart: unless-stopped
    command: >
      sh -c "
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --no-reload
      "

  db:
    image: postgres:16
    container_name: sc_postgres_prod
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: sc_redis_prod
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 🚀 Proceso de Deploy

### Opción 1: Docker Swarm

```bash
# Inicializar swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml sc

# Verificar
docker service ls
```

### Opción 2: Docker Compose

```bash
# Build image
docker-compose -f docker-compose.prod.yml build

# Iniciar
docker-compose -f docker-compose.prod.yml up -d

# Verificar
docker-compose -f docker-compose.prod.yml ps
```

### Opción 3: Kubernetes

```bash
# Crear namespace
kubectl create namespace sistema-comercial

# Aplicar manifests
kubectl apply -f k8s/ -n sistema-comercial

# Verificar
kubectl get pods -n sistema-comercial
```

---

## 🔒 SSL/TLS (Recomendado)

### Con Nginx

```nginx
server {
    listen 80;
    server_name tudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tudominio.com;

    ssl_certificate /etc/ssl/certs/tudominio.com.crt;
    ssl_certificate_key /etc/ssl/private/tudominio.com.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Con Traefik

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.sc.rule=Host(`tudominio.com`)"
  - "traefik.http.routers.sc.entrypoints=websecure"
  - "traefik.http.routers.sc.tls.certresolver=letsencrypt"
```

---

## 🔍 Health Checks

### Endpoints de Verificación

```bash
# Health check básico
curl http://tudominio.com/

# API docs
curl http://tudominio.com/docs

# Frontend
curl http://tudominio.com/app

# Monitoring
curl http://tudominio.com/monitoring/health
```

### Monitoreo Recomendado

- **Uptime:** UptimeRobot, Pingdom
- **Logs:** ELK Stack, Datadog
- **Metrics:** Prometheus + Grafana
- **Errors:** Sentry

---

## 💾 Backups

### Configurar Backups Automáticos

El sistema tiene backups automáticos programados a las 02:30 AM.

**Verificar:**
```bash
# Entrar al contenedor
docker exec -it sc_backend bash

# Ver backups
ls -lh /app/backups/

# Crear backup manual
curl -X POST http://localhost:8000/backups \
  -H "Authorization: Bearer <token>"
```

### Backup de PostgreSQL

```bash
# Backup manual
docker exec sc_postgres pg_dump -U user dbname > backup.sql

# Restaurar
docker exec -i sc_postgres psql -U user dbname < backup.sql
```

---

## 🔄 Actualización

### Rolling Update

```bash
# Pull latest code
git pull origin main

# Rebuild
docker-compose -f docker-compose.prod.yml build

# Recreate con mínimo downtime
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend
```

### Con CI/CD

1. Push a `main`
2. GitHub Actions build automático
3. Tag release: `git tag v2.0.1 && git push --tags`
4. Deploy automático (si configurado)

---

## 📊 Monitoreo

### Logs

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f backend

# Logs estructurados (JSON)
docker-compose -f docker-compose.prod.yml logs backend | jq

# Filtrar por nivel
docker-compose logs backend | grep "ERROR"
```

### Métricas

```bash
# Stats de contenedores
docker stats

# Uso de recursos
docker-compose -f docker-compose.prod.yml top
```

---

## 🐛 Troubleshooting

### Backend no inicia

```bash
# Ver logs detallados
docker-compose logs backend

# Verificar variables de entorno
docker-compose config

# Reiniciar
docker-compose restart backend
```

### Base de datos no conecta

```bash
# Verificar que PostgreSQL esté healthy
docker-compose ps db

# Logs de BD
docker-compose logs db

# Test de conexión
docker exec sc_backend python -c "from app.db.database import engine; engine.connect()"
```

### Redis no disponible

```bash
# Verificar Redis
docker-compose ps redis

# Test de conexión
docker exec sc_redis redis-cli ping
```

---

## 🎯 Checklist de Producción

### Antes del Deploy
- [ ] Tests passing localmente
- [ ] CI passing en GitHub
- [ ] Variables de entorno configuradas
- [ ] SECRET_KEY generada
- [ ] Password de admin cambiada
- [ ] DATABASE_URL configurada
- [ ] Dominio apuntando al servidor

### Durante el Deploy
- [ ] Build de imagen exitoso
- [ ] Contenedores iniciados
- [ ] Health checks OK
- [ ] Migraciones aplicadas (si hay)
- [ ] Datos seed aplicados (si se necesita)

### Después del Deploy
- [ ] Login funciona
- [ ] Dashboard accesible
- [ ] Todos los módulos funcionan
- [ ] API docs accesible
- [ ] Backups configurados
- [ ] Monitoreo activo
- [ ] Logs funcionando
- [ ] SSL/TLS activo (si aplica)

---

## 📞 Soporte Post-Deploy

### Logs
```bash
# Logs de aplicación
docker-compose -f docker-compose.prod.yml logs -f backend

# Logs structured (JSON)
docker-compose logs backend --tail=100 | jq '.message'
```

### Performance
```bash
# Ver queries lentas
docker-compose logs backend | grep "SLOW QUERY"

# Stats de Redis
docker exec sc_redis redis-cli info stats
```

### Seguridad
```bash
# Ejecutar security scan
cd backend
safety check --file requirements.txt
bandit -r app
```

---

## ✅ Verificación Post-Deploy

```bash
# Health check
curl https://tudominio.com/

# Frontend
curl https://tudominio.com/app

# API docs
curl https://tudominio.com/docs

# Login (API)
curl -X POST https://tudominio.com/auth/oauth2/token \
  -d "username=admin&password=<tu-password>"
```

---

## 🎉 ¡Deploy Exitoso!

Si todos los checks pasan, tu sistema está:

✅ **Funcionando en producción**
✅ **Monitoreado**
✅ **Con backups**
✅ **Seguro**
✅ **Optimizado**

---

**Versión:** 2.0.0  
**Build:** Production  
**Estado:** ✅ Ready


