@echo off
echo ========================================
echo    VERIFICANDO SISTEMA COMERCIAL
echo ========================================

echo.
echo 1. Verificando contenedores Docker...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo 2. Verificando PostgreSQL...
docker exec sc_postgres pg_isready -U sc_user -d sc_db 2>nul
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL: FUNCIONANDO
) else (
    echo ❌ PostgreSQL: NO FUNCIONA
)

echo.
echo 3. Verificando Redis...
docker exec sc_redis redis-cli ping 2>nul | findstr "PONG" >nul
if %errorlevel% equ 0 (
    echo ✅ Redis: FUNCIONANDO
) else (
    echo ❌ Redis: NO FUNCIONA
)

echo.
echo 4. Verificando Backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend: FUNCIONANDO (http://localhost:8000)
) else (
    echo ❌ Backend: NO FUNCIONA
)

echo.
echo 5. Verificando Frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend: FUNCIONANDO (http://localhost:3000)
) else (
    echo ❌ Frontend: NO FUNCIONA
)

echo.
echo 6. Verificando API Documentation...
curl -s http://localhost:8000/docs >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API Docs: FUNCIONANDO (http://localhost:8000/docs)
) else (
    echo ❌ API Docs: NO FUNCIONA
)

echo.
echo ========================================
echo    RESUMEN DE VERIFICACIÓN
echo ========================================
echo.
echo Si todo está funcionando, puedes acceder a:
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo.
pause


