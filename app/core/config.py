"""
Configuración centralizada de la aplicación IDP
"""

import logging
import sys
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Entorno
    environment: str = "development"
    log_level: str = "INFO"
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment_name: str = "gpt-4o"
    azure_openai_api_version: str = "2025-01-01-preview"
    
    # Azure Document Intelligence
    azure_document_intelligence_endpoint: str
    azure_document_intelligence_api_key: str
    
    # Azure Cosmos DB
    azure_cosmos_endpoint: str = ""
    azure_cosmos_key: str = ""
    azure_cosmos_database_name: str = "idp-database"
    azure_cosmos_container_documents: str = "documents"
    azure_cosmos_container_extractions: str = "extractions"
    azure_cosmos_container_jobs: str = "processing_jobs"
    
    # Azure Storage (Blob y Queue)
    azure_storage_connection_string: Optional[str] = None
    azure_storage_account_name: Optional[str] = None
    azure_storage_account_key: Optional[str] = None
    azure_storage_queue_name: str = "document-processing"
    
    # Configuración específica de Blob Storage
    azure_blob_retry_delay_seconds: int = 5  # Retraso optimizado antes de descargar
    azure_blob_max_retries: int = 3  # Máximo de reintentos
    azure_blob_retry_backoff_factor: float = 1.5  # Factor de crecimiento optimizado
    
    # Configuración del sistema
    sync_processing_threshold_mb: int = 10
    max_processing_time_seconds: int = 300
    max_file_size_mb: int = 50

    # Configuración de CORS
    cors_origins: List[str] = ["*"]
    
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
    logger.info(f"🌍 Entorno: {settings.environment}")


def is_production() -> bool:
    """Verificar si estamos en entorno de producción"""
    return settings.environment.lower() == "production"


def get_cors_origins() -> List[str]:
    """Obtener orígenes CORS permitidos"""
    if is_production():
        # En producción, solo permitir orígenes específicos
        return [
            "https://your-app.azurewebsites.net",
            "https://your-power-app.powerapps.com"
        ]
    else:
        # En desarrollo, permitir 159.203.149.247
        return ["http://159.203.149.247:3000", "http://159.203.149.247:8000"]


# Configurar logging al importar el módulo
setup_logging()
