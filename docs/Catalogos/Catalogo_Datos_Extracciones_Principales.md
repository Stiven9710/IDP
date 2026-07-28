# 📊 CATÁLOGO DE DATOS - EXTRACCIONES PRINCIPALES

## 🎯 **DESCRIPCIÓN GENERAL**
Este catálogo documenta la estructura y contenido de los datos de extracciones principales almacenados en Azure Cosmos DB, incluyendo metadatos, campos extraídos y configuraciones de procesamiento.

---

## 🗂️ **ESTRUCTURA DE DATOS**

### **📋 TABLA PRINCIPAL: `extractions`**

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` | String | Identificador único de la extracción | `"ext_1234567890"` |
| `job_id` | String | ID del trabajo de procesamiento | `"job_20240101_001"` |
| `created_at` | DateTime | Fecha y hora de creación | `"2024-01-01T10:30:00Z"` |
| `updated_at` | DateTime | Fecha y hora de última actualización | `"2024-01-01T10:35:00Z"` |
| `status` | String | Estado del procesamiento | `"completed"`, `"failed"`, `"processing"` |
| `processing_mode` | String | Modo de procesamiento utilizado | `"gpt_vision_only"`, `"hybrid"` |
| `document_type` | String | Tipo de documento procesado | `"invoice"`, `"proposal"`, `"contract"` |
| `extraction_data` | Array | Array de campos extraídos | Ver estructura detallada abajo |
| `metadata` | Object | Metadatos adicionales | Ver estructura detallada abajo |
| `confidence_scores` | Object | Puntuaciones de confianza | Ver estructura detallada abajo |
| `processing_strategies` | Object | Estrategias de procesamiento | Ver estructura detallada abajo |

---

## 🔍 **CAMPOS EXTRAÍDOS (`extraction_data`)**

### **📝 ESTRUCTURA DE CAMPO INDIVIDUAL**
```json
{
  "name": "nombre_del_campo",
  "type": "tipo_de_dato",
  "value": "valor_extraído",
  "confidence": 0.95,
  "source_strategy": "gpt_vision",
  "extraction_metadata": {
    "page_number": 1,
    "coordinates": [100, 200, 300, 400],
    "processing_time_ms": 1500
  }
}
```

### **📊 TIPOS DE CAMPOS SOPORTADOS**

| Tipo | Descripción | Ejemplos | Validación |
|------|-------------|----------|------------|
| `string` | Texto libre | `"Banco Caribe"`, `"Propuesta Técnica"` | Longitud máxima: 1000 caracteres |
| `number` | Número decimal | `1500000.50`, `25.75` | Rango: -999999999 a 999999999 |
| `integer` | Número entero | `100`, `-50` | Rango: -2147483648 a 2147483647 |
| `boolean` | Verdadero/Falso | `true`, `false` | Solo valores booleanos |
| `array` | Lista de elementos | `[{"item": "valor1"}, {"item": "valor2"}]` | Array de objetos JSON |
| `date` | Fecha | `"2024-01-01"`, `"2024-01-01T10:30:00Z"` | Formato ISO 8601 |
| `currency` | Moneda | `"$1,500,000.00"`, `"€2,500.50"` | Formato de moneda estándar |

---

## 🏷️ **CAMPOS COMUNES POR TIPO DE DOCUMENTO**

### **📄 FACTURAS (`invoice`)**
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `numero_factura` | String | Número de la factura | `"FAC-2024-001"` |
| `fecha_factura` | Date | Fecha de emisión | `"2024-01-01"` |
| `proveedor` | String | Nombre del proveedor | `"Empresa ABC S.A.S."` |
| `cliente` | String | Nombre del cliente | `"Banco Caja Social"` |
| `subtotal` | Currency | Subtotal de la factura | `"$1,500,000.00"` |
| `impuestos` | Currency | Total de impuestos | `"$285,000.00"` |
| `total` | Currency | Total de la factura | `"$1,785,000.00"` |
| `items_de_linea` | Array | Lista de items de la factura | Ver estructura de items abajo |

### **📋 PROPUESTAS (`proposal`)**
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `nombre_propuesta` | String | Título de la propuesta | `"Propuesta Perfil Transaccional IB"` |
| `resumen_propuesta` | String | Resumen ejecutivo | `"Implementación de sistema de perfil transaccional"` |
| `tecnologia_implementar` | String | Tecnologías a implementar | `"Python, FastAPI, Azure, PostgreSQL"` |
| `requisitos_infraestructura_software` | Array | Requisitos de infraestructura | Ver estructura de requisitos abajo |
| `total_horas` | Number | Total de horas estimadas | `1200` |

### **📄 CONTRATOS (`contract`)**
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `numero_contrato` | String | Número del contrato | `"CON-2024-001"` |
| `fecha_inicio` | Date | Fecha de inicio | `"2024-01-01"` |
| `fecha_fin` | Date | Fecha de finalización | `"2024-12-31"` |
| `valor_contrato` | Currency | Valor total del contrato | `"$50,000,000.00"` |
| `clausulas_importantes` | Array | Lista de cláusulas | Ver estructura de cláusulas abajo |

---

## 📦 **ESTRUCTURAS DE DATOS COMPLEJAS**

### **🛒 ITEMS DE LÍNEA (Facturas)**
```json
{
  "descripcion": "Descripción del producto/servicio",
  "cantidad": 10,
  "precio_unitario": 150000.00,
  "impuesto_porcentaje": 19.0,
  "total_linea": 1785000.00
}
```

### **🏗️ REQUISITOS DE INFRAESTRUCTURA (Propuestas)**
```json
{
  "descripcion": "Servidor de base de datos",
  "cantidad": 2,
  "especificaciones": "16GB RAM, 500GB SSD",
  "costo_estimado": 5000000.00
}
```

### **📋 CLÁUSULAS DE CONTRATO**
```json
{
  "numero": "Cláusula 5.1",
  "titulo": "Obligaciones del contratista",
  "contenido": "El contratista se compromete a...",
  "importancia": "alta"
}
```

---

## 🎯 **PUNTUACIONES DE CONFIANZA**

### **📊 ESCALA DE CONFIANZA**
| Rango | Nivel | Descripción |
|-------|-------|-------------|
| 0.9 - 1.0 | Excelente | Extracción muy confiable |
| 0.8 - 0.9 | Buena | Extracción confiable |
| 0.7 - 0.8 | Regular | Extracción aceptable |
| 0.6 - 0.7 | Baja | Extracción dudosa |
| 0.0 - 0.6 | Muy Baja | Extracción no confiable |

### **🔍 FACTORES QUE AFECTAN LA CONFIANZA**
- **Calidad del documento**: Resolución, legibilidad, formato
- **Complejidad del campo**: Campos simples vs. complejos
- **Estrategia de procesamiento**: GPT Vision vs. OCR vs. Híbrido
- **Contexto disponible**: Información circundante
- **Validaciones**: Coherencia con otros campos

---

## ⚙️ **ESTRATEGIAS DE PROCESAMIENTO**

### **🤖 MODOS DISPONIBLES**
| Modo | Descripción | Uso Recomendado |
|------|-------------|-----------------|
| `gpt_vision_only` | Solo GPT Vision | Documentos con texto claro |
| `hybrid` | GPT Vision + OCR | Documentos complejos o escaneados |
| `ocr_only` | Solo OCR | Documentos escaneados simples |

### **📈 ESTRATEGIAS POR CAMPO**
| Estrategia | Descripción | Campos Aplicables |
|------------|-------------|-------------------|
| `gpt_vision` | Procesamiento con IA | Todos los tipos |
| `regex_pattern` | Patrones regulares | Números, fechas, códigos |
| `template_matching` | Coincidencia de plantillas | Campos estructurados |
| `context_analysis` | Análisis de contexto | Campos complejos |

---

## 📊 **METADATOS DE PROCESAMIENTO**

### **⏱️ INFORMACIÓN TEMPORAL**
```json
{
  "processing_start_time": "2024-01-01T10:30:00Z",
  "processing_end_time": "2024-01-01T10:35:00Z",
  "total_processing_time_ms": 300000,
  "gpt_vision_time_ms": 250000,
  "ocr_time_ms": 50000
}
```

### **📄 INFORMACIÓN DEL DOCUMENTO**
```json
{
  "document_size_mb": 2.5,
  "total_pages": 10,
  "pages_processed": 10,
  "document_format": "PDF",
  "document_quality": "high"
}
```

### **🔧 CONFIGURACIÓN DE PROCESAMIENTO**
```json
{
  "prompt_general": "Instrucciones generales para la extracción",
  "field_definitions": [...],
  "persistencia": true,
  "processing_mode": "gpt_vision_only"
}
```

---

## 🚨 **CÓDIGOS DE ERROR Y ESTADOS**

### **📊 ESTADOS DE PROCESAMIENTO**
| Estado | Código | Descripción |
|--------|--------|-------------|
| `pending` | 0 | Pendiente de procesamiento |
| `processing` | 1 | En proceso |
| `completed` | 2 | Completado exitosamente |
| `failed` | 3 | Falló el procesamiento |
| `cancelled` | 4 | Cancelado por el usuario |

### **❌ CÓDIGOS DE ERROR COMUNES**
| Código | Descripción | Solución |
|--------|-------------|----------|
| `DOCUMENT_TOO_LARGE` | Documento muy grande | Reducir tamaño o usar procesamiento asíncrono |
| `UNSUPPORTED_FORMAT` | Formato no soportado | Convertir a PDF o formato soportado |
| `LOW_QUALITY` | Calidad de imagen baja | Mejorar resolución del documento |
| `EXTRACTION_TIMEOUT` | Tiempo de extracción agotado | Usar procesamiento asíncrono |
| `API_QUOTA_EXCEEDED` | Cuota de API excedida | Esperar o aumentar límites |

---

## 📈 **MÉTRICAS Y ESTADÍSTICAS**

### **📊 MÉTRICAS DE RENDIMIENTO**
- **Tiempo promedio de procesamiento**: 2-5 minutos por documento
- **Tasa de éxito**: 95%+ para documentos de buena calidad
- **Campos extraídos por documento**: 10-50 campos promedio
- **Confianza promedio**: 0.85+ para documentos estándar

### **📋 ESTADÍSTICAS DE USO**
- **Documentos procesados por día**: 100-500
- **Tipos de documento más comunes**: Facturas (60%), Propuestas (25%), Contratos (15%)
- **Modo de procesamiento más usado**: `gpt_vision_only` (70%)
- **Tasa de persistencia**: 80% de documentos se conservan

---

## 🔒 **CONSIDERACIONES DE SEGURIDAD**

### **🛡️ DATOS SENSIBLES**
- **Información financiera**: Cifrado en tránsito y en reposo
- **Datos personales**: Anonimización automática
- **Documentos confidenciales**: Marcado especial para eliminación automática

### **🔐 CONTROL DE ACCESO**
- **Autenticación**: Tokens JWT requeridos
- **Autorización**: Roles y permisos por usuario
- **Auditoría**: Log de todas las operaciones

---

## 📚 **REFERENCIAS Y ENLACES**

- [Documentación de la API](../README.md)
- [Guía de Implementación Técnica](./Guia_Tecnica_Implementacion.md)
- [Funcionalidad de Persistencia](./Funcionalidad_Persistencia_Documentos.md)
- [Seguridad de URLs Externas](./Seguridad_URLs_Externas.md)

---

**📅 Última actualización**: 2024-01-08  
**👤 Mantenido por**: Equipo de Desarrollo API IDP Expert System  
**🔄 Versión**: 1.0.0
