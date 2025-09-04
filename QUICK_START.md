# 🚀 Sistema Comercial - Quick Start

## ⚡ Inicio Rápido (5 minutos)

### 1. **Clonar y Levantar**
```bash
git clone <tu-repositorio>
cd sistema-comercial
docker-compose up -d
```

### 2. **Configurar Base de Datos**
```bash
# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Poblar datos iniciales
docker-compose exec backend python -c "from app.seed import run; run()"
```

### 3. **¡Listo! Acceder al Sistema**
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Usuario**: `admin` / `admin123`

---

## 🔑 Comandos Esenciales

### **Autenticación**
```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Usar token
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/users/usuarios/me
```

### **Operaciones Básicas**
```bash
# Crear cliente
curl -X POST "http://localhost:8000/clientes" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Cliente Test","email":"cliente@test.com"}'

# Crear producto
curl -X POST "http://localhost:8000/productos" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Producto Test","precio":100.0}'

# Crear compra
curl -X POST "http://localhost:8000/compras" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"proveedor_id":1,"items":[{"producto_id":1,"cantidad":10,"costo_unitario":50.0}]}'

# Crear venta
curl -X POST "http://localhost:8000/ventas" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cliente_id":1,"items":[{"producto_id":1,"cantidad":5}]}'
```

---

## 📊 Monitoreo Rápido

### **Health Check**
```bash
curl http://localhost:8000/monitoring/health
```

### **Métricas**
```bash
curl http://localhost:8000/monitoring/metrics
```

### **Estado del Sistema**
```bash
curl http://localhost:8000/monitoring/status
```

---

## 🛠️ Troubleshooting Rápido

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

## 📚 Documentación Completa

- **Guía Completa**: `GUIA_COMPLETA.md`
- **README**: `backend/README.md`
- **API Docs**: http://localhost:8000/docs

---

## 🎯 Próximos Pasos

1. **Explorar la API** en http://localhost:8000/docs
2. **Crear tus primeros datos** (clientes, productos, etc.)
3. **Probar el flujo completo** (compra → stock → venta)
4. **Configurar para producción** usando `./deploy.sh`
5. **Personalizar** según tus necesidades

---

**¡Sistema Comercial listo para usar! 🚀**
