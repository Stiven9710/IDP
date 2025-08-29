# Documentación de Proyecto: Solución IDP Experta (Versión Final)

**Proyecto:** Sistema de Procesamiento Inteligente de Documentos (IDP) con Despachador Adaptativo  
**Versión:** 5.0 (Final)  
**Fecha:** 12 de agosto de 2025

---

## 1. Introducción y Alcance

### 1.1. Propósito

El propósito de este proyecto es desarrollar una solución de software como servicio (SaaS) alojada en Azure para automatizar la extracción de información de documentos. El sistema utilizará servicios de Inteligencia Artificial (IA) de vanguardia para ofrecer una extracción de datos flexible, precisa y rentable, controlada a través de una API RESTful.

### 1.2. Alcance

El alcance de este proyecto incluye el diseño, desarrollo y despliegue de la API, la lógica de procesamiento de IA, y la infraestructura de almacenamiento de datos. El proyecto **no** incluye el desarrollo de las aplicaciones cliente (ej. flujos de Power Automate) que consumirán la API ni la creación de los tableros de Power BI.

---

## 2. Arquitectura de Referencia en Texto

```
   ********************************************************************************
   * CLIENTE (Ej. Power Automate)                *
   ********************************************************************************
   [ Cliente de API ]
   |
   | 1. Llama a un ÚNICO endpoint: /api/ProcessDocumentSmart con JSON de entrada
   |
   +----------------------------------------------------------------------------+
                                                                                 |
   ********************************************************************************
   * CAPA DE API Y APLICACIÓN (AZURE)                      *
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
   * PROCESAMIENTO EN SEGUNDO PLANO Y ALMACENAMIENTO (AZURE)     *
   ********************************************************************************

   [ Azure Queue Storage ] ---> [ Fn-Process-Async ] ---> [ Orquestador de IA ] ---> [ Azure Cosmos DB (Capa Plata) ]
   (Dispara la función)                               (Llama a los servicios de IA)
   
```

---

## 3. Guía del Experto: Reglas para la Extracción de Información

Esta sección define las mejores prácticas para estructurar las solicitudes y maximizar la precisión.

### 3.1. Estructura del Prompt General

El `prompt_general` debe establecer el contexto y las reglas globales.

- **Asignar un Rol:** `"Actúa como un asistente experto en contabilidad especializado en analizar facturas."`
- **Proveer Contexto:** `"Estás analizando una factura de un proveedor de Colombia."`
- **Establecer Reglas Globales:** `"Si un campo no se encuentra, devuélvelo como null. No inventes información."`

### 3.2. Definición Detallada de Campos

El array `fields` permite un control granular. Cada objeto debe contener:

- **`name`**: La clave en el JSON de salida (ej. `"numero_factura"`).
- **`type`**: El tipo de dato deseado (ej. `"string"`, `"date"`, `"number"`, `"boolean"`, `"array"`).
- **`description`**: Un **mini-prompt** específico para ese campo, con pistas y reglas.

### 3.3. Técnicas Avanzadas de Prompting

- **Manejo de Formatos:** Sé explícito. `"Extrae todas las fechas únicamente en formato YYYY-MM-DD."`
- **Uso de Pistas Contextuales:** Ayuda a la IA a desambiguar. `"El 'total a pagar' es el valor final después de impuestos y suele ser el monto más grande y destacado."`
- **Extracción de Ítems de Línea:** Usa el `type: "array"` y describe la estructura de los objetos internos. `"Extrae cada línea de producto como un objeto separado en este array, con las claves: 'descripcion', 'cantidad', y 'precio_unitario'."`

---

## 4. Requerimientos Funcionales (RF)

### RF-1: Ingesta y Selección de Estrategia

- **RF-1.1:** El sistema deberá aceptar solicitudes `POST` en `/api/ProcessDocumentSmart`.
- **RF-1.2:** El cuerpo de la solicitud JSON deberá contener `document_path`, `processing_mode`, `prompt_general`, y un array de objetos `fields`. Cada objeto en `fields` deberá contener `name`, `type`, y `description`.
- **RF-1.3:** El sistema deberá implementar tres estrategias de extracción (`"dual_service"`, `"gpt_vision_only"`, `"hybrid_consensus"`) y usar tanto el `prompt_general` como las `description` de cada campo para guiar a la IA.

### RF-2: Lógica de Procesamiento y Salida

- **RF-2.1:** Un despachador inteligente manejará la ruta de ejecución (sincrónica/asincrónica) según el tamaño del archivo.
- **RF-2.2 (Reconciliación Híbrida):** En el modo `"hybrid_consensus"`, el sistema comparará los resultados de las dos estrategias. Si existe una diferencia significativa, el resultado final tomará el valor de la estrategia `"dual_service"` y marcará el campo para revisión humana en la salida.
- **RF-2.3 (Estructura de Salida):** El JSON de salida deberá contener los datos extraídos (`extraction_data`) y un resumen del proceso (`processing_summary`), que incluye un estado (`processing_status`) y las banderas de revisión (`review_flags`).

### RF-3: Almacenamiento y Consulta

- **RF-3.1:** Todos los resultados exitosos deberán ser persistidos en **Azure Cosmos DB** (Capa Plata).
- **RF-3.2:** El sistema deberá proveer un endpoint para consultar el estado de los trabajos asincrónicos.

---

## 5. Especificación de la API

### Endpoint Principal

**URL:** `POST /api/ProcessDocumentSmart`

### JSON de Entrada ***(Ejemplo Final)***

```json
{
  "document_path": "https://tuempresa.sharepoint.com/sites/Contabilidad/Documentos/Facturas/proveedor_acme_inv_9981.pdf",
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
    "correlation_id": "flow-run-55ab8c7d-e9f0-4g1a-9b2c-8d7e6f5a4b3c"
  }
}
```

---

## 6. Requerimientos Técnicos (RT)

- **RT-1: Plataforma:** Microsoft Azure.
- **RT-2: Servicios Principales:** Azure Functions, Azure Cosmos DB (Capa Gratuita), Azure API Management (Consumo), Azure Key Vault, Azure Blob Storage, Azure Queue Storage, Azure AI Services.
- **RT-3: Lenguaje:** Python 3.9+.
- **RT-4: Infraestructura como Código:** Se recomienda el uso de Bicep o Terraform.
- **RT-5: Monitoreo:** Integración completa con Azure Application Insights.

---

## 7. Estructura y Estándares de Programación en Python

### 7.1. Estructura de Carpetas

```
idp-solution/
├── .venv/
├── host.json
├── local.settings.json
├── requirements.txt
│
├── shared_code/            # Código común (helpers para IA, Cosmos DB, etc.)
│   ├── __init__.py
│   └── ai_orchestrator.py
│
├── FnSmartDispatcher/      # Función del despachador
│   ├── __init__.py
│   └── function.json
│
├── FnProcessAsync/         # Función de la cola asincrónica
│   ├── __init__.py
│   └── function.json
│
└── tests/                  # Pruebas unitarias
```

### 7.2. Estándares de Programación

- **Formato:** Cumplimiento estricto de **PEP 8** (reforzado con `black` y `flake8`).
- **Tipado:** Uso obligatorio de **Type Hinting** (verificado con `mypy`).
- **Seguridad:** Cero secretos en el código; leer desde Key Vault mediante Identidades Administradas.
- **Modularidad:** Código reutilizable en la carpeta `shared_code`.
- **Manejo de Errores:** Uso de bloques `try...except` para una gestión robusta.