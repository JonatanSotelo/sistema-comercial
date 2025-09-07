@echo off
echo 🚀 Instalando Sistema Comercial...

REM Verificar que Docker esté instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está instalado. Por favor instala Docker Desktop.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose no está instalado. Por favor instala Docker Compose.
    pause
    exit /b 1
)

REM Crear directorios necesarios
echo 📁 Creando directorios...
if not exist "database" mkdir database
if not exist "nginx\ssl" mkdir nginx\ssl
if not exist "modules\facturacion" mkdir modules\facturacion
if not exist "modules\logistica" mkdir modules\logistica
if not exist "modules\envios" mkdir modules\envios
if not exist "modules\mobile-api" mkdir modules\mobile-api

REM Crear archivo de inicialización de base de datos
echo 🗄️ Configurando base de datos...
(
echo -- Script de inicialización de la base de datos
echo CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
echo.
echo -- Crear esquemas para módulos
echo CREATE SCHEMA IF NOT EXISTS facturacion;
echo CREATE SCHEMA IF NOT EXISTS logistica;
echo CREATE SCHEMA IF NOT EXISTS envios;
echo CREATE SCHEMA IF NOT EXISTS mobile;
echo.
echo -- Usuario para módulos
echo CREATE USER IF NOT EXISTS modules_user WITH PASSWORD 'modules_pass';
echo GRANT USAGE ON SCHEMA facturacion, logistica, envios, mobile TO modules_user;
echo GRANT CREATE ON SCHEMA facturacion, logistica, envios, mobile TO modules_user;
) > database\init.sql

REM Construir y ejecutar contenedores
echo 🔨 Construyendo contenedores...
docker-compose build

echo 🚀 Iniciando servicios...
docker-compose up -d

REM Esperar a que los servicios estén listos
echo ⏳ Esperando a que los servicios estén listos...
timeout /t 30 /nobreak >nul

REM Verificar estado
echo ✅ Verificando estado de los servicios...
docker-compose ps

echo.
echo 🎉 ¡Sistema Comercial instalado correctamente!
echo.
echo 📱 Accesos:
echo    • Frontend: http://localhost
echo    • API Docs: http://localhost/docs
echo    • PgAdmin: http://localhost:5050
echo    • Backend API: http://localhost:8000
echo.
echo 🔧 Comandos útiles:
echo    • Ver logs: docker-compose logs -f
echo    • Parar servicios: docker-compose down
echo    • Reiniciar: docker-compose restart
echo    • Con módulos: docker-compose --profile modules up -d
echo.
echo 📚 Para más información, consulta el README.md
pause


