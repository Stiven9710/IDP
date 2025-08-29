# Arquitectura de Referencia: IDP con Integración de Base de Datos para Analítica

Esta arquitectura de referencia presenta una solución ajustada para incluir la base de datos como el destino final de los datos extraídos, sirviendo como la **Capa Plata** en la implementación de la arquitectura Medallón.

## 1. Diagrama de la Arquitectura Ajustada

El cambio principal se refleja en el destino final del flujo asincrónico. En lugar de guardar un archivo JSON en Blob Storage, la función de procesamiento ahora escribe directamente en una base de datos estructurada.

## 2. Componentes de la Arquitectura

La tabla de componentes ahora incluye una capa específica para la base de datos analítica.

| Capa | Servicio | Rol y Responsabilidades |
|------|----------|------------------------|
| **Cliente** | **Power Automate** | Orquesta los flujos de negocio. Inicia las solicitudes de procesamiento. |
| **API y Seguridad** | **Azure API Management** | Puerta de enlace única y segura para todas las API. |
| | **Azure Key Vault** | Almacén seguro para todas las credenciales, incluyendo la cadena de conexión de la base de datos. |
| **Aplicación (Serverless)** | **Azure Functions** | El núcleo lógico: `Fn-Ingest`, `Fn-Process-Async`, `Fn-Get-Status`. **La `Fn-Process-Async` ahora tiene la lógica para conectarse y escribir en la base de datos.** |
| **Datos y Estado** | **Azure Blob Storage** | **Capa Bronce**: Almacena los documentos originales (`docs-para-procesar`) para auditoría. |
| | **Azure Queue Storage** | Desacopla la ingesta del procesamiento, garantizando la resiliencia y escalabilidad. |
| **Inteligencia** | **Azure AI Services** | Document Intelligence y Azure OpenAI para la extracción de datos. |
| **Datos Analíticos** | **Azure SQL Database** (o similar) | **Capa Plata**: Almacena los datos extraídos en un formato limpio, estructurado y relacional. Es la fuente de datos directa para la creación de modelos en la Capa Oro y para el consumo desde Power BI. |

## 3. Flujo Asincrónico Actualizado

Los pasos 1 al 4 no cambian. El cambio fundamental está en el paso 5.

### Pasos del Procesamiento

1. **Inicio:** Power Automate llama al endpoint `/api/StartProcessingJob`.

2. **Ingesta:** `Fn-Ingest` sube el documento a Blob Storage (Capa Bronce).

3. **Encolado:** `Fn-Ingest` pone un mensaje en la cola con el `jobId`.

4. **Respuesta Inmediata:** La API devuelve el `jobId` a Power Automate.

5. **Procesamiento y Escritura (Paso Clave Actualizado):**
   - La función `Fn-Process-Async` se activa por el mensaje en la cola.
   - Realiza la orquestación de llamadas a Document Intelligence y Azure OpenAI.
   - **Se conecta a la base de datos (p. ej., Azure SQL Database) y escribe los datos extraídos en las tablas correspondientes.** Este es el momento en que los datos aterrizan en tu Capa Plata.

## 4. Elección de la Base de Datos (Capa Plata)

Tienes excelentes opciones en Azure. La elección depende de la estructura de tus datos y tus preferencias.

### Recomendación Principal: Azure SQL Database

**¿Por qué?**
- Es una base de datos relacional gestionada que se integra de forma nativa y perfecta con Power BI.
- Si los datos que extraes son estructurados (números de factura, fechas, totales, nombres, etc.), este es el estándar de oro.
- Te permite definir un esquema claro, asegurar la integridad de los datos y usar el poder de T-SQL para consultas.

### Alternativa Excelente: Azure Cosmos DB

**¿Por qué?**
- Si los datos extraídos son semi-estructurados o tienen un esquema que varía mucho entre documentos (JSON anidados y complejos), Cosmos DB es ideal.
- Puedes almacenar los resultados como documentos JSON directamente.
- Power BI también tiene un conector nativo para Cosmos DB.
- Es extremadamente escalable y rápido, aunque puede ser más costoso para cargas de trabajo simples.

## 5. Diagrama de Arquitectura Completo

```
********************************************************************************
* CLIENTE                                                                      *
********************************************************************************

[ Power Automate ]
|
| 1. Llama a un ÚNICO endpoint: /api/ProcessDocumentSmart
|
+----------------------------------------------------------------------------+
|
********************************************************************************
* CAPA DE API Y APLICACIÓN (AZURE)                                           *
********************************************************************************

[ Azure API Management ]
|
v
[ Fn-Smart-Dispatcher (HTTP Trigger) ]
|
| a. Obtiene el archivo y verifica su tamaño contra un umbral (ej. 5 MB).
|
+----[ DECISIÓN: ¿Archivo Pequeño? ]-----------------------------------------+
|                                                                             |
v (RUTA SINCRÓNICA)                                    v (RUTA ASINCRÓNICA)
|                                                      |
| b. Procesa de inmediato:                             | b. Inicia el proceso en segundo plano:
| - Llama a Azure AI Services.                         | - Sube el archivo a Blob Storage (Capa Bronce).
| - Escribe en la Base de Datos (Capa Plata).         | - Encola un mensaje en Queue Storage.
|                                                      |
| c. Devuelve una respuesta completa:                  | c. Devuelve una respuesta de aceptación:
| <-- [ HTTP 200 OK + Datos Extraídos ] --<           | <-- [ HTTP 202 Accepted + jobId ] --<
|                                                      |
+---------------------------------------------------------------------------+
|
<-- (Power Automate recibe la respuesta y verifica el CÓDIGO DE ESTADO para decidir el siguiente paso)

********************************************************************************
* PROCESAMIENTO EN SEGUNDO PLANO (AZURE) - (Solo para ruta asincrónica)      *
********************************************************************************

[ Azure Queue Storage ] ---> [ Fn-Process-Async (Queue Trigger) ] ---> [ Base de Datos (Capa Plata) ]
(Dispara la función)         (Realiza el trabajo pesado de IA)          (Guarda el resultado final)
```

## Conclusión

Esta arquitectura ajustada proporciona una base sólida y profesional para no solo procesar documentos, sino también para construir un sistema de inteligencia de negocio robusto sobre los datos extraídos. La integración directa con la base de datos en la Capa Plata permite un acceso eficiente y estructurado a los datos procesados, facilitando su posterior análisis y visualización en herramientas como Power BI.