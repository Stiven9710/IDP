# 📚 Documentación Funcional y Técnica del API IDP Expert System

## 🎯 **Descripción General**

El **IDP Expert System** es una API robusta y escalable para el procesamiento inteligente de documentos que combina múltiples estrategias de extracción de datos utilizando servicios de Azure AI.

---

## 🏗️ **Arquitectura del Sistema**

### **Componentes Principales**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│ Document Service │───▶│ AI Orchestrator │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Storage       │    │   Queue Service  │    │ Azure AI        │
│   Service       │    │                  │    │ Services        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Flujo de Datos**

1. **Cliente** envía documento a la API
2. **Document Service** decide procesamiento síncrono/asíncrono
3. **AI Orchestrator** coordina servicios de IA
4. **Azure AI Services** procesan el documento
5. **Storage Service** almacena resultados
6. **Response** retorna datos extraídos

---

## 🔄 **Procesamiento de Documentos**

### **Decisión de Procesamiento**

```python
# Umbral configurable: 10MB
if file_size_mb <= SYNC_PROCESSING_THRESHOLD_MB:
    # Procesamiento SÍNCRONO
    result = await process_sync(document)
    return HTTP_200_OK + result
else:
    # Procesamiento ASÍNCRONO
    job_id = await process_async(document)
    return HTTP_202_ACCEPTED + job_id
```

### **Procesamiento Síncrono (≤ 10MB)**

```
Cliente → API → FastAPI → Document Service → AI Orchestrator → Azure AI → Response
```

**Tiempo estimado**: 2-6 segundos
**Respuesta**: Datos extraídos inmediatamente

### **Procesamiento Asíncrono (> 10MB)**

```
Cliente → API → FastAPI → Document Service → Blob Storage → Queue → Background Task
                                                                    ↓
Response (Job ID) ←─────────────────────────────────────────────────┘

Background Task → AI Orchestrator → Azure AI → Storage → Cosmos DB
```

**Tiempo estimado**: 10-60 segundos
**Respuesta**: Job ID para consultar estado

---

## 🎯 **Estrategias de Extracción**

### **1. GPT Vision Only** ✅

**Funcionamiento:**
```
PDF → DocumentConverter → Imágenes PNG → GPT-4o → JSON
```

**Ventajas:**
- ⚡ **Rápido**: 2-3 segundos
- 💰 **Económico**: Solo usa OpenAI
- 🎯 **Preciso**: GPT-4o es excelente para extracción

**Casos de uso:**
- Documentos simples
- Procesamiento rápido requerido
- Costo optimizado

**Ejemplo de resultado:**
```json
{
  "numero_factura": "2082463105",
  "fecha_factura": "2025-03-02",
  "proveedor_nombre": "Amazon Web Services, Inc.",
  "cliente_nombre": "Ronald Estiven Rios Hernandez",
  "total_a_pagar": 0.16,
  "moneda": "USD"
}
```

### **2. Dual Service** ✅

**Funcionamiento:**
```
PDF → Document Intelligence (texto) → GPT-4o (análisis) → JSON
```

**Ventajas:**
- 🔍 **Preciso**: Doble validación
- 📝 **Completo**: Extrae texto + analiza contenido
- 🎯 **Confiable**: Dos servicios validan

**Casos de uso:**
- Documentos complejos
- Alta precisión requerida
- Validación doble necesaria

**Ejemplo de resultado:**
```json
{
  "numero_factura": "2082463105",
  "fecha_factura": "2025-03-02",
  "proveedor_nombre": "Amazon Web Services, Inc.",
  "cliente_nombre": "Ronald Estiven Rios Hernandez",
  "total_a_pagar": 0.16,
  "items_de_linea": [
    {"descripcion": "Amazon Redshift", "total_linea": 0.16},
    {"descripcion": "AWS Glue", "total_linea": 0.0}
  ],
  "moneda": "USD"
}
```

### **3. Hybrid Consensus** ✅

**Funcionamiento:**
```
PDF → [GPT Vision + Document Intelligence] → Consenso Inteligente → JSON
```

**Ventajas:**
- 🎯 **Máxima confiabilidad**: Validación cruzada
- 🔍 **Consenso automático**: Resuelve discrepancias
- 📊 **Información detallada**: Muestra fuente de cada campo

**Casos de uso:**
- Documentos críticos
- Auditoría requerida
- Máxima precisión necesaria

**Ejemplo de resultado:**
```json
{
  "numero_factura": {
    "value": "2082463105",
    "confidence": "high",
    "source": "consensus",
    "vision_value": "2082463105",
    "text_value": "2082463105"
  },
  "items_de_linea": {
    "value": [{"descripcion": "AWS Service Charges", "total_linea": 0.16}],
    "confidence": "medium",
    "source": "vision",
    "note": "Valores diferentes, usando el más detallado"
  }
}
```

---

## 🌐 **Endpoints de la API**

### **POST /api/v1/documents/process-upload**

**Descripción:** Procesar documento subido por el usuario

**Form Data:**
- `file`: Archivo del documento (PDF, imagen, etc.)
- `fields_config`: JSON string con configuración de campos
- `prompt_general`: Prompt general para la extracción
- `processing_mode`: Modo de procesamiento

**Ejemplo de uso:**
```bash
curl -X POST 'http://localhost:8000/api/v1/documents/process-upload' \
  -F 'file=@tests/Documentos/Invoice_2082463105.pdf' \
  -F 'fields_config=[{"name": "numero_factura", "type": "string", "description": "..."}]' \
  -F 'prompt_general=Actúa como un analista financiero...' \
  -F 'processing_mode=hybrid_consensus'
```

**Respuesta exitosa:**
```json
{
  "job_id": "65dd7fb8-8810-42ef-9818-43739bacbff1",
  "extraction_data": [...],
  "processing_summary": {
    "processing_status": "completed",
    "processing_time_ms": 2000,
    "strategy_used": "hybrid_consensus"
  },
  "message": "Documento procesado exitosamente"
}
```

### **POST /api/v1/documents/process-upload-custom**

**Descripción:** Procesar documento con configuración personalizada

**Similar a process-upload pero con lógica adicional para campos personalizados**

### **GET /api/v1/documents/{job_id}/status**

**Descripción:** Consultar estado de un trabajo

**Respuesta:**
```json
{
  "job_id": "65dd7fb8-8810-42ef-9818-43739bacbff1",
  "status": "completed",
  "progress": 100,
  "estimated_completion": null
}
```

### **GET /api/v1/health**

**Descripción:** Verificar salud del servicio

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-19T01:40:07.848053",
  "version": "1.0.0",
  "services": {
    "azure_openai": "healthy",
    "azure_document_intelligence": "healthy",
    "storage": "healthy"
  }
}
```

---

## 📊 **Configuración de Campos**

### **Estructura de Campo**

```json
{
  "name": "numero_factura",
  "type": "string",
  "description": "El identificador único de la factura. Busca en frases que contengan Factura o Invoice Number"
}
```

### **Tipos de Campo Soportados**

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `string` | Texto simple | "INV-001", "Amazon Web Services" |
| `date` | Fechas | "2025-03-02" (formato YYYY-MM-DD) |
| `number` | Números | 0.16, 150000.00 |
| `boolean` | Valores lógicos | true, false |
| `array` | Listas de objetos | `[{"descripcion": "item", "total": 0.16}]` |

### **Ejemplo Completo de Configuración**

```json
[
  {
    "name": "numero_factura",
    "type": "string",
    "description": "El identificador único de la factura. Busca en frases que contengan Factura o Invoice Number"
  },
  {
    "name": "fecha_factura",
    "type": "date",
    "description": "La fecha de emisión de la factura. Busca invoice date en la parte superior del documento y formatéala como YYYY-MM-DD."
  },
  {
    "name": "proveedor_nombre",
    "type": "string",
    "description": "El nombre completo de la empresa o persona que emite la factura. Busca en la parte superior izquierda del documento."
  },
  {
    "name": "total_a_pagar",
    "type": "number",
    "description": "El valor final y total de la factura después de todos los impuestos. Es el monto más grande y destacado en la sección de totales."
  },
  {
    "name": "items_de_linea",
    "type": "array",
    "description": "Extrae todos los productos o servicios listados en la tabla de la factura. Cada línea debe ser un objeto JSON con las claves: descripcion, y total_linea."
  }
]
```

---

## 🎨 **Prompts y Reglas del Sistema**

### **Prompt General**

```
Actúa como un analista financiero experto especializado en facturas colombianas. 
Analiza la siguiente factura de un proveedor y extrae los campos detallados a continuación 
de forma precisa. Si un campo no está presente, devuélvelo como null. 
Para fechas, usa formato YYYY-MM-DD. Para montos, extrae solo el valor numérico 
sin símbolos de moneda.
```

### **Reglas del Sistema (Automáticas)**

```
REGLAS DEL SISTEMA:
1. Respuesta DEBE SER EXCLUSIVAMENTE JSON válido. Sin texto ANTES/DESPUÉS.
2. NO uses formato markdown (```json o ```). Devuelve SOLO el JSON puro.
3. JSON debe contener campos: [lista_de_campos].
4. [prompt_general] No uses conocimiento externo.
5. Si campo no está en el documento, valor DEBE ser "N/A" o null. No inventes.
6. Analiza el documento y PREGUNTA para valores.
7. Para fechas, usa formato YYYY-MM-DD.
8. Para montos, extrae solo el valor numérico sin símbolos de moneda.
9. Para arrays, estructura correctamente con objetos JSON.

CRÍTICO: Responde ÚNICAMENTE con el JSON puro, sin ```json, sin ```, sin texto adicional.
```

---

## 🔧 **Configuración del Sistema**

### **Variables de Entorno**

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
MAX_FILE_SIZE_MB=50
LOG_LEVEL=INFO
```

### **Configuración de Logging**

```python
# Niveles de log
INFO: 🚀 Inicio de operaciones
WARNING: ⚠️ Advertencias y casos especiales
ERROR: ❌ Errores y fallos
SUCCESS: ✅ Operaciones exitosas

# Ejemplos de logs
2025-08-18 20:34:23,012 - app.api.v1.endpoints.documents - INFO - 🚀 Endpoint /process-upload llamado
2025-08-18 20:34:26,184 - app.utils.azure_clients - INFO - ✅ Texto extraído exitosamente: 2389 caracteres
2025-08-18 20:34:29,138 - app.utils.azure_clients - INFO - 📝 Respuesta de GPT-4o: {...}
```

---

## 📈 **Monitoreo y Métricas**

### **Métricas de Rendimiento**

- **Tiempo de procesamiento**: Por modo y tamaño de archivo
- **Tasa de éxito**: Porcentaje de extracciones exitosas
- **Uso de recursos**: CPU, memoria, llamadas a APIs
- **Latencia**: Tiempo de respuesta por endpoint

### **Logs Estructurados**

```json
{
  "timestamp": "2025-08-18 20:34:29.138",
  "level": "INFO",
  "module": "app.utils.azure_clients",
  "message": "✅ Datos extraídos exitosamente de GPT-4o",
  "job_id": "65dd7fb8-8810-42ef-9818-43739bacbff1",
  "processing_mode": "dual_service",
  "file_size_mb": 0.09
}
```

### **Health Checks**

- **`/health`**: Estado básico del servicio
- **`/health/detailed`**: Estado detallado de todos los componentes
- **`/health/ready`**: Verificación de preparación para recibir tráfico

---

## 🚀 **Casos de Uso y Ejemplos**

### **Caso 1: Factura Colombiana**

**Configuración:**
```json
{
  "processing_mode": "hybrid_consensus",
  "prompt_general": "Actúa como un analista financiero experto especializado en facturas colombianas...",
  "fields": [
    {"name": "numero_factura", "type": "string", "description": "..."},
    {"name": "fecha_factura", "type": "date", "description": "..."},
    {"name": "total_a_pagar", "type": "number", "description": "..."}
  ]
}
```

**Resultado:**
- ✅ **Consenso alto**: 6 campos validados por ambos métodos
- 🔄 **Consenso medio**: 2 campos con diferencias resueltas
- 📝 **Solo texto**: 1 campo extraído únicamente por Document Intelligence

### **Caso 2: Contrato Legal**

**Configuración:**
```json
{
  "processing_mode": "dual_service",
  "prompt_general": "Actúa como un abogado experto en contratos...",
  "fields": [
    {"name": "partes_contrato", "type": "array", "description": "..."},
    {"name": "fecha_inicio", "type": "date", "description": "..."},
    {"name": "valor_contrato", "type": "number", "description": "..."}
  ]
}
```

### **Caso 3: Reporte Financiero**

**Configuración:**
```json
{
  "processing_mode": "gpt_vision_only",
  "prompt_general": "Actúa como un analista financiero...",
  "fields": [
    {"name": "periodo_reporte", "type": "string", "description": "..."},
    {"name": "indicadores_clave", "type": "array", "description": "..."}
  ]
}
```

---

## 🔍 **Troubleshooting y Debugging**

### **Errores Comunes**

1. **Error 404 en Document Intelligence**
   - Verificar endpoint y API key
   - Confirmar que el modelo esté habilitado
   - Usar `gpt_vision_only` como fallback

2. **Error de parsing JSON**
   - Verificar formato de `fields_config`
   - Asegurar que sea JSON válido
   - Revisar logs para detalles

3. **Timeout en procesamiento**
   - Verificar tamaño del archivo
   - Considerar procesamiento asíncrono
   - Revisar configuración de timeouts

### **Logs de Debug**

```bash
# Ver logs en tiempo real
tail -f idp.log

# Filtrar por nivel
grep "ERROR" idp.log

# Filtrar por job_id
grep "65dd7fb8-8810-42ef-9818-43739bacbff1" idp.log
```

---

## 📚 **Recursos Adicionales**

### **Documentación Técnica**
- **Guía de Implementación**: `docs/Guia_Tecnica_Implementacion.md`
- **Arquitectura**: `Arquitectura de Referencia/IDP_Arquitectura_FastAPI_Consolidada.md`
- **API Specs**: `docs/api-specs/openapi.json`

### **Scripts de Prueba**
- **`test_idp_with_json.py`**: Prueba automática del sistema
- **`test_request_example.json`**: Configuración de ejemplo
- **`tests/Documentos/`**: Documentos de prueba

### **Herramientas de Desarrollo**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Checks**: http://localhost:8000/health

---

## 🎯 **Próximos Pasos**

1. **Configurar credenciales** de Azure en `.env`
2. **Ejecutar pruebas** con `python test_idp_with_json.py`
3. **Probar diferentes modos** de procesamiento
4. **Personalizar campos** según tus necesidades
5. **Implementar en producción** con monitoreo

---

*Esta documentación se actualiza regularmente. Para la versión más reciente, consulta el repositorio.*
