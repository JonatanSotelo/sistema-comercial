@echo off
echo ========================================
echo    LEVANTANDO SISTEMA COMPLETO
echo ========================================

echo.
echo 1. Limpiando contenedores anteriores...
cd infra
docker-compose down

echo.
echo 2. Construyendo backend...
docker-compose build backend

echo.
echo 3. Construyendo frontend...
docker-compose build frontend

echo.
echo 4. Levantando base de datos...
docker-compose up -d db redis

echo.
echo 5. Esperando que la base de datos este lista...
timeout /t 15 /nobreak

echo.
echo 6. Levantando backend...
docker-compose up -d backend

echo.
echo 7. Esperando que el backend este listo...
timeout /t 10 /nobreak

echo.
echo 8. Levantando frontend...
docker-compose up -d frontend

echo.
echo 9. Verificando contenedores...
docker-compose ps

echo.
echo ========================================
echo    SISTEMA LISTO
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Presiona cualquier tecla para ver logs...
pause

echo.
echo Logs del Frontend:
docker-compose logs frontend

echo.
echo Logs del Backend:
docker-compose logs backend


