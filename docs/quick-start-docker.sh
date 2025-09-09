#!/bin/bash

# 🚀 Script de Inicio Rápido para Docker - IDP Expert System
# Uso: ./quick-start-docker.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar prerrequisitos
check_prerequisites() {
    log "🔍 Verificando prerrequisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error "❌ Docker no está instalado. Instálalo desde: https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "❌ Docker Compose no está instalado"
        exit 1
    fi
    
    # Verificar que Docker esté ejecutándose
    if ! docker info &> /dev/null; then
        error "❌ Docker no está ejecutándose. Inicia Docker Desktop"
        exit 1
    fi
    
    # Verificar archivo .env
    if [ ! -f ".env" ]; then
        warning "⚠️ Archivo .env no encontrado"
        if [ -f "env.example" ]; then
            log "📋 Copiando env.example a .env"
            cp env.example .env
            warning "⚠️ Edita el archivo .env con tus credenciales de Azure"
            read -p "Presiona Enter cuando hayas configurado el .env..."
        else
            error "❌ No se encontró env.example. Configura manualmente el archivo .env"
            exit 1
        fi
    fi
    
    success "✅ Prerrequisitos verificados"
}

# Función para limpiar recursos existentes
cleanup_existing() {
    log "🧹 Limpiando recursos existentes..."
    
    # Detener contenedores si están ejecutándose
    docker-compose down 2>/dev/null || true
    
    # Limpiar contenedores huérfanos
    docker container prune -f 2>/dev/null || true
    
    success "✅ Limpieza completada"
}

# Función para construir imagen
build_image() {
    log "🔨 Construyendo imagen Docker..."
    
    # Construir imagen
    docker build -t idp-expert-system:latest .
    
    success "✅ Imagen construida exitosamente"
}

# Función para levantar servicios
start_services() {
    log "🚀 Levantando servicios..."
    
    # Levantar servicios en background
    docker-compose up -d
    
    success "✅ Servicios iniciados"
}

# Función para esperar que la API esté lista
wait_for_api() {
    log "⏳ Esperando que la API esté lista..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://159.203.149.247:8000/health > /dev/null 2>&1; then
            success "✅ API funcionando correctamente"
            return 0
        fi
        
        log "   Intento $attempt/$max_attempts - Esperando..."
        sleep 10
        ((attempt++))
    done
    
    error "❌ API no respondió después de $max_attempts intentos"
    return 1
}

# Función para mostrar información del despliegue
show_deployment_info() {
    log "📊 Información del despliegue:"
    echo ""
    echo "🌐 API URL: http://159.203.149.247:8000"
    echo "📚 Swagger UI: http://159.203.149.247:8000/docs"
    echo "📖 ReDoc: http://159.203.149.247:8000/redoc"
    echo "🔍 Health Check: http://159.203.149.247:8000/health"
    echo ""
    echo "📋 Contenedores ejecutándose:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
}

# Función para mostrar comandos útiles
show_useful_commands() {
    log "💡 Comandos útiles:"
    echo ""
    echo "📊 Ver logs en tiempo real:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🔄 Reiniciar servicios:"
    echo "   docker-compose restart"
    echo ""
    echo "🛑 Detener servicios:"
    echo "   docker-compose down"
    echo ""
    echo "🧹 Limpiar recursos:"
    echo "   docker system prune -a -f"
    echo ""
}

# Función para test rápido
quick_test() {
    log "🧪 Ejecutando test rápido..."
    
    # Test de health check
    if curl -f http://159.203.149.247:8000/health > /dev/null 2>&1; then
        success "✅ Health check exitoso"
    else
        error "❌ Health check falló"
        return 1
    fi
    
    # Test de storage health
    if curl -f http://159.203.149.247:8000/api/v1/health/storage > /dev/null 2>&1; then
        success "✅ Storage health check exitoso"
    else
        warning "⚠️ Storage health check falló (puede ser normal si Azure no está configurado)"
    fi
    
    success "✅ Test rápido completado"
}

# Función principal
main() {
    echo "🚀 INICIO RÁPIDO - IDP Expert System en Docker"
    echo "================================================"
    echo ""
    
    # Verificar prerrequisitos
    check_prerequisites
    
    # Limpiar recursos existentes
    cleanup_existing
    
    # Construir imagen
    build_image
    
    # Levantar servicios
    start_services
    
    # Esperar que la API esté lista
    if wait_for_api; then
        # Mostrar información del despliegue
        show_deployment_info
        
        # Ejecutar test rápido
        quick_test
        
        # Mostrar comandos útiles
        show_useful_commands
        
        success "🎉 ¡Despliegue completado exitosamente!"
        echo ""
        echo "🌐 Tu API está disponible en: http://159.203.149.247:8000"
        echo "📚 Documentación en: http://159.203.149.247:8000/docs"
        echo ""
        echo "💡 Para más información, consulta: docs/Guia_Despliegue_Local_Docker.md"
        
    else
        error "❌ El despliegue falló. Revisa los logs:"
        echo "   docker-compose logs -f"
        exit 1
    fi
}

# Ejecutar función principal
main "$@"
