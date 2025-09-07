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

echo.
echo 3. Iniciando Redis...
docker run -d --name sc_redis -p 6379:6379 redis:7-alpine

echo.
echo 4. Esperando que las bases de datos estén listas...
timeout /t 10 /nobreak

echo.
echo 5. Iniciando Backend...
start "Backend" cmd /k "cd /d %~dp0 && levantar_backend.bat"

echo.
echo 6. Esperando que el backend esté listo...
timeout /t 5 /nobreak

echo.
echo 7. Iniciando Frontend...
start "Frontend" cmd /k "cd /d %~dp0 && levantar_frontend.bat"

echo.
echo ========================================
echo    SISTEMA INICIADO
echo ========================================
echo.
echo URLs:
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul
start http://localhost:3000


