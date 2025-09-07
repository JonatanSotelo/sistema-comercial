@echo off
title Sistema Comercial - Iniciando
color 0A

echo.
echo ========================================
echo    INICIANDO SISTEMA COMERCIAL
echo ========================================
echo.

echo 1. Verificando contenedores...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo 2. Configurando Backend...
cd backend
set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db
echo DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db > .env

echo.
echo 3. Iniciando Backend...
start "Backend" cmd /k "cd /d %~dp0backend && set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo 4. Esperando que el backend esté listo...
timeout /t 10 /nobreak

echo.
echo 5. Verificando Backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend: FUNCIONANDO
) else (
    echo ❌ Backend: NO FUNCIONA
)

echo.
echo 6. Configurando Frontend...
cd ..\frontend

echo.
echo 7. Iniciando Frontend...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"

echo.
echo 8. Esperando que el frontend esté listo...
timeout /t 15 /nobreak

echo.
echo 9. Verificando Frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend: FUNCIONANDO
) else (
    echo ❌ Frontend: NO FUNCIONA
)

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


