# 📚 ÍNDICE DE CATÁLOGOS DE DATOS - IDP EXPERT SYSTEM

## 🎯 **DESCRIPCIÓN GENERAL**
Este índice proporciona una visión general de todos los catálogos de datos y documentación técnica del sistema IDP Expert System, facilitando la navegación y consulta de la información.

---

## 📋 **CATÁLOGOS DE DATOS PRINCIPALES**

### **1. 📊 [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md)**
**Descripción**: Documenta la estructura y contenido de los datos de extracciones principales almacenados en Azure Cosmos DB.

**Contenido**:
- Estructura de la tabla `extractions`
- Campos extraídos (`extraction_data`)
- Tipos de campos soportados
- Campos comunes por tipo de documento
- Estructuras de datos complejas
- Puntuaciones de confianza
- Estrategias de procesamiento
- Metadatos de procesamiento
- Códigos de error y estados
- Métricas y estadísticas
- Consideraciones de seguridad

**Audiencia**: Desarrolladores, analistas de datos, administradores de sistema

---

### **2. 📦 [Catálogo de Tabla de Productos](./Catalogo_Datos_Tabla_Productos.md)**
**Descripción**: Documenta la estructura y contenido de la tabla de productos expandida, que contiene los items de línea individuales extraídos de facturas.

**Contenido**:
- Estructura de la tabla `products_table`
- Detalles de campos
- Tipos de productos comunes
- Validaciones y reglas de negocio
- Métricas y estadísticas
- Relaciones con otras tablas
- Vistas y consultas comunes
- Códigos de error específicos
- Consideraciones de seguridad

**Audiencia**: Analistas de datos, desarrolladores, usuarios de negocio

---

### **3. 🗄️ [Modelo de Datos Completo](./Modelo_Datos_Completo.md)**
**Descripción**: Presenta el modelo de datos completo del sistema, incluyendo todas las entidades, relaciones y restricciones.

**Contenido**:
- Arquitectura de datos
- Entidades principales
- Estructuras de datos detalladas
- Relaciones entre entidades
- Índices y optimización
- Restricciones y validaciones
- Métricas y monitoreo
- Seguridad y privacidad
- Migraciones y versionado
- Escalabilidad y rendimiento

**Audiencia**: Arquitectos de datos, desarrolladores senior, administradores de base de datos

---

### **4. ⚙️ [Catálogo de Metadatos y Configuraciones](./Catalogo_Datos_Metadatos_Configuraciones.md)**
**Descripción**: Documenta la estructura y contenido de los metadatos y configuraciones del sistema.

**Contenido**:
- Estructura de metadatos
- Configuraciones de procesamiento
- Configuraciones de seguridad
- Configuraciones de persistencia
- Configuraciones de monitoreo
- Configuraciones de alertas
- Configuraciones de procesamiento asíncrono

**Audiencia**: Administradores de sistema, desarrolladores, operadores

---

## 🔍 **GUÍAS DE NAVEGACIÓN**

### **📊 Por Tipo de Usuario**

#### **👨‍💻 Desarrolladores**
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Para entender la arquitectura
- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Para trabajar con datos
- [Catálogo de Metadatos y Configuraciones](./Catalogo_Datos_Metadatos_Configuraciones.md) - Para configurar el sistema

#### **📈 Analistas de Datos**
- [Catálogo de Tabla de Productos](./Catalogo_Datos_Tabla_Productos.md) - Para análisis de productos
- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Para análisis de extracciones
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Para consultas complejas

#### **🔧 Administradores de Sistema**
- [Catálogo de Metadatos y Configuraciones](./Catalogo_Datos_Metadatos_Configuraciones.md) - Para configurar el sistema
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Para optimización y mantenimiento
- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Para monitoreo

#### **👥 Usuarios de Negocio**
- [Catálogo de Tabla de Productos](./Catalogo_Datos_Tabla_Productos.md) - Para entender los datos de productos
- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Para entender los datos extraídos

### **🎯 Por Tipo de Tarea**

#### **🔍 Consultas y Análisis**
- [Catálogo de Tabla de Productos](./Catalogo_Datos_Tabla_Productos.md) - Vistas y consultas comunes
- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Estructura de datos
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Relaciones entre entidades

#### **⚙️ Configuración y Administración**
- [Catálogo de Metadatos y Configuraciones](./Catalogo_Datos_Metadatos_Configuraciones.md) - Configuraciones del sistema
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Índices y optimización

#### **🚨 Monitoreo y Alertas**
- [Catálogo de Metadatos y Configuraciones](./Catalogo_Datos_Metadatos_Configuraciones.md) - Configuraciones de alertas
- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Códigos de error
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Métricas y monitoreo

#### **🔒 Seguridad y Privacidad**
- [Catálogo de Metadatos y Configuraciones](./Catalogo_Datos_Metadatos_Configuraciones.md) - Configuraciones de seguridad
- [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Consideraciones de seguridad
- [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Datos sensibles

---

## 📊 **DIAGRAMA DE RELACIONES**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CATÁLOGOS DE DATOS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   EXTRACTIONS   │    │    PRODUCTS     │    │    JOBS     │ │
│  │                 │    │                 │    │             │ │
│  │ • Estructura    │◄───┤ • Estructura    │    │ • Estructura│ │
│  │ • Campos        │    │ • Validaciones  │    │ • Estados   │ │
│  │ • Tipos         │    │ • Relaciones    │    │ • Configs   │ │
│  │ • Validaciones  │    │ • Consultas     │    │ • Métricas  │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                       │                       │     │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              MODELO DE DATOS COMPLETO                      │ │
│  │                                                             │ │
│  │ • Arquitectura general                                      │ │
│  │ • Relaciones entre entidades                               │ │
│  │ • Índices y optimización                                   │ │
│  │ • Restricciones y validaciones                             │ │
│  │ • Escalabilidad y rendimiento                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           METADATOS Y CONFIGURACIONES                      │ │
│  │                                                             │ │
│  │ • Configuraciones de procesamiento                         │ │
│  │ • Configuraciones de seguridad                             │ │
│  │ • Configuraciones de persistencia                          │ │
│  │ • Configuraciones de monitoreo                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 **GUÍAS DE INICIO RÁPIDO**

### **🆕 Nuevo en el Sistema**
1. **Leer**: [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Para entender la arquitectura general
2. **Revisar**: [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Para entender los datos principales
3. **Configurar**: [Catálogo de Metadatos y Configuraciones](./Catalogo_Datos_Metadatos_Configuraciones.md) - Para configurar el sistema

### **📊 Análisis de Datos**
1. **Revisar**: [Catálogo de Tabla de Productos](./Catalogo_Datos_Tabla_Productos.md) - Para análisis de productos
2. **Consultar**: [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Para análisis de extracciones
3. **Optimizar**: [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Para consultas complejas

### **🔧 Administración del Sistema**
1. **Configurar**: [Catálogo de Metadatos y Configuraciones](./Catalogo_Datos_Metadatos_Configuraciones.md) - Para configuraciones
2. **Monitorear**: [Modelo de Datos Completo](./Modelo_Datos_Completo.md) - Para métricas y alertas
3. **Mantener**: [Catálogo de Extracciones Principales](./Catalogo_Datos_Extracciones_Principales.md) - Para códigos de error

---

## 📚 **DOCUMENTACIÓN RELACIONADA**

### **🔗 Enlaces Internos**
- [Documentación Funcional de la API](./Documentacion_Funcional_API.md)
- [Guía Técnica de Implementación](./Guia_Tecnica_Implementacion.md)
- [Guía de Despliegue Local con Docker](./Guia_Despliegue_Local_Docker.md)
- [Funcionalidad de Persistencia de Documentos](./Funcionalidad_Persistencia_Documentos.md)
- [Seguridad de URLs Externas](./Seguridad_URLs_Externas.md)

### **🌐 Enlaces Externos**
- [Documentación de Azure Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [Documentación de Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Documentación de Azure Queue Storage](https://docs.microsoft.com/en-us/azure/storage/queues/)
- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Pydantic](https://pydantic-docs.helpmanual.io/)

---

## 🔄 **ACTUALIZACIONES Y VERSIONADO**

### **📅 Historial de Versiones**
- **v1.0.0** (2024-01-08): Versión inicial con todos los catálogos
- **v1.1.0** (Próxima): Agregar catálogo de logs y auditoría
- **v1.2.0** (Próxima): Agregar catálogo de métricas de rendimiento

### **🔄 Proceso de Actualización**
1. **Revisión**: Los catálogos se revisan mensualmente
2. **Actualización**: Se actualizan cuando hay cambios en el sistema
3. **Versionado**: Se mantiene un historial de versiones
4. **Notificación**: Se notifica a los usuarios sobre cambios importantes

---

## 📞 **CONTACTO Y SOPORTE**

### **👥 Equipo de Desarrollo**
- **Arquitecto de Datos**: [nombre@empresa.com]
- **Desarrollador Principal**: [nombre@empresa.com]
- **Administrador de Sistema**: [nombre@empresa.com]

### **📧 Canales de Comunicación**
- **Issues**: [GitHub Issues](https://github.com/empresa/idp-expert-system/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/empresa/idp-expert-system/discussions)
- **Email**: [soporte@empresa.com]

---

**📅 Última actualización**: 2024-01-08  
**👤 Mantenido por**: Equipo de Desarrollo API IDP Expert System  
**🔄 Versión**: 1.0.0
