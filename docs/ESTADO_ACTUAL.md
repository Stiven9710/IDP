# Estado Actual del Proyecto — IDP Expert System

**Fecha de generación:** 2026-06-13
**Versión del sistema:** v2.1.0 (declarada en código: 2.0.0)
**Rama activa:** `dev`
**Commit HEAD:** `399d1fe` — "Se realiza la carga del codigo desplegado en ambiente de desarrollo"

---

## 1. Identidad del Repositorio

| Campo | Valor |
|---|---|
| Repositorio remoto | https://github.com/Stiven9710/IDP.git |
| Nombre del remote | `origin` |
| Tag de versión estable | `v1.0.0-stable` |
| Tag de versión actual | `v2.1.0` (commit `1e2c0ff`) |
| Desarrollado por | Ronald Estiven Rios Hernandez |
| Organización | Banco Caja Social |

**Ramas del repositorio:**

| Rama | Último commit | Descripción |
|---|---|---|
| `main` | `f4f3de4` (2026-06-13) | Rama principal de producción |
| `dev` | `399d1fe` (2025-09-08) | Rama de desarrollo activa |
| `release/DigitalOcean` | `08c6e23` (2025-11-05) | Release para despliegue en Digital Ocean |

---

## 2. Estado de Sincronización con el Remoto

### Rama `dev` — SINCRONIZADA

Tras el pull ejecutado el 2026-06-13, la rama `dev` local está al día con `origin/dev`.

```
HEAD: 399d1fe (origin/dev)
```

### Desfase respecto a `origin/main`

La rama `dev` local **no incluye** los siguientes commits que sí están en `main`:

| Hash | Fecha | Mensaje |
|---|---|---|
| `f4f3de4` | 2026-06-13 | Merge pull request #11 from Stiven9710/release/DigitalOcean |
| `08c6e23` | 2025-11-05 | Se suben los cambios correspondientes al ambiente de Digital Ocean |
| `9cb97b9` | 2025-09-09 | Merge pull request #10 from Stiven9710/dev |

Estos cambios corresponden a la integración de la rama `release/DigitalOcean` a `main`. Son cambios de despliegue en Digital Ocean que aún no han sido retroportados a `dev`.

---

## 3. Arquitectura y Stack Tecnológico

### Lenguaje y Framework

| Componente | Versión |
|---|---|
| Python | 3.9+ |
| FastAPI | 0.115.6 |
| Uvicorn | 0.32.1 (con soporte standard) |
| Pydantic | 2.5.0 |
| pydantic-settings | 2.1.0 |

### Servicios Azure

| Servicio | Librería / Versión | Uso |
|---|---|---|
| Azure OpenAI (GPT-4o) | openai 1.3.0 | Análisis de imágenes, extracción con visión |
| Azure Document Intelligence | azure-ai-documentintelligence 1.0.0 / azure-ai-formrecognizer 3.3.0 | OCR y análisis de documentos |
| Azure Cosmos DB | azure-cosmos 4.4.0 | Persistencia de documentos, extracciones y jobs |
| Azure Blob Storage | azure-storage-blob 12.19.0 | Almacenamiento temporal para procesamiento asíncrono |
| Azure Queue Storage | azure-storage-queue 12.6.0 | Cola de mensajes para jobs asíncronos |
| Azure Key Vault | azure-keyvault-secrets 4.7.0 | Gestión de secretos |
| Azure Monitor | azure-monitor-opentelemetry 1.0.0 | Observabilidad y métricas |
| Azure Identity | azure-identity 1.15.0 | Autenticación unificada |

### Procesamiento de Documentos

| Librería | Versión | Uso |
|---|---|---|
| PyMuPDF | 1.23.8 | Conversión PDF a imagen |
| Pillow | 10.1.0 | Manipulación de imágenes |
| python-pptx | 0.6.21 | Procesamiento de presentaciones |
| lxml | 4.9.3 | Procesamiento HTML/XML |

### Infraestructura

- **Contenedores:** Dockerfile + docker-compose.yml
- **Despliegue Azure:** `azure-deploy.yml`, `azure-app-service-config.json`
- **IaC:** Bicep templates en `infrastructure/`
- **CI/CD:** GitHub Actions en `.github/workflows/`
- **n8n:** Integración con n8n vía `n8n/docker-compose.yml` y nginx (`n8n/nginx/nginx.conf`) — agregado en commit `399d1fe`

### Entrypoint

```
main.py                       # Punto de entrada principal
  └── app/main.py             # Aplicación FastAPI (versión "2.0.0" declarada en código)
        └── app/api/v1/router.py  # Registro de todos los routers
```

---

## 4. Funcionalidades Operativas

### 4.1 Estrategias de Extracción

| Estrategia | Tiempo aprox. | Descripción |
|---|---|---|
| `gpt_vision_only` | ~2-3 s | PDF → PNG → GPT-4o. Rápido, dependiente de visión IA |
| `dual_service` | ~3-5 s | Document Intelligence + GPT-4o en paralelo |
| `hybrid_consensus` | ~4-6 s | Ambos servicios + validación cruzada de resultados |

### 4.2 Procesamiento Híbrido

- **Síncrono (≤10 MB):** respuesta HTTP 200 con datos extraídos directamente
- **Asíncrono (>10 MB):** HTTP 202 + `job_id` → Blob Storage → Queue → Background Worker → resultado disponible vía polling
- **Cascada con contexto:** documentos de más de 5 páginas se procesan en cascada para mantener coherencia

### 4.3 Persistencia en Cosmos DB

Containers activos:

| Container | Propósito |
|---|---|
| `documents` | Metadata de documentos procesados |
| `extractions` | Datos extraídos con confianzas por campo |
| `processing_jobs` | Estado y resultado de jobs asíncronos |

Control de persistencia introducido en v2.1.0: eliminación configurable usando APIs nativas de Azure Cosmos DB.

### 4.4 Formatos de Documento Soportados

PDF, DOCX, DOC, TXT, RTF, PNG, JPG, TIFF, BMP, GIF, XLSX, XLS, PPTX, PPT, HTML

### 4.5 Endpoints de la API (v1)

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/documents/process-upload` | Subir y procesar un documento |
| GET | `/api/v1/documents/{job_id}/status` | Estado de un job asíncrono |
| GET | `/api/v1/documents/{job_id}/result` | Resultado de un job completado |
| GET | `/api/v1/documents/extractions/history/{document_id}` | Historial de extracciones |
| GET | `/api/v1/documents/extractions/search` | Búsqueda en extracciones |
| GET | `/api/v1/jobs` | Lista de todos los jobs |
| GET | `/api/v1/health` | Health check básico |
| GET | `/api/v1/health/cosmos` | Health check de Cosmos DB |
| GET | `/api/v1/health/detailed` | Health check detallado de todos los servicios |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |

### 4.6 Seguridad de URLs Externas

- Whitelist de dominios permitidos
- HTTPS obligatorio
- Bloqueo de extensiones peligrosas
- Timeouts configurables

### 4.7 Evidencia de Uso

Los logs indican ejecución intensiva del sistema:

| Archivo | Tamaño |
|---|---|
| `logs/idp.log` | ~23 MB |
| `logs/api.log` | ~639 KB |

---

## 5. Estructura de Carpetas (trackeadas en git)

```
/ (raíz)
├── main.py                             # Entrypoint uvicorn
├── config.py                           # Configuración global
├── run_background_worker.py            # Entrypoint del worker
├── Dockerfile                          # Imagen Docker
├── docker-compose.yml                  # Despliegue local con Docker
├── docker-deploy.sh                    # Script de despliegue
├── azure-app-service-config.json       # Configuración Azure App Service
├── azure-deploy.yml                    # Pipeline de despliegue Azure
├── GUIA_DESPLIEGUE_DOCKER_AZURE.md    # Guía de despliegue
├── requirements.txt                    # Dependencias Python
├── .env.example / env.example          # Plantillas de variables de entorno
│
├── app/                                # Código principal FastAPI
│   ├── api/v1/                         # Endpoints versionados
│   ├── core/                           # config.py, security, exceptions
│   ├── models/                         # document, request, response
│   ├── schemas/                        # Pydantic schemas
│   └── services/                       # ai_orchestrator, cosmos_service,
│                                       # document_service, background_worker,
│                                       # blob/queue/storage services
│
├── docs/                               # Documentación técnica y funcional
│   ├── README.md                       # Índice de documentación
│   ├── Documentacion_Funcional_API.md
│   ├── Funcionalidad_Persistencia_Documentos.md
│   ├── Guia_Despliegue_Local_Docker.md
│   ├── Seguridad_URLs_Externas.md
│   ├── quick-start-docker.sh
│   └── Catalogos/                      # [NO COMMITEADO — ver Sección 6]
│
├── n8n/                                # Integración n8n (agregado en 399d1fe)
│   ├── docker-compose.yml
│   ├── docker-compose-nginx.yml
│   └── nginx/nginx.conf
│
├── scripts/                            # Scripts de utilidad (algunos trackeados)
│
├── tests/
│   └── unit/                           # Tests de integración y curl scripts
│
├── infrastructure/                     # Bicep templates + parameters
│
├── Arquitectura de Referencia/         # Documentos de arquitectura
│   └── IDP_Arquitectura_FastAPI_Consolidada.md
│
└── .github/workflows/                  # GitHub Actions
```

---

## 6. Trabajo Activo NO Commiteado

Los siguientes recursos existen localmente pero **no están en el repositorio remoto**. Representan trabajo activo y/o material de referencia en progreso.

### 6.1 `Arquitectura de Referencia/Script BAse/`

Scripts base del proceso R_VLD (Validación Legalización Desembolso) del Banco Caja Social.

| Archivo | Descripción |
|---|---|
| `R_VLD_ValidacionLegalizacionDesembolso/` | Carpeta del proyecto R_VLD |
| `Scripts R_VLD_ValidacionLegalizacionDesembolso V1.1.zip` | Paquete comprimido de la versión 1.1 |

**Estado:** Material de referencia local. No es código del API IDP en sí, sino scripts de proceso de negocio relacionados.

---

### 6.2 `docs/Catalogos/` — Modelo de Datos Completo

Documentación exhaustiva del modelo de datos del sistema, generada con base en el estado real de Cosmos DB.

| Archivo | Audiencia principal | Contenido |
|---|---|---|
| `Indice_Catalogos_Datos.md` | Todos | Mapa de navegación a todos los catálogos |
| `Modelo_Datos_Completo.md` | Arquitectos, desarrolladores senior | Arquitectura de datos, relaciones, índices, escalabilidad |
| `Catalogo_Datos_Extracciones_Principales.md` | Desarrolladores, analistas | Estructura del container `extractions`, campos, confianzas, estrategias |
| `Catalogo_Datos_Tabla_Productos.md` | Analistas, usuarios de negocio | Estructura de items de línea expandidos, validaciones, consultas comunes |
| `Catalogo_Datos_Metadatos_Configuraciones.md` | Administradores, operadores | Configuraciones de procesamiento, seguridad, persistencia, monitoreo |

**Estado:** Documentación lista, pendiente de commit.

---

### 6.3 `scripts/` — Toolkit de Consolidación y Exportación a Excel

Scripts independientes para conectar a Cosmos DB, consolidar datos de extracciones y exportarlos como archivos Excel para análisis. Requieren variables de entorno de Cosmos DB (`AZURE_COSMOS_ENDPOINT`, `AZURE_COSMOS_KEY`, `AZURE_COSMOS_DATABASE_NAME`).

**Dependencias adicionales:** `pandas`, `openpyxl`, `azure-cosmos`

| Script | Propósito |
|---|---|
| `setup_consolidation.py` | Instala dependencias y configura el entorno — ejecutar primero |
| `test_consolidation.py` | Prueba la conexión a Cosmos DB y la consolidación sin guardar archivos |
| `consolidate_extractions.py` | Conecta a container `extractions` y consolida datos en DataFrames (principal) |
| `expand_products_table.py` | Expande arrays `items_de_linea` en registros individuales para análisis |
| `export_complete_data.py` | Exporta DataFrame principal + tabla de productos expandida en un solo paso |
| `export_dataframes_to_excel.py` | Exporta DataFrames como archivos Excel separados |
| `get_dataframes_as_excel.py` | Retorna DataFrames como archivos Excel listos para usar |
| `example_usage.py` | Ejemplos de uso de los scripts de consolidación |
| `fix_products_parsing.py` | Parseo corregido de productos con comillas simples en los datos |
| `debug_products_parsing.py` | Herramienta de debugging para investigar problemas de parsing de productos |

**Flujo de uso recomendado:**
```bash
python scripts/setup_consolidation.py        # 1. Configurar
python scripts/test_consolidation.py         # 2. Verificar conexión
python scripts/export_complete_data.py       # 3. Exportar todo
```

---

### 6.4 `output/` — Resultados Excel Generados

Archivos Excel generados por los scripts de consolidación a partir de datos reales de Cosmos DB.

| Archivo | Fecha | Tamaño | Descripción |
|---|---|---|---|
| `extractions_main_20250908_215814.xlsx` | 2025-09-08 | 60 KB | Extracciones principales (ejecución inicial) |
| `extractions_arrays_20250908_215814.xlsx` | 2025-09-08 | 40 KB | Arrays de productos (ejecución inicial) |
| `products_table_fixed_20250908_220919.xlsx` | 2025-09-08 | 84 KB | Tabla de productos con parseo corregido |
| `extractions_main_20250927_172357.xlsx` | 2025-09-27 | 238 KB | Extracciones principales (consolidación completa) |
| `extractions_consolidated_20250927_172357.xlsx` | 2025-09-27 | 289 KB | Datos consolidados completos |
| `products_table_20250927_172357.xlsx` | 2025-09-27 | 272 KB | Tabla de productos completa |
| `summary_report_20250927_172357.xlsx` | 2025-09-27 | 7 KB | Reporte de resumen de métricas |

**Nota:** El crecimiento entre la ejecución del 2025-09-08 y la del 2025-09-27 (de ~60 KB a ~289 KB en datos principales) evidencia volumen significativo de procesamiento real en ese período.

---

## 7. Configuración y Despliegue

### Variables de Entorno Requeridas

Plantilla disponible en `.env.example` (y duplicado en `env.example`). Variables clave:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT=

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=
AZURE_DOCUMENT_INTELLIGENCE_KEY=

# Azure Cosmos DB
AZURE_COSMOS_ENDPOINT=
AZURE_COSMOS_KEY=
AZURE_COSMOS_DATABASE_NAME=

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=
AZURE_BLOB_CONTAINER_NAME=
AZURE_QUEUE_NAME=
```

### Levantar el Sistema

```bash
# Opción 1: Directo con uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Docker Compose
docker-compose up --build

# Worker asíncrono (proceso separado si no se usa el integrado)
python run_background_worker.py
```

### URLs de Acceso

| URL | Descripción |
|---|---|
| `http://localhost:8000/` | Raíz de la API |
| `http://localhost:8000/docs` | Swagger UI interactivo |
| `http://localhost:8000/redoc` | ReDoc UI |
| `http://localhost:8000/api/v1/health` | Health check básico |
| `http://localhost:8000/api/v1/health/detailed` | Health check completo |

Para referencia de despliegue completa: ver `GUIA_DESPLIEGUE_DOCKER_AZURE.md` en la raíz.

---

## 8. Pendientes y Consideraciones

| Item | Prioridad | Descripción |
|---|---|---|
| Commits de `origin/main` no en `dev` | Media | 3 commits de `release/DigitalOcean` (cambios Digital Ocean) no integrados a `dev`. Evaluar si retroportar. |
| Carpeta `n8n/` en remoto | Revisar | Ahora presente localmente (llegó con `399d1fe`). Integración n8n + nginx para flujos de automatización. |
| Scripts `scripts/*.py` sin commitear | Alta | Toolkit de consolidación probado y con outputs generados. Listo para commitear. |
| `docs/Catalogos/` sin commitear | Alta | Documentación del modelo de datos completa y útil. Lista para commitear. |
| `output/` sin commitear | Baja | Archivos de datos generados. Considerar si deben ir en git (archivos binarios grandes) o en `.gitignore`. |
| `Arquitectura de Referencia/Script BAse/` | Media | Scripts R_VLD de referencia. Evaluar si pertenecen a este repo o a uno separado. |
| Versión en código desactualizada | Baja | `app/main.py` declara `version="2.0.0"` pero el sistema ya está en v2.1.0. Actualizar string. |
| Logs grandes | Baja | `logs/idp.log` (~23 MB). Configurar rotación de logs para evitar crecimiento ilimitado. |
| `.env.example` duplicado | Baja | Existen `.env.example` y `env.example` (sin punto). Consolidar en uno solo. |

---

## 9. Cómo Verificar el Estado en Vivo

```bash
# 1. Health check básico
curl http://localhost:8000/api/v1/health

# 2. Health check completo (incluye Cosmos DB)
curl http://localhost:8000/api/v1/health/detailed

# 3. Procesar un documento de prueba
curl -X POST http://localhost:8000/api/v1/documents/process-upload \
  -F "file=@Invoice_2082463105.pdf" \
  -F "extraction_strategy=gpt_vision_only"

# 4. Verificar Swagger UI
open http://localhost:8000/docs

# 5. Probar conexión a Cosmos DB y datos disponibles
python scripts/test_consolidation.py
```

---

*Documento generado el 2026-06-13. Commit HEAD: `399d1fe`. Rama: `dev`.*
