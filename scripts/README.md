# 📊 Scripts de Consolidación de Extracciones

## 🎯 **Descripción**

Scripts independientes para consolidar datos de extracciones desde Cosmos DB y convertirlos en DataFrames de pandas para análisis.

## 📁 **Archivos Incluidos**

### **1. `consolidate_extractions.py`** - Script Principal
- **Función**: Conecta a Cosmos DB y consolida extracciones
- **Salida**: Archivo Excel con datos consolidados
- **Características**:
  - Extrae datos del container `extractions`
  - Consolida campos en DataFrame principal
  - Extrae arrays en DataFrame separado
  - Genera reporte de resumen

### **2. `test_consolidation.py`** - Script de Prueba
- **Función**: Prueba la consolidación sin guardar archivos
- **Uso**: Verificar que la conexión y consolidación funcionen
- **Salida**: Reporte en consola

### **3. `setup_consolidation.py`** - Script de Configuración
- **Función**: Instala dependencias y configura entorno
- **Uso**: Ejecutar antes de usar los otros scripts
- **Salida**: Configuración del entorno

## 🚀 **Instalación y Uso**

### **Paso 1: Configurar Entorno**
```bash
# Ejecutar script de configuración
python scripts/setup_consolidation.py
```

### **Paso 2: Probar Conexión**
```bash
# Probar consolidación
python scripts/test_consolidation.py
```

### **Paso 3: Ejecutar Consolidación**
```bash
# Consolidar datos y generar Excel
python scripts/consolidate_extractions.py
```

## 📊 **Estructura de Salida**

### **DataFrame Principal (`Extractions_Main`)**
- **Columnas base**: `extraction_id`, `job_id`, `created_at`, `processing_mode`
- **Columnas de campos**: `{field_name}_value`, `{field_name}_confidence`, `{field_name}_strategy`
- **Ejemplo**: `numero_factura_value`, `numero_factura_confidence`, `numero_factura_strategy`

### **DataFrame de Arrays (`Extractions_Arrays`)**
- **Columnas base**: `extraction_id`, `job_id`, `field_name`, `array_index`
- **Columnas de items**: `item_{property_name}`
- **Ejemplo**: `item_descripcion`, `item_cantidad`, `item_precio_unitario`

### **Hoja de Resumen (`Summary`)**
- **Métricas**: Total de extracciones, campos únicos, elementos en arrays
- **Fecha de generación**: Timestamp del proceso

## 🔧 **Configuración Requerida**

### **Variables de Entorno (.env)**
```env
AZURE_COSMOS_ENDPOINT=https://tu-cosmos.documents.azure.com:443/
AZURE_COSMOS_KEY=tu-clave-de-cosmos
AZURE_COSMOS_DATABASE_NAME=idp-database
```

### **Dependencias Python**
- `pandas` - Manipulación de datos
- `openpyxl` - Escritura de archivos Excel
- `azure-cosmos` - Cliente de Cosmos DB

## 📈 **Ejemplo de Uso**

```python
from consolidate_extractions import ExtractionConsolidator

# Crear consolidador
consolidator = ExtractionConsolidator()

# Obtener extracciones
extractions = consolidator.get_all_extractions()

# Consolidar en DataFrame
df_main = consolidator.consolidate_extractions(extractions)

# Extraer arrays
df_arrays = consolidator.extract_array_fields(extractions)

# Guardar en Excel
consolidator.save_to_excel(df_main, df_arrays, "mi_consolidacion.xlsx")
```

## 🎯 **Casos de Uso**

### **1. Análisis de Facturas**
- Consolidar datos de facturas procesadas
- Analizar campos más comunes
- Identificar patrones en extracciones

### **2. Auditoría de Calidad**
- Revisar confianza de extracciones
- Comparar estrategias de procesamiento
- Identificar campos problemáticos

### **3. Reportes Ejecutivos**
- Generar estadísticas de procesamiento
- Crear dashboards con datos consolidados
- Exportar para análisis en BI

## ⚠️ **Consideraciones**

### **Rendimiento**
- Scripts optimizados para grandes volúmenes
- Uso de queries eficientes en Cosmos DB
- Procesamiento en lotes para arrays

### **Seguridad**
- Credenciales desde variables de entorno
- No hardcodeo de claves
- Conexión segura a Cosmos DB

### **Mantenimiento**
- Scripts modulares y reutilizables
- Logs detallados para debugging
- Manejo robusto de errores

## 🆘 **Solución de Problemas**

### **Error de Conexión a Cosmos DB**
- Verificar variables de entorno
- Comprobar credenciales
- Revisar firewall y red

### **Error de Dependencias**
- Ejecutar `setup_consolidation.py`
- Verificar versión de Python (3.9+)
- Revisar permisos de instalación

### **Error de Memoria**
- Procesar en lotes más pequeños
- Aumentar memoria disponible
- Optimizar queries de Cosmos DB

---

*Scripts desarrollados para IDP Expert System v2.1.0*
