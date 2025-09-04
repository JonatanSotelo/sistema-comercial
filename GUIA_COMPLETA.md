# 🏪 Sistema Comercial - Guía Completa de Uso

## 📋 Tabla de Contenidos
- [Descripción General](#-descripción-general)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Configuración de Producción](#-configuración-de-producción)
- [API Endpoints](#-api-endpoints)
- [Sistema de Monitoreo](#-sistema-de-monitoreo)
- [Validaciones de Negocio](#-validaciones-de-negocio)
- [Testing](#-testing)
- [CI/CD y Deployment](#-cicd-y-deployment)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)

---

## 🎯 Descripción General

Sistema de gestión comercial completo desarrollado con **FastAPI** y **PostgreSQL**. Incluye gestión de clientes, proveedores, productos, stock, compras, ventas, usuarios, auditoría y respaldos automáticos.

### ✨ Características Principales
- **Gestión Completa**: Clientes, proveedores, productos, stock, compras, ventas
- **Autenticación JWT**: Sistema seguro de usuarios y roles
- **Control de Stock**: Movimientos automáticos IN/OUT con validaciones
- **Auditoría**: Registro completo de todas las operaciones
- **Respaldos Automáticos**: Backups diarios programados
- **Monitoreo**: Métricas, alertas y health checks en tiempo real
- **Validaciones**: Reglas de negocio robustas y rate limiting
- **CI/CD**: Pipeline automatizado de testing y deployment
- **Producción**: Configuración lista para producción con Nginx y SSL

---

## 🏗️ Arquitectura del Sistema

### **Estructura de Carpetas**
```
backend/
├── app/
│   ├── core/           # Configuración central
│   │   ├── settings.py      # Variables de entorno
│   │   ├── validators.py    # Validaciones de negocio
│   │   ├── rate_limiter.py  # Rate limiting
│   │   └── monitoring.py    # Sistema de monitoreo
│   ├── db/             # Base de datos
│   │   └── database.py      # Conexión y sesiones
│   ├── models/         # Modelos SQLAlchemy
│   ├── schemas/        # Esquemas Pydantic
│   ├── services/       # Lógica de negocio
│   ├── routers/        # Endpoints FastAPI
│   └── seed/           # Datos iniciales
├── tests/              # Tests automatizados
├── migrations/         # Migraciones Alembic
├── requirements.txt    # Dependencias Python
├── pyproject.toml      # Configuración Poetry
├── Dockerfile          # Imagen Docker
└── README.md           # Esta documentación
```

### **Tecnologías Utilizadas**
- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT con Passlib
- **Testing**: Pytest con coverage
- **Deployment**: Docker, Docker Compose, Nginx
- **CI/CD**: GitHub Actions
- **Monitoreo**: Sistema custom de métricas y alertas

---

## 🚀 Instalación y Configuración

### **Requisitos Previos**
- Python 3.11+
- PostgreSQL 15+
- Docker (opcional)
- Git

### **Instalación Local**

1. **Clonar el repositorio**
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
# Crear base de datos PostgreSQL
createdb sistema_comercial

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones
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

### **Instalación con Docker**

1. **Configurar variables de entorno**
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

4. **Poblar datos iniciales**
```bash
docker-compose exec backend python -c "from app.seed import run; run()"
```

---

## ⚙️ Configuración de Producción

### **Variables de Entorno**

Copia `env.example` a `.env` y configura:

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

# Monitoreo
SENTRY_DSN=https://tu-sentry-dsn@sentry.io/project-id
```

### **Deployment Automatizado**

```bash
# Ejecutar script de deployment
./deploy.sh
```

El script automáticamente:
- Verifica variables de entorno
- Genera certificados SSL
- Levanta servicios con Docker Compose
- Ejecuta migraciones
- Crea usuario admin
- Pobla datos iniciales
- Verifica funcionamiento

---

## 🔌 API Endpoints

### **Autenticación**
```bash
POST /auth/login          # Login de usuario
POST /auth/register       # Registro de usuario
GET  /auth/me            # Usuario actual
```

### **Usuarios**
```bash
GET    /users/usuarios/        # Listar usuarios
POST   /users/usuarios/        # Crear usuario
GET    /users/usuarios/{id}    # Obtener usuario
PUT    /users/usuarios/{id}    # Actualizar usuario
DELETE /users/usuarios/{id}    # Eliminar usuario
```

### **Clientes**
```bash
GET    /clientes/        # Listar clientes
POST   /clientes/        # Crear cliente
GET    /clientes/{id}    # Obtener cliente
PUT    /clientes/{id}    # Actualizar cliente
DELETE /clientes/{id}    # Eliminar cliente
```

### **Proveedores**
```bash
GET    /proveedores/        # Listar proveedores
POST   /proveedores/        # Crear proveedor
GET    /proveedores/{id}    # Obtener proveedor
PUT    /proveedores/{id}    # Actualizar proveedor
DELETE /proveedores/{id}    # Eliminar proveedor
```

### **Productos**
```bash
GET    /productos/        # Listar productos
POST   /productos/        # Crear producto
GET    /productos/{id}    # Obtener producto
PUT    /productos/{id}    # Actualizar producto
DELETE /productos/{id}    # Eliminar producto
```

### **Stock**
```bash
GET /stock/{producto_id}  # Stock de producto
```

### **Compras**
```bash
GET    /compras/        # Listar compras
POST   /compras/        # Crear compra
GET    /compras/{id}    # Obtener compra
DELETE /compras/{id}    # Eliminar compra
```

### **Ventas**
```bash
GET    /ventas/        # Listar ventas
POST   /ventas/        # Crear venta
GET    /ventas/{id}    # Obtener venta
DELETE /ventas/{id}    # Eliminar venta
```

### **Auditoría**
```bash
GET /auditoria/        # Listar auditoría
```

### **Respaldos**
```bash
GET  /backup/          # Listar respaldos
POST /backup/          # Crear respaldo
GET  /backup/{id}      # Descargar respaldo
```

### **Monitoreo**
```bash
GET /monitoring/health      # Health check
GET /monitoring/metrics     # Métricas
GET /monitoring/alerts      # Alertas (admin)
GET /monitoring/status      # Estado básico
GET /monitoring/endpoints   # Estadísticas (admin)
GET /monitoring/performance # Rendimiento (admin)
```

---

## 📊 Sistema de Monitoreo

### **Health Check**
```bash
curl http://localhost:8000/monitoring/health
```

Respuesta:
```json
{
  "overall_status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "database": {
    "status": "healthy",
    "response_time": 0.002
  },
  "backup": {
    "status": "healthy",
    "backup_dir": "/app/backups"
  },
  "metrics": {
    "uptime_seconds": 3600,
    "total_requests": 150,
    "error_rate": 0.02
  }
}
```

### **Métricas en Tiempo Real**
```bash
curl http://localhost:8000/monitoring/metrics
```

### **Alertas Automáticas**
- **Error Rate Alto**: >10% de requests fallan
- **Response Time Alto**: >5 segundos promedio
- **Errores Consecutivos**: >5 errores seguidos
- **Base de Datos**: Conexión fallida
- **Sistema de Backup**: Directorio no accesible

---

## 🛡️ Validaciones de Negocio

### **Validaciones Implementadas**

#### **Email**
- Formato válido con regex
- Opcional en clientes/proveedores

#### **Teléfono**
- Formato internacional
- Mínimo 7 caracteres
- Solo números, guiones, paréntesis, espacios

#### **Precios y Costos**
- Valores positivos
- Máximo 2 decimales
- Validación de precisión

#### **Cantidades**
- Valores positivos
- Validación de stock disponible

#### **Usuarios**
- Username: 3-50 caracteres, alfanumérico
- Contraseña: 8+ caracteres, mayúscula, minúscula, número

#### **Rate Limiting**
- 100 requests/minuto por IP
- 5 requests/minuto para endpoints de auth
- Headers de rate limit en respuestas

---

## 🧪 Testing

### **Ejecutar Tests**

```bash
# Tests básicos
cd backend
pytest

# Tests con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_ventas_completas.py -v
pytest tests/test_compras_completas.py -v
pytest tests/test_stock_completo.py -v

# Tests con reporte detallado
pytest -v --tb=short
```

### **Cobertura de Tests**

- **Ventas**: Stock insuficiente, precios personalizados, clientes
- **Compras**: Validaciones de proveedores, productos, costos
- **Stock**: Movimientos múltiples, validaciones de inventario
- **Autenticación**: Login, registro, roles
- **Validaciones**: Reglas de negocio, rate limiting

### **Tests de Integración**

```bash
# Test completo del flujo de venta
pytest tests/test_ventas_completas.py::test_crear_venta_con_stock -v

# Test de validaciones de negocio
pytest tests/test_compras_completas.py::test_compra_con_cantidad_negativa -v

# Test de control de stock
pytest tests/test_stock_completo.py::test_stock_multiples_movimientos -v
```

---

## 🚀 CI/CD y Deployment

### **Pipeline Automatizado**

El pipeline se ejecuta automáticamente en:
- **Push a main/develop**
- **Pull requests a main**

#### **Etapas del Pipeline**

1. **Testing**
   - Linting (flake8, black, isort)
   - Tests unitarios con coverage
   - Security scan (bandit, safety)

2. **Build**
   - Docker image multi-stage
   - Optimización de tamaño
   - Cache de dependencias

3. **Deploy**
   - Verificación de variables
   - Levantado de servicios
   - Ejecución de migraciones
   - Verificación de funcionamiento

### **Deployment Manual**

```bash
# Configurar variables de entorno
cp env.example .env
nano .env

# Ejecutar deployment
./deploy.sh
```

### **Configuración de Producción**

#### **Docker Compose**
```yaml
# docker-compose.prod.yml
services:
  postgres:    # Base de datos
  redis:       # Cache (futuro)
  backend:     # API FastAPI
  nginx:       # Proxy reverso
```

#### **Nginx**
- SSL/TLS con certificados
- Rate limiting
- Headers de seguridad
- Compresión gzip
- Proxy a backend

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

### **Logs y Debugging**

```bash
# Ver logs del backend
docker-compose logs -f backend

# Ver logs de PostgreSQL
docker-compose logs -f postgres

# Ver logs de Nginx
docker-compose logs -f nginx

# Ver logs de monitoreo
curl http://localhost:8000/monitoring/alerts
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
```

---

## 🗺️ Roadmap

### **Funcionalidades Futuras**

#### **Fase 1 - Mejoras de UX**
- [ ] Dashboard web con React/Vue
- [ ] Notificaciones en tiempo real
- [ ] Reportes y gráficos avanzados
- [ ] Exportación a Excel/PDF mejorada

#### **Fase 2 - Funcionalidades Avanzadas**
- [ ] Sistema de inventario con códigos de barras
- [ ] Integración con sistemas de pago
- [ ] API para integración con otros sistemas
- [ ] Sistema de notificaciones por email

#### **Fase 3 - Escalabilidad**
- [ ] Cache con Redis
- [ ] Load balancing
- [ ] Microservicios
- [ ] Kubernetes deployment

#### **Fase 4 - Inteligencia de Negocio**
- [ ] Análisis predictivo de ventas
- [ ] Recomendaciones de productos
- [ ] Optimización de stock
- [ ] Machine learning para tendencias

---

## 📞 Soporte y Contacto

### **Documentación Adicional**
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/monitoring/health

### **Comandos Útiles**

```bash
# Reiniciar servicios
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Crear respaldo manual
docker-compose exec backend python -c "from app.services.backup_service import create_backup_zip; create_backup_zip()"

# Ver estadísticas de uso
curl http://localhost:8000/monitoring/performance
```

---

## 🎉 ¡Sistema Listo para Producción!

El **Sistema Comercial** está completamente implementado con:

✅ **Funcionalidad Completa** - Todos los módulos operativos  
✅ **Testing Exhaustivo** - Cobertura completa con casos edge  
✅ **Validaciones Robustas** - Reglas de negocio y rate limiting  
✅ **Monitoreo Avanzado** - Métricas, alertas y health checks  
✅ **CI/CD Automatizado** - Pipeline completo de testing y deployment  
✅ **Configuración de Producción** - Docker, Nginx, SSL, optimizaciones  

**¡Disfruta tu sistema comercial! 🚀**
