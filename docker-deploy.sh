#!/bin/bash

# 🐳 Script de Build y Despliegue para IDP Expert System
# Uso: ./docker-deploy.sh [build|test|deploy|clean]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
IMAGE_NAME="idp-expert-system"
TAG="latest"
CONTAINER_NAME="idp-expert-system"

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

# Función para build de la imagen
build_image() {
    log "🔨 Construyendo imagen Docker..."
    
    # Verificar que existe Dockerfile
    if [ ! -f "Dockerfile" ]; then
        error "❌ Dockerfile no encontrado"
        exit 1
    fi
    
    # Verificar que existe requirements.txt
    if [ ! -f "requirements.txt" ]; then
        error "❌ requirements.txt no encontrado"
        exit 1
    fi
    
    # Build de la imagen
    docker build -t ${IMAGE_NAME}:${TAG} .
    
    success "✅ Imagen construida exitosamente: ${IMAGE_NAME}:${TAG}"
    
    # Mostrar información de la imagen
    log "📊 Información de la imagen:"
    docker images ${IMAGE_NAME}:${TAG}
}

# Función para test local
test_local() {
    log "🧪 Probando aplicación localmente..."
    
    # Detener contenedores existentes
    docker-compose down 2>/dev/null || true
    
    # Construir y levantar servicios
    docker-compose up --build -d
    
    # Esperar que la API esté lista
    log "⏳ Esperando que la API esté lista..."
    sleep 30
    
    # Verificar health check
    if curl -f http://159.203.149.247:8000/health > /dev/null 2>&1; then
        success "✅ API funcionando correctamente en http://159.203.149.247:8000"
        log "📚 Documentación disponible en:"
        log "   • Swagger UI: http://159.203.149.247:8000/docs"
        log "   • ReDoc: http://159.203.149.247:8000/redoc"
    else
        error "❌ API no responde al health check"
        docker-compose logs idp-api
        exit 1
    fi
}

# Función para deploy en Azure
deploy_azure() {
    log "☁️ Preparando despliegue en Azure..."
    
    # Verificar que existe .env
    if [ ! -f ".env" ]; then
        error "❌ Archivo .env no encontrado. Configura las variables de entorno primero."
        exit 1
    fi
    
    # Verificar Azure CLI
    if ! command -v az &> /dev/null; then
        error "❌ Azure CLI no está instalado. Instálalo primero: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Verificar login en Azure
    if ! az account show &> /dev/null; then
        error "❌ No estás logueado en Azure. Ejecuta: az login"
        exit 1
    fi
    
    log "🔐 Configurando Azure Container Registry..."
    
    # Variables de Azure (configurar según tu entorno)
    RESOURCE_GROUP="idp-resource-group"
    LOCATION="eastus"
    ACR_NAME="idpacr$(date +%s | tail -c 4)"
    ACI_NAME="idp-api-aci"
    
    # Crear Resource Group si no existe
    az group create --name $RESOURCE_GROUP --location $LOCATION
    
    # Crear Azure Container Registry
    az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
    
    # Login al ACR
    az acr login --name $ACR_NAME
    
    # Tag de la imagen para ACR
    ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
    docker tag ${IMAGE_NAME}:${TAG} ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${TAG}
    
    # Push de la imagen
    docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${TAG}
    
    # Crear Container Instance
    log "🚀 Desplegando en Azure Container Instances..."
    
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name $ACI_NAME \
        --image ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${TAG} \
        --dns-name-label idp-api-$(date +%s | tail -c 4) \
        --ports 8000 \
        --environment-variables ENVIRONMENT=production LOG_LEVEL=INFO \
        --registry-login-server $ACR_LOGIN_SERVER \
        --registry-username $(az acr credential show --name $ACR_NAME --query username --output tsv) \
        --registry-password $(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)
    
    success "✅ Aplicación desplegada en Azure Container Instances"
    
    # Mostrar información del despliegue
    log "📊 Información del despliegue:"
    az container show --resource-group $RESOURCE_GROUP --name $ACI_NAME --query "{FQDN:ipAddress.fqdn,Status:provisioningState,Ports:containers[0].ports}" --output table
}

# Función para limpiar
clean() {
    log "🧹 Limpiando recursos Docker..."
    
    # Detener y remover contenedores
    docker-compose down 2>/dev/null || true
    
    # Remover imagen
    docker rmi ${IMAGE_NAME}:${TAG} 2>/dev/null || true
    
    # Limpiar contenedores huérfanos
    docker container prune -f
    
    # Limpiar imágenes huérfanas
    docker image prune -f
    
    success "✅ Limpieza completada"
}

# Función para mostrar ayuda
show_help() {
    echo "🐳 Script de Build y Despliegue para IDP Expert System"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  build     - Construir imagen Docker"
    echo "  test      - Probar aplicación localmente con Docker Compose"
    echo "  deploy    - Desplegar en Azure Container Instances"
    echo "  clean     - Limpiar recursos Docker"
    echo "  help      - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 build          # Solo construir imagen"
    echo "  $0 test           # Solo probar localmente"
    echo "  $0 deploy         # Solo desplegar en Azure"
    echo "  $0 clean          # Solo limpiar recursos"
}

# Función principal
main() {
    case "${1:-help}" in
        build)
            build_image
            ;;
        test)
            test_local
            ;;
        deploy)
            deploy_azure
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "❌ Comando no válido: $1"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
