#!/bin/bash
# Script para iniciar el Sistema Comercial con el nuevo frontend Python

echo "================================================"
echo "🚀 Sistema Comercial - Frontend Python"
echo "================================================"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -d "backend" ]; then
    echo "❌ Error: No se encuentra el directorio 'backend'"
    echo "   Por favor ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Ir al directorio backend
cd backend

# Verificar si existe virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar virtual environment
echo "🔄 Activando entorno virtual..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Instalar/actualizar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt --quiet

echo ""
echo "================================================"
echo "✅ Configuración completada"
echo "================================================"
echo ""
echo "🌐 Iniciando servidor..."
echo ""
echo "   Frontend Web: http://localhost:8000/app"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "   Usuario:      admin"
echo "   Password:     admin123"
echo ""
echo "================================================"
echo ""

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


