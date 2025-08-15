# IDP Expert System - Sistema de Procesamiento Inteligente de Documentos

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Azure](https://img.shields.io/badge/Azure-Cloud-blue.svg)](https://azure.microsoft.com)

## 🎯 **Descripción del Proyecto**

IDP Expert System es una solución robusta y escalable para el procesamiento inteligente de documentos utilizando tecnologías de vanguardia:

- **FastAPI** como framework web asíncrono de alto rendimiento
- **Azure AI Services** para extracción inteligente de datos (GPT-4o + Document Intelligence)
- **Arquitectura híbrida** que combina procesamiento síncrono y asíncrono
- **Umbral inteligente** de 10MB para decidir el tipo de procesamiento

## 🚀 **Características Principales**

### **Procesamiento Inteligente**
- **Síncrono**: Documentos ≤ 10MB se procesan inmediatamente
- **Asíncrono**: Documentos > 10MB se procesan en segundo plano
- **Múltiples estrategias**: `dual_service`, `gpt_vision_only`, `hybrid_consensus`

### **Servicios de IA Integrados**
- **Azure OpenAI GPT-4o**: Procesamiento de imágenes y documentos
- **Azure Document Intelligence**: OCR y análisis de documentos
- **Consenso híbrido**: Comparación y validación entre servicios

### **Formatos Soportados**
- **Documentos**: PDF, DOCX, DOC, TXT, RTF
- **Imágenes**: PNG, JPG, JPEG, TIFF, BMP, GIF
- **Office**: XLSX, XLS, PPTX, PPT
- **Web**: HTML, HTM

## 📋 **Requisitos del Sistema**

- **Python**: 3.9+
- **FastAPI**: 0.104+
- **Azure Services**: OpenAI, Document Intelligence, Cosmos DB, Storage
- **Dependencias**: Ver `requirements.txt`

## ⚙️ **Instalación y Configuración**

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/Stiven9710/IDP.git
cd IDP
git checkout dev
```

### **2. Crear Entorno Virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar Variables de Entorno**
```bash
cp env.example .env
# Editar .env con tus credenciales de Azure
```

### **5. Configuración de Azure**
```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://uc-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://uc-documentintelligencee.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_API_KEY=tu-api-key
```

## 🧪 **Pruebas del Sistema**

### **Script de Prueba Automático**
```bash
python test_idp_with_json.py
```

### **JSON de Ejemplo**
El sistema incluye un archivo `test_request_example.json` con un ejemplo completo para facturas colombianas:

```json
{
  "document_path": "https://example.com/Invoice_2082463105.pdf",
  "processing_mode": "hybrid_consensus",
  "prompt_general": "Actúa como un analista financiero experto...",
  "fields": [
    {
      "name": "numero_factura",
      "type": "string",
      "description": "El identificador único de la factura..."
    }
    // ... más campos
  ],
  "metadata": {
    "correlation_id": "test-invoice-2082463105",
    "document_type": "invoice",
    "country": "Colombia"
  }
}
```

## 🌐 **Uso de la API**

### **1. Iniciar el Servidor**
```bash
python main.py
```

### **2. Documentación Interactiva**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **3. Endpoint Principal**
```bash
POST /api/v1/documents/process
```

**Request Body:**
```json
{
  "document_path": "URL_DEL_DOCUMENTO",
  "processing_mode": "hybrid_consensus",
  "prompt_general": "PROMPT_PARA_LA_IA",
  "fields": [
    {
      "name": "nombre_campo",
      "type": "string|date|number|boolean|array",
      "description": "Descripción detallada del campo"
    }
  ],
  "metadata": {
    "correlation_id": "id-unico",
    "source_system": "sistema-origen"
  }
}
```

### **4. Endpoints Adicionales**
- `GET /api/v1/documents/{job_id}/status` - Consultar estado
- `GET /api/v1/documents/{job_id}/result` - Obtener resultado
- `GET /api/v1/documents/search` - Buscar documentos
- `GET /api/v1/health` - Verificar salud del servicio
- `GET /api/v1/jobs` - Listar trabajos

## 🔄 **Flujos de Procesamiento**

### **Procesamiento Síncrono (≤ 10MB)**
```
1. Cliente → API → FastAPI
2. FastAPI → Document Service
3. Document Service → AI Orchestrator
4. AI Orchestrator → Azure AI Services
5. AI Orchestrator → Storage Service
6. Response → Cliente (HTTP 200 + Datos)
```

### **Procesamiento Asíncrono (> 10MB)**
```
1. Cliente → API → FastAPI
2. FastAPI → Document Service
3. Document Service → Blob Storage (Bronce)
4. Document Service → Queue Storage
5. Response → Cliente (HTTP 202 + Job ID)
6. Background Task → AI Orchestrator
7. AI Orchestrator → Azure AI Services
8. AI Orchestrator → Storage Service
9. Storage Service → Cosmos DB (Plata)
```

## 🎯 **Modos de Procesamiento**

### **1. Dual Service**
- Usa ambos servicios de IA en paralelo
- Compara resultados para mayor precisión
- Ideal para documentos críticos

### **2. GPT Vision Only**
- Solo Azure OpenAI GPT-4o
- Más rápido, menor costo
- Ideal para documentos simples

### **3. Hybrid Consensus**
- Combina ambos servicios inteligentemente
- OpenAI como autoridad en discrepancias
- Marca campos para revisión humana

## 📊 **Tipos de Campos Soportados**

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `string` | Texto simple | "INV-001" |
| `date` | Fechas | "2025-01-12" |
| `number` | Números | 150000.00 |
| `boolean` | Valores lógicos | true/false |
| `array` | Listas de objetos | `[{"item": "valor"}]` |

## 🔧 **Configuración Avanzada**

### **Variables de Entorno Clave**
```bash
# Umbral de procesamiento
SYNC_PROCESSING_THRESHOLD_MB=10

# Tiempo máximo de procesamiento
MAX_PROCESSING_TIME_SECONDS=300

# Tamaño máximo de archivo
MAX_FILE_SIZE_MB=50

# Nivel de logging
LOG_LEVEL=INFO
```

### **Personalización de Prompts**
- **Prompt General**: Contexto y reglas globales
- **Descripción de Campos**: Instrucciones específicas por campo
- **Ejemplos**: Incluir ejemplos en las descripciones

## 📈 **Monitoreo y Logs**

### **Logs Estructurados**
- Emojis para identificación visual rápida
- Timestamps precisos
- Niveles de log configurables
- Archivo de log: `idp.log`

### **Health Checks**
- `/health` - Estado básico
- `/health/detailed` - Estado detallado
- `/health/ready` - Preparación del servicio

## 🚀 **Despliegue**

### **Desarrollo Local**
```bash
python main.py
# Servidor en http://localhost:8000
```

### **Docker**
```bash
docker build -t idp-expert-system .
docker run -p 8000:8000 idp-expert-system
```

### **Azure App Service**
- Usar el Dockerfile incluido
- Configurar variables de entorno en Azure
- Habilitar Application Insights

## 🧪 **Ejemplos de Uso**

### **Factura Colombiana**
```bash
# Usar el JSON de ejemplo incluido
curl -X POST "http://localhost:8000/api/v1/documents/process" \
     -H "Content-Type: application/json" \
     -d @test_request_example.json
```

### **Documento Personalizado**
1. Copiar `test_request_example.json`
2. Modificar campos según el tipo de documento
3. Ajustar prompt general
4. Cambiar modo de procesamiento

## 📚 **Documentación Adicional**

- **Arquitectura**: `Arquitectura de Referencia/IDP_Arquitectura_FastAPI_Consolidada.md`
- **API Specs**: `docs/api-specs/openapi.json`
- **Infraestructura**: `infrastructure/` (Bicep templates)

## 🤝 **Contribución**

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 **Contacto y Soporte**

**Desarrollador Principal:** Ronald  
**Proyecto:** IDP Expert System  
**Organización:** Banco Caja Social  
**Repositorio:** https://github.com/Stiven9710/IDP  
**Rama de Desarrollo:** `dev`

## 📄 **Licencia**

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 🎯 **Próximos Pasos**

1. **Configurar credenciales de Azure** en `.env`
2. **Ejecutar pruebas** con `python test_idp_with_json.py`
3. **Iniciar servidor** con `python main.py`
4. **Probar API** en http://localhost:8000/docs
5. **Personalizar campos** según tus necesidades

¡El sistema IDP está listo para procesar documentos reales! 🚀
