"""
Endpoint de verificación de salud del servicio IDP
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import os

router = APIRouter()


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
        # Información del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
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
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            },
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
