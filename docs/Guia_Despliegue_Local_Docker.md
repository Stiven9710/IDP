# 🐳 Guía de Despliegue Local en Docker - IDP Expert System

## 🎯 **Descripción General**

Esta guía te llevará paso a paso para implementar y ejecutar la API IDP Expert System en tu entorno local usando Docker. La solución incluye:

- **🌐 API FastAPI** con procesamiento de documentos
- **🔄 Background Worker** para tareas asíncronas
- **🗄️ Redis** para cache y colas
- **☁️ Integración con Azure Services** (OpenAI, Storage, Cosmos DB)

---

## 📋 **Prerrequisitos**

### **🐳 Software Requerido:**
```bash
# 1. Docker Desktop
# Descargar desde: https://www.docker.com/products/docker-desktop/

# 2. Verificar instalación
docker --version
docker-compose --version

# 3. Git (para clonar el repositorio)
git --version

# 4. Editor de código (VS Code, PyCharm, etc.)
```

### **☁️ Configuración de Azure:**
- **Azure OpenAI** con GPT-4o
- **Azure Storage Account** (Blob + Queue)
- **Azure Cosmos DB**
- **Azure Document Intelligence** (opcional)

---

## 🚀 **PASO 1: PREPARAR EL ENTORNO**

### **1.1 Clonar el Repositorio**
```bash
# Clonar el repositorio
git clone https://github.com/Stiven9710/IDP.git
cd IDP

# Cambiar a la rama de desarrollo
git checkout dev
```

### **1.2 Verificar Funcionalidades Implementadas**
```bash
# ✅ Funcionalidades disponibles en esta versión:
# - Procesamiento síncrono/asíncrono (umbral 10MB)
# - 3 estrategias de extracción: gpt_vision_only, dual_service, hybrid_consensus
# - Procesamiento en cascada para documentos grandes
# - 💾 Control de persistencia de documentos (persistencia=true/false)
# - 🔒 Validación de seguridad para URLs externas
# - 🗄️ Persistencia automática en Cosmos DB
# - 🐳 Dockerización completa para desarrollo local
```

### **1.2 Configurar Variables de Entorno**
```bash
# 1. Copiar archivo de ejemplo
cp env.example .env

# 2. Editar .env con tus credenciales
nano .env
```

**📋 Contenido mínimo del .env:**
```env
# Entorno
ENVIRONMENT=development
LOG_LEVEL=INFO

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://tu-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...

# Azure Cosmos DB
AZURE_COSMOS_ENDPOINT=https://idp-database.documents.azure.com:443/
AZURE_COSMOS_KEY=...

# Azure Document Intelligence (opcional)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://tu-ocr.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_API_KEY=...
```

---

## 🐳 **PASO 2: DESPLIEGUE CON DOCKER**

### **2.1 Opción A: Script Automatizado (Recomendado)**
```bash
# 1. Hacer ejecutable el script
chmod +x docker-deploy.sh

# 2. Construir imagen
./docker-deploy.sh build

# 3. Probar localmente
./docker-deploy.sh test

# 4. Limpiar recursos
./docker-deploy.sh clean
```

### **2.2 Opción B: Comandos Manuales**
```bash
# 1. Construir imagen
docker build -t idp-expert-system .

# 2. Levantar servicios
docker-compose up --build -d

# 3. Verificar estado
docker ps

# 4. Ver logs
docker-compose logs -f
```

---

## 🧪 **PASO 3: VERIFICAR FUNCIONAMIENTO**

### **3.1 Health Check Básico**
```bash
# Verificar que la API esté funcionando
curl http://localhost:8000/health

# Respuesta esperada:
{
  "status": "healthy",
  "service": "IDP Expert System",
  "version": "2.0.0"
}
```

### **3.2 Health Check Detallado**
```bash
# Verificar todos los servicios
curl http://localhost:8000/api/v1/health/storage

# Verificar Cosmos DB
curl http://localhost:8000/api/v1/health/cosmos
```

### **3.3 Documentación de la API**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 **PASO 4: MONITOREO Y LOGS**

### **4.1 Ver Logs en Tiempo Real**
```bash
# Logs de la API
docker-compose logs -f idp-api

# Logs del Background Worker
docker-compose logs -f idp-worker

# Logs de Redis
docker-compose logs -f redis

# Todos los logs
docker-compose logs -f
```

### **4.2 Ver Estado de los Contenedores**
```bash
# Estado general
docker ps

# Estadísticas de recursos
docker stats

# Información detallada
docker inspect idp-expert-system
```

---

## 🧪 **PASO 5: PRUEBAS DE LA API**

### **5.1 Test Simple con Health Check**
```bash
# Usar Postman o curl
curl -X GET "http://localhost:8000/health"
```

### **5.2 Test de Procesamiento de Documentos**
```bash
# Procesar un PDF
curl -X POST "http://localhost:8000/api/v1/documents/process-upload" \
  -F "file=@./tests/Documentos/Invoice_2082463105.pdf" \
  -F "processing_mode=gpt_vision_only" \
  -F "prompt_general=Extrae información de esta factura" \
  -F "fields_config=[{\"name\":\"test\",\"type\":\"string\",\"description\":\"Campo de prueba\"}]"
```

### **5.3 Test de Procesamiento Asíncrono**
```bash
# Para documentos grandes (>10MB)
curl -X POST "http://localhost:8000/api/v1/documents/process-upload" \
  -F "file=@./tests/Documentos/Banco Caribe - Propuesta Perfil Transaccional IB Final.pptx" \
  -F "processing_mode=gpt_vision_only" \
  -F "prompt_general=Analiza esta propuesta técnica" \
  -F "fields_config=[{\"name\":\"titulo\",\"type\":\"string\",\"description\":\"Título del documento\"}]"
```

---

## 🔧 **PASO 6: SOLUCIÓN DE PROBLEMAS**

### **6.1 Problema: Puerto 8000 ocupado**
```bash
# Ver qué está usando el puerto
lsof -i :8000

# Detener proceso
kill -9 <PID>

# O cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Puerto 8001 en host, 8000 en contenedor
```

### **6.2 Problema: Contenedor no inicia**
```bash
# Ver logs de error
docker-compose logs idp-api

# Verificar configuración
docker-compose config

# Reconstruir desde cero
docker-compose down
docker-compose up --build
```

### **6.3 Problema: Error de Azure Services**
```bash
# Verificar variables de entorno
docker-compose exec idp-api env | grep AZURE

# Verificar conectividad
docker-compose exec idp-api curl -f https://tu-openai.openai.azure.com/
```

### **6.4 Problema: Background Worker no procesa**
```bash
# Ver logs del worker
docker-compose logs -f idp-worker

# Verificar colas de Azure
curl http://localhost:8000/api/v1/health/storage

# Reiniciar worker
docker-compose restart idp-worker
```

---

## 📋 **PASO 7: COMANDOS ÚTILES**

### **7.1 Gestión de Contenedores**
```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver estado
docker-compose ps
```

### **7.2 Gestión de Imágenes**
```bash
# Listar imágenes
docker images

# Eliminar imagen
docker rmi idp-expert-system:latest

# Limpiar imágenes no utilizadas
docker image prune -f
```

### **7.3 Limpieza del Sistema**
```bash
# Limpiar contenedores detenidos
docker container prune -f

# Limpiar volúmenes no utilizados
docker volume prune -f

# Limpieza completa
docker system prune -a -f
```

---

## 🎯 **PASO 8: CONFIGURACIONES AVANZADAS**

### **8.1 Personalizar Puerto**
```yaml
# docker-compose.yml
services:
  idp-api:
    ports:
      - "8001:8000"  # Puerto personalizado
```

### **8.2 Configurar Volúmenes Persistentes**
```yaml
# docker-compose.yml
services:
  idp-api:
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
```

### **8.3 Configurar Variables de Entorno**
```yaml
# docker-compose.yml
services:
  idp-api:
    environment:
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
```

---

## 📚 **PASO 9: RECURSOS ADICIONALES**

### **9.1 Archivos de Configuración**
- **`Dockerfile`**: Configuración de la imagen Docker
- **`docker-compose.yml`**: Orquestación de servicios
- **`.dockerignore`**: Archivos excluidos del build
- **`docker-deploy.sh`**: Script de automatización

### **9.2 Documentación Relacionada**
- **`Guia_Tecnica_Implementacion.md`**: Arquitectura técnica
- **`Documentacion_Funcional_API.md`**: Funcionalidades de la API
- **`GUIA_DESPLIEGUE_DOCKER_AZURE.md`**: Despliegue en Azure

### **9.3 Enlaces Útiles**
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🚨 **PROBLEMAS COMUNES Y SOLUCIONES**

### **Problema: "ModuleNotFoundError: No module named 'azure.ai.documentintelligence'"**
**Solución**: Verificar que `requirements.txt` incluya todas las dependencias

### **Problema: "Connection refused" en puerto 8000**
**Solución**: Verificar que Docker esté ejecutándose y el puerto esté libre

### **Problema: "Azure services not configured"**
**Solución**: Verificar archivo `.env` y credenciales de Azure

### **Problema: "Background worker not processing jobs"**
**Solución**: Verificar conectividad con Azure Queue Storage

---

## 🎉 **¡DESPLIEGUE COMPLETADO!**

### **✅ Verificaciones Finales:**
1. **🌐 API funcionando**: http://localhost:8000/health
2. **📚 Documentación**: http://localhost:8000/docs
3. **🔄 Background Worker**: Procesando colas
4. **🗄️ Redis**: Funcionando en puerto 6379
5. **☁️ Azure Services**: Conectados y funcionando

### **🚀 Próximos Pasos:**
1. **🧪 Probar endpoints de la API**
2. **📄 Procesar documentos de prueba**
3. **📊 Monitorear logs y métricas**
4. **☁️ Considerar despliegue en Azure**

---

**¡Tu API IDP Expert System está funcionando perfectamente en Docker local!** 🎉🐳✨
