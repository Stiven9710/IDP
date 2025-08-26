"""
Endpoint de verificación de salud del servicio IDP
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def health_check():
    """Verificación básica de salud del servicio"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "IDP Expert System",
        "version": "2.0.0"
    }


@router.get("/detailed")
async def detailed_health_check():
    """Verificación detallada de salud del servicio"""
    try:
        # Verificar variables de entorno críticas
        critical_env_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_COSMOS_ENDPOINT",
            "AZURE_STORAGE_CONNECTION_STRING"
        ]
        
        env_status = {}
        for var in critical_env_vars:
            env_status[var] = "configured" if os.getenv(var) else "missing"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "IDP Expert System",
            "version": "2.0.0",
            "environment": env_status
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en verificación de salud: {str(e)}"
        )


@router.get("/ready")
async def readiness_check():
    """Verificación de preparación del servicio para recibir tráfico"""
    # Aquí podrías agregar verificaciones de conectividad a servicios externos
    # como Azure Cosmos DB, Azure Storage, etc.
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Servicio listo para recibir tráfico"
    }


@router.get("/cosmos")
async def cosmos_health_check():
    """Verificar salud de Cosmos DB"""
    try:
        from app.services.cosmos_service import CosmosService
        
        cosmos_service = CosmosService()
        health_status = await cosmos_service.health_check()
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Error verificando salud de Cosmos DB: {str(e)}")
        return {
            "status": "error",
            "message": f"Error verificando Cosmos DB: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/blob-storage")
async def blob_storage_health():
    """Verificar salud del servicio de Blob Storage"""
    try:
        from app.services.blob_storage_service import BlobStorageService
        
        blob_service = BlobStorageService()
        health_status = await blob_service.health_check()
        
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Error verificando Blob Storage: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/queue-storage")
async def queue_storage_health():
    """Verificar salud del servicio de Queue Storage"""
    try:
        from app.services.queue_storage_service import QueueStorageService
        
        queue_service = QueueStorageService()
        health_status = await queue_service.health_check()
        
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Error verificando Queue Storage: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/storage")
async def storage_health():
    """Verificar salud de todos los servicios de Storage"""
    try:
        from app.services.blob_storage_service import BlobStorageService
        from app.services.queue_storage_service import QueueStorageService
        
        # Verificar Blob Storage
        blob_service = BlobStorageService()
        blob_health = await blob_service.health_check()
        
        # Verificar Queue Storage
        queue_service = QueueStorageService()
        queue_health = await queue_service.health_check()
        
        # Determinar estado general
        overall_status = "healthy"
        if blob_health.get("status") != "healthy" or queue_health.get("status") != "healthy":
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "blob_storage": blob_health,
                "queue_storage": queue_health
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Error verificando servicios de Storage: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
