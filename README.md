# 🏪 Sistema Comercial - UI Python (HTMX)

## 🎯 Descripción General

Sistema de gestión comercial completo desarrollado con **FastAPI**, **PostgreSQL** y **UI Python (HTMX/Jinja2)**. 

Incluye gestión completa de clientes, proveedores, productos, stock, compras, ventas, pedidos, facturación electrónica AFIP, cobros, auditoría y reportes.

### ✨ Características Principales

- **UI Python con HTMX**: Frontend moderno sin JavaScript pesado, renderizado server-side
- **Gestión Completa**: Clientes, proveedores, productos, stock, compras, ventas, pedidos
- **Facturación Electrónica AFIP**: WSFEv1 con CAE, QR y PDF
- **Cobros y Caja**: Gestión de cobros, saldos por cliente, recibos PDF
- **Pedidos y Reservas**: Estados de pedidos (NUEVO → EN_PREPARACION → LISTO → FACTURADO), reservas de stock
- **Integración WhatsApp**: Creación automática de pedidos/ventas desde bot
- **Auditoría**: Registro completo de todas las operaciones
- **Import/Export**: CSV y XLSX para clientes, productos, proveedores
- **Backups**: Respaldos automáticos programados
- **Reportes**: Ventas, compras, pedidos, IVA ventas/compras, cuentas corrientes

---

## 🚀 Inicio Rápido (Desarrollo)

### **1. Requisitos**
- Docker y Docker Compose
- Git

### **2. Clonar y Configurar**
```bash
git clone <tu-repositorio>
cd sistema-comercial
```

### **3. Levantar Servicios**
```bash
docker compose -f docker-compose.dev.yml up -d --build
```

### **4. Ejecutar Migraciones**
```bash
docker compose -f docker-compose.dev.yml exec sc_backend alembic upgrade head
```

### **5. Verificar Migración Actual**
```bash
docker compose -f docker-compose.dev.yml exec sc_backend alembic current
```

### **6. Acceder al Sistema**
- **UI (HTMX)**: http://localhost:8000/app/login
- **API Docs**: http://localhost:8000/docs
- **PgAdmin**: http://localhost:5050

**Credenciales por defecto:**
- Usuario: `admin`
- Password: `admin123`

---

## 🧪 Tests y Smoke

### **Ejecutar Tests**
```bash
# Suite completa
docker compose -f docker-compose.dev.yml exec sc_backend pytest -v

# Tests específicos
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_cobros.py -v
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_pedidos.py -v
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_reservas.py -v
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_facturacion_afip.py -v
```

### **Smoke Tests**
```bash
# Bash (Linux/Mac/WSL)
bash scripts/smoke.sh

# PowerShell (Windows)
powershell -ExecutionPolicy Bypass -File scripts\test_cobros_simple.ps1
```

---

## 📦 Estructura del Proyecto

```
sistema-comercial/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── core/              # Auth, settings, deps, validators
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── web/               # UI HTMX routers
│   │   └── templates/         # Jinja2 templates (HTMX)
│   ├── migrations/            # Alembic migrations
│   ├── tests/                 # Pytest tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── env.example
├── scripts/                   # Smoke tests y utilidades
│   ├── smoke.sh
│   ├── test_cobros_simple.ps1
│   └── sql/
├── docker-compose.dev.yml     # Desarrollo
├── docker-compose.prod.yml    # Producción
└── README.md
```

---

## 🔧 Configuración

### **Variables de Entorno (.env)**

Copiar `backend/env.example` a `backend/.env` y configurar:

```bash
# Base de datos
DATABASE_URL=postgresql://appuser:apppass@sc_postgres:5432/appdb

# JWT
SECRET_KEY=tu-secret-key-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Facturación AFIP (opcional)
AFIP_ENV=homologacion
AFIP_CUIT=20123456789
AFIP_CERT_PATH=/secrets/cert.pem
AFIP_KEY_PATH=/secrets/key.pem
FACTURA_PTO_VTA=1

# Notificaciones (opcional)
NOTIFY_ON_READY=false
NOTIFY_WHATS_ENDPOINT=http://whatsapp-bot/webhook
```

---

## 📚 Módulos Implementados

### **v0.9.1 - Cobros & Caja + IVA Compras** ✅
- Registro de cobros por venta (efectivo, transferencia, cheque, etc.)
- Cálculo de saldos por venta y por cliente
- Recibos PDF con detalle de cobros
- Libro IVA Compras (registro manual de facturas de compra)
- Reportes: Cuentas corrientes, IVA Compras

### **v0.9.0 - Facturación Electrónica AFIP** ✅
- Integración WSFEv1 (WSAA + WSFEv1)
- Emisión de Facturas A/B/C con CAE
- QR AFIP en facturas
- PDF de facturas con datos fiscales
- Libro IVA Ventas (export CSV/XLSX)

### **v0.8.0 - Notificaciones + Remito + Etiqueta** ✅
- Notificaciones WhatsApp/Email cuando Pedido → LISTO
- Remito PDF para ventas
- Etiqueta PDF con QR para pedidos

### **v0.7.5 - Reservas de Stock** ✅
- Reservas soft de stock al cambiar Pedido a EN_PREPARACION
- Cálculo de stock disponible = stock - reservas activas
- Consumo de reservas al facturar
- Liberación de reservas al cancelar

### **Pedidos (v0.7.x)** ✅
- Estados: NUEVO → EN_PREPARACION → LISTO → FACTURADO / CANCELADO
- Integración con WhatsApp para crear pedidos automáticamente
- Packing lists (HTML/PDF)
- Acciones masivas (bulk state changes)
- Reportes de pedidos agrupados

### **Core (v0.5.x - v0.6.x)** ✅
- CRUD Clientes, Proveedores, Productos
- Compras y Ventas con items
- Control de stock (IN/OUT)
- Import/Export CSV/XLSX
- Backups automáticos
- Auditoría completa
- Dashboard con métricas

---

## 🗂️ Historial de Arquitectura

### **Línea Principal: HTMX (actual)**
Esta rama (`main`) utiliza **UI Python (HTMX + Jinja2)** para el frontend, con renderizado server-side y actualizaciones dinámicas sin JavaScript pesado.

### **Frontend React (legacy)**
El frontend React/TypeScript original está archivado en la rama `react-legacy` para referencia histórica.

**Para acceder al código React legacy:**
```bash
git checkout react-legacy
```

**Nota:** La línea HTMX es la activa y recomendada. El frontend React no se mantiene activamente.

---

## 📖 Documentación Adicional

- **[API_REFERENCE.md](API_REFERENCE.md)** - Referencia completa de endpoints
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Guía de deployment a producción
- **[backend/README.md](backend/README.md)** - Documentación técnica del backend
- **[QUICK_START.md](QUICK_START.md)** - Guía de inicio rápido
- **[GUIA_COMPLETA.md](GUIA_COMPLETA.md)** - Guía completa del sistema

---

## 🏷️ Versiones

- **v0.9.1** - Cobros & Caja + IVA Compras (actual)
- **v0.9.0** - Facturación Electrónica AFIP
- **v0.8.0** - Notificaciones + Remito + Etiqueta
- **v0.7.5** - Reservas de Stock
- **v0.7.0** - Módulo Pedidos + WhatsApp
- **v0.6.0** - Import/Export + Backups
- **v0.5.0** - Core CRUD + Stock

**Ver changelog completo:** `git tag -l -n9`

---

## 🤝 Contribuir

1. Crear rama desde `main`: `git checkout -b feature/mi-feature`
2. Implementar cambios con tests
3. Ejecutar smoke tests: `bash scripts/smoke.sh`
4. Commit y push
5. Crear Pull Request a `main`

**Convenciones:**
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bugs
- `chore:` - Tareas de mantenimiento
- `docs:` - Documentación
- `test:` - Tests

---

## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

---

## 🆘 Soporte

Para problemas o consultas:
1. Revisar documentación en `/docs`
2. Verificar logs: `docker compose -f docker-compose.dev.yml logs sc_backend --tail=100`
3. Ejecutar health check: `curl http://localhost:8000/health`
