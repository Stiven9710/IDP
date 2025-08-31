# 🔧 Guía Técnica de Implementación - IDP Expert System

## 🎯 **Descripción Técnica**

Esta guía detalla la implementación técnica del IDP Expert System, incluyendo arquitectura, código, configuración y despliegue.

## 🏗️ **Arquitectura del Sistema**

### **Componentes Principales**

```
app/
├── main.py                 # Punto de entrada de FastAPI
├── core/
│   ├── config.py          # Configuración y variables de entorno
│   └── logging.py         # Configuración de logging
├── api/
│   └── v1/
│       ├── endpoints/     # Endpoints de la API
│       └── router.py      # Enrutamiento de la API
├── services/              # Lógica de negocio
├── utils/                 # Utilidades y clientes de Azure
└── models/                # Modelos Pydantic
```

### **Flujo de Datos Técnico**

1. **FastAPI** recibe request HTTP
2. **Document Service** valida y procesa archivo
3. **AI Orchestrator** coordina servicios de IA
4. **Azure Clients** interactúan con APIs externas
5. **Response** se serializa y retorna

## 🔧 **Implementación Técnica**

### **1. Configuración del Sistema**

**config.py:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment_name: str = "gpt-4o"
    
    # Azure Document Intelligence
    azure_document_intelligence_endpoint: str
    azure_document_intelligence_api_key: str
    
    # Configuración del sistema
    sync_processing_threshold_mb: int = 10
    max_processing_time_seconds: int = 300
    
    class Config:
        env_file = ".env"
```

### **2. Cliente de Azure OpenAI**

**azure_clients.py:**
```python
class AzureOpenAIClient:
    async def process_document_vision(
        self,
        document_b64: str,
        prompt: str,
        fields: List[FieldDefinition],
        processing_mode: str = "gpt_vision_only"
    ) -> Dict[str, Any]:
        
        if processing_mode == "gpt_vision_only":
            return await self._process_gpt_vision_only(pdf_bytes, prompt, fields)
        elif processing_mode == "dual_service":
            return await self._process_dual_service(pdf_bytes, prompt, fields)
        elif processing_mode == "hybrid_consensus":
            return await self._process_hybrid_consensus(pdf_bytes, prompt, fields)
```

### **3. Procesamiento de Imágenes y Documentos Office**

**document_converter.py:**
```python
class DocumentConverter:
    def pdf_to_images_png(self, pdf_bytes: bytes, dpi: int = 300) -> List[str]:
        """Convierte PDF a imágenes PNG optimizadas para GPT-4o"""
        
        # Usar PyMuPDF para renderizar PDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images_base64 = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            
            # Convertir a PIL Image para optimización
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Optimizar imagen
```

**office_converter.py:**
```python
class OfficeConverter:
    def office_to_images_png(self, document_content: bytes) -> List[str]:
        """Convierte documentos Office (.pptx, .docx, .xlsx) a imágenes PNG"""
        
        # Detectar tipo de archivo usando magic bytes
        file_type = self._detect_file_type(document_content)
        
        if file_type == '.pptx':
            return self._convert_presentation(temp_file_path)
        # ... otros formatos
```

### **4. Procesamiento en Cascada para Documentos Grandes**

**ai_orchestrator.py:**
```python
async def _process_with_openai_cascade(self, document_content: bytes, prompt: str, fields: List[FieldDefinition]) -> Dict[str, Any]:
    """Procesamiento inteligente con estrategia de cascada"""
    
    # Convertir documento a imágenes
    if self._is_pdf(document_content):
        converter = DocumentConverter()
        images = converter.pdf_to_images_png(document_content)
    else:
        converter = OfficeConverter()
        images = converter.office_to_images_png(document_content)
    
    # Decidir estrategia basada en número de páginas
    if len(images) <= 5:
        return await self._process_single_batch(images, prompt, fields)
    else:
        return await self._process_cascade_batches(images, prompt, fields)
```
            img = self._optimize_image_for_gpt4o(img)
            
            # Convertir a base64
            img_base64 = self._image_to_base64(img)
            images_base64.append(img_base64)
        
        return images_base64
```

### **4. Consenso Híbrido**

**Lógica de consenso:**
```python
def _generate_consensus(
    self,
    vision_result: Dict[str, Any],
    text_result: Dict[str, Any],
    fields: List[FieldDefinition]
) -> Dict[str, Any]:
    
    consensus_result = {}
    
    for field in fields:
        field_name = field.name
        vision_value = vision_result.get(field_name)
        text_value = text_result.get(field_name)
        
        if vision_value == text_value and vision_value is not None:
            # Consenso alto
            consensus_result[field_name] = {
                "value": vision_value,
                "confidence": "high",
                "source": "consensus",
                "vision_value": vision_value,
                "text_value": text_value
            }
        elif vision_value is not None and text_value is not None:
            # Consenso medio - usar el más detallado
            consensus_result[field_name] = {
                "value": self._select_best_value(vision_value, text_value),
                "confidence": "medium",
                "source": "vision" if len(str(vision_value)) > len(str(text_value)) else "text",
                "vision_value": vision_value,
                "text_value": text_value,
                "note": "Valores diferentes, usando el más detallado"
            }
```

## 🚀 **Despliegue y Configuración**

### **1. Variables de Entorno**

**.env:**
```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://uc-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://uc-ocr.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_API_KEY=tu-api-key

# Configuración del Sistema
SYNC_PROCESSING_THRESHOLD_MB=10
MAX_PROCESSING_TIME_SECONDS=300
LOG_LEVEL=INFO
```

### **2. Dependencias**

**requirements.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
httpx==0.25.2
azure-ai-documentintelligence==1.0.2
azure-core==1.35.0
PyMuPDF==1.23.8
Pillow==10.1.0
```

### **3. Inicio del Servidor**

**main.py:**
```python
import uvicorn
from app.core.config import setup_logging
from app.api.v1.router import api_router
from fastapi import FastAPI

# Configurar logging
setup_logging()

# Crear aplicación FastAPI
app = FastAPI(
    title="IDP Expert System",
    description="Sistema de Procesamiento Inteligente de Documentos",
    version="1.0.0"
)

# Incluir rutas
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

## 🔍 **Troubleshooting Técnico**

### **1. Error de Importación**

**Problema:** `ModuleNotFoundError: No module named 'azure.ai.documentintelligence'`

**Solución:**
```bash
pip install azure-ai-documentintelligence
```

### **2. Conflicto de Nombres**

**Problema:** `DocumentIntelligenceClient.__init__() got an unexpected keyword argument 'endpoint'`

**Solución:** Renombrar clase personalizada para evitar conflicto con librería de Azure

### **3. Error de Parsing JSON**

**Problema:** `TypeError: the JSON object must be str, bytes or bytearray, not dict`

**Solución:** Verificar tipo de datos antes de usar `json.loads()`

## 📊 **Métricas y Monitoreo**

### **1. Logs Estructurados**

```python
import logging

logger = logging.getLogger(__name__)

# Logs con emojis para identificación visual
logger.info("🚀 Endpoint /process-upload llamado")
logger.info("✅ Documento procesado exitosamente")
logger.warning("⚠️ Campo no encontrado en la respuesta")
logger.error("❌ Error procesando archivo")
```

### **2. Health Checks**

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "azure_openai": check_openai_health(),
            "azure_document_intelligence": check_di_health(),
            "storage": check_storage_health()
        }
    }
```

## 🧪 **Testing y Validación**

### **1. Script de Prueba**

**test_idp_with_json.py:**
```python
import asyncio
import json
from app.services.document_service import DocumentService

async def test_idp_system():
    # Cargar configuración de prueba
    with open('test_request_example.json', 'r') as f:
        config = json.load(f)
    
    # Crear servicio
    doc_service = DocumentService()
    
    # Probar diferentes modos
    modes = ["gpt_vision_only", "dual_service", "hybrid_consensus"]
    
    for mode in modes:
        print(f"Testing mode: {mode}")
        result = await doc_service.process_document(config, mode)
        print(f"Result: {result}")
        print("---")

if __name__ == "__main__":
    asyncio.run(test_idp_system())
```

### **2. Validación de Resultados**

```python
def validate_extraction_result(result: Dict[str, Any]) -> bool:
    """Valida que el resultado de extracción sea correcto"""
    
    required_fields = ["job_id", "extraction_data", "processing_summary"]
    
    # Verificar campos requeridos
    for field in required_fields:
        if field not in result:
            return False
    
    # Verificar datos extraídos
    if not result["extraction_data"]:
        return False
    
    # Verificar resumen de procesamiento
    summary = result["processing_summary"]
    if summary["processing_status"] != "completed":
        return False
    
    return True
```

## 🚀 **Optimizaciones y Mejoras**

### **1. Caché de Resultados**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_extraction_result(document_hash: str) -> Dict[str, Any]:
    """Cache de resultados de extracción para documentos repetidos"""
    pass
```

### **2. Procesamiento en Lote**

```python
async def process_documents_batch(
    documents: List[bytes],
    fields: List[FieldDefinition],
    processing_mode: str
) -> List[Dict[str, Any]]:
    """Procesa múltiples documentos en paralelo"""
    
    tasks = []
    for doc in documents:
        task = process_single_document(doc, fields, processing_mode)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### **3. Retry y Circuit Breaker**

```python
import tenacity

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10)
)
async def call_azure_api_with_retry(api_call):
    """Llamada a API de Azure con reintentos automáticos"""
    return await api_call()
```

### **4. 💾 Control de Persistencia de Documentos**

**Implementación en Background Worker:**
```python
# app/services/background_worker.py - PASO 9: LIMPIEZA AUTOMÁTICA
if not persistencia:
    logger.info(f"🧹 LIMPIEZA AUTOMÁTICA ACTIVADA - Eliminando documento del storage")
    
    # 🆕 IMPLEMENTACIÓN CON MÉTODOS NATIVOS DE AZURE
    try:
        # Listar blobs en container 'processed' para encontrar el archivo real
        processed_blobs = await self.blob_service.list_blobs_in_container(
            container_name="processed",
            name_starts_with=f"{job_id_part}/"
        )
        
        if processed_blobs:
            # Buscar blob que coincida con job_id
            target_blob = None
            for blob in processed_blobs:
                if job_id_part in blob.name:
                    target_blob = blob
                    break
            
            if target_blob:
                # 🆕 USAR MÉTODO NATIVO: delete_blob con container_name y blob_name
                deletion_result = await self.blob_service.delete_blob_native(
                    container_name="processed",
                    blob_name=target_blob.name
                )
                
                if deletion_result:
                    logger.info(f"✅ Documento eliminado exitosamente usando método nativo de Azure")
                    
    except Exception as azure_error:
        logger.error(f"❌ Error usando métodos nativos de Azure: {str(azure_error)}")
```

**Métodos nativos implementados en BlobStorageService:**
```python
# app/services/blob_storage_service.py
async def list_blobs_in_container(
    self, 
    container_name: str, 
    name_starts_with: Optional[str] = None
) -> List[Any]:
    """Listar blobs usando métodos nativos de Azure"""
    container_client = self.blob_service_client.get_container_client(container_name)
    blobs = list(container_client.list_blobs(name_starts_with=name_starts_with))
    return blobs

async def delete_blob_native(
    self, 
    container_name: str, 
    blob_name: str
) -> bool:
    """Eliminar blob usando métodos nativos de Azure"""
    container_client = self.blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    if blob_client.exists():
        blob_client.delete_blob()
        return True
    return False
```

**Ventajas de la implementación nativa:**
- **🔐 Autenticación automática**: Usa credenciales configuradas en el servicio
- **✅ Verificación previa**: Confirma existencia del blob antes de eliminar
- **📊 Logs detallados**: Registra todo el proceso de eliminación
- **🛡️ Manejo de errores**: Captura y registra errores específicos de Azure
- **⚡ Rendimiento**: Operaciones directas sin construcción manual de URLs

## 📚 **Recursos Adicionales**

### **Documentación Oficial**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure AI Services](https://azure.microsoft.com/services/ai/)
- [Azure Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)

### **Código de Referencia**
- [GitHub Repository](https://github.com/Stiven9710/IDP)
- [Arquitectura de Referencia](Arquitectura%20de%20Referencia/IDP_Arquitectura_FastAPI_Consolidada.md)

---

*Esta guía técnica se actualiza con cada versión del sistema.*
