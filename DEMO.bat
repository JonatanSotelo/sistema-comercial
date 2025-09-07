@echo off
title Sistema Comercial - DEMO
color 0A

echo.
echo ========================================
echo    SISTEMA COMERCIAL - DEMO
echo ========================================
echo.

echo 1. Verificando bases de datos...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr "sc_"

echo.
echo 2. Configurando Backend...
cd backend
set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db
echo DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db > .env

echo.
echo 3. Iniciando Backend en nueva ventana...
start "Backend - Sistema Comercial" cmd /k "cd /d %~dp0backend && set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo 4. Esperando que el backend esté listo...
timeout /t 8 /nobreak

echo.
echo 5. Verificando Backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend: FUNCIONANDO
) else (
    echo ⚠️ Backend: Iniciando...
)

echo.
echo 6. Configurando Frontend...
cd ..\frontend

echo.
echo 7. Iniciando Frontend en nueva ventana...
start "Frontend - Sistema Comercial" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"

echo.
echo 8. Esperando que el frontend esté listo...
timeout /t 10 /nobreak

echo.
echo ========================================
echo    SISTEMA COMERCIAL - DEMO LISTO
echo ========================================
echo.
echo 🌐 URLs de acceso:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 🔑 Credenciales:
echo    Usuario: admin
echo    Password: admin123
echo.
echo 📊 Bases de datos:
echo    PostgreSQL: localhost:5432 (sc_user/sc_pass/sc_db)
echo    Redis: localhost:6379
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

echo Abriendo navegador...
start http://localhost:3000

echo.
echo ¡DEMO LISTO PARA EL COMPRADOR!
echo.
pause


