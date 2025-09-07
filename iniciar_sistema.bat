@echo off
echo ========================================
echo    INICIANDO SISTEMA COMERCIAL
echo ========================================

echo.
echo 1. Limpiando contenedores existentes...
docker stop sc_postgres sc_redis 2>nul
docker rm sc_postgres sc_redis 2>nul

echo.
echo 2. Iniciando PostgreSQL...
docker run -d --name sc_postgres -e POSTGRES_USER=sc_user -e POSTGRES_PASSWORD=sc_pass -e POSTGRES_DB=sc_db -p 5432:5432 postgres:16
if %errorlevel% neq 0 (
    echo ERROR: No se pudo iniciar PostgreSQL
    pause
    exit /b 1
)

echo.
echo 3. Iniciando Redis...
docker run -d --name sc_redis -p 6379:6379 redis:7-alpine
if %errorlevel% neq 0 (
    echo ERROR: No se pudo iniciar Redis
    pause
    exit /b 1
)

echo.
echo 4. Esperando que las bases de datos estén listas...
timeout /t 10 /nobreak

echo.
echo 5. Verificando que PostgreSQL esté funcionando...
docker exec sc_postgres pg_isready -U sc_user -d sc_db
if %errorlevel% neq 0 (
    echo ERROR: PostgreSQL no está respondiendo
    pause
    exit /b 1
)

echo.
echo 6. Configurando backend...
cd backend
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

echo Activando entorno virtual...
call venv\Scripts\activate

echo Instalando dependencias...
pip install -r requirements.txt

echo Configurando variables de entorno...
echo DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db > .env

echo.
echo 7. Iniciando Backend en nueva ventana...
start "Backend - Sistema Comercial" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo 8. Esperando que el backend esté listo...
timeout /t 5 /nobreak

echo.
echo 9. Verificando que el backend esté funcionando...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Backend no responde aún, pero debería estar iniciando...
)

echo.
echo 10. Configurando frontend...
cd ..\frontend

echo Instalando dependencias del frontend...
npm install

echo.
echo 11. Iniciando Frontend en nueva ventana...
start "Frontend - Sistema Comercial" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo    SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo URLs de acceso:
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo.
echo Credenciales:
echo - Usuario: admin
echo - Password: admin123
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

echo Abriendo navegador...
start http://localhost:3000

echo.
echo Para detener el sistema, ejecuta: detener_sistema.bat
pause


