# 🗄️ MODELO DE DATOS COMPLETO - IDP EXPERT SYSTEM

## 🎯 **DESCRIPCIÓN GENERAL**
Este documento presenta el modelo de datos completo del sistema IDP Expert System, incluyendo todas las entidades, relaciones, restricciones y reglas de negocio implementadas en Azure Cosmos DB.

---

## 🏗️ **ARQUITECTURA DE DATOS**

### **📊 DIAGRAMA DE ENTIDADES**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EXTRACTIONS   │    │   PRODUCTS      │    │     JOBS        │
│                 │    │                 │    │                 │
│ • id            │◄───┤ • extraction_id │    │ • id            │
│ • job_id        │    │ • job_id        │───►│ • status        │
│ • status        │    │ • invoice_number│    │ • created_at    │
│ • created_at    │    │ • descripcion   │    │ • processing_mode│
│ • processing_mode│   │ • cantidad      │    │ • metadata      │
│ • extraction_data│   │ • precio_unitario│   │ • blob_path     │
│ • metadata      │    │ • total_linea   │    │ • persistencia  │
│ • confidence    │    │ • confidence    │    │ • results       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   BLOB STORAGE  │    │   QUEUE STORAGE │    │   LOGS & AUDIT  │
│                 │    │                 │    │                 │
│ • documents/    │    │ • processing    │    │ • processing_logs│
│ • processed/    │    │ • notifications │    │ • error_logs    │
│ • metadata      │    │ • retry_queue   │    │ • audit_trail   │
│ • retention     │    │ • dlq           │    │ • performance   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📋 **ENTIDADES PRINCIPALES**

### **1. EXTRACTIONS (Extracciones)**
```json
{
  "id": "string (PK)",
  "job_id": "string (FK)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "status": "enum",
  "processing_mode": "enum",
  "document_type": "string",
  "extraction_data": "array",
  "metadata": "object",
  "confidence_scores": "object",
  "processing_strategies": "object",
  "ttl": "number"
}
```

**🔑 Claves Primarias:**
- `id`: Identificador único de la extracción

**🔗 Claves Foráneas:**
- `job_id`: Referencia a la tabla JOBS

**📊 Índices:**
- `job_id` (Hash)
- `created_at` (Range)
- `status` (Hash)
- `processing_mode` (Hash)

### **2. PRODUCTS (Productos)**
```json
{
  "extraction_id": "string (FK)",
  "job_id": "string (FK)",
  "invoice_number": "string",
  "created_at": "datetime",
  "processing_mode": "string",
  "item_index": "number",
  "descripcion": "string",
  "cantidad": "number",
  "precio_unitario": "number",
  "impuesto_porcentaje": "number",
  "total_linea": "number",
  "confidence": "number",
  "source_strategy": "string"
}
```

**🔑 Claves Primarias:**
- `extraction_id` + `item_index` (Composite)

**🔗 Claves Foráneas:**
- `extraction_id`: Referencia a EXTRACTIONS
- `job_id`: Referencia a JOBS

**📊 Índices:**
- `extraction_id` (Hash)
- `job_id` (Hash)
- `invoice_number` (Hash)
- `created_at` (Range)

### **3. JOBS (Trabajos)**
```json
{
  "id": "string (PK)",
  "status": "enum",
  "created_at": "datetime",
  "updated_at": "datetime",
  "processing_mode": "enum",
  "document_type": "string",
  "blob_path": "string",
  "persistencia": "boolean",
  "metadata": "object",
  "results": "object",
  "error_details": "object",
  "ttl": "number"
}
```

**🔑 Claves Primarias:**
- `id`: Identificador único del trabajo

**📊 Índices:**
- `status` (Hash)
- `created_at` (Range)
- `processing_mode` (Hash)
- `persistencia` (Hash)

---

## 🔍 **ESTRUCTURAS DE DATOS DETALLADAS**

### **📝 EXTRACTION_DATA (Campos Extraídos)**
```json
{
  "name": "string",
  "type": "enum",
  "value": "any",
  "confidence": "number",
  "source_strategy": "string",
  "extraction_metadata": {
    "page_number": "number",
    "coordinates": "array",
    "processing_time_ms": "number",
    "validation_status": "string"
  }
}
```

**🎯 Tipos de Campo Soportados:**
- `string`: Texto libre
- `number`: Número decimal
- `integer`: Número entero
- `boolean`: Verdadero/Falso
- `array`: Lista de elementos
- `date`: Fecha
- `currency`: Moneda

### **📊 CONFIDENCE_SCORES (Puntuaciones de Confianza)**
```json
{
  "overall": "number",
  "field_scores": {
    "field_name": "number"
  },
  "strategy_scores": {
    "gpt_vision": "number",
    "ocr": "number",
    "hybrid": "number"
  },
  "validation_status": "string"
}
```

### **⚙️ PROCESSING_STRATEGIES (Estrategias de Procesamiento)**
```json
{
  "primary_strategy": "string",
  "fallback_strategies": "array",
  "field_strategies": {
    "field_name": "string"
  },
  "processing_metadata": {
    "gpt_vision_time_ms": "number",
    "ocr_time_ms": "number",
    "total_time_ms": "number"
  }
}
```

---

## 🔗 **RELACIONES ENTRE ENTIDADES**

### **1. EXTRACTIONS ↔ JOBS**
```
EXTRACTIONS.job_id = JOBS.id
```
- **Tipo**: Muchos a Uno
- **Cardinalidad**: N:1
- **Integridad**: Referencial
- **Cascada**: Eliminación en cascada

### **2. PRODUCTS ↔ EXTRACTIONS**
```
PRODUCTS.extraction_id = EXTRACTIONS.id
```
- **Tipo**: Muchos a Uno
- **Cardinalidad**: N:1
- **Integridad**: Referencial
- **Cascada**: Eliminación en cascada

### **3. PRODUCTS ↔ JOBS**
```
PRODUCTS.job_id = JOBS.id
```
- **Tipo**: Muchos a Uno
- **Cardinalidad**: N:1
- **Integridad**: Referencial
- **Cascada**: No cascada

---

## 📊 **ÍNDICES Y OPTIMIZACIÓN**

### **🔍 ÍNDICES PRINCIPALES**

#### **EXTRACTIONS**
```sql
-- Índice principal
CREATE INDEX idx_extractions_job_id ON extractions (job_id)

-- Índice de rango temporal
CREATE INDEX idx_extractions_created_at ON extractions (created_at)

-- Índice de estado
CREATE INDEX idx_extractions_status ON extractions (status)

-- Índice compuesto
CREATE INDEX idx_extractions_job_status ON extractions (job_id, status)
```

#### **PRODUCTS**
```sql
-- Índice principal
CREATE INDEX idx_products_extraction_id ON products (extraction_id)

-- Índice de factura
CREATE INDEX idx_products_invoice_number ON products (invoice_number)

-- Índice compuesto
CREATE INDEX idx_products_invoice_item ON products (invoice_number, item_index)
```

#### **JOBS**
```sql
-- Índice principal
CREATE INDEX idx_jobs_status ON jobs (status)

-- Índice temporal
CREATE INDEX idx_jobs_created_at ON jobs (created_at)

-- Índice de modo de procesamiento
CREATE INDEX idx_jobs_processing_mode ON jobs (processing_mode)
```

### **⚡ OPTIMIZACIONES DE RENDIMIENTO**

#### **Particionamiento**
- **EXTRACTIONS**: Particionado por `job_id`
- **PRODUCTS**: Particionado por `extraction_id`
- **JOBS**: Particionado por `created_at` (mensual)

#### **TTL (Time To Live)**
- **EXTRACTIONS**: 90 días por defecto
- **PRODUCTS**: 90 días por defecto
- **JOBS**: 30 días por defecto

---

## 🚨 **RESTRICCIONES Y VALIDACIONES**

### **✅ RESTRICCIONES DE INTEGRIDAD**

#### **EXTRACTIONS**
```sql
-- Clave primaria
PRIMARY KEY (id)

-- Clave foránea
FOREIGN KEY (job_id) REFERENCES jobs(id)

-- Restricciones de dominio
CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
CHECK (processing_mode IN ('gpt_vision_only', 'hybrid', 'ocr_only'))
CHECK (created_at <= updated_at)
```

#### **PRODUCTS**
```sql
-- Clave primaria compuesta
PRIMARY KEY (extraction_id, item_index)

-- Claves foráneas
FOREIGN KEY (extraction_id) REFERENCES extractions(id)
FOREIGN KEY (job_id) REFERENCES jobs(id)

-- Restricciones de dominio
CHECK (cantidad > 0)
CHECK (precio_unitario > 0)
CHECK (impuesto_porcentaje >= 0 AND impuesto_porcentaje <= 100)
CHECK (confidence >= 0 AND confidence <= 1)
CHECK (item_index >= 0)
```

#### **JOBS**
```sql
-- Clave primaria
PRIMARY KEY (id)

-- Restricciones de dominio
CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
CHECK (processing_mode IN ('gpt_vision_only', 'hybrid', 'ocr_only'))
CHECK (created_at <= updated_at)
```

### **🔍 VALIDACIONES DE NEGOCIO**

#### **Validaciones de Coherencia**
1. **Total de línea**: `total_linea = cantidad * precio_unitario * (1 + impuesto_porcentaje/100)`
2. **Confianza**: Debe estar entre 0 y 1
3. **Fechas**: `created_at` no puede ser mayor que `updated_at`
4. **Estados**: Transiciones válidas de estado

#### **Validaciones de Formato**
1. **IDs**: Formato específico según el tipo
2. **Fechas**: Formato ISO 8601
3. **Números**: Precisión decimal apropiada
4. **Strings**: Longitud máxima según el campo

---

## 📈 **MÉTRICAS Y MONITOREO**

### **📊 MÉTRICAS DE RENDIMIENTO**

#### **Volumen de Datos**
- **EXTRACTIONS**: ~1,000 registros/día
- **PRODUCTS**: ~5,000 registros/día
- **JOBS**: ~1,000 registros/día

#### **Tamaño de Almacenamiento**
- **EXTRACTIONS**: ~2MB por registro promedio
- **PRODUCTS**: ~1KB por registro promedio
- **JOBS**: ~500KB por registro promedio

#### **Tiempos de Respuesta**
- **Consultas simples**: <100ms
- **Consultas complejas**: <500ms
- **Agregaciones**: <1s

### **🔍 MÉTRICAS DE CALIDAD**

#### **Tasa de Éxito**
- **Extracciones exitosas**: 95%+
- **Productos extraídos**: 92%+
- **Confianza promedio**: 0.85+

#### **Errores Comunes**
- **Parseo JSON**: 5%
- **Validación de campos**: 3%
- **Cálculos incorrectos**: 2%

---

## 🔒 **SEGURIDAD Y PRIVACIDAD**

### **🛡️ CIFRADO**

#### **En Tránsito**
- **Protocolo**: TLS 1.3
- **Certificados**: Azure-managed
- **Algoritmos**: AES-256

#### **En Reposo**
- **Algoritmo**: AES-256
- **Gestión de claves**: Azure Key Vault
- **Rotación**: Automática cada 90 días

### **🔐 CONTROL DE ACCESO**

#### **Roles y Permisos**
```json
{
  "admin": {
    "read": ["*"],
    "write": ["*"],
    "delete": ["*"]
  },
  "analyst": {
    "read": ["extractions", "products", "jobs"],
    "write": [],
    "delete": []
  },
  "processor": {
    "read": ["jobs"],
    "write": ["extractions", "products"],
    "delete": []
  }
}
```

#### **Auditoría**
- **Log de acceso**: Todas las operaciones
- **Retención**: 2 años
- **Alertas**: Accesos no autorizados

---

## 📚 **MIGRACIONES Y VERSIONADO**

### **🔄 ESTRATEGIA DE MIGRACIÓN**

#### **Versión 1.0 → 1.1**
- **Cambios**: Agregar campo `persistencia` a JOBS
- **Migración**: Script de actualización automática
- **Rollback**: Reversión automática disponible

#### **Versión 1.1 → 1.2**
- **Cambios**: Optimización de índices
- **Migración**: Recreación de índices
- **Downtime**: Mínimo (5 minutos)

### **📋 PROCEDIMIENTOS DE MANTENIMIENTO**

#### **Limpieza de Datos**
- **Frecuencia**: Diaria
- **Criterios**: TTL + reglas de negocio
- **Retención**: 90 días por defecto

#### **Optimización de Índices**
- **Frecuencia**: Semanal
- **Criterios**: Uso y rendimiento
- **Automático**: Sí

---

## 🚀 **ESCALABILIDAD Y RENDIMIENTO**

### **📈 ESTRATEGIA DE ESCALADO**

#### **Escalado Horizontal**
- **Particionamiento**: Por fecha y tipo
- **Distribución**: Automática en Azure
- **Balanceo**: Round-robin

#### **Escalado Vertical**
- **CPU**: Escalado automático
- **Memoria**: Escalado automático
- **Almacenamiento**: Escalado automático

### **⚡ OPTIMIZACIONES**

#### **Consultas**
- **Índices**: Optimizados para patrones comunes
- **Caché**: Redis para consultas frecuentes
- **Compresión**: LZ4 para datos históricos

#### **Almacenamiento**
- **Particionamiento**: Por fecha
- **Compresión**: Automática
- **Tiering**: Hot/Cool/Archive

---

## 📚 **REFERENCIAS Y ENLACES**

- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md)
- [Catálogo de Tabla de Productos](./Catalogo_Datos_Tabla_Productos.md)
- [Guía de Implementación Técnica](./Guia_Tecnica_Implementacion.md)
- [Documentación de la API](./Documentacion_Funcional_API.md)

---

**📅 Última actualización**: 2024-01-08  
**👤 Mantenido por**: Equipo de Desarrollo API IDP Expert System  
**🔄 Versión**: 1.0.0
