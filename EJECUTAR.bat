@echo off
echo ========================================
echo    EJECUTANDO SISTEMA COMPLETO
echo ========================================

echo.
echo 1. Limpiando contenedores anteriores...
docker-compose -f infra/docker-compose.yml down

echo.
echo 2. Construyendo y levantando sistema...
docker-compose -f infra/docker-compose.yml up -d --build

echo.
echo 3. Esperando que los servicios esten listos...
timeout /t 20 /nobreak

echo.
echo 4. Verificando contenedores...
docker-compose -f infra/docker-compose.yml ps

echo.
echo 5. Verificando logs del frontend...
docker-compose -f infra/docker-compose.yml logs frontend

echo.
echo 6. Verificando logs del backend...
docker-compose -f infra/docker-compose.yml logs backend

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


