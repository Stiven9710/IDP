# 🔒 Seguridad para URLs Externas - IDP Expert System

## 📋 **RESUMEN EJECUTIVO**

**Problema:** Las URLs de documentos que vienen de Power Automate pueden representar **vulnerabilidades de seguridad** si no se validan adecuadamente.

**Solución:** Sistema completo de **validación de seguridad** con lista blanca de dominios, bloqueo de extensiones peligrosas y timeouts de seguridad.

---

## 🚨 **RIESGOS DE SEGURIDAD IDENTIFICADOS**

### **🔴 Amenazas Principales:**

#### **1. URLs Maliciosas**
- **Phishing:** URLs que simulan sitios legítimos
- **Malware:** Descarga de archivos ejecutables
- **Scam:** Sitios fraudulentos para robo de datos

#### **2. Acceso No Autorizado**
- **Archivos privados** de otras organizaciones
- **Información sensible** expuesta públicamente
- **Recursos internos** accesibles externamente

#### **3. Ataques Técnicos**
- **SSRF (Server-Side Request Forgery):** Forzar al servidor a acceder a recursos internos
- **DoS (Denial of Service):** Consumo excesivo de recursos
- **Data Exfiltration:** Extracción no autorizada de datos

---

## 🛡️ **SOLUCIONES IMPLEMENTADAS**

### **1. 🔒 Lista Blanca de Dominios**

#### **✅ Dominios Permitidos (Microsoft/Azure):**
```
🌐 Microsoft Office 365 / SharePoint:
   - sharepoint.com
   - onedrive.live.com
   - office.com
   - microsoft.com
   - outlook.com
   - live.com

☁️ Azure Storage:
   - blob.core.windows.net
   - storage.azure.com
   - file.core.windows.net

🏢 OneDrive Business:
   - sharepoint.com
   - office365.com

🔧 Otros Servicios Microsoft:
   - teams.microsoft.com
   - portal.office.com
   - admin.microsoft.com
```

#### **🚫 Dominios Bloqueados (Lista Negra):**
```
🚨 Dominios Maliciosos Conocidos:
   - malicious.com
   - phishing.net
   - scam.org
   - evil.com
   - hack.com
   - virus.com
   - malware.net

🎣 Dominios de Phishing:
   - phish.com
   - fake.com
   - spoof.net
   - trick.com
```

### **2. ⚠️ Bloqueo de Extensiones Peligrosas**

#### **🚫 Extensiones Bloqueadas:**
```
💻 Ejecutables:
   - exe, bat, cmd, com, pif

📜 Scripts:
   - ps1, vbs, js, jse, wsf, wsh

☕ Java:
   - jar, class

📦 Instaladores:
   - msi, msu, msp

⚠️ Otros Peligrosos:
   - scr, hta, chm, hlp
```

### **3. ⏱️ Timeouts y Límites de Seguridad**

#### **🔒 Configuraciones de Seguridad:**
```
⏱️ Timeout de Descarga: 30 segundos
📏 Tamaño Máximo de Archivo: 100 MB
🔄 Máximo de Redirecciones: 5
🚦 Rate Limiting: 60/min, 1000/h
```

---

## 🏗️ **ARQUITECTURA DE SEGURIDAD**

### **📊 Flujo de Validación:**

```
1. 📥 Recibir URL del documento
   ↓
2. 🔍 Validar formato de URL
   ↓
3. 🌐 Extraer dominio
   ↓
4. 🚫 Verificar lista negra
   ↓
5. ✅ Verificar lista blanca
   ↓
6. 🏠 Verificar URLs locales/privadas
   ↓
7. 📏 Validar tamaño del archivo
   ↓
8. ⚠️ Verificar extensión del archivo
   ↓
9. ✅ Procesar documento seguro
```

### **🔧 Componentes de Seguridad:**

#### **1. SecurityConfig (`app/core/security_config.py`)**
- **Configuración centralizada** de seguridad
- **Validadores Pydantic** para configuración
- **Métodos de validación** reutilizables

#### **2. DocumentService (`app/services/document_service.py`)**
- **Integración** de validaciones de seguridad
- **Logging detallado** de eventos de seguridad
- **Manejo de errores** de seguridad

---

## 📝 **IMPLEMENTACIÓN TÉCNICA**

### **🔒 Configuración de Seguridad:**

```python
# app/core/security_config.py
class SecurityConfig(BaseSettings):
    # Dominios permitidos (lista blanca)
    ALLOWED_DOMAINS: List[str] = [
        'sharepoint.com',
        'onedrive.live.com',
        'blob.core.windows.net',
        # ... más dominios
    ]
    
    # Dominios bloqueados (lista negra)
    BLOCKED_DOMAINS: List[str] = [
        'malicious.com',
        'phishing.net',
        # ... más dominios
    ]
    
    # Extensiones peligrosas
    DANGEROUS_EXTENSIONS: List[str] = [
        'exe', 'bat', 'cmd', 'ps1', 'vbs'
        # ... más extensiones
    ]
    
    # Configuraciones de seguridad
    DOWNLOAD_TIMEOUT_SECONDS: int = 30
    MAX_FILE_SIZE_MB: int = 100
    MAX_REDIRECTS: int = 5
```

### **🛡️ Validación de URLs:**

```python
# app/services/document_service.py
async def validate_external_url(self, url: str) -> Dict[str, Any]:
    """
    Valida que la URL externa sea segura para procesar
    """
    try:
        # Verificar que sea una URL válida
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {'is_valid': False, 'reason': 'URL inválida'}
        
        # Verificar que sea HTTPS
        if parsed_url.scheme.lower() != 'https':
            return {'is_valid': False, 'reason': 'Protocolo no seguro'}
        
        # Extraer dominio
        domain = parsed_url.netloc.lower()
        
        # Verificar dominios permitidos/bloqueados
        if not self.security_config.is_domain_allowed(domain):
            return {'is_valid': False, 'reason': 'Dominio no permitido'}
        
        # Verificar URLs locales/privadas
        if any(private_ip in domain for private_ip in ['localhost', '127.0.0.1']):
            return {'is_valid': False, 'reason': 'URL local/privada'}
        
        return {'is_valid': True, 'reason': 'URL segura'}
        
    except Exception as e:
        return {'is_valid': False, 'reason': f'Error de validación: {str(e)}'}
```

### **🔍 Validación de Documentos:**

```python
async def validate_document_security(self, url: str, file_size_mb: float) -> Dict[str, Any]:
    """
    Valida la seguridad del documento antes del procesamiento
    """
    # Validar URL
    url_validation = await self.validate_external_url(url)
    if not url_validation['is_valid']:
        return url_validation
    
    # Validar tamaño del archivo
    if file_size_mb > self.security_config.MAX_FILE_SIZE_MB:
        return {
            'is_valid': False,
            'reason': 'Archivo demasiado grande'
        }
    
    # Validar extensión del archivo
    file_extension = url.lower().split('.')[-1] if '.' in url else ''
    if self.security_config.is_extension_dangerous(file_extension):
        return {
            'is_valid': False,
            'reason': 'Extensión peligrosa'
        }
    
    return {'is_valid': True, 'reason': 'Documento seguro'}
```

---

## 🚀 **INTEGRACIÓN EN EL FLUJO PRINCIPAL**

### **📥 Procesamiento de Documentos:**

```python
async def process_document(self, request: DocumentProcessingRequest):
    """
    Procesar un documento con validaciones de seguridad
    """
    try:
        # 🔒 VALIDACIÓN DE SEGURIDAD PARA URLs EXTERNAS
        logger.info("🔒 INICIANDO VALIDACIONES DE SEGURIDAD")
        
        # Validar formato del documento
        if not self._validate_document_format(str(request.document_path)):
            raise ValueError("Formato de documento no soportado")
        
        # Obtener tamaño del archivo
        file_size_mb = await self._get_document_size(str(request.document_path))
        
        # Validar seguridad del documento (URL + tamaño + extensión)
        security_validation = await self.validate_document_security(
            str(request.document_path), 
            file_size_mb
        )
        
        if not security_validation['is_valid']:
            logger.error(f"🚫 VALIDACIÓN DE SEGURIDAD FALLIDA: {security_validation['reason']}")
            raise ValueError(f"Documento rechazado por seguridad: {security_validation['reason']}")
        
        logger.info(f"✅ VALIDACIÓN DE SEGURIDAD EXITOSA")
        
        # Continuar con el procesamiento...
        
    except Exception as e:
        logger.error(f"❌ Error en el procesamiento: {str(e)}")
        raise
```

---

## 📊 **LOGGING Y MONITOREO DE SEGURIDAD**

### **🔍 Eventos Registrados:**

#### **✅ Accesos Permitidos:**
```
🔒 Validando seguridad de URL: https://company.sharepoint.com/document.pdf
🌐 Dominio extraído: company.sharepoint.com
✅ Dominio permitido: company.sharepoint.com
✅ URL validada exitosamente
✅ Documento validado como seguro
```

#### **🚫 Accesos Bloqueados:**
```
🔒 Validando seguridad de URL: https://malicious.com/file.exe
🌐 Dominio extraído: malicious.com
🚫 Dominio bloqueado o no permitido: malicious.com
🚫 VALIDACIÓN DE SEGURIDAD FALLIDA: Dominio no permitido
```

### **📈 Métricas de Seguridad:**

```python
def get_security_summary(self) -> Dict[str, Any]:
    """
    Obtener resumen de la configuración de seguridad
    """
    return {
        'allowed_domains_count': len(self.ALLOWED_DOMAINS),
        'blocked_domains_count': len(self.BLOCKED_DOMAINS),
        'dangerous_extensions_count': len(self.DANGEROUS_EXTENSIONS),
        'download_timeout': f"{self.DOWNLOAD_TIMEOUT_SECONDS}s",
        'max_file_size': f"{self.MAX_FILE_SIZE_MB} MB",
        'max_redirects': self.MAX_REDIRECTS,
        'rate_limiting': {
            'per_minute': self.MAX_REQUESTS_PER_MINUTE,
            'per_hour': self.MAX_REQUESTS_PER_HOUR
        }
    }
```

---

## ⚙️ **CONFIGURACIÓN Y PERSONALIZACIÓN**

### **🔧 Variables de Entorno:**

```bash
# .env
# Dominios permitidos (separados por comas)
ALLOWED_DOMAINS=sharepoint.com,onedrive.live.com,blob.core.windows.net

# Dominios bloqueados (separados por comas)
BLOCKED_DOMAINS=malicious.com,phishing.net,scam.org

# Extensiones peligrosas (separadas por comas)
DANGEROUS_EXTENSIONS=exe,bat,cmd,ps1,vbs,js

# Configuraciones de seguridad
DOWNLOAD_TIMEOUT_SECONDS=30
MAX_FILE_SIZE_MB=100
MAX_REDIRECTS=5
MAX_REQUESTS_PER_MINUTE=60
MAX_REQUESTS_PER_HOUR=1000
```

### **📋 Personalización de Dominios:**

#### **Para Organizaciones Específicas:**
```python
# Agregar dominios corporativos
ALLOWED_DOMAINS = [
    'sharepoint.com',
    'onedrive.live.com',
    'company.com',           # Dominio corporativo
    'internal.company.com',  # Subdominio interno
    'docs.company.com'       # Servidor de documentos
]
```

#### **Para Entornos de Desarrollo:**
```python
# Permitir URLs locales en desarrollo
ALLOW_LOCAL_URLS = True
ALLOW_PRIVATE_IPS = True
ALLOW_HTTP = True  # Solo en desarrollo
```

---

## 🧪 **PRUEBAS DE SEGURIDAD**

### **✅ Casos de Prueba Positivos:**

#### **1. URLs Válidas de Microsoft:**
```
✅ https://company.sharepoint.com/document.pdf
✅ https://onedrive.live.com/file.docx
✅ https://storage.blob.core.windows.net/container/file.pptx
```

#### **2. Archivos Seguros:**
```
✅ Documentos: PDF, DOCX, PPTX, XLSX
✅ Imágenes: JPG, PNG, GIF, BMP
✅ Texto: TXT, RTF, MD
```

### **❌ Casos de Prueba Negativos:**

#### **1. URLs Maliciosas:**
```
❌ https://malicious.com/file.exe
❌ https://phishing.net/document.pdf
❌ http://evil.com/file.bat
```

#### **2. Archivos Peligrosos:**
```
❌ https://sharepoint.com/file.exe
❌ https://onedrive.com/script.ps1
❌ https://microsoft.com/virus.bat
```

#### **3. URLs Locales/Privadas:**
```
❌ http://localhost/document.pdf
❌ https://192.168.1.100/file.docx
❌ https://10.0.0.1/document.pptx
```

---

## 🚨 **RESPUESTA A INCIDENTES**

### **🔍 Detección de Amenazas:**

#### **1. URLs Bloqueadas:**
```
🚫 Dominio bloqueado detectado: malicious.com
🚫 VALIDACIÓN DE SEGURIDAD FALLIDA: Dominio no permitido
📋 Detalles: El dominio malicious.com no está en la lista blanca o está bloqueado
```

#### **2. Archivos Peligrosos:**
```
🚫 Extensión peligrosa detectada: exe
🚫 VALIDACIÓN DE SEGURIDAD FALLIDA: Extensión peligrosa
📋 Detalles: No se permiten archivos con extensión exe
```

#### **3. Archivos Demasiado Grandes:**
```
⚠️ Archivo demasiado grande: 150.00 MB > 100 MB
🚫 VALIDACIÓN DE SEGURIDAD FALLIDA: Archivo demasiado grande
📋 Detalles: El archivo excede el tamaño máximo permitido: 150.00 MB > 100 MB
```

### **📊 Acciones de Respuesta:**

#### **1. Bloqueo Inmediato:**
- **Rechazar** el documento
- **Registrar** el intento de acceso
- **Notificar** al equipo de seguridad

#### **2. Logging Detallado:**
- **Timestamp** del intento
- **URL** del documento
- **IP** de origen
- **Usuario** que realizó la petición

#### **3. Análisis Post-Incidente:**
- **Revisar** logs de seguridad
- **Identificar** patrones de ataque
- **Actualizar** listas de dominios

---

## 🔄 **MANTENIMIENTO Y ACTUALIZACIONES**

### **📅 Tareas Periódicas:**

#### **1. Revisión Mensual:**
- **Actualizar** lista de dominios bloqueados
- **Revisar** logs de seguridad
- **Analizar** intentos de acceso bloqueados

#### **2. Revisión Trimestral:**
- **Evaluar** dominios permitidos
- **Revisar** extensiones peligrosas
- **Actualizar** configuraciones de timeout

#### **3. Revisión Anual:**
- **Auditoría** completa de seguridad
- **Revisión** de políticas de acceso
- **Actualización** de procedimientos

### **🔧 Actualización de Configuración:**

```python
# Agregar nuevo dominio malicioso
BLOCKED_DOMAINS.append('new-malicious.com')

# Agregar nueva extensión peligrosa
DANGEROUS_EXTENSIONS.append('new-dangerous')

# Actualizar timeout de descarga
DOWNLOAD_TIMEOUT_SECONDS = 45

# Aplicar cambios
security_config = SecurityConfig()
```

---

## 📚 **MEJORES PRÁCTICAS**

### **🛡️ Recomendaciones de Seguridad:**

#### **1. Lista Blanca Estricta:**
- **Solo permitir** dominios conocidos y confiables
- **Revisar regularmente** la lista de dominios permitidos
- **Documentar** el propósito de cada dominio

#### **2. Monitoreo Continuo:**
- **Revisar logs** de seguridad diariamente
- **Configurar alertas** para intentos bloqueados
- **Analizar patrones** de acceso sospechoso

#### **3. Actualización Regular:**
- **Mantener actualizadas** las listas de dominios
- **Revisar** nuevas amenazas de seguridad
- **Actualizar** configuraciones según sea necesario

### **🚫 Lo que NO hacer:**

#### **1. Permitir URLs HTTP:**
```
❌ http://sharepoint.com/document.pdf
✅ https://sharepoint.com/document.pdf
```

#### **2. Permitir Dominios Desconocidos:**
```
❌ https://unknown-domain.com/file.pdf
✅ https://sharepoint.com/file.pdf
```

#### **3. Ignorar Extensiones Peligrosas:**
```
❌ Procesar archivos .exe, .bat, .ps1
✅ Solo procesar documentos seguros
```

---

## 🎯 **CONCLUSIONES**

### **💪 Beneficios de la Implementación:**

1. **🔒 Seguridad Garantizada:** Solo URLs de dominios confiables
2. **🚫 Bloqueo Proactivo:** Prevención de amenazas conocidas
3. **📊 Monitoreo Completo:** Logging detallado de eventos de seguridad
4. **⚙️ Configuración Flexible:** Fácil personalización según necesidades
5. **🔄 Mantenimiento Sencillo:** Actualización centralizada de configuraciones

### **🚀 Recomendaciones Finales:**

1. **Implementar** todas las validaciones de seguridad
2. **Configurar** listas de dominios según la organización
3. **Monitorear** continuamente los logs de seguridad
4. **Actualizar** regularmente las configuraciones
5. **Documentar** todos los cambios de seguridad

---

## 📞 **SOPORTE Y CONTACTO**

### **🆘 Problemas Comunes:**

- **URL bloqueada:** Verificar lista de dominios permitidos
- **Archivo rechazado:** Verificar extensión y tamaño
- **Timeout de descarga:** Ajustar configuración de timeout

### **📧 Contacto:**

- **Equipo de Desarrollo:** IDP Expert System
- **Repositorio:** [GitHub IDP](https://github.com/Stiven9710/IDP)
- **Documentación:** Carpeta `docs/`

---

**📅 Última Actualización:** $(date +"%d/%m/%Y")  
**🔧 Versión del Documento:** 1.0  
**👨‍💻 Mantenido por:** Equipo IDP Expert System  

---

*"La seguridad no es un producto, es un proceso continuo de protección y mejora."* 🛡️✨
