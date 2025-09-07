#!/bin/bash

# Script de instalación del Sistema Comercial
echo "🚀 Instalando Sistema Comercial..."

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose."
    exit 1
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p database
mkdir -p nginx/ssl
mkdir -p modules/{facturacion,logistica,envios,mobile-api}

# Crear archivo de inicialización de base de datos
echo "🗄️ Configurando base de datos..."
cat > database/init.sql << 'EOF'
-- Script de inicialización de la base de datos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear esquemas para módulos
CREATE SCHEMA IF NOT EXISTS facturacion;
CREATE SCHEMA IF NOT EXISTS logistica;
CREATE SCHEMA IF NOT EXISTS envios;
CREATE SCHEMA IF NOT EXISTS mobile;

-- Usuario para módulos
CREATE USER IF NOT EXISTS modules_user WITH PASSWORD 'modules_pass';
GRANT USAGE ON SCHEMA facturacion, logistica, envios, mobile TO modules_user;
GRANT CREATE ON SCHEMA facturacion, logistica, envios, mobile TO modules_user;
EOF

# Construir y ejecutar contenedores
echo "🔨 Construyendo contenedores..."
docker-compose build

echo "🚀 Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 30

# Verificar estado
echo "✅ Verificando estado de los servicios..."
docker-compose ps

echo ""
echo "🎉 ¡Sistema Comercial instalado correctamente!"
echo ""
echo "📱 Accesos:"
echo "   • Frontend: http://localhost"
echo "   • API Docs: http://localhost/docs"
echo "   • PgAdmin: http://localhost:5050"
echo "   • Backend API: http://localhost:8000"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver logs: docker-compose logs -f"
echo "   • Parar servicios: docker-compose down"
echo "   • Reiniciar: docker-compose restart"
echo "   • Con módulos: docker-compose --profile modules up -d"
echo ""
echo "📚 Para más información, consulta el README.md"


