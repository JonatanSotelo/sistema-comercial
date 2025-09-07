# Sistema Comercial - Versión Docker

Sistema comercial modular y escalable con arquitectura de microservicios usando Docker.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │    Frontend     │    │    Backend      │
│  (Proxy) :80    │◄──►│   React :3000   │◄──►│   FastAPI :8000 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │      :5432      │
                    └─────────────────┘
```

## 🚀 Instalación Rápida

### Windows
```bash
# Ejecutar como administrador
install.bat
```

### Linux/Mac
```bash
chmod +x install.sh
./install.sh
```

## 📱 Accesos

- **Frontend**: http://localhost
- **API Docs**: http://localhost/docs
- **Backend API**: http://localhost:8000
- **PgAdmin**: http://localhost:5050

## 🔧 Comandos Útiles

### Gestión de Servicios
```bash
# Iniciar todos los servicios
docker-compose up -d

# Iniciar con módulos adicionales
docker-compose --profile modules up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart backend
```

### Desarrollo
```bash
# Reconstruir un servicio
docker-compose build backend

# Ejecutar comandos en contenedores
docker-compose exec backend python manage.py migrate
docker-compose exec frontend npm install

# Acceder al shell de un contenedor
docker-compose exec backend bash
```

## 🏢 Módulos Disponibles

### Core (Siempre activo)
- ✅ **Backend API**: API principal con FastAPI
- ✅ **Frontend**: Interfaz web con React
- ✅ **Base de datos**: PostgreSQL
- ✅ **Cache**: Redis

### Módulos Adicionales (Opcionales)
- 🔄 **Facturación**: Gestión de facturas y comprobantes
- 🔄 **Logística**: Gestión de inventario y almacenes
- 🔄 **Envíos**: Seguimiento de envíos y entregas
- 🔄 **Mobile API**: API para aplicación móvil

## 🌐 Despliegue en la Nube

### AWS
```bash
# Usar docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

### Azure
```bash
# Usar Azure Container Instances
az container create --resource-group myRG --name sistema-comercial --image myregistry/sistema-comercial
```

### Google Cloud
```bash
# Usar Cloud Run
gcloud run deploy sistema-comercial --image gcr.io/myproject/sistema-comercial
```

## 🔒 Seguridad

### Variables de Entorno
```bash
# Crear archivo .env
SECRET_KEY=tu-clave-super-secreta
DATABASE_URL=postgresql://user:pass@db:5432/db
REDIS_URL=redis://redis:6379/0
```

### SSL/TLS
```bash
# Colocar certificados en nginx/ssl/
# El sistema detectará automáticamente los certificados
```

## 📊 Monitoreo

### Logs
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
```

### Métricas
- **Health Check**: http://localhost/health
- **API Status**: http://localhost:8000/health
- **Database**: PgAdmin en http://localhost:5050

## 🛠️ Desarrollo

### Estructura de Módulos
```
modules/
├── facturacion/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── logistica/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
└── envios/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
```

### Agregar Nuevo Módulo
1. Crear directorio en `modules/nuevo-modulo/`
2. Agregar Dockerfile
3. Actualizar `docker-compose.yml`
4. Agregar perfil `modules`

## 🚨 Solución de Problemas

### Puerto en uso
```bash
# Cambiar puertos en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### Base de datos no conecta
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose logs db

# Reiniciar base de datos
docker-compose restart db
```

### Frontend no carga
```bash
# Verificar que el frontend esté construido
docker-compose logs frontend

# Reconstruir frontend
docker-compose build frontend
```

## 📞 Soporte

Para soporte técnico o consultas:
- 📧 Email: soporte@sistema-comercial.com
- 📱 WhatsApp: +54 9 11 1234-5678
- 🌐 Web: https://sistema-comercial.com

---

**¡Sistema Comercial - Modular, Escalable y Profesional!** 🚀


