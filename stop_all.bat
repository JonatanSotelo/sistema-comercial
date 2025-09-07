@echo off
echo Deteniendo Sistema Comercial...

echo.
echo 1. Deteniendo contenedores...
docker stop sc_postgres sc_redis
docker rm sc_postgres sc_redis

echo.
echo 2. Matando procesos de Python y Node...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo ¡Sistema Comercial detenido!
pause


