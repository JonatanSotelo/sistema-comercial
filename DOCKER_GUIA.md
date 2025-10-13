# 🐳 Guía Docker - Sistema Comercial Python-First

## 📋 Resumen

El nuevo `docker-compose.yml` está **actualizado para el frontend Python**. Ya **NO incluye** el contenedor frontend React (obsoleto).

---

## 🎯 Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **backend** | 8000 | FastAPI + Frontend Python (Jinja2 + HTMX) |
| **db** (PostgreSQL) | 5433 | Base de datos principal |
| **redis** | 6379 | Caché y sesiones |
| **pgadmin** | 5050 | Administrador de BD (opcional) |

**❌ ELIMINADO:** Contenedor `frontend` (React/Vite) - Ya no es necesario

---

## 🚀 Inicio Rápido

### 1. Iniciar Todos los Servicios

```bash
cd sistema-comercial
docker-compose up -d
```

Esto iniciará:
- ✅ PostgreSQL (puerto 5433)
- ✅ Redis (puerto 6379)
- ✅ Backend + Frontend Python (puerto 8000)

### 2. Verificar Estado

```bash
docker-compose ps
```

Deberías ver:
```
NAME          STATUS    PORTS
sc_backend    Up        0.0.0.0:8000->8000/tcp
sc_postgres   Up        0.0.0.0:5433->5432/tcp
sc_redis      Up        0.0.0.0:6379->6379/tcp
```

### 3. Acceder al Sistema

- **🌐 Frontend Web**: http://localhost:8000/app
- **📚 API Docs**: http://localhost:8000/docs
- **💾 Health Check**: http://localhost:8000/

**Login:**
- Usuario: `admin`
- Password: `admin123`

---

## 📦 Comandos Útiles

### Ver Logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo base de datos
docker-compose logs -f db
```

### Detener Servicios

```bash
# Detener (conserva datos)
docker-compose stop

# Detener y eliminar contenedores (conserva volúmenes)
docker-compose down

# Detener y eliminar TODO (incluyendo datos)
docker-compose down -v
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo backend
docker-compose restart backend
```

### Reconstruir Backend

```bash
# Si cambias Dockerfile o requirements.txt
docker-compose build backend
docker-compose up -d backend
```

---

## 🔧 Configuración Avanzada

### Iniciar con pgAdmin

Por defecto, pgAdmin no se inicia (para ahorrar recursos). Para iniciarlo:

```bash
docker-compose --profile tools up -d
```

Acceder a: http://localhost:5050
- Email: `admin@example.com`
- Password: `admin`

**Conectar a PostgreSQL desde pgAdmin:**
- Host: `db` (nombre del servicio)
- Port: `5432`
- Database: `sc_db`
- User: `sc_user`
- Password: `sc_pass`

### Variables de Entorno

Puedes crear un archivo `.env` en la raíz:

```bash
# .env
DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@db:5432/sc_db
SECRET_KEY=mi-secret-key-super-segura
ADMIN_USERNAME=miadmin
ADMIN_PASSWORD=mipassword
API_BASE_URL=http://localhost:8000
```

Y docker-compose lo usará automáticamente.

### Solo Base de Datos (sin backend)

Si solo necesitas la BD:

```bash
docker-compose up -d db redis
```

---

## 🐛 Troubleshooting

### Problema: "Port 5432 is already allocated"

**Causa:** Ya tienes PostgreSQL corriendo en tu máquina.

**Solución 1 - Usar puerto diferente:**
Edita `docker-compose.yml`:
```yaml
ports:
  - "5434:5432"  # Cambia 5433 a 5434 u otro
```

**Solución 2 - Detener PostgreSQL local:**
```bash
# Windows (como servicio)
net stop postgresql-x64-16

# Linux
sudo systemctl stop postgresql
```

### Problema: "Cannot connect to database"

**Verificar que la BD esté lista:**
```bash
docker-compose logs db | grep "ready to accept"
```

**Esperar healthcheck:**
El backend espera a que PostgreSQL esté healthy. Puede tomar 10-20 segundos.

### Problema: Frontend no carga

**Verificar que backend esté corriendo:**
```bash
docker-compose logs backend
```

**Verificar puertos:**
```bash
curl http://localhost:8000/
# Debería retornar: {"ok":true,"app":"Sistema Comercial"}
```

**Acceder al frontend:**
- ✅ Correcto: http://localhost:8000/app
- ❌ Incorrecto: http://localhost:3000 (puerto React ya no existe)

### Problema: "Migraciones no aplicadas"

```bash
# Entrar al contenedor
docker-compose exec backend bash

# Aplicar migraciones
alembic upgrade head
```

### Problema: Volúmenes con datos viejos

```bash
# Eliminar volúmenes y empezar limpio
docker-compose down -v
docker-compose up -d
```

---

## 📊 Comparación: Antes vs Ahora

### Antes (con frontend React)

```yaml
services:
  backend:    # Puerto 8000 - Solo API REST
  frontend:   # Puerto 3000 - React/Vite ❌
  db:         # Puerto 5433 - PostgreSQL
  redis:      # Puerto 6379 - Redis
```

**Acceso:**
- Frontend: http://localhost:3000 (React)
- API: http://localhost:8000/api

**Problemas:**
- 2 contenedores para frontend+backend
- Build de npm necesario
- node_modules en volumen
- Más recursos consumidos

### Ahora (frontend Python)

```yaml
services:
  backend:    # Puerto 8000 - API REST + Frontend Web ✅
  db:         # Puerto 5433 - PostgreSQL
  redis:      # Puerto 6379 - Redis
```

**Acceso:**
- Frontend: http://localhost:8000/app (Python/Jinja2)
- API: http://localhost:8000/docs

**Ventajas:**
- ✅ 1 solo contenedor
- ✅ No necesita npm/build
- ✅ Menos recursos
- ✅ Más simple

---

## 🔄 Migración desde Docker Antiguo

### Si ya tienes contenedores corriendo:

```bash
# 1. Detener todo
docker-compose -f infra/docker-compose.yml down

# 2. Usar nuevo docker-compose
docker-compose up -d

# 3. Verificar
docker-compose ps
```

### Si quieres mantener datos:

Los volúmenes `pg_data` y `backups_data` se conservan automáticamente.

### Si quieres empezar limpio:

```bash
# Eliminar TODO (contenedores + volúmenes)
docker-compose down -v

# Iniciar desde cero
docker-compose up -d
```

---

## 🎯 Desarrollo Local

### Opción 1: Docker (Recomendado para Producción)

```bash
docker-compose up -d
```

**Ventajas:**
- ✅ Entorno aislado
- ✅ PostgreSQL incluido
- ✅ Fácil para deployment

**Desventajas:**
- Más lento en hot-reload
- Necesita rebuild en cambios de dependencias

### Opción 2: Sin Docker (Recomendado para Desarrollo)

```bash
# Iniciar solo la BD con Docker
docker-compose up -d db redis

# Ejecutar backend localmente
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Ventajas:**
- ✅ Hot-reload instantáneo
- ✅ Debug más fácil
- ✅ Menos recursos

**Desventajas:**
- Necesitas Python instalado localmente
- DATABASE_URL debe apuntar a localhost:5433

---

## 🚀 Producción

Para producción, considera:

1. **Variables de entorno seguras:**
```yaml
environment:
  SECRET_KEY: ${SECRET_KEY}  # Desde .env
  DATABASE_URL: ${DATABASE_URL}
  ADMIN_PASSWORD: ${ADMIN_PASSWORD}
```

2. **Sin modo reload:**
```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

3. **Limitar recursos:**
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

4. **Health checks:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## ✅ Checklist de Verificación

Después de `docker-compose up -d`:

- [ ] ✅ Contenedor `sc_backend` corriendo
- [ ] ✅ Contenedor `sc_postgres` healthy
- [ ] ✅ Contenedor `sc_redis` corriendo
- [ ] ❌ Contenedor `sc_frontend` NO existe (correcto!)
- [ ] ✅ Puerto 8000 accesible
- [ ] ✅ http://localhost:8000/ retorna JSON
- [ ] ✅ http://localhost:8000/docs carga Swagger
- [ ] ✅ http://localhost:8000/app carga login
- [ ] ✅ Login funciona (admin/admin123)
- [ ] ✅ Dashboard accesible

---

## 📚 Recursos Adicionales

- **[FRONTEND_PYTHON.md](FRONTEND_PYTHON.md)** - Guía del frontend
- **[RESUMEN_MIGRACION.md](RESUMEN_MIGRACION.md)** - Resumen ejecutivo
- **[backend/Dockerfile](backend/Dockerfile)** - Dockerfile del backend

---

## 🎉 Conclusión

El nuevo `docker-compose.yml` es **más simple** porque:
- ✅ 1 contenedor menos (frontend eliminado)
- ✅ Sin npm/node_modules
- ✅ Menos recursos
- ✅ Más rápido

**El frontend Python está integrado en el backend y se sirve desde el mismo puerto 8000.** 🚀

---

**Última actualización:** Octubre 2025
**Versión:** 2.0 - Python-First


