# 🚀 Sistema Comercial - Instrucciones Rápidas

## ✅ Estado Actual
- ✅ PostgreSQL funcionando en puerto 5432
- ✅ Redis funcionando en puerto 6379
- ✅ Backend configurado y listo
- ✅ Frontend configurado y listo

## 🎯 Inicio Rápido

### Opción 1: Script Automático (Recomendado)
```bash
# Doble clic en:
start_all.bat
```

### Opción 2: Manual
```bash
# 1. Levantar bases de datos
docker run -d --name sc_postgres -e POSTGRES_USER=sc_user -e POSTGRES_PASSWORD=sc_pass -e POSTGRES_DB=sc_db -p 5432:5432 postgres:16
docker run -d --name sc_redis -p 6379:6379 redis:7-alpine

# 2. Levantar backend
cd backend
source venv/Scripts/activate
set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Levantar frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

## 🌐 URLs de Acceso
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🔧 Credenciales
- **PostgreSQL**: usuario: `sc_user`, password: `sc_pass`, base: `sc_db`
- **Admin**: usuario: `admin`, password: `admin123`

## 🛑 Parar el Sistema
```bash
# Doble clic en:
stop_all.bat
```

## 📁 Archivos Importantes
- `start_all.bat` - Inicia todo el sistema
- `stop_all.bat` - Detiene todo el sistema
- `backend/.env` - Configuración del backend
- `docker-compose.yml` - Configuración de Docker

## ⚠️ Notas
- El sistema está configurado para desarrollo local
- Las bases de datos se crean automáticamente
- El backend tiene recarga automática (hot reload)
- El frontend tiene recarga automática (hot reload)


