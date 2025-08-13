# IDP Expert System - Sistema de Procesamiento Inteligente de Documentos

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Azure](https://img.shields.io/badge/Azure-Cloud-blue.svg)](https://azure.microsoft.com)

## 🎯 **Descripción del Proyecto**

IDP Expert System es una solución robusta y escalable para el procesamiento inteligente de documentos utilizando tecnologías de vanguardia:

- **FastAPI** como framework web asíncrono de alto rendimiento
- **Azure AI Services** para extracción inteligente de datos
- **Azure Cosmos DB** para almacenamiento estructurado
- **Arquitectura híbrida** que combina procesamiento síncrono y asíncrono

## 🚀 **Características Principales**

- ✅ **Procesamiento Híbrido**: Síncrono para archivos pequeños (<5MB), asíncrono para archivos grandes
- ✅ **Múltiples Estrategias de IA**: Dual Service, GPT-4 Vision, Hybrid Consensus
- ✅ **Validación Automática**: Con Pydantic para prevenir errores de datos
- ✅ **Escalabilidad**: Diseñado para manejar alto volumen de documentos
- ✅ **Monitoreo Integral**: Application Insights y métricas personalizadas
- ✅ **Seguridad**: Autenticación JWT y autorización basada en roles

## 🏗️ **Arquitectura del Sistema**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Power Automate│    │  API Management │    │   FastAPI App   │
│   (Cliente)     │───▶│   (Gateway)     │───▶│   (Backend)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                       ┌─────────────────────────────────────────┐
                       │           Services Layer                │
                       │  ┌─────────────┐ ┌─────────────────┐   │
                       │  │AI Orchestrator│ │Storage Service │   │
                       │  └─────────────┘ └─────────────────┘   │
                       └─────────────────────────────────────────┘
                                                       │
                                                       ▼
                       ┌─────────────────────────────────────────┐
                       │         Azure AI Services               │
                       │  ┌─────────────┐ ┌─────────────────┐   │
                       │  │Azure OpenAI │ │Document Intel.  │   │
                       │  └─────────────┘ └─────────────────┘   │
                       └─────────────────────────────────────────┘
```

## 📋 **Requisitos Previos**

- Python 3.9 o superior
- Cuenta de Azure con suscripción activa
- Azure OpenAI Service configurado
- Azure Document Intelligence configurado
- Azure Cosmos DB configurado
- Azure Storage Account configurado

## 🛠️ **Instalación y Configuración**

### 1. **Clonar el Repositorio**

```bash
git clone https://github.com/Stiven9710/IDP.git
cd IDP
git checkout dev
```

### 2. **Configurar Entorno Virtual**

```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. **Instalar Dependencias**

```bash
pip install -r requirements.txt
```

### 4. **Configurar Variables de Entorno**

```bash
cp .env.example .env
# Editar .env con tus credenciales de Azure
```

### 5. **Ejecutar la Aplicación**

```bash
python main.py
```

La aplicación estará disponible en: http://localhost:8000

## 🌐 **Endpoints de la API**

### **Base URL:** `http://localhost:8000/api/v1`

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/health` | GET | Estado del servicio | No |
| `/health/detailed` | GET | Estado detallado | No |
| `/health/ready` | GET | Verificación de preparación | No |
| `/documents/process` | POST | Procesar documento | JWT |
| `/documents/{job_id}/status` | GET | Estado del trabajo | JWT |
| `/documents/{job_id}/result` | GET | Resultado del trabajo | JWT |

### **Documentación Automática**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📊 **Ejemplo de Uso**

### **Procesar un Documento**

```bash
curl -X POST "http://localhost:8000/api/v1/documents/process" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "document_path": "https://sharepoint.com/documento.pdf",
    "processing_mode": "hybrid_consensus",
    "prompt_general": "Extrae información de esta factura",
    "fields": [
      {
        "name": "numero_factura",
        "type": "string",
        "description": "Número de la factura"
      }
    ]
  }'
```

## 🧪 **Testing**

### **Ejecutar Pruebas Unitarias**

```bash
pytest tests/unit/
```

### **Ejecutar Pruebas de Integración**

```bash
pytest tests/integration/
```

### **Ejecutar Todas las Pruebas**

```bash
pytest
```

## 🚀 **Despliegue en Azure**

### **Usando Bicep**

```bash
# Desplegar en desarrollo
az deployment group create \
  --resource-group your-rg \
  --template-file infrastructure/main.bicep \
  --parameters infrastructure/parameters/dev.parameters.json

# Desplegar en producción
az deployment group create \
  --resource-group your-rg \
  --template-file infrastructure/main.bicep \
  --parameters infrastructure/parameters/prod.parameters.json
```

### **Usando Docker**

```bash
# Construir imagen
docker build -t idp-expert-system .

# Ejecutar contenedor
docker run -p 8000:8000 idp-expert-system
```

## 📁 **Estructura del Proyecto**

```
idp-solution/
├── app/                    # Código principal de la aplicación
│   ├── api/               # Endpoints de la API
│   ├── core/              # Configuración central
│   ├── services/          # Lógica de negocio
│   ├── models/            # Modelos Pydantic
│   ├── schemas/           # Esquemas de base de datos
│   └── utils/             # Utilidades
├── infrastructure/         # Infraestructura como código (Bicep)
├── tests/                  # Pruebas unitarias y de integración
├── docs/                   # Documentación
├── scripts/                # Scripts de utilidad
└── .github/                # GitHub Actions (CI/CD)
```

## 🔒 **Seguridad**

- **Autenticación**: JWT con Azure AD
- **Autorización**: Roles basados en claims
- **Rate Limiting**: 1000 requests/min por cliente
- **CORS**: Configuración restrictiva
- **HTTPS**: Obligatorio en producción
- **Secrets**: Azure Key Vault

## 📈 **Monitoreo y Métricas**

- **Application Insights**: Telemetría completa
- **Logging**: Structured logging con Python
- **Métricas**: Performance counters personalizados
- **Alertas**: Azure Monitor
- **Health Checks**: Endpoints automáticos

## 🤝 **Contribución**

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 **Contacto y Soporte**

**Desarrollador Principal:** Ronald  
**Proyecto:** IDP Expert System  
**Organización:** Banco Caja Social  
**Email:** [tu-email@bancocajasocial.com.co]  
**Documentación:** [link-a-documentacion]  

## 🙏 **Agradecimientos**

- Equipo de Azure AI Services
- Comunidad de FastAPI
- Banco Caja Social por el apoyo al proyecto

---

**⭐ Si este proyecto te resulta útil, por favor dale una estrella en GitHub!**
