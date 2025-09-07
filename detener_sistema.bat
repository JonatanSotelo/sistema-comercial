@echo off
echo ========================================
echo    DETENIENDO SISTEMA COMERCIAL
echo ========================================

echo.
echo 1. Deteniendo contenedores Docker...
docker stop sc_postgres sc_redis 2>nul
docker rm sc_postgres sc_redis 2>nul

echo.
echo 2. Deteniendo procesos de Python (Backend)...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul

echo.
echo 3. Deteniendo procesos de Node.js (Frontend)...
taskkill /f /im node.exe 2>nul

echo.
echo 4. Limpiando archivos temporales...
if exist backend\__pycache__ rmdir /s /q backend\__pycache__
if exist frontend\node_modules\.cache rmdir /s /q frontend\node_modules\.cache

echo.
echo ========================================
echo    SISTEMA DETENIDO CORRECTAMENTE
echo ========================================
echo.
pause


