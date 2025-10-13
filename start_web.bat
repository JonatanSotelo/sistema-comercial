@echo off
REM Script para iniciar el Sistema Comercial con el nuevo frontend Python

echo ================================================
echo Sistema Comercial - Frontend Python
echo ================================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "backend" (
    echo Error: No se encuentra el directorio 'backend'
    echo Por favor ejecuta este script desde el directorio raiz del proyecto
    pause
    exit /b 1
)

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no esta instalado
    pause
    exit /b 1
)

echo Python encontrado
echo.

REM Ir al directorio backend
cd backend

REM Verificar si existe virtual environment
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar virtual environment
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar/actualizar dependencias
echo Instalando dependencias...
pip install -r requirements.txt --quiet

echo.
echo ================================================
echo Configuracion completada
echo ================================================
echo.
echo Iniciando servidor...
echo.
echo    Frontend Web: http://localhost:8000/app
echo    API Docs:     http://localhost:8000/docs
echo.
echo    Usuario:      admin
echo    Password:     admin123
echo.
echo ================================================
echo.

REM Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


