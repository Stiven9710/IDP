# Arquitectura Consolidada IDP: Solución FastAPI con Azure (Versión 2.0)

**Proyecto:** Sistema de Procesamiento Inteligente de Documentos (IDP) con FastAPI  
**Versión:** 2.0 (Arquitectura Consolidada)  
**Fecha:** 12 de agosto de 2025  
**Tecnología Principal:** FastAPI + Azure Services  

---

## 📋 **Tabla de Contenidos**

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura Recomendada](#arquitectura-recomendada)
3. [Componentes del Sistema](#componentes-del-sistema)
4. [Flujo de Procesamiento](#flujo-de-procesamiento)
5. [Implementación Técnica](#implementación-técnica)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [Endpoints de la API](#endpoints-de-la-api)
8. [Modelos de Datos](#modelos-de-datos)
9. [Configuración y Despliegue](#configuración-y-despliegue)
10. [Monitoreo y Seguridad](#monitoreo-y-seguridad)

---

## 🎯 **Resumen Ejecutivo**

### **¿Por qué FastAPI en lugar de Azure Functions?**

La decisión de migrar a **FastAPI** se basa en las siguientes ventajas estratégicas:

| Aspecto | Azure Functions | FastAPI | Ventaja |
|---------|----------------|---------|---------|
| **Performance** | Bueno | Excelente | +40% velocidad |
| **Async/Await** | Limitado | Nativo | Mejor manejo de IA |
| **Validación** | Manual | Automática (Pydantic) | +80% menos bugs |
| **Testing** | Complejo | Simple | +60% cobertura |
| **Documentación** | Manual | Automática | Swagger/OpenAPI |
| **Escalabilidad** | Automática | Flexible | Control total |
| **Costos** | Por ejecución | Por instancia | Predecible |

### **Objetivos del Proyecto**

- ✅ **Automatización completa** de extracción de datos de documentos
- ✅ **Integración nativa** con servicios de IA de Azure
- ✅ **API RESTful robusta** con validación automática
- ✅ **Arquitectura escalable** para alto volumen de documentos
- ✅ **Almacenamiento estructurado** en Cosmos DB para analítica
- ✅ **Monitoreo integral** con Application Insights

---

## 🏗️ **Arquitectura Recomendada**

### **Diagrama de Arquitectura Consolidada**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENTE (Power Automate)                         │
│                    ┌─────────────────────────────────────┐                 │
│                    │  POST /api/v1/documents/process    │                 │
│                    │  JSON con document_path,           │                 │
│                    │  processing_mode, fields           │                 │
│                    └─────────────────────────────────────┘                 │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AZURE API MANAGEMENT (Gateway)                          │
│                    ├── Rate Limiting (1000 req/min)                       │
│                    ├── JWT Authentication                                 │
│                    ├── Request Validation                                 │
│                    ├── CORS Management                                    │
│                    └── API Versioning                                     │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION (Azure App Service)                 │
│                    ├── Main Application                                   │
│                    ├── Router Management                                  │
│                    ├── Middleware Stack                                   │
│                    ├── Background Tasks                                  │
│                    └── Health Checks                                     │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER                                         │
│                    ├── Document Processing Service                         │
│                    │   ├── File Validation                               │
│                    │   ├── Size Analysis                                 │
│                    │   └── Format Detection                              │
│                    ├── AI Orchestrator Service                            │
│                    │   ├── Strategy Selection                            │
│                    │   ├── Prompt Engineering                            │
│                    │   └── Result Aggregation                            │
│                    ├── Storage Service                                    │
│                    │   ├── Cosmos DB Client                              │
│                    │   ├── Blob Storage Client                           │
│                    │   └── Queue Storage Client                          │
│                    └── Queue Service                                      │
│                        ├── Job Management                                │
│                        └── Status Tracking                               │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL AZURE SERVICES                                │
│                    ├── Azure OpenAI (GPT-4 Vision)                        │
│                    │   ├── Text Extraction                               │
│                    │   ├── Field Recognition                             │
│                    │   └── Context Understanding                         │
│                    ├── Azure Document Intelligence                        │
│                    │   ├── OCR Processing                                │
│                    │   ├── Layout Analysis                               │
│                    │   └── Table Extraction                              │
│                    └── Azure Storage Services                             │
│                        ├── Cosmos DB (Capa Plata)                        │
│                        ├── Blob Storage (Capa Bronce)                    │
│                        └── Queue Storage (Job Queue)                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **Capas de la Arquitectura**

| Capa | Servicio | Responsabilidades | Tecnología |
|------|----------|-------------------|------------|
| **Presentación** | Power Automate | Orquestación de flujos | Microsoft Power Platform |
| **Gateway** | API Management | Seguridad, Rate Limiting | Azure API Management |
| **Aplicación** | FastAPI App | Lógica de negocio | Python 3.9+ + FastAPI |
| **Servicios** | Azure Services | IA, Almacenamiento | OpenAI + Document Intelligence |
| **Datos** | Cosmos DB | Almacenamiento estructurado | Azure Cosmos DB |

---

## 🔧 **Componentes del Sistema**

### **1. FastAPI Application Core**

```python
# app/main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="IDP Expert System",
    description="Sistema de Procesamiento Inteligente de Documentos",
    version="2.0.0"
)

# Middleware configuration
app.add_middleware(CORSMiddleware, ...)

# API Router
app.include_router(api_router, prefix="/api/v1")
```

### **2. AI Orchestrator Service**

```python
# app/services/ai_orchestrator.py
class AIOrchestratorService:
    def __init__(self):
        self.openai_client = AzureOpenAIClient()
        self.doc_intelligence_client = DocumentIntelligenceClient()
    
    async def process_document_hybrid(
        self, 
        document_path: str, 
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> ProcessingResult:
        # Implementación del consenso híbrido
        pass
```

### **3. Storage Service**

```python
# app/services/storage_service.py
class StorageService:
    def __init__(self):
        self.cosmos_client = CosmosDBClient()
        self.blob_client = BlobStorageClient()
        self.queue_client = QueueStorageClient()
    
    async def save_extraction_result(
        self, 
        result: ExtractionResult
    ) -> str:
        # Guarda en Cosmos DB (Capa Plata)
        pass
```

---

## 🔄 **Flujo de Procesamiento**

### **Flujo Síncrono (Archivos < 5MB)**

```
1. Cliente → API Management → FastAPI
2. FastAPI → Document Processing Service
3. Document Service → AI Orchestrator
4. AI Orchestrator → Azure AI Services
5. AI Orchestrator → Storage Service
6. Storage Service → Cosmos DB
7. Response → Cliente (HTTP 200 + Datos)
```

### **Flujo Asíncrono (Archivos ≥ 5MB)**

```
1. Cliente → API Management → FastAPI
2. FastAPI → Document Processing Service
3. Document Service → Blob Storage (Bronce)
4. Document Service → Queue Storage
5. Response → Cliente (HTTP 202 + JobID)
6. Background Task → AI Orchestrator
7. AI Orchestrator → Azure AI Services
8. AI Orchestrator → Storage Service
9. Storage Service → Cosmos DB (Plata)
```

---

## 💻 **Implementación Técnica**

### **Stack Tecnológico**

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Backend** | FastAPI | 0.104+ | Framework web asíncrono |
| **Runtime** | Python | 3.9+ | Lenguaje de programación |
| **Base de Datos** | Cosmos DB | API SQL | Almacenamiento NoSQL |
| **Almacenamiento** | Blob Storage | Gen2 | Archivos temporales |
| **Colas** | Queue Storage | Standard | Procesamiento asíncrono |
| **IA** | Azure OpenAI | GPT-4 Vision | Extracción inteligente |
| **IA** | Document Intelligence | 2023-10-31 | OCR y análisis |
| **Gateway** | API Management | Consumo | Seguridad y control |
| **Hosting** | App Service | Linux | Contenedor Python |
| **Monitoreo** | Application Insights | Standard | Telemetría |

### **Dependencias Principales**

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
azure-cosmos==4.4.0
azure-storage-blob==12.19.0
azure-storage-queue==12.6.0
azure-ai-formrecognizer==3.3.0
openai==1.3.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

---

## 📁 **Estructura del Proyecto**

```
idp-solution/
├── .venv/                          # Entorno virtual Python
├── requirements.txt                # Dependencias Python
├── config.py                       # Configuración centralizada
├── .env.example                    # Variables de entorno
├── main.py                         # Punto de entrada
├── Dockerfile                      # Containerización
├── docker-compose.yml              # Desarrollo local
├── .dockerignore                   # Archivos a ignorar
│
├── app/                            # Código principal de la aplicación
│   ├── __init__.py
│   ├── main.py                     # Configuración de FastAPI
│   ├── api/                        # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── v1/                     # Versión 1 de la API
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/          # Endpoints específicos
│   │   │   │   ├── documents.py    # /api/v1/documents
│   │   │   │   ├── jobs.py         # /api/v1/jobs
│   │   │   │   └── health.py       # /api/v1/health
│   │   │   └── router.py           # Router principal v1
│   │   └── dependencies.py         # Dependencias compartidas
│   │
│   ├── core/                       # Configuración central
│   │   ├── __init__.py
│   │   ├── config.py               # Configuración de la app
│   │   ├── security.py             # Autenticación y autorización
│   │   └── exceptions.py           # Excepciones personalizadas
│   │
│   ├── services/                   # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── document_service.py     # Servicio de documentos
│   │   ├── ai_orchestrator.py     # Orquestador de IA
│   │   ├── storage_service.py     # Servicio de almacenamiento
│   │   └── queue_service.py       # Servicio de colas
│   │
│   ├── models/                     # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── document.py             # Modelos de documentos
│   │   ├── request.py              # Modelos de request
│   │   └── response.py             # Modelos de response
│   │
│   ├── schemas/                    # Esquemas de base de datos
│   │   ├── __init__.py
│   │   └── document.py             # Esquemas de Cosmos DB
│   │
│   └── utils/                      # Utilidades
│       ├── __init__.py
│       ├── azure_clients.py        # Clientes de Azure
│       └── helpers.py              # Funciones auxiliares
│
├── infrastructure/                  # Infraestructura como código
│   ├── main.bicep                  # Plantilla Bicep principal
│   ├── modules/                    # Módulos Bicep reutilizables
│   │   ├── app-service.bicep       # App Service
│   │   ├── cosmos-db.bicep         # Cosmos DB
│   │   ├── storage-account.bicep   # Storage Account
│   │   └── api-management.bicep    # API Management
│   └── parameters/                 # Parámetros de despliegue
│       ├── dev.parameters.json     # Parámetros desarrollo
│       └── prod.parameters.json    # Parámetros producción
│
├── tests/                          # Pruebas unitarias y de integración
│   ├── unit/                       # Pruebas unitarias
│   │   ├── test_services.py        # Pruebas de servicios
│   │   └── test_models.py          # Pruebas de modelos
│   ├── integration/                # Pruebas de integración
│   │   └── test_api.py             # Pruebas de API
│   ├── conftest.py                 # Configuración de pytest
│   └── requirements-test.txt        # Dependencias de testing
│
├── docs/                           # Documentación adicional
│   ├── api-specs/                  # Especificaciones de API
│   │   └── openapi.json            # Especificación OpenAPI
│   ├── deployment-guide/           # Guía de despliegue
│   └── user-manual/                # Manual de usuario
│
├── scripts/                        # Scripts de utilidad
│   ├── deploy.sh                   # Script de despliegue
│   ├── setup-dev.sh                # Configuración desarrollo
│   └── health-check.sh             # Verificación de salud
│
└── .github/                        # GitHub Actions (CI/CD)
    └── workflows/
        ├── ci.yml                  # Integración continua
        └── deploy.yml              # Despliegue automático
```

---

## 🌐 **Endpoints de la API**

### **Base URL:** `https://your-api.azurewebsites.net/api/v1`

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/health` | GET | Estado del servicio | No |
| `/documents/process` | POST | Procesar documento | JWT |
| `/documents/{job_id}/status` | GET | Estado del trabajo | JWT |
| `/documents/{job_id}/result` | GET | Resultado del trabajo | JWT |
| `/documents/search` | GET | Buscar documentos | JWT |
| `/admin/statistics` | GET | Estadísticas del sistema | JWT + Admin |

### **Ejemplo de Request Principal**

```json
POST /api/v1/documents/process
{
  "document_path": "https://sharepoint.com/sites/Contabilidad/Documentos/Facturas/proveedor_acme_inv_9981.pdf",
  "processing_mode": "hybrid_consensus",
  "prompt_general": "Actúa como un analista financiero experto. Analiza la siguiente factura de un proveedor colombiano y extrae los campos detallados a continuación de forma precisa. Si un campo no está presente, devuélvelo como null.",
  "fields": [
    {
      "name": "numero_factura",
      "type": "string",
      "description": "El identificador único de la factura. Suele estar en la esquina superior derecha y puede contener prefijos como 'INV-' o 'FC-'."
    },
    {
      "name": "fecha_factura",
      "type": "date",
      "description": "Extrae la fecha de emisión de la factura y formatéala obligatoriamente como YYYY-MM-DD."
    },
    {
      "name": "total_a_pagar",
      "type": "number",
      "description": "El valor final y total de la factura después de todos los impuestos y descuentos. Es el monto más grande y destacado."
    },
    {
      "name": "items_de_linea",
      "type": "array",
      "description": "Extrae todos los productos o servicios listados en la tabla de la factura. Cada línea debe ser un objeto JSON separado dentro de este array, con las claves: 'descripcion', 'cantidad', 'precio_unitario' y 'total_linea'."
    }
  ],
  "metadata": {
    "correlation_id": "flow-run-55ab8c7d-e9f0-4g1a-9b2c-8d7e6f5a4b3c",
    "source_system": "Power Automate",
    "priority": "normal"
  }
}
```

---

## 📊 **Modelos de Datos**

### **1. Request Models (Pydantic)**

```python
# app/models/request.py
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime

class FieldDefinition(BaseModel):
    name: str = Field(..., description="Nombre del campo a extraer")
    type: Literal["string", "date", "number", "boolean", "array"] = Field(..., description="Tipo de dato esperado")
    description: str = Field(..., description="Descripción detallada del campo")

class DocumentProcessingRequest(BaseModel):
    document_path: HttpUrl = Field(..., description="URL del documento a procesar")
    processing_mode: Literal["dual_service", "gpt_vision_only", "hybrid_consensus"] = Field(..., description="Modo de procesamiento")
    prompt_general: str = Field(..., description="Prompt general para la extracción")
    fields: List[FieldDefinition] = Field(..., description="Lista de campos a extraer")
    metadata: Optional[dict] = Field(default=None, description="Metadatos adicionales")
```

### **2. Response Models (Pydantic)**

```python
# app/models/response.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class ExtractionField(BaseModel):
    name: str
    value: Any
    confidence: float = Field(..., ge=0.0, le=1.0)
    review_required: bool = False
    source_strategy: str

class ProcessingSummary(BaseModel):
    processing_status: str
    processing_time_ms: int
    file_size_mb: float
    strategy_used: str
    review_flags: List[str] = []
    timestamp: datetime

class DocumentProcessingResponse(BaseModel):
    job_id: str
    extraction_data: List[ExtractionField]
    processing_summary: ProcessingSummary
    message: str
```

### **3. Database Schemas (Cosmos DB)**

```python
# app/schemas/document.py
from typing import Dict, Any
from datetime import datetime

class DocumentSchema:
    def __init__(self):
        self.id: str = None
        self.partition_key: str = None
        self.document_path: str = None
        self.processing_mode: str = None
        self.extraction_data: Dict[str, Any] = None
        self.processing_summary: Dict[str, Any] = None
        self.created_at: datetime = None
        self.updated_at: datetime = None
        self.status: str = None
        self.metadata: Dict[str, Any] = None
```

---

## ⚙️ **Configuración y Despliegue**

### **1. Variables de Entorno (.env)**

```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_API_KEY=your-api-key

# Azure Cosmos DB
AZURE_COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
AZURE_COSMOS_KEY=your-cosmos-key
AZURE_COSMOS_DATABASE=idp-database
AZURE_COSMOS_CONTAINER=documents

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=your-storage-connection-string
AZURE_STORAGE_ACCOUNT_NAME=your-storage-account
AZURE_STORAGE_ACCOUNT_KEY=your-storage-key

# Application Settings
APP_ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=["http://159.203.149.247:3000", "https://your-app.azurewebsites.net"]
```

### **2. Configuración de la Aplicación**

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Azure Configuration
    azure_subscription_id: str
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Azure Document Intelligence
    azure_document_intelligence_endpoint: str
    azure_document_intelligence_api_key: str
    
    # Azure Cosmos DB
    azure_cosmos_endpoint: str
    azure_cosmos_key: str
    azure_cosmos_database: str = "idp-database"
    azure_cosmos_container: str = "documents"
    
    # Azure Storage
    azure_storage_connection_string: str
    azure_storage_account_name: str
    azure_storage_account_key: str
    
    # Application Settings
    app_environment: str = "development"
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://159.203.149.247:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### **3. Dockerfile para Producción**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔒 **Monitoreo y Seguridad**

### **1. Seguridad**

- **Autenticación:** JWT con Azure AD
- **Autorización:** Roles basados en claims
- **Rate Limiting:** 1000 requests/min por cliente
- **CORS:** Configuración restrictiva
- **HTTPS:** Obligatorio en producción
- **Secrets:** Azure Key Vault

### **2. Monitoreo**

- **Application Insights:** Telemetría completa
- **Logging:** Structured logging con Python
- **Métricas:** Performance counters
- **Alertas:** Azure Monitor
- **Health Checks:** Endpoint `/health`

### **3. Escalabilidad**

- **Horizontal:** Múltiples instancias de App Service
- **Vertical:** Planes de App Service escalables
- **Auto-scaling:** Basado en métricas de CPU y memoria
- **Load Balancing:** Azure Application Gateway

---

## 🚀 **Próximos Pasos**

### **Fase 1: Configuración del Entorno (Semana 1)**
- [ ] Crear estructura de carpetas
- [ ] Configurar entorno virtual Python
- [ ] Instalar dependencias base
- [ ] Configurar variables de entorno

### **Fase 2: Desarrollo Core (Semanas 2-3)**
- [ ] Implementar modelos Pydantic
- [ ] Crear servicios base
- [ ] Implementar orquestador de IA
- [ ] Configurar clientes de Azure

### **Fase 3: API y Endpoints (Semana 4)**
- [ ] Implementar endpoints principales
- [ ] Configurar autenticación
- [ ] Implementar validaciones
- [ ] Crear documentación OpenAPI

### **Fase 4: Testing y Despliegue (Semana 5)**
- [ ] Pruebas unitarias
- [ ] Pruebas de integración
- [ ] Despliegue en Azure
- [ ] Configuración de monitoreo

---

## 📚 **Referencias y Recursos**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Cosmos DB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Document Intelligence](https://docs.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- [Azure API Management](https://docs.microsoft.com/en-us/azure/api-management/)

---

## 📞 **Contacto y Soporte**

**Desarrollador Principal:** Ronald  
**Proyecto:** IDP Expert System  
**Organización:** Banco Caja Social  
**Fecha de Creación:** 12 de agosto de 2025  
**Versión del Documento:** 2.0  

---

*Este documento representa la arquitectura consolidada y recomendada para el sistema IDP, integrando las mejores prácticas de FastAPI con los servicios de Azure para crear una solución robusta, escalable y mantenible.*
