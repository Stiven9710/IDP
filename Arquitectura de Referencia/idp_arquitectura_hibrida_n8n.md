# Arquitectura Híbrida IDP: n8n + Digital Ocean + Azure

**Proyecto:** Sistema de Procesamiento Inteligente de Documentos (IDP) con Arquitectura Híbrida  
**Versión:** 6.0 (Arquitectura Híbrida)  
**Fecha:** Diciembre 2024

---

## 1. Introducción y Alcance

### 1.1. Propósito

Esta nueva arquitectura híbrida mantiene Azure como backend robusto para los servicios de IA y almacenamiento, mientras expone la API a través de Digital Ocean para optimizar costos y utiliza n8n como plataforma de automatización principal para la ingesta automática de documentos desde correos electrónicos.

### 1.2. Alcance

El alcance incluye la migración del cliente de Power Automate a n8n, el despliegue de la API en Digital Ocean como proxy inteligente hacia Azure, y la automatización completa del flujo de ingesta de documentos sin intervención manual.

---

## 2. Diagrama de la Nueva Arquitectura

```
********************************************************************************
* CLIENTE PRINCIPAL (n8n)                                                     *
********************************************************************************
[ n8n - Orquestador de Automatización ]
|
| 1. Monitorea bandeja de entrada automáticamente
| 2. Detecta correos con adjuntos
| 3. Descarga archivos automáticamente
| 4. Envía a API IDP para procesamiento
| 5. Monitorea estado y notifica resultados
|
+----------------------------------------------------------------------------+
|
********************************************************************************
* CAPA DE EXPOSICIÓN (DIGITAL OCEAN)                                         *
********************************************************************************
[ API FastAPI (IDP) - Proxy Inteligente ]
|
| a. Recibe solicitudes de n8n y valida autenticación
| b. Enruta hacia Azure (manteniendo toda la lógica de negocio)
| c. Maneja respuestas y errores
| d. Proporciona endpoints para consulta de estado
|
+----------------------------------------------------------------------------+
|
********************************************************************************
* CAPA DE API Y APLICACIÓN (AZURE)                                           *
********************************************************************************
[ Azure API Management ]
|
v
[ Fn-Smart-Dispatcher (HTTP Trigger) ]
|
| a. Obtiene archivo, verifica tamaño y lee "processing_mode" del JSON.
|
+----[ DECISIÓN: ¿Archivo Pequeño? mayor a 5 mb ]-----------------------------------------+
|                                                                           |
v (RUTA SINCRÓNICA)                                               v (RUTA ASINCRÓNICA)
|                                                                           |
| b. Llama al orquestador de IA.                                    | b. Sube a Blob (Bronce) y encola mensaje.
| c. Escribe resultado en Cosmos DB (Plata).                        |
| d. Devuelve [HTTP 200 OK + Resultado Final]                      | d. Devuelve [HTTP 202 Accepted + jobId]
|                                                                           |
+---------------------------------------------------------------------------+

********************************************************************************
* PROCESAMIENTO EN SEGUNDO PLANO Y ALMACENAMIENTO (AZURE)                     *
********************************************************************************

[ Azure Queue Storage ] ---> [ Fn-Process-Async ] ---> [ Orquestador de IA ] ---> [ Azure Cosmos DB (Capa Plata) ]
(Dispara la función)                               (Llama a los servicios de IA)
```

---

## 3. Componentes de la Nueva Arquitectura

| Capa | Servicio | Rol y Responsabilidades |
|------|----------|------------------------|
| **Cliente Principal** | **n8n (Digital Ocean)** | Orquesta la automatización completa: monitoreo de correos, descarga de adjuntos, envío a API y seguimiento. |
| **Exposición** | **API FastAPI (Digital Ocean)** | Proxy inteligente que mantiene toda la lógica de negocio y enruta hacia Azure. Maneja autenticación y validaciones. |
| **Automatización** | **n8n Workflows** | Flujos automatizados para procesamiento de correos, gestión de archivos y notificaciones. |
| **API y Seguridad** | **Azure API Management** | Puerta de enlace única y segura para todas las API. |
| | **Azure Key Vault** | Almacén seguro para todas las credenciales y secretos. |
| **Aplicación (Serverless)** | **Azure Functions** | El núcleo lógico: `Fn-Ingest`, `Fn-Process-Async`, `Fn-Get-Status`. |
| **Datos y Estado** | **Azure Blob Storage** | **Capa Bronce**: Almacena los documentos originales para auditoría. |
| | **Azure Queue Storage** | Desacopla la ingesta del procesamiento, garantizando resiliencia. |
| **Inteligencia** | **Azure AI Services** | Document Intelligence y Azure OpenAI para la extracción de datos. |
| **Datos Analíticos** | **Azure Cosmos DB** | **Capa Plata**: Almacena los datos extraídos en formato estructurado. |

---

## 4. Flujo de Trabajo Automatizado con n8n

### 4.1. Workflow Principal de Monitoreo de Correos

```
[ Email Trigger ] → [ Filter Attachments ] → [ Download Files ] → [ Process with IDP ] → [ Monitor Status ] → [ Notify Results ]
```

### 4.2. Pasos Detallados del Workflow

1. **Email Trigger**: Monitorea bandeja de entrada cada 5 minutos
2. **Filter Attachments**: Filtra correos que contengan adjuntos (PDF, DOC, etc.)
3. **Download Files**: Descarga automáticamente los archivos adjuntos
4. **Process with IDP**: Envía archivo a la API IDP para procesamiento
5. **Monitor Status**: Consulta estado del procesamiento cada 30 segundos
6. **Notify Results**: Envía notificación con resultados o errores

### 4.3. Configuración del Workflow n8n

```json
{
  "name": "IDP Document Processing Workflow",
  "nodes": [
    {
      "id": "email-trigger",
      "type": "n8n-nodes-base.emailTrigger",
      "parameters": {
        "pollTimes": "every 5 minutes",
        "filters": {
          "hasAttachments": true,
          "fileTypes": ["pdf", "doc", "docx", "jpg", "jpeg", "png"]
        }
      }
    },
    {
      "id": "download-attachments",
      "type": "n8n-nodes-base.download",
      "parameters": {
        "operation": "download",
        "binaryData": true
      }
    },
    {
      "id": "send-to-idp",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "{{ $env.IDP_API_URL }}/api/ProcessDocumentSmart",
        "body": {
          "document_path": "{{ $json.file_path }}",
          "processing_mode": "hybrid_consensus",
          "prompt_general": "Actúa como un analista financiero experto...",
          "fields": [...]
        }
      }
    }
  ]
}
```

---

## 5. Configuración de Digital Ocean

### 5.1. Droplet 1: API FastAPI

**Especificaciones:**
- **Tipo**: Basic Droplet
- **Plan**: $6/mes (1GB RAM, 1 vCPU, 25GB SSD)
- **Sistema Operativo**: Ubuntu 22.04 LTS
- **Software**: Docker, Docker Compose

**Configuración:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  idp-api:
    image: idp-api:latest
    ports:
      - "80:8000"
    environment:
      - AZURE_COSMOS_CONNECTION_STRING=${AZURE_COSMOS_CONNECTION_STRING}
      - AZURE_AI_ENDPOINT=${AZURE_AI_ENDPOINT}
      - AZURE_AI_KEY=${AZURE_AI_KEY}
    volumes:
      - ./logs:/app/logs
```

### 5.2. Droplet 2: n8n

**Especificaciones:**
- **Tipo**: Basic Droplet
- **Plan**: $6/mes (1GB RAM, 1 vCPU, 25GB SSD)
- **Sistema Operativo**: Ubuntu 22.04 LTS
- **Software**: Docker, n8n

**Configuración:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - WEBHOOK_URL=${WEBHOOK_URL}
    volumes:
      - n8n_data:/home/node/.n8n
```

---

## 6. Endpoints de la API

### 6.1. Endpoint Principal

**URL:** `POST /api/ProcessDocumentSmart`

**Descripción:** Procesa documentos de forma inteligente con estrategias adaptativas.

### 6.2. Endpoint de Estado

**URL:** `GET /api/jobs/{job_id}/status`

**Descripción:** Consulta el estado de un trabajo de procesamiento asincrónico.

### 6.3. Endpoint de Salud

**URL:** `GET /health`

**Descripción:** Verifica el estado de la API y su conectividad con Azure.

---

## 7. Ventajas de la Nueva Arquitectura

### 7.1. **Costos Optimizados**
- Digital Ocean: $12/mes vs Azure App Service: $30+/mes
- n8n gratuito vs Power Automate: $15+/mes por usuario

### 7.2. **Automatización Completa**
- Sin intervención manual en la ingesta de documentos
- Monitoreo 24/7 de correos
- Notificaciones automáticas de resultados

### 7.3. **Flexibilidad y Escalabilidad**
- Escalado independiente de cada componente
- Fácil migración entre proveedores
- Mantenimiento simplificado

### 7.4. **Robustez del Backend**
- Mantienes toda la infraestructura Azure probada
- Sin cambios en la lógica de negocio
- Servicios de IA de clase empresarial

---

## 8. Plan de Implementación

### Fase 1: Preparación (Semana 1)
- Configurar Droplets en Digital Ocean
- Preparar Docker images para API y n8n
- Configurar variables de entorno

### Fase 2: Despliegue API (Semana 2)
- Desplegar API FastAPI en Digital Ocean
- Configurar Nginx y SSL
- Probar conectividad con Azure

### Fase 3: Configuración n8n (Semana 3)
- Instalar y configurar n8n
- Crear workflows de automatización
- Probar flujos de correo

### Fase 4: Pruebas y Optimización (Semana 4)
- Pruebas de carga y rendimiento
- Optimización de workflows
- Documentación final

---

## 9. Monitoreo y Mantenimiento

### 9.1. **Monitoreo de la API**
- Logs de acceso y errores
- Métricas de rendimiento
- Alertas de disponibilidad

### 9.2. **Monitoreo de n8n**
- Estado de workflows
- Logs de ejecución
- Notificaciones de fallos

### 9.3. **Mantenimiento**
- Actualizaciones de seguridad mensuales
- Backups automáticos de configuraciones
- Rotación de logs

---

## 10. Conclusión

Esta nueva arquitectura híbrida proporciona la mejor combinación de costos, funcionalidad y mantenibilidad. Al mantener Azure como backend robusto y utilizar Digital Ocean + n8n para la exposición y automatización, obtienes:

- **Reducción de costos** del 60-70%
- **Automatización completa** del flujo de ingesta
- **Mantenimiento simplificado** de la infraestructura
- **Escalabilidad** según necesidades del negocio

La migración es gradual y no afecta la funcionalidad existente, permitiendo una transición suave y controlada.
