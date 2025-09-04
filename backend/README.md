# Sistema Comercial — Sistema de Gestión Completo

FastAPI + SQLAlchemy + Alembic + PostgreSQL + Docker + JWT + Excel Export + Backup Automático

## 🚀 Estado del Proyecto

**✅ SISTEMA COMPLETAMENTE FUNCIONAL**

* **Autenticación JWT** completa con roles `admin` y `consulta`
* **Módulos completos**: usuarios, productos, clientes, proveedores, compras, ventas, stock, auditoría
* **Exportación Excel** para todos los módulos
* **Backup automático** programado diariamente
* **API documentada** en `/docs` con Swagger UI
* **Tests implementados** con pytest

---

## 🏗️ Arquitectura

### Estructura del Proyecto
```
backend/
├── app/
│   ├── core/           # Configuración, seguridad, dependencias
│   ├── db/             # Base de datos y modelos
│   ├── models/         # Modelos SQLAlchemy
│   ├── schemas/        # Validaciones Pydantic
│   ├── services/       # Lógica de negocio
│   ├── routers/        # Endpoints de API
│   └── main.py         # Aplicación FastAPI
├── migrations/         # Migraciones Alembic
├── tests/             # Tests automatizados
└── requirements.txt   # Dependencias
```

### Tecnologías
- **Backend**: FastAPI 0.116+ con Python 3.11+
- **Base de Datos**: PostgreSQL con SQLAlchemy 2.0
- **Autenticación**: JWT con python-jose
- **Validación**: Pydantic 2.11+
- **Exportación**: OpenPyXL para Excel
- **Scheduler**: APScheduler para tareas automáticas
- **Testing**: pytest con httpx

---

## 🚀 Instalación y Uso

### Requisitos
* Docker Desktop
* Git

### Arranque Rápido

```bash
# 1) Clonar el repositorio
git clone https://github.com/JonatanSotelo/sistema-comercial.git
cd sistema-comercial

# 2) Levantar servicios con Docker
docker compose -f infra/docker-compose.yml up -d --build

# 3) Ver logs del backend
docker compose -f infra/docker-compose.yml logs -f backend --tail=100
# Esperar: "Application startup complete."
```

### Variables de Entorno

Crear archivo `backend/.env`:
```ini
# Base de datos
DATABASE_URL=postgresql+psycopg2://postgres:postgres@sc_postgres:5432/postgres

# JWT (cambiar en producción)
SECRET_KEY=tu-clave-secreta-super-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Backup
BACKUP_DIR=/app/backups
```

---

## 🔐 Autenticación

### Credenciales Iniciales
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Rol**: `admin` (acceso completo)

### Obtener Token

**Opción A - Form (recomendado para /docs):**
```bash
curl -X POST "http://localhost:8000/auth/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Opción B - JSON:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Usar Token
```bash
curl -H "Authorization: Bearer TU_TOKEN_AQUI" \
  http://localhost:8000/users/usuarios/me
```

---

## 📚 API Endpoints

### 🔐 Autenticación
- `POST /auth/oauth2/token` - Login con form
- `POST /auth/login` - Login con JSON

### 👥 Usuarios
- `GET /users/` - Listar usuarios (admin)
- `GET /users/usuarios/me` - Usuario actual
- `POST /users/` - Crear usuario (admin)
- `PUT /users/{id}` - Actualizar usuario (admin)
- `DELETE /users/{id}` - Eliminar usuario (admin)

### 📦 Productos
- `GET /productos` - Listar con paginación y filtros
- `GET /productos/{id}` - Obtener producto
- `POST /productos` - Crear producto (admin)
- `PUT /productos/{id}` - Actualizar producto (admin)
- `DELETE /productos/{id}` - Eliminar producto (admin)
- `GET /productos/export` - Exportar a Excel

### 👤 Clientes
- `GET /clientes` - Listar con paginación
- `GET /clientes/{id}` - Obtener cliente
- `POST /clientes` - Crear cliente
- `PUT /clientes/{id}` - Actualizar cliente
- `DELETE /clientes/{id}` - Eliminar cliente
- `GET /clientes/export` - Exportar a Excel

### 🏢 Proveedores
- `GET /proveedores` - Listar con paginación
- `GET /proveedores/{id}` - Obtener proveedor
- `POST /proveedores` - Crear proveedor
- `PUT /proveedores/{id}` - Actualizar proveedor
- `DELETE /proveedores/{id}` - Eliminar proveedor
- `GET /proveedores/export` - Exportar a Excel

### 🛒 Compras
- `GET /compras` - Listar compras
- `GET /compras/{id}` - Obtener compra
- `POST /compras` - Crear compra
- `GET /compras/stock/{producto_id}` - Stock actual

### 💰 Ventas
- `GET /ventas` - Listar ventas
- `GET /ventas/{id}` - Obtener venta
- `POST /ventas` - Crear venta
- `PUT /ventas/{id}` - Actualizar venta
- `DELETE /ventas/{id}` - Eliminar venta

### 📊 Stock
- `GET /stock` - Stock actual de productos

### 📋 Auditoría
- `GET /auditoria` - Logs de auditoría (admin)

### 💾 Backup
- `POST /backup/run` - Ejecutar backup manual
- `GET /backup/download` - Descargar último backup

### 🏥 Sistema
- `GET /` - Health check básico
- `GET /health` - Health check con base de datos

---

## 🔍 Parámetros de Consulta

### Paginación
- `page` - Número de página (default: 1)
- `size` - Tamaño de página (default: 20, max: 200)

### Filtros
- `search` - Búsqueda de texto (busca en nombre, email, etc.)
- `sort` - Ordenamiento (ej: `nombre,-precio` para nombre ASC, precio DESC)

### Ejemplos
```bash
# Listar productos con paginación
GET /productos?page=1&size=10

# Buscar clientes
GET /clientes?search=empresa&page=1&size=5

# Ordenar productos por precio descendente
GET /productos?sort=-precio
```

---

## 🧪 Testing

### Ejecutar Tests
```bash
# Desde el directorio backend
cd backend
pytest

# Con verbose
pytest -v

# Tests específicos
pytest tests/test_auth.py
```

### Tests Disponibles
- `test_00_health.py` - Health checks
- `test_01_auth.py` - Autenticación
- `test_02_users_crud.py` - CRUD de usuarios
- `test_productos.py` - Productos
- `test_clientes.py` - Clientes
- `test_proveedores.py` - Proveedores
- `test_backup.py` - Sistema de backup

---

## 📊 Funcionalidades Avanzadas

### Exportación Excel
Todos los módulos principales soportan exportación a Excel:
```bash
# Exportar productos
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/productos/export" \
  -o productos.xlsx

# Exportar clientes
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/clientes/export" \
  -o clientes.xlsx
```

### Sistema de Stock
- **Movimientos automáticos**: Las compras incrementan stock, las ventas lo decrementan
- **Validación**: No se pueden hacer ventas sin stock suficiente
- **Trazabilidad**: Cada movimiento queda registrado con motivo y referencia

### Auditoría
- **Registro automático** de todas las operaciones CRUD
- **Información capturada**: usuario, IP, método HTTP, datos modificados
- **Consulta**: Disponible en `/auditoria` para administradores

### Backup Automático
- **Programado**: Diariamente a las 02:30 AM
- **Formato**: ZIP con dump de PostgreSQL
- **Descarga**: Disponible en `/backup/download`

---

## 🐳 Docker

### Comandos Útiles
```bash
# Ver logs
docker compose -f infra/docker-compose.yml logs -f backend

# Reiniciar solo backend
docker compose -f infra/docker-compose.yml restart backend

# Acceder al contenedor
docker exec -it sc_backend bash

# Ver estado de servicios
docker compose -f infra/docker-compose.yml ps
```

### Backup Manual
```bash
# Crear backup
docker exec sc_postgres pg_dump -U postgres -d postgres > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker exec -i sc_postgres psql -U postgres -d postgres < backup_file.sql
```

---

## 🔧 Desarrollo

### Estructura de Código
- **Models**: Definición de entidades de base de datos
- **Schemas**: Validación de datos de entrada/salida
- **Services**: Lógica de negocio
- **Routers**: Endpoints de API
- **Core**: Configuración, seguridad, dependencias

### Agregar Nuevo Módulo
1. Crear modelo en `app/models/`
2. Crear schemas en `app/schemas/`
3. Crear servicio en `app/services/`
4. Crear router en `app/routers/`
5. Registrar router en `app/routers/__init__.py`

### Migraciones
```bash
# Crear migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

---

## 🚨 Troubleshooting

### Problemas Comunes

**401 Unauthorized**
- Verificar que el token sea válido
- Comprobar formato del header: `Authorization: Bearer TOKEN`

**403 Forbidden**
- Verificar que el usuario tenga rol `admin` para operaciones administrativas
- Consultar en base de datos: `SELECT username, role FROM users;`

**500 Internal Server Error**
- Revisar logs del backend
- Verificar conexión a base de datos
- Comprobar configuración de variables de entorno

**Error de conexión a base de datos**
- Verificar que PostgreSQL esté corriendo
- Comprobar URL de conexión en `settings.py`
- Revisar logs de Docker

### Logs
```bash
# Logs del backend
docker compose -f infra/docker-compose.yml logs backend

# Logs de base de datos
docker compose -f infra/docker-compose.yml logs sc_postgres

# Logs en tiempo real
docker compose -f infra/docker-compose.yml logs -f backend
```

---

## 📈 Roadmap

### Próximas Funcionalidades
- [ ] Dashboard con métricas
- [ ] Reportes avanzados
- [ ] Notificaciones por email
- [ ] API de integración con sistemas externos
- [ ] Modo offline con sincronización
- [ ] App móvil

### Mejoras Técnicas
- [ ] Cache con Redis
- [ ] Rate limiting
- [ ] Monitoreo con Prometheus
- [ ] CI/CD con GitHub Actions
- [ ] Tests de integración E2E

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.

---

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

---

## 📞 Soporte

Para soporte técnico o consultas:
- **Email**: bbip@live.com.ar
- **Issues**: GitHub Issues
- **Documentación**: `/docs` en la aplicación

---

**¡Sistema Comercial - Gestión empresarial completa y moderna!** 🚀