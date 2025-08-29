# 📚 Documentación IDP Expert System

## 🎯 **Descripción General**

Esta carpeta contiene toda la documentación necesaria para entender, implementar y mantener el sistema IDP Expert System. La documentación está organizada por temas y niveles de experiencia.

---

## 📋 **Índice de Documentación**

### **🚀 🐳 DESPLIEGUE LOCAL (DOCKER)**

#### **📖 Guía Principal de Despliegue**
- **`Guia_Despliegue_Local_Docker.md`** - Guía completa paso a paso para desplegar la API en Docker local
- **`quick-start-docker.sh`** - Script automatizado para despliegue rápido
- **`env.example`** - Archivo de ejemplo para configuración de variables de entorno

**🎯 Para quién es:**
- Desarrolladores que quieren probar la API localmente
- DevOps que necesitan configurar entornos de desarrollo
- Usuarios que quieren entender cómo funciona Docker

**⏱️ Tiempo estimado:** 15-30 minutos

---

### **🏗️ 🏛️ ARQUITECTURA Y IMPLEMENTACIÓN**

#### **📖 Guía Técnica**
- **`Guia_Tecnica_Implementacion.md`** - Arquitectura técnica detallada del sistema
- **`Documentacion_Funcional_API.md`** - Funcionalidades y endpoints de la API

**🎯 Para quién es:**
- Arquitectos de software
- Desarrolladores senior
- DevOps engineers
- Técnicos que necesitan entender el sistema

**⏱️ Tiempo estimado:** 45-60 minutos

---

### **☁️ 🚀 DESPLIEGUE EN AZURE**

#### **📖 Guía de Azure**
- **`GUIA_DESPLIEGUE_DOCKER_AZURE.md`** - Despliegue completo en Azure (ACI, App Service)

**🎯 Para quién es:**
- DevOps engineers
- Arquitectos de nube
- Equipos de infraestructura
- Desarrolladores que quieren desplegar en producción

**⏱️ Tiempo estimado:** 60-90 minutos

---

### **📁 📂 CARPETAS ESPECIALIZADAS**

#### **📖 `api-specs/`**
- Especificaciones técnicas de la API
- Documentación OpenAPI/Swagger
- Ejemplos de requests/responses

#### **📖 `deployment-guide/`**
- Guías de despliegue avanzadas
- Configuraciones de producción
- Monitoreo y alertas

#### **📖 `user-manual/`**
- Manual de usuario final
- Tutoriales de uso
- Casos de uso comunes

---

## 🎯 **RUTA DE APRENDIZAJE RECOMENDADA**

### **🆕 Para Principiantes:**
1. **`Guia_Despliegue_Local_Docker.md`** - Entender cómo funciona localmente
2. **`Documentacion_Funcional_API.md`** - Conocer las funcionalidades
3. **`quick-start-docker.sh`** - Desplegar rápidamente

### **🔄 Para Desarrolladores:**
1. **`Guia_Tecnica_Implementacion.md`** - Entender la arquitectura
2. **`Guia_Despliegue_Local_Docker.md`** - Configurar entorno de desarrollo
3. **`api-specs/`** - Explorar endpoints y funcionalidades

### **🚀 Para DevOps/Producción:**
1. **`GUIA_DESPLIEGUE_DOCKER_AZURE.md`** - Desplegar en Azure
2. **`deployment-guide/`** - Configuraciones avanzadas
3. **`Guia_Tecnica_Implementacion.md`** - Entender la infraestructura

---

## 🛠️ **HERRAMIENTAS Y SCRIPTS**

### **🐳 Scripts de Docker:**
- **`quick-start-docker.sh`** - Despliegue automatizado local
- **`docker-deploy.sh`** (en raíz) - Script principal de Docker

### **📋 Archivos de Configuración:**
- **`env.example`** - Variables de entorno de ejemplo
- **`docker-compose.yml`** (en raíz) - Orquestación de servicios
- **`Dockerfile`** (en raíz) - Imagen de la aplicación

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **❓ Problemas Comunes:**
1. **Docker no inicia** → Ver `Guia_Despliegue_Local_Docker.md#problemas-comunes`
2. **API no responde** → Ver logs con `docker-compose logs -f`
3. **Error de Azure** → Verificar archivo `.env` y credenciales

### **🔍 Comandos de Diagnóstico:**
```bash
# Ver estado de contenedores
docker ps

# Ver logs en tiempo real
docker-compose logs -f

# Verificar health check
curl http://localhost:8000/health

# Ver configuración de Docker Compose
docker-compose config
```

---

## 📞 **SOPORTE Y AYUDA**

### **📧 Contacto:**
- **Desarrollador Principal**: Ronald Estiven Rios Hernandez
- **Organización**: Banco Caja Social
- **Proyecto**: IDP Expert System

### **🔗 Enlaces Útiles:**
- **Repositorio**: https://github.com/Stiven9710/IDP
- **Documentación Azure**: https://docs.microsoft.com/en-us/azure/
- **Docker Documentation**: https://docs.docker.com/

---

## 📝 **CONTRIBUCIÓN A LA DOCUMENTACIÓN**

### **✏️ Cómo Contribuir:**
1. **Identificar** áreas que necesiten documentación
2. **Crear** o **actualizar** archivos Markdown
3. **Mantener** consistencia en el formato
4. **Probar** los pasos documentados

### **📋 Estándares de Documentación:**
- Usar **Markdown** para todos los archivos
- Incluir **emojis** para mejor legibilidad
- Mantener **estructura clara** con headers
- Incluir **ejemplos prácticos** y **comandos**
- Documentar **problemas comunes** y **soluciones**

---

## 🎉 **¡DOCUMENTACIÓN COMPLETA!**

### **✅ Lo que tienes disponible:**
- **🐳 Despliegue local** con Docker
- **🏗️ Arquitectura técnica** completa
- **☁️ Despliegue en Azure** paso a paso
- **🧪 Scripts automatizados** para facilitar el proceso
- **📋 Ejemplos de configuración** listos para usar

### **🚀 Próximos pasos:**
1. **Elegir** tu ruta de aprendizaje
2. **Seguir** las guías paso a paso
3. **Probar** en tu entorno local
4. **Contribuir** mejorando la documentación

---

**¡Bienvenido al sistema IDP Expert System!** 🎉📚✨

**La documentación está diseñada para que puedas implementar y usar el sistema de manera efectiva, sin importar tu nivel de experiencia.** 🚀
