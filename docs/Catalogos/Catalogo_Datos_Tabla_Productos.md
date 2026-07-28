# 📦 CATÁLOGO DE DATOS - TABLA DE PRODUCTOS

## 🎯 **DESCRIPCIÓN GENERAL**
Este catálogo documenta la estructura y contenido de la tabla de productos expandida, que contiene los items de línea individuales extraídos de facturas y otros documentos comerciales.

---

## 🗂️ **ESTRUCTURA DE DATOS**

### **📋 TABLA PRINCIPAL: `products_table`**

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `extraction_id` | String | ID de la extracción origen | `"ext_1234567890"` |
| `job_id` | String | ID del trabajo de procesamiento | `"job_20240101_001"` |
| `invoice_number` | String | Número de factura | `"FAC-2024-001"` |
| `created_at` | DateTime | Fecha de creación del registro | `"2024-01-01T10:30:00Z"` |
| `processing_mode` | String | Modo de procesamiento | `"gpt_vision_only"` |
| `item_index` | Integer | Índice del item en la factura | `0`, `1`, `2` |
| `descripcion` | String | Descripción del producto/servicio | `"Servicio de consultoría técnica"` |
| `cantidad` | Number | Cantidad del item | `10.0`, `5.5` |
| `precio_unitario` | Number | Precio unitario | `150000.00` |
| `impuesto_porcentaje` | Number | Porcentaje de impuesto | `19.0` |
| `total_linea` | Number | Total de la línea | `1785000.00` |
| `confidence` | Number | Puntuación de confianza | `0.95` |
| `source_strategy` | String | Estrategia de extracción | `"gpt_vision"` |

---

## 🔍 **DETALLES DE CAMPOS**

### **📝 CAMPOS IDENTIFICADORES**

#### **`extraction_id`**
- **Tipo**: String
- **Formato**: `"ext_" + timestamp + "_" + random_string`
- **Ejemplo**: `"ext_20240101103000_abc123"`
- **Propósito**: Vincular el producto con su extracción origen
- **Restricciones**: Único, no nulo

#### **`job_id`**
- **Tipo**: String
- **Formato**: `"job_" + fecha + "_" + secuencia`
- **Ejemplo**: `"job_20240101_001"`
- **Propósito**: Identificar el trabajo de procesamiento
- **Restricciones**: No nulo, formato específico

#### **`invoice_number`**
- **Tipo**: String
- **Formato**: Variable según el proveedor
- **Ejemplo**: `"FAC-2024-001"`, `"INV-001-2024"`, `"2024-0001"`
- **Propósito**: Identificar la factura origen
- **Restricciones**: No nulo, máximo 50 caracteres

### **📊 CAMPOS DE PRODUCTO**

#### **`descripcion`**
- **Tipo**: String
- **Longitud**: 1-500 caracteres
- **Ejemplo**: `"Servicio de consultoría técnica especializada"`
- **Propósito**: Descripción detallada del producto/servicio
- **Restricciones**: No nulo, texto descriptivo

#### **`cantidad`**
- **Tipo**: Number (Decimal)
- **Rango**: 0.01 - 999999.99
- **Ejemplo**: `10.0`, `5.5`, `0.25`
- **Propósito**: Cantidad del producto/servicio
- **Restricciones**: Positivo, máximo 2 decimales

#### **`precio_unitario`**
- **Tipo**: Number (Decimal)
- **Rango**: 0.01 - 999999999.99
- **Ejemplo**: `150000.00`, `2500.50`
- **Propósito**: Precio por unidad del producto/servicio
- **Restricciones**: Positivo, máximo 2 decimales

#### **`impuesto_porcentaje`**
- **Tipo**: Number (Decimal)
- **Rango**: 0.0 - 100.0
- **Ejemplo**: `19.0`, `5.0`, `0.0`
- **Propósito**: Porcentaje de impuesto aplicado
- **Restricciones**: No negativo, máximo 2 decimales

#### **`total_linea`**
- **Tipo**: Number (Decimal)
- **Rango**: 0.01 - 999999999.99
- **Ejemplo**: `1785000.00`, `2625.00`
- **Propósito**: Total calculado de la línea
- **Fórmula**: `cantidad * precio_unitario * (1 + impuesto_porcentaje/100)`
- **Restricciones**: Positivo, máximo 2 decimales

### **🎯 CAMPOS DE CONTROL**

#### **`item_index`**
- **Tipo**: Integer
- **Rango**: 0 - 9999
- **Ejemplo**: `0`, `1`, `2`
- **Propósito**: Orden del item en la factura
- **Restricciones**: No negativo, secuencial

#### **`confidence`**
- **Tipo**: Number (Decimal)
- **Rango**: 0.0 - 1.0
- **Ejemplo**: `0.95`, `0.87`, `0.72`
- **Propósito**: Nivel de confianza en la extracción
- **Escala**: 0.0 (muy baja) - 1.0 (excelente)
- **Restricciones**: Entre 0 y 1

#### **`source_strategy`**
- **Tipo**: String
- **Valores**: `"gpt_vision"`, `"regex_pattern"`, `"template_matching"`
- **Ejemplo**: `"gpt_vision"`
- **Propósito**: Estrategia utilizada para la extracción
- **Restricciones**: Valor de lista predefinida

---

## 📊 **TIPOS DE PRODUCTOS COMUNES**

### ** SERVICIOS PROFESIONALES**
| Descripción | Cantidad | Precio Unitario | Impuesto |
|-------------|----------|-----------------|----------|
| `"Servicio de consultoría técnica"` | `40.0` | `150000.00` | `19.0` |
| `"Desarrollo de software"` | `120.0` | `200000.00` | `19.0` |
| `"Capacitación especializada"` | `16.0` | `300000.00` | `19.0` |

### ** PRODUCTOS TANGIBLES**
| Descripción | Cantidad | Precio Unitario | Impuesto |
|-------------|----------|-----------------|----------|
| `"Servidor Dell PowerEdge"` | `2.0` | `5000000.00` | `19.0` |
| `"Licencia de software"` | `10.0` | `500000.00` | `19.0` |
| `"Cable de red UTP Cat6"` | `100.0` | `5000.00` | `19.0` |

### ** SERVICIOS DE INFRAESTRUCTURA**
| Descripción | Cantidad | Precio Unitario | Impuesto |
|-------------|----------|-----------------|----------|
| `"Hosting en la nube"` | `12.0` | `500000.00` | `19.0` |
| `"Mantenimiento preventivo"` | `1.0` | `2000000.00` | `19.0` |
| `"Soporte técnico 24/7"` | `1.0` | `3000000.00` | `19.0` |

---

## 🔍 **VALIDACIONES Y REGLAS DE NEGOCIO**

### **✅ VALIDACIONES OBLIGATORIAS**
1. **`extraction_id`**: Debe existir en la tabla de extracciones
2. **`job_id`**: Debe existir en la tabla de trabajos
3. **`invoice_number`**: No puede estar vacío
4. **`descripcion`**: Mínimo 5 caracteres
5. **`cantidad`**: Debe ser mayor a 0
6. **`precio_unitario`**: Debe ser mayor a 0

### **🔍 VALIDACIONES DE COHERENCIA**
1. **`total_linea`**: Debe coincidir con el cálculo
2. **`impuesto_porcentaje`**: Debe estar entre 0 y 100
3. **`confidence`**: Debe estar entre 0 y 1
4. **`item_index`**: Debe ser secuencial por factura

### **⚠️ REGLAS DE NEGOCIO**
1. **Cantidad**: No puede ser negativa
2. **Precios**: No pueden ser negativos
3. **Impuestos**: Deben ser porcentajes válidos
4. **Totales**: Deben ser coherentes con los cálculos

---

## 📈 **MÉTRICAS Y ESTADÍSTICAS**

### **📊 MÉTRICAS DE VOLUMEN**
- **Total de productos**: 887 registros (última exportación)
- **Productos por factura**: 1-50 items promedio
- **Facturas con productos**: 95% de las facturas procesadas
- **Tasa de extracción exitosa**: 92%

### **📋 DISTRIBUCIÓN POR TIPO**
| Tipo de Producto | Porcentaje | Cantidad |
|------------------|------------|----------|
| Servicios Profesionales | 45% | 399 |
| Productos Tangibles | 30% | 266 |
| Servicios de Infraestructura | 25% | 222 |

### **💰 MÉTRICAS FINANCIERAS**
- **Valor total de productos**: $2,500,000,000.00
- **Valor promedio por producto**: $2,818,000.00
- **Producto más caro**: $50,000,000.00
- **Producto más barato**: $1,000.00

---

## 🔗 **RELACIONES CON OTRAS TABLAS**

### ** RELACIÓN CON EXTRACCIONES**
```sql
products_table.extraction_id = extractions.id
```
- **Tipo**: Uno a Muchos
- **Propósito**: Vincular productos con su extracción origen
- **Integridad**: Referencial

### ** RELACIÓN CON TRABAJOS**
```sql
products_table.job_id = jobs.id
```
- **Tipo**: Muchos a Uno
- **Propósito**: Agrupar productos por trabajo de procesamiento
- **Integridad**: Referencial

### ** RELACIÓN CON FACTURAS**
```sql
products_table.invoice_number = invoices.number
```
- **Tipo**: Muchos a Uno
- **Propósito**: Agrupar productos por factura
- **Integridad**: Lógica

---

## 📊 **VISTAS Y CONSULTAS COMUNES**

### ** VISTA: RESUMEN POR FACTURA**
```sql
SELECT 
    invoice_number,
    COUNT(*) as total_items,
    SUM(cantidad) as total_quantity,
    SUM(total_linea) as total_amount,
    AVG(confidence) as avg_confidence
FROM products_table
GROUP BY invoice_number
ORDER BY total_amount DESC;
```

### ** VISTA: TOP PRODUCTOS**
```sql
SELECT 
    descripcion,
    COUNT(*) as frequency,
    SUM(cantidad) as total_quantity,
    SUM(total_linea) as total_amount
FROM products_table
GROUP BY descripcion
ORDER BY total_amount DESC
LIMIT 20;
```

### ** VISTA: ANÁLISIS DE CONFIANZA**
```sql
SELECT 
    source_strategy,
    AVG(confidence) as avg_confidence,
    COUNT(*) as total_items,
    COUNT(CASE WHEN confidence >= 0.9 THEN 1 END) as high_confidence_items
FROM products_table
GROUP BY source_strategy;
```

---

## 🚨 **CÓDIGOS DE ERROR ESPECÍFICOS**

### **❌ ERRORES DE EXTRACCIÓN**
| Código | Descripción | Solución |
|--------|-------------|----------|
| `PRODUCT_PARSE_ERROR` | Error al parsear JSON de productos | Revisar formato del campo `items_de_linea` |
| `INVALID_QUANTITY` | Cantidad inválida | Validar formato numérico |
| `INVALID_PRICE` | Precio inválido | Validar formato numérico |
| `CALCULATION_MISMATCH` | Total calculado no coincide | Revisar fórmula de cálculo |

### **⚠️ ADVERTENCIAS COMUNES**
| Código | Descripción | Acción |
|--------|-------------|--------|
| `LOW_CONFIDENCE` | Confianza menor a 0.7 | Revisar extracción manualmente |
| `MISSING_DESCRIPTION` | Descripción muy corta | Validar extracción |
| `UNUSUAL_PRICE` | Precio fuera del rango normal | Verificar con proveedor |

---

## 🔒 **CONSIDERACIONES DE SEGURIDAD**

### **🛡️ DATOS SENSIBLES**
- **Información financiera**: Cifrado en tránsito y en reposo
- **Datos de proveedores**: Anonimización opcional
- **Montos**: Redondeo para privacidad si es necesario

### **🔐 CONTROL DE ACCESO**
- **Lectura**: Usuarios con rol `analyst` o superior
- **Escritura**: Solo sistema de procesamiento
- **Eliminación**: Solo administradores

---

## 📚 **REFERENCIAS Y ENLACES**

- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md)
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md)
- [Guía de Implementación Técnica](./Guia_Tecnica_Implementacion.md)

---

**📅 Última actualización**: 2024-01-08  
**👤 Mantenido por**: Equipo de Desarrollo API IDP Expert System  
**🔄 Versión**: 1.0.0
