# 🏪 Sistema Comercial - Documentación Principal

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

## 📚 Documentación Disponible

### **🚀 Inicio Rápido**
- **[QUICK_START.md](QUICK_START.md)** - Guía de inicio rápido (5 minutos)
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Guía completa de deployment

### **📖 Documentación Técnica**
- **[GUIA_COMPLETA.md](GUIA_COMPLETA.md)** - Guía completa del sistema
- **[API_REFERENCE.md](API_REFERENCE.md)** - Referencia completa de la API
- **[backend/README.md](backend/README.md)** - Documentación técnica del backend

### **🔧 Configuración**
- **[env.example](backend/env.example)** - Plantilla de variables de entorno
- **[docker-compose.prod.yml](docker-compose.prod.yml)** - Configuración de producción
- **[nginx.conf](nginx.conf)** - Configuración de Nginx

---

## ⚡ Inicio Rápido

### **1. Clonar y Levantar**
```bash
git clone <tu-repositorio>
cd sistema-comercial
docker-compose up -d
```

### **2. Configurar Base de Datos**
```bash
# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Poblar datos iniciales
docker-compose exec backend python -c "from app.seed import run; run()"
```

### **3. ¡Listo! Acceder al Sistema**
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Usuario**: `admin` / `admin123`

---

## 🏗️ Arquitectura del Sistema

### **Tecnologías Utilizadas**
- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT con Passlib
- **Testing**: Pytest con coverage
- **Deployment**: Docker, Docker Compose, Nginx
- **CI/CD**: GitHub Actions
- **Monitoreo**: Sistema custom de métricas y alertas

### **Estructura del Proyecto**
```
sistema-comercial/
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── core/           # Configuración central
│   │   ├── db/             # Base de datos
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Esquemas Pydantic
│   │   ├── services/       # Lógica de negocio
│   │   └── routers/        # Endpoints FastAPI
│   ├── tests/              # Tests automatizados
│   ├── migrations/         # Migraciones Alembic
│   └── requirements.txt    # Dependencias
├── .github/workflows/      # CI/CD Pipeline
├── docker-compose.yml      # Desarrollo
├── docker-compose.prod.yml # Producción
├── nginx.conf              # Configuración Nginx
├── deploy.sh               # Script de deployment
└── README.md               # Esta documentación
```

---

## 🔌 API Endpoints Principales

### **Autenticación**
- `POST /auth/login` - Login de usuario
- `GET /auth/me` - Usuario actual

### **Gestión de Datos**
- `GET /clientes/` - Listar clientes
- `GET /proveedores/` - Listar proveedores
- `GET /productos/` - Listar productos
- `GET /compras/` - Listar compras
- `GET /ventas/` - Listar ventas

### **Monitoreo**
- `GET /monitoring/health` - Health check
- `GET /monitoring/metrics` - Métricas
- `GET /monitoring/status` - Estado del sistema

---

## 🧪 Testing

### **Ejecutar Tests**
```bash
cd backend
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_ventas_completas.py -v
```

### **Cobertura de Tests**
- **Ventas**: Stock insuficiente, precios personalizados, clientes
- **Compras**: Validaciones de proveedores, productos, costos
- **Stock**: Movimientos múltiples, validaciones de inventario
- **Autenticación**: Login, registro, roles
- **Validaciones**: Reglas de negocio, rate limiting

---

## 🚀 Deployment

### **Desarrollo**
```bash
docker-compose up -d
```

### **Producción**
```bash
# Configurar variables
cp backend/env.example .env
nano .env

# Ejecutar deployment
./deploy.sh
```

### **CI/CD**
El pipeline se ejecuta automáticamente en:
- Push a main/develop
- Pull requests a main

---

## 📊 Monitoreo y Alertas

### **Health Checks**
```bash
curl http://localhost:8000/monitoring/health
```

### **Métricas en Tiempo Real**
```bash
curl http://localhost:8000/monitoring/metrics
```

### **Alertas Automáticas**
- Error Rate Alto (>10%)
- Response Time Alto (>5s)
- Errores Consecutivos (>5)
- Base de Datos no disponible
- Sistema de Backup no accesible

---

## 🛡️ Validaciones de Negocio

### **Validaciones Implementadas**
- **Email**: Formato válido con regex
- **Teléfono**: Formato internacional
- **Precios**: Valores positivos, máximo 2 decimales
- **Cantidades**: Valores positivos, validación de stock
- **Usuarios**: Username válido, contraseña segura
- **Rate Limiting**: 100 requests/minuto por IP

---

## 🔧 Troubleshooting

### **Problemas Comunes**

#### **Sistema no responde**
```bash
# Ver logs
docker-compose logs -f backend

# Reiniciar
docker-compose restart backend
```

#### **Error de base de datos**
```bash
# Verificar PostgreSQL
docker-compose ps postgres

# Reiniciar base de datos
docker-compose restart postgres
```

#### **Error de autenticación**
```bash
# Verificar usuario admin
docker-compose exec backend python -c "
from app.db.database import SessionLocal
from app.models.user_model import User
db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
print('Admin existe:', admin is not None)
db.close()
"
```

---

## 📈 Roadmap

### **Funcionalidades Futuras**

#### **Fase 1 - Mejoras de UX**
- [ ] Dashboard web con React/Vue
- [ ] Notificaciones en tiempo real
- [ ] Reportes y gráficos avanzados

#### **Fase 2 - Funcionalidades Avanzadas**
- [ ] Sistema de inventario con códigos de barras
- [ ] Integración con sistemas de pago
- [ ] API para integración con otros sistemas

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

---

## 📚 Enlaces Rápidos

- **[🚀 Quick Start](QUICK_START.md)** - Inicio rápido
- **[📖 Guía Completa](GUIA_COMPLETA.md)** - Documentación completa
- **[🔧 Deployment](DEPLOYMENT_GUIDE.md)** - Guía de deployment
- **[📚 API Reference](API_REFERENCE.md)** - Referencia de la API
- **[🔧 Backend README](backend/README.md)** - Documentación técnica