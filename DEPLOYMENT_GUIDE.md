# 🚀 Guía de Deployment - Sistema Comercial

## 📋 Tabla de Contenidos
- [Deployment Local](#-deployment-local)
- [Deployment con Docker](#-deployment-con-docker)
- [Deployment de Producción](#-deployment-de-producción)
- [Configuración de Variables](#-configuración-de-variables)
- [Monitoreo y Logs](#-monitoreo-y-logs)
- [Troubleshooting](#-troubleshooting)

---

## 🏠 Deployment Local

### **Requisitos**
- Python 3.11+
- PostgreSQL 15+
- Git

### **Pasos**

1. **Clonar repositorio**
```bash
git clone <tu-repositorio>
cd sistema-comercial
```

2. **Configurar entorno virtual**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
```bash
# Crear base de datos
createdb sistema_comercial

# Configurar variables
cp env.example .env
# Editar .env con tu configuración
```

5. **Ejecutar migraciones**
```bash
alembic upgrade head
```

6. **Poblar datos iniciales**
```bash
python -c "from app.seed import run; run()"
```

7. **Iniciar servidor**
```bash
uvicorn app.main:app --reload
```

---

## 🐳 Deployment con Docker

### **Desarrollo**

1. **Configurar variables**
```bash
cp env.example .env
# Editar .env
```

2. **Levantar servicios**
```bash
docker-compose up -d
```

3. **Ejecutar migraciones**
```bash
docker-compose exec backend alembic upgrade head
```

4. **Poblar datos**
```bash
docker-compose exec backend python -c "from app.seed import run; run()"
```

### **Verificar funcionamiento**
```bash
# Ver logs
docker-compose logs -f backend

# Verificar salud
curl http://localhost:8000/health

# Verificar API
curl http://localhost:8000/docs
```

---

## 🏭 Deployment de Producción

### **Requisitos**
- Docker y Docker Compose
- Dominio (opcional)
- Certificados SSL (opcional)

### **Configuración**

1. **Configurar variables de producción**
```bash
cp env.example .env
nano .env
```

**Variables importantes:**
```bash
# Base de datos
DATABASE_URL=postgresql+psycopg2://usuario:password@host:5432/database

# JWT - CAMBIAR EN PRODUCCIÓN
SECRET_KEY=tu-clave-secreta-super-segura-de-al-menos-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Aplicación
APP_NAME=Sistema Comercial
ENV=production
BACKUP_DIR=/app/backups

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# CORS (para producción)
ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

2. **Ejecutar deployment automatizado**
```bash
./deploy.sh
```

### **Deployment Manual**

1. **Levantar servicios de producción**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. **Ejecutar migraciones**
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

3. **Crear usuario admin**
```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
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
```

4. **Poblar datos iniciales**
```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.seed import run; run()"
```

---

## ⚙️ Configuración de Variables

### **Variables Obligatorias**

```bash
# Base de datos
DATABASE_URL=postgresql+psycopg2://usuario:password@host:5432/database

# JWT
SECRET_KEY=tu-clave-secreta-super-segura-de-al-menos-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### **Variables Opcionales**

```bash
# Aplicación
APP_NAME=Sistema Comercial
ENV=development
API_PREFIX=

# Backup
BACKUP_DIR=/app/backups
BACKUP_DATABASE_URL=

# Email (futuro)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# Redis (futuro)
REDIS_URL=

# Logging
LOG_LEVEL=INFO
LOG_FILE=

# CORS
ALLOWED_ORIGINS=*

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Monitoreo
SENTRY_DSN=
```

---

## 📊 Monitoreo y Logs

### **Health Checks**

```bash
# Health check básico
curl http://localhost:8000/health

# Health check completo
curl http://localhost:8000/monitoring/health

# Estado del sistema
curl http://localhost:8000/monitoring/status
```

### **Métricas**

```bash
# Métricas básicas
curl http://localhost:8000/monitoring/metrics

# Estadísticas de rendimiento
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/monitoring/performance

# Alertas
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/monitoring/alerts
```

### **Logs**

```bash
# Logs del backend
docker-compose logs -f backend

# Logs de PostgreSQL
docker-compose logs -f postgres

# Logs de Nginx
docker-compose logs -f nginx

# Logs en tiempo real
docker-compose logs -f
```

---

## 🔧 Troubleshooting

### **Problemas Comunes**

#### **1. Error de Conexión a Base de Datos**
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Verificar logs
docker-compose logs postgres

# Verificar variables de entorno
echo $DATABASE_URL
```

#### **2. Error de Autenticación**
```bash
# Verificar que el usuario admin existe
docker-compose exec backend python -c "
from app.db.database import SessionLocal
from app.models.user_model import User
db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
print('Admin existe:', admin is not None)
db.close()
"
```

#### **3. Error de Stock Insuficiente**
```bash
# Verificar stock de producto
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/stock/1

# Crear compra para tener stock
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"proveedor_id": 1, "items": [{"producto_id": 1, "cantidad": 10, "costo_unitario": 50.0}]}' \
  http://localhost:8000/compras
```

#### **4. Error de Rate Limiting**
```bash
# Verificar headers de rate limit
curl -I http://localhost:8000/

# Headers esperados:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 99
# X-RateLimit-Reset: 1642248600
```

### **Comandos de Diagnóstico**

```bash
# Verificar salud del sistema
curl http://localhost:8000/monitoring/health

# Ver métricas
curl http://localhost:8000/monitoring/metrics

# Ver estado de servicios
docker-compose ps

# Ver uso de recursos
docker stats

# Ver logs de monitoreo
curl http://localhost:8000/monitoring/alerts
```

---

## 🚀 Comandos Útiles

### **Gestión de Servicios**

```bash
# Reiniciar servicios
docker-compose restart

# Reiniciar solo backend
docker-compose restart backend

# Parar servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v
```

### **Base de Datos**

```bash
# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Crear migración
docker-compose exec backend alembic revision --autogenerate -m "descripcion"

# Revertir migración
docker-compose exec backend alembic downgrade -1
```

### **Respaldos**

```bash
# Crear respaldo manual
docker-compose exec backend python -c "from app.services.backup_service import create_backup_zip; create_backup_zip()"

# Descargar respaldo
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/backup/download \
  -o backup.zip
```

### **Testing**

```bash
# Ejecutar tests
docker-compose exec backend pytest

# Tests con coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Tests específicos
docker-compose exec backend pytest tests/test_ventas_completas.py -v
```

---

## 📚 Documentación Adicional

- **Guía Completa**: `GUIA_COMPLETA.md`
- **Quick Start**: `QUICK_START.md`
- **README**: `backend/README.md`
- **API Docs**: http://localhost:8000/docs

---

## 🎉 ¡Deployment Completado!

El **Sistema Comercial** está listo para producción con:

✅ **Docker Compose** - Servicios containerizados  
✅ **Nginx** - Proxy reverso con SSL  
✅ **Monitoreo** - Health checks y métricas  
✅ **Logs** - Sistema de logging centralizado  
✅ **Respaldos** - Backups automáticos  
✅ **CI/CD** - Pipeline automatizado  

**¡Sistema comercial desplegado exitosamente! 🚀**
