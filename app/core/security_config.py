"""
Configuración de seguridad para URLs externas y documentos
"""

from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import validator


class SecurityConfig(BaseSettings):
    """
    Configuración de seguridad para el procesamiento de documentos
    """
    
    # Dominios permitidos (lista blanca)
    ALLOWED_DOMAINS: List[str] = [
        # Microsoft Office 365 / SharePoint
        'sharepoint.com',
        'onedrive.live.com',
        'office.com',
        'microsoft.com',
        'outlook.com',
        'live.com',
        
        # Azure Storage
        'blob.core.windows.net',
        'storage.azure.com',
        'file.core.windows.net',
        
        # OneDrive Business
        'sharepoint.com',
        'office365.com',
        
        # Otros servicios de Microsoft
        'teams.microsoft.com',
        'portal.office.com',
        'admin.microsoft.com'
    ]
    
    # Dominios bloqueados (lista negra)
    BLOCKED_DOMAINS: List[str] = [
        # Dominios maliciosos conocidos
        'malicious.com',
        'phishing.net',
        'scam.org',
        'evil.com',
        'hack.com',
        'virus.com',
        'malware.net',
        
        # Dominios de phishing
        'phish.com',
        'fake.com',
        'spoof.net',
        'trick.com'
    ]
    
    # Extensiones de archivo peligrosas
    DANGEROUS_EXTENSIONS: List[str] = [
        # Ejecutables
        'exe', 'bat', 'cmd', 'com', 'pif',
        
        # Scripts
        'ps1', 'vbs', 'js', 'jse', 'wsf', 'wsh',
        
        # Java
        'jar', 'class',
        
        # Instaladores
        'msi', 'msu', 'msp',
        
        # Otros peligrosos
        'scr', 'hta', 'chm', 'hlp'
    ]
    
    # Configuración de timeouts y límites
    DOWNLOAD_TIMEOUT_SECONDS: int = 30
    MAX_FILE_SIZE_MB: int = 100
    MAX_REDIRECTS: int = 5
    
    # Configuración de validación de contenido
    ALLOW_LOCAL_URLS: bool = False
    ALLOW_PRIVATE_IPS: bool = False
    ALLOW_HTTP: bool = False
    
    # Configuración de logging de seguridad
    LOG_SECURITY_EVENTS: bool = True
    LOG_BLOCKED_ATTEMPTS: bool = True
    LOG_ALLOWED_ACCESS: bool = False
    
    # Configuración de rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_REQUESTS_PER_HOUR: int = 1000
    
    @validator('ALLOWED_DOMAINS', 'BLOCKED_DOMAINS', 'DANGEROUS_EXTENSIONS')
    def validate_lists(cls, v):
        """Validar que las listas no estén vacías"""
        if not v:
            raise ValueError('Las listas no pueden estar vacías')
        return v
    
    @validator('DOWNLOAD_TIMEOUT_SECONDS', 'MAX_FILE_SIZE_MB', 'MAX_REDIRECTS')
    def validate_positive_integers(cls, v):
        """Validar que los valores sean enteros positivos"""
        if v <= 0:
            raise ValueError('Los valores deben ser positivos')
        return v
    
    @validator('MAX_REQUESTS_PER_MINUTE', 'MAX_REQUESTS_PER_HOUR')
    def validate_rate_limits(cls, v):
        """Validar límites de rate limiting"""
        if v <= 0:
            raise ValueError('Los límites de rate limiting deben ser positivos')
        return v
    
    def is_domain_allowed(self, domain: str) -> bool:
        """
        Verificar si un dominio está permitido
        
        Args:
            domain: Dominio a verificar
            
        Returns:
            True si está permitido, False en caso contrario
        """
        domain_lower = domain.lower()
        
        # Verificar dominios bloqueados primero
        for blocked_domain in self.BLOCKED_DOMAINS:
            if blocked_domain in domain_lower:
                return False
        
        # Verificar dominios permitidos
        for allowed_domain in self.ALLOWED_DOMAINS:
            if allowed_domain in domain_lower:
                return True
        
        return False
    
    def is_extension_dangerous(self, extension: str) -> bool:
        """
        Verificar si una extensión de archivo es peligrosa
        
        Args:
            extension: Extensión del archivo
            
        Returns:
            True si es peligrosa, False en caso contrario
        """
        return extension.lower() in [ext.lower() for ext in self.DANGEROUS_EXTENSIONS]
    
    def get_security_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de la configuración de seguridad
        
        Returns:
            Dict con resumen de la configuración
        """
        return {
            'allowed_domains_count': len(self.ALLOWED_DOMAINS),
            'blocked_domains_count': len(self.BLOCKED_DOMAINS),
            'dangerous_extensions_count': len(self.DANGEROUS_EXTENSIONS),
            'download_timeout': f"{self.DOWNLOAD_TIMEOUT_SECONDS}s",
            'max_file_size': f"{self.MAX_FILE_SIZE_MB} MB",
            'max_redirects': self.MAX_REDIRECTS,
            'allow_local_urls': self.ALLOW_LOCAL_URLS,
            'allow_private_ips': self.ALLOW_PRIVATE_IPS,
            'allow_http': self.ALLOW_HTTP,
            'log_security_events': self.LOG_SECURITY_EVENTS,
            'rate_limiting': {
                'per_minute': self.MAX_REQUESTS_PER_MINUTE,
                'per_hour': self.MAX_REQUESTS_PER_HOUR
            }
        }


# Instancia global de configuración de seguridad
security_config = SecurityConfig()
