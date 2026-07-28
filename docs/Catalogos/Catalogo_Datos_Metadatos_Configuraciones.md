# ⚙️ CATÁLOGO DE DATOS - METADATOS Y CONFIGURACIONES

## 🎯 **DESCRIPCIÓN GENERAL**
Este catálogo documenta la estructura y contenido de los metadatos y configuraciones del sistema IDP Expert System, incluyendo configuraciones de procesamiento, metadatos de documentos y configuraciones de seguridad.

---

## 🗂️ **ESTRUCTURA DE METADATOS**

### **📋 METADATOS DE EXTRACCIÓN**

#### **🔍 METADATOS BÁSICOS**
```json
{
  "extraction_id": "string",
  "job_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "processing_mode": "enum",
  "document_type": "string",
  "source": "string",
  "version": "string"
}
```

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `extraction_id` | String | ID único de la extracción | `"ext_20240101103000_abc123"` |
| `job_id` | String | ID del trabajo de procesamiento | `"job_20240101_001"` |
| `created_at` | DateTime | Fecha de creación | `"2024-01-01T10:30:00Z"` |
| `updated_at` | DateTime | Fecha de actualización | `"2024-01-01T10:35:00Z"` |
| `processing_mode` | Enum | Modo de procesamiento | `"gpt_vision_only"` |
| `document_type` | String | Tipo de documento | `"invoice"`, `"proposal"` |
| `source` | String | Origen del documento | `"file_upload"`, `"url"` |
| `version` | String | Versión del sistema | `"1.0.0"` |

#### **📄 METADATOS DEL DOCUMENTO**
```json
{
  "document_metadata": {
    "filename": "string",
    "file_size_mb": "number",
    "file_format": "string",
    "total_pages": "number",
    "pages_processed": "number",
    "document_quality": "string",
    "upload_timestamp": "datetime",
    "blob_path": "string",
    "blob_container": "string"
  }
}
```

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `filename` | String | Nombre del archivo | `"factura_001.pdf"` |
| `file_size_mb` | Number | Tamaño en MB | `2.5` |
| `file_format` | String | Formato del archivo | `"PDF"`, `"DOCX"` |
| `total_pages` | Number | Total de páginas | `10` |
| `pages_processed` | Number | Páginas procesadas | `10` |
| `document_quality` | String | Calidad del documento | `"high"`, `"medium"`, `"low"` |
| `upload_timestamp` | DateTime | Fecha de subida | `"2024-01-01T10:30:00Z"` |
| `blob_path` | String | Ruta en Azure Blob | `"documents/job_001/factura_001.pdf"` |
| `blob_container` | String | Contenedor de Azure | `"documents"`, `"processed"` |

---

## ⚙️ **CONFIGURACIONES DE PROCESAMIENTO**

### **🤖 CONFIGURACIÓN DE IA**

#### **🔍 CONFIGURACIÓN GPT VISION**
```json
{
  "gpt_vision_config": {
    "model": "string",
    "max_tokens": "number",
    "temperature": "number",
    "top_p": "number",
    "frequency_penalty": "number",
    "presence_penalty": "number",
    "timeout_seconds": "number",
    "retry_attempts": "number"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `model` | String | Modelo de IA a usar | `"gpt-4-vision-preview"` |
| `max_tokens` | Number | Máximo de tokens | `4000` |
| `temperature` | Number | Creatividad (0-1) | `0.1` |
| `top_p` | Number | Diversidad (0-1) | `0.9` |
| `frequency_penalty` | Number | Penalización de frecuencia | `0.0` |
| `presence_penalty` | Number | Penalización de presencia | `0.0` |
| `timeout_seconds` | Number | Timeout en segundos | `300` |
| `retry_attempts` | Number | Intentos de reintento | `3` |

#### **📊 CONFIGURACIÓN OCR**
```json
{
  "ocr_config": {
    "engine": "string",
    "language": "string",
    "confidence_threshold": "number",
    "preprocessing": "object",
    "postprocessing": "object"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `engine` | String | Motor OCR | `"azure_cognitive"` |
| `language` | String | Idioma del documento | `"es"` |
| `confidence_threshold` | Number | Umbral de confianza | `0.7` |
| `preprocessing` | Object | Configuración de preprocesamiento | Ver abajo |
| `postprocessing` | Object | Configuración de postprocesamiento | Ver abajo |

### **🔧 CONFIGURACIÓN DE CAMPOS**

#### **📝 DEFINICIÓN DE CAMPOS**
```json
{
  "field_definitions": [
    {
      "name": "string",
      "type": "enum",
      "description": "string",
      "required": "boolean",
      "validation_rules": "object",
      "extraction_strategy": "string",
      "confidence_threshold": "number"
    }
  ]
}
```

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `name` | String | Nombre del campo | `"numero_factura"` |
| `type` | Enum | Tipo de dato | `"string"`, `"number"`, `"array"` |
| `description` | String | Descripción del campo | `"Número de la factura"` |
| `required` | Boolean | Si es obligatorio | `true` |
| `validation_rules` | Object | Reglas de validación | Ver abajo |
| `extraction_strategy` | String | Estrategia de extracción | `"gpt_vision"` |
| `confidence_threshold` | Number | Umbral de confianza | `0.8` |

#### **✅ REGLAS DE VALIDACIÓN**
```json
{
  "validation_rules": {
    "min_length": "number",
    "max_length": "number",
    "pattern": "string",
    "min_value": "number",
    "max_value": "number",
    "allowed_values": "array",
    "custom_validator": "string"
  }
}
```

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `min_length` | Number | Longitud mínima | `5` |
| `max_length` | Number | Longitud máxima | `100` |
| `pattern` | String | Patrón regex | `"^[A-Z]{3}-[0-9]{4}-[0-9]{3}$"` |
| `min_value` | Number | Valor mínimo | `0` |
| `max_value` | Number | Valor máximo | `999999999` |
| `allowed_values` | Array | Valores permitidos | `["pending", "completed"]` |
| `custom_validator` | String | Validador personalizado | `"validate_invoice_number"` |

---

## 🔒 **CONFIGURACIONES DE SEGURIDAD**

### **🛡️ CONFIGURACIÓN DE SEGURIDAD DE URLs**

#### **🌐 DOMINIOS PERMITIDOS**
```json
{
  "security_config": {
    "allowed_domains": "array",
    "blocked_domains": "array",
    "max_file_size_mb": "number",
    "download_timeout_seconds": "number",
    "scan_for_malware": "boolean",
    "validate_ssl": "boolean"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `allowed_domains` | Array | Dominios permitidos | `["*.microsoft.com", "*.google.com"]` |
| `blocked_domains` | Array | Dominios bloqueados | `["*.malicious.com"]` |
| `max_file_size_mb` | Number | Tamaño máximo en MB | `50` |
| `download_timeout_seconds` | Number | Timeout de descarga | `30` |
| `scan_for_malware` | Boolean | Escaneo de malware | `true` |
| `validate_ssl` | Boolean | Validación SSL | `true` |

#### **🔐 CONFIGURACIÓN DE AUTENTICACIÓN**
```json
{
  "auth_config": {
    "jwt_secret": "string",
    "jwt_expiry_hours": "number",
    "api_key_required": "boolean",
    "rate_limit_per_minute": "number",
    "max_requests_per_day": "number"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `jwt_secret` | String | Secreto JWT | `"your-secret-key"` |
| `jwt_expiry_hours` | Number | Expiración en horas | `24` |
| `api_key_required` | Boolean | Requiere API key | `true` |
| `rate_limit_per_minute` | Number | Límite por minuto | `100` |
| `max_requests_per_day` | Number | Límite por día | `10000` |

---

## 💾 **CONFIGURACIONES DE PERSISTENCIA**

### **🗂️ CONFIGURACIÓN DE ALMACENAMIENTO**

#### **📦 CONFIGURACIÓN AZURE BLOB STORAGE**
```json
{
  "blob_storage_config": {
    "connection_string": "string",
    "containers": {
      "documents": "string",
      "processed": "string",
      "temp": "string"
    },
    "retention_policy": {
      "default_days": "number",
      "temp_days": "number",
      "processed_days": "number"
    },
    "encryption": {
      "enabled": "boolean",
      "key_vault_url": "string"
    }
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `connection_string` | String | Cadena de conexión | `"DefaultEndpointsProtocol=https..."` |
| `containers.documents` | String | Contenedor de documentos | `"documents"` |
| `containers.processed` | String | Contenedor procesados | `"processed"` |
| `containers.temp` | String | Contenedor temporal | `"temp"` |
| `retention_policy.default_days` | Number | Días de retención por defecto | `90` |
| `retention_policy.temp_days` | Number | Días para archivos temporales | `7` |
| `retention_policy.processed_days` | Number | Días para archivos procesados | `365` |
| `encryption.enabled` | Boolean | Cifrado habilitado | `true` |
| `encryption.key_vault_url` | String | URL del Key Vault | `"https://your-vault.vault.azure.net/"` |

#### **🗄️ CONFIGURACIÓN COSMOS DB**
```json
{
  "cosmos_db_config": {
    "endpoint": "string",
    "key": "string",
    "database_name": "string",
    "containers": {
      "extractions": "string",
      "jobs": "string",
      "products": "string"
    },
    "throughput": {
      "extractions": "number",
      "jobs": "number",
      "products": "number"
    },
    "ttl": {
      "extractions": "number",
      "jobs": "number",
      "products": "number"
    }
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `endpoint` | String | Endpoint de Cosmos DB | `"https://your-cosmos.documents.azure.com:443/"` |
| `key` | String | Clave de acceso | `"your-cosmos-key"` |
| `database_name` | String | Nombre de la base de datos | `"idp_expert_system"` |
| `containers.extractions` | String | Contenedor de extracciones | `"extractions"` |
| `containers.jobs` | String | Contenedor de trabajos | `"jobs"` |
| `containers.products` | String | Contenedor de productos | `"products"` |
| `throughput.extractions` | Number | Throughput de extracciones | `400` |
| `throughput.jobs` | Number | Throughput de trabajos | `400` |
| `throughput.products` | Number | Throughput de productos | `400` |
| `ttl.extractions` | Number | TTL de extracciones (días) | `90` |
| `ttl.jobs` | Number | TTL de trabajos (días) | `30` |
| `ttl.products` | Number | TTL de productos (días) | `90` |

---

## 📊 **CONFIGURACIONES DE MONITOREO**

### **📈 CONFIGURACIÓN DE MÉTRICAS**

#### **🔍 CONFIGURACIÓN DE LOGGING**
```json
{
  "logging_config": {
    "level": "string",
    "format": "string",
    "outputs": "array",
    "retention_days": "number",
    "structured_logging": "boolean"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `level` | String | Nivel de logging | `"INFO"` |
| `format` | String | Formato de logs | `"json"` |
| `outputs` | Array | Salidas de logging | `["console", "file"]` |
| `retention_days` | Number | Días de retención | `30` |
| `structured_logging` | Boolean | Logging estructurado | `true` |

#### **📊 CONFIGURACIÓN DE MÉTRICAS**
```json
{
  "metrics_config": {
    "enabled": "boolean",
    "collection_interval": "number",
    "retention_days": "number",
    "custom_metrics": "array",
    "alerts": "object"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `enabled` | Boolean | Métricas habilitadas | `true` |
| `collection_interval` | Number | Intervalo de recolección (segundos) | `60` |
| `retention_days` | Number | Días de retención | `90` |
| `custom_metrics` | Array | Métricas personalizadas | `[]` |
| `alerts` | Object | Configuración de alertas | Ver abajo |

---

## 🚨 **CONFIGURACIONES DE ALERTAS**

### **⚠️ CONFIGURACIÓN DE ALERTAS**

#### **📊 ALERTAS DE RENDIMIENTO**
```json
{
  "performance_alerts": {
    "response_time_threshold_ms": "number",
    "error_rate_threshold_percent": "number",
    "throughput_threshold_per_minute": "number",
    "memory_usage_threshold_percent": "number",
    "cpu_usage_threshold_percent": "number"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `response_time_threshold_ms` | Number | Umbral de tiempo de respuesta | `5000` |
| `error_rate_threshold_percent` | Number | Umbral de tasa de error | `5.0` |
| `throughput_threshold_per_minute` | Number | Umbral de throughput | `1000` |
| `memory_usage_threshold_percent` | Number | Umbral de uso de memoria | `80.0` |
| `cpu_usage_threshold_percent` | Number | Umbral de uso de CPU | `80.0` |

#### **🔒 ALERTAS DE SEGURIDAD**
```json
{
  "security_alerts": {
    "failed_auth_threshold": "number",
    "suspicious_activity_threshold": "number",
    "malware_detection": "boolean",
    "unauthorized_access": "boolean"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `failed_auth_threshold` | Number | Umbral de autenticaciones fallidas | `10` |
| `suspicious_activity_threshold` | Number | Umbral de actividad sospechosa | `5` |
| `malware_detection` | Boolean | Detección de malware | `true` |
| `unauthorized_access` | Boolean | Acceso no autorizado | `true` |

---

## 🔄 **CONFIGURACIONES DE PROCESAMIENTO ASÍNCRONO**

### **📋 CONFIGURACIÓN DE COLAS**

#### **🚀 CONFIGURACIÓN AZURE QUEUE STORAGE**
```json
{
  "queue_config": {
    "connection_string": "string",
    "queues": {
      "processing": "string",
      "notifications": "string",
      "retry": "string",
      "dlq": "string"
    },
    "visibility_timeout": "number",
    "max_retry_attempts": "number",
    "retry_delay_seconds": "number"
  }
}
```

| Campo | Tipo | Descripción | Valor por Defecto |
|-------|------|-------------|-------------------|
| `connection_string` | String | Cadena de conexión | `"DefaultEndpointsProtocol=https..."` |
| `queues.processing` | String | Cola de procesamiento | `"document-processing"` |
| `queues.notifications` | String | Cola de notificaciones | `"notifications"` |
| `queues.retry` | String | Cola de reintentos | `"retry-queue"` |
| `queues.dlq` | String | Cola de mensajes fallidos | `"dead-letter-queue"` |
| `visibility_timeout` | Number | Timeout de visibilidad (segundos) | `300` |
| `max_retry_attempts` | Number | Máximo de intentos | `3` |
| `retry_delay_seconds` | Number | Delay entre reintentos | `60` |

---

## 📚 **REFERENCIAS Y ENLACES**

- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md)
- [Catálogo de Tabla de Productos](./Catalogo_Datos_Tabla_Productos.md)
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md)
- [Guía de Implementación Técnica](./Guia_Tecnica_Implementacion.md)

---

**📅 Última actualización**: 2024-01-08  
**👤 Mantenido por**: Equipo de Desarrollo API IDP Expert System  
**🔄 Versión**: 1.0.0
