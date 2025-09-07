@echo off
echo Iniciando Sistema Comercial...

echo.
echo 1. Iniciando PostgreSQL...
docker run -d --name sc_postgres -e POSTGRES_USER=sc_user -e POSTGRES_PASSWORD=sc_pass -e POSTGRES_DB=sc_db -p 5432:5432 postgres:16

echo.
echo 2. Iniciando Redis...
docker run -d --name sc_redis -p 6379:6379 redis:7-alpine

echo.
echo 3. Esperando 10 segundos para que las bases de datos estén listas...
timeout /t 10 /nobreak

echo.
echo 4. Iniciando Backend...
start "Backend" cmd /k "cd backend && call venv\Scripts\activate && set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo 5. Esperando 5 segundos para que el backend esté listo...
timeout /t 5 /nobreak

echo.
echo 6. Iniciando Frontend...
start "Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ¡Sistema Comercial iniciado!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo PostgreSQL: localhost:5432 (usuario: sc_user, password: sc_pass, db: sc_db)
echo Redis: localhost:6379
echo.
pause


