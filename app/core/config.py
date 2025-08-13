"""
Configuración centralizada de la aplicación IDP
"""

import logging
import sys
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno"""
    
    # ===========================================
    # CONFIGURACIÓN DE AZURE
    # ===========================================
    azure_subscription_id: str = ""
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    
    # ===========================================
    # AZURE OPENAI
    # ===========================================
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: str = "gpt-4-vision"
    
    # ===========================================
    # AZURE DOCUMENT INTELLIGENCE
    # ===========================================
    azure_document_intelligence_endpoint: str = ""
    azure_document_intelligence_api_key: str = ""
    
    # ===========================================
    # AZURE COSMOS DB
    # ===========================================
    azure_cosmos_endpoint: str = ""
    azure_cosmos_key: str = ""
    azure_cosmos_database: str = "idp-database"
    azure_cosmos_container: str = "documents"
    
    # ===========================================
    # AZURE STORAGE
    # ===========================================
    azure_storage_connection_string: str = ""
    azure_storage_account_name: str = ""
    azure_storage_account_key: str = ""
    azure_storage_container_bronze: str = "docs-para-procesar"
    azure_storage_queue_name: str = "idp-processing-queue"
    
    # ===========================================
    # AZURE KEY VAULT
    # ===========================================
    azure_key_vault_url: str = ""
    
    # ===========================================
    # CONFIGURACIÓN DE LA APLICACIÓN
    # ===========================================
    app_environment: str = "development"
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # ===========================================
    # CONFIGURACIÓN DE SEGURIDAD
    # ===========================================
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # ===========================================
    # CONFIGURACIÓN DE PROCESAMIENTO
    # ===========================================
    max_file_size_mb: int = 50
    sync_processing_threshold_mb: int = 10  # Cambiado a 10MB según requerimiento
    max_processing_time_seconds: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()


def setup_logging():
    """Configurar logging de la aplicación"""
    # Configurar formato del log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configurar nivel de log
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configurar logging básico
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("idp.log")
        ]
    )
    
    # Configurar logging específico para la aplicación
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    
    # Configurar logging para librerías externas
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Logging configurado correctamente")
    logger.info(f"📊 Nivel de log: {settings.log_level}")
    logger.info(f"🌍 Entorno: {settings.app_environment}")


def get_azure_credentials() -> dict:
    """Obtener credenciales de Azure para autenticación"""
    return {
        "subscription_id": settings.azure_subscription_id,
        "tenant_id": settings.azure_tenant_id,
        "client_id": settings.azure_client_id,
        "client_secret": settings.azure_client_secret
    }


def is_production() -> bool:
    """Verificar si estamos en entorno de producción"""
    return settings.app_environment.lower() == "production"


def get_cors_origins() -> List[str]:
    """Obtener orígenes CORS permitidos"""
    if is_production():
        # En producción, solo permitir orígenes específicos
        return [
            "https://your-app.azurewebsites.net",
            "https://your-power-app.powerapps.com"
        ]
    else:
        # En desarrollo, permitir localhost
        return ["http://localhost:3000", "http://localhost:8000"]


# Configurar logging al importar el módulo
setup_logging()
