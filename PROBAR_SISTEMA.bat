@echo off
echo ========================================
echo    PROBANDO SISTEMA COMPLETO
echo ========================================

echo.
echo 1. Limpiando contenedores anteriores...
cd infra
docker-compose down

echo.
echo 2. Construyendo y levantando sistema...
docker-compose up -d --build

echo.
echo 3. Esperando que los servicios esten listos...
timeout /t 10 /nobreak

echo.
echo 4. Verificando contenedores...
docker-compose ps

echo.
echo 5. Verificando logs del frontend...
docker-compose logs frontend

echo.
echo 6. Verificando logs del backend...
docker-compose logs backend

echo.
echo ========================================
echo    SISTEMA LISTO
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Presiona cualquier tecla para continuar...
pause


