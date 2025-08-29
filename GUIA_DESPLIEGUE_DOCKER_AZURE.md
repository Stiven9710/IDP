# 🐳🚀 Guía de Despliegue Docker y Azure - IDP Expert System

## 🎯 **Descripción General**

Esta guía te llevará paso a paso para implementar la API IDP Expert System en:
1. **🐳 Docker local** para desarrollo y pruebas
2. **☁️ Azure Container Instances** para pruebas rápidas
3. **🚀 Azure App Service** para producción

---

## 🐳 **PASO 1: DESARROLLO LOCAL CON DOCKER**

### **1.1 Prerrequisitos**
```bash
# Verificar que Docker esté instalado
docker --version
docker-compose --version

# Verificar que curl esté disponible
curl --version
```

### **1.2 Configuración del Entorno**
```bash
# 1. Copiar archivo de ejemplo
cp env.example .env

# 2. Editar .env con tus credenciales de Azure
nano .env
```

### **1.3 Build y Test Local**
```bash
# Opción 1: Usar script automatizado
./docker-deploy.sh build    # Construir imagen
./docker-deploy.sh test     # Probar localmente
./docker-deploy.sh clean    # Limpiar recursos

# Opción 2: Comandos manuales
docker build -t idp-expert-system .
docker-compose up --build -d
```

### **1.4 Verificar Funcionamiento**
```bash
# Health check
curl http://localhost:8000/health

# Documentación
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc

# Probar API
curl -X POST "http://localhost:8000/api/v1/documents/process-upload" \
  -F "file=@tests/unit/test_request_example.json" \
  -F "processing_mode=gpt_vision_only"
```

---

## ☁️ **PASO 2: DESPLIEGUE EN AZURE CONTAINER INSTANCES (ACI)**

### **2.1 Prerrequisitos Azure**
```bash
# 1. Instalar Azure CLI
# macOS: brew install azure-cli
# Windows: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows

# 2. Login en Azure
az login

# 3. Verificar suscripción
az account show
az account list --output table
```

### **2.2 Despliegue Automatizado**
```bash
# Usar script automatizado
./docker-deploy.sh deploy

# El script:
# 1. Crea Resource Group
# 2. Crea Azure Container Registry
# 3. Hace push de la imagen
# 4. Despliega en ACI
```

### **2.3 Despliegue Manual**
```bash
# 1. Crear Resource Group
az group create --name idp-resource-group --location eastus

# 2. Crear Azure Container Registry
az acr create --resource-group idp-resource-group --name idpacr$(date +%s | tail -c 4) --sku Basic

# 3. Login al ACR
az acr login --name <nombre-del-acr>

# 4. Tag y push de la imagen
docker tag idp-expert-system:latest <nombre-del-acr>.azurecr.io/idp-expert-system:latest
docker push <nombre-del-acr>.azurecr.io/idp-expert-system:latest

# 5. Desplegar en ACI
az container create \
  --resource-group idp-resource-group \
  --name idp-api-aci \
  --image <nombre-del-acr>.azurecr.io/idp-expert-system:latest \
  --dns-name-label idp-api-$(date +%s | tail -c 4) \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production LOG_LEVEL=INFO
```

---

## 🚀 **PASO 3: DESPLIEGUE EN AZURE APP SERVICE**

### **3.1 Crear App Service Plan**
```bash
# Crear plan de servicio
az appservice plan create \
  --name idp-app-service-plan \
  --resource-group idp-resource-group \
  --sku B1 \
  --is-linux
```

### **3.2 Crear Web App**
```bash
# Crear web app
az webapp create \
  --resource-group idp-resource-group \
  --plan idp-app-service-plan \
  --name idp-expert-system \
  --deployment-local-git
```

### **3.3 Configurar Docker**
```bash
# Configurar para usar Docker
az webapp config container set \
  --resource-group idp-resource-group \
  --name idp-expert-system \
  --docker-custom-image-name <nombre-del-acr>.azurecr.io/idp-expert-system:latest \
  --docker-registry-server-url https://<nombre-del-acr>.azurecr.io \
  --docker-registry-server-user <username> \
  --docker-registry-server-password <password>
```

### **3.4 Configurar Variables de Entorno**
```bash
# Configurar variables críticas
az webapp config appsettings set \
  --resource-group idp-resource-group \
  --name idp-expert-system \
  --settings \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    WEBSITES_PORT=8000
```

---

## 🔐 **PASO 4: CONFIGURACIÓN DE SEGURIDAD**

### **4.1 Azure Key Vault (Recomendado)**
```bash
# 1. Crear Key Vault
az keyvault create \
  --name idp-keyvault \
  --resource-group idp-resource-group \
  --location eastus

# 2. Agregar secretos
az keyvault secret set \
  --vault-name idp-keyvault \
  --name azure-openai-api-key \
  --value "tu-api-key"

# 3. Configurar acceso para App Service
az webapp config appsettings set \
  --resource-group idp-resource-group \
  --name idp-expert-system \
  --settings \
    AZURE_OPENAI_API_KEY="@Microsoft.KeyVault(SecretUri=https://idp-keyvault.vault.azure.net/secrets/azure-openai-api-key/)"
```

### **4.2 Configuración de CORS**
```bash
# Configurar CORS para producción
az webapp cors add \
  --resource-group idp-resource-group \
  --name idp-expert-system \
  --allowed-origins "https://tu-dominio.com"
```

---

## 📊 **PASO 5: MONITOREO Y LOGS**

### **5.1 Application Insights**
```bash
# 1. Crear Application Insights
az monitor app-insights component create \
  --app idp-insights \
  --location eastus \
  --resource-group idp-resource-group \
  --application-type web

# 2. Obtener instrumentation key
az monitor app-insights component show \
  --app idp-insights \
  --resource-group idp-resource-group \
  --query instrumentationKey

# 3. Configurar en App Service
az webapp config appsettings set \
  --resource-group idp-resource-group \
  --name idp-expert-system \
  --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY=<instrumentation-key>
```

### **5.2 Logs en Tiempo Real**
```bash
# Ver logs en tiempo real
az webapp log tail \
  --resource-group idp-resource-group \
  --name idp-expert-system

# Descargar logs
az webapp log download \
  --resource-group idp-resource-group \
  --name idp-expert-system
```

---

## 🧪 **PASO 6: PRUEBAS POST-DESPLIEGUE**

### **6.1 Health Check**
```bash
# Verificar que la API esté funcionando
curl https://idp-expert-system.azurewebsites.net/health

# Respuesta esperada:
{
  "status": "healthy",
  "service": "IDP Expert System",
  "version": "2.0.0"
}
```

### **6.2 Probar Endpoint Principal**
```bash
# Probar con documento de ejemplo
curl -X POST "https://idp-expert-system.azurewebsites.net/api/v1/documents/process-upload" \
  -F "file=@tests/unit/test_request_example.json" \
  -F "processing_mode=gpt_vision_only" \
  -F "prompt_general=Extrae información de este documento" \
  -F "fields_config=[{\"name\":\"test\",\"type\":\"string\",\"description\":\"Campo de prueba\"}]"
```

### **6.3 Verificar Documentación**
- **Swagger UI**: https://idp-expert-system.azurewebsites.net/docs
- **ReDoc**: https://idp-expert-system.azurewebsites.net/redoc

---

## 🔧 **PASO 7: MANTENIMIENTO Y ACTUALIZACIONES**

### **7.1 Actualizar Imagen**
```bash
# 1. Rebuild de la imagen
docker build -t idp-expert-system:latest .

# 2. Tag para ACR
docker tag idp-expert-system:latest <nombre-del-acr>.azurecr.io/idp-expert-system:latest

# 3. Push a ACR
docker push <nombre-del-acr>.azurecr.io/idp-expert-system:latest

# 4. Restart de App Service
az webapp restart \
  --resource-group idp-resource-group \
  --name idp-expert-system
```

### **7.2 Escalado**
```bash
# Escalar App Service Plan
az appservice plan update \
  --name idp-app-service-plan \
  --resource-group idp-resource-group \
  --sku S1

# Configurar auto-scaling
az monitor autoscale create \
  --resource-group idp-resource-group \
  --resource idp-app-service-plan \
  --resource-type Microsoft.Web/serverfarms \
  --name idp-autoscale \
  --min-count 1 \
  --max-count 10 \
  --count 1
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS COMUNES**

### **Problema 1: API no responde**
```bash
# Verificar logs
az webapp log tail --resource-group idp-resource-group --name idp-expert-system

# Verificar configuración
az webapp config show --resource-group idp-resource-group --name idp-expert-system
```

### **Problema 2: Error de conexión a Azure Services**
```bash
# Verificar variables de entorno
az webapp config appsettings list --resource-group idp-resource-group --name idp-expert-system

# Verificar conectividad de red
az webapp config show --resource-group idp-resource-group --name idp-expert-system --query outboundIpAddresses
```

### **Problema 3: Imagen Docker no se despliega**
```bash
# Verificar ACR
az acr repository list --name <nombre-del-acr>

# Verificar permisos
az acr show --name <nombre-del-acr> --query accessPolicies
```

---

## 📚 **RECURSOS ADICIONALES**

### **Documentación Oficial**
- [Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/)
- [Azure Container Instances](https://docs.microsoft.com/en-us/azure/container-instances/)

### **Scripts y Herramientas**
- `docker-deploy.sh` - Script automatizado para build y deploy
- `docker-compose.yml` - Configuración para desarrollo local
- `azure-app-service-config.json` - Configuración de App Service

### **Monitoreo**
- [Azure Monitor](https://docs.microsoft.com/en-us/azure/azure-monitor/)
- [Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)

---

## 🎯 **PRÓXIMOS PASOS**

1. **🐳 Probar Docker localmente**
2. **☁️ Desplegar en Azure Container Instances**
3. **🚀 Migrar a Azure App Service**
4. **🔐 Configurar Azure Key Vault**
5. **📊 Implementar Application Insights**
6. **🔄 Configurar CI/CD con GitHub Actions**

---

**¡Tu API IDP Expert System estará funcionando en Azure en poco tiempo!** 🚀✨
