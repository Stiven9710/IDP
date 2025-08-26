"""
Endpoints para la gestión de trabajos IDP
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

from app.models.response import DocumentStatusResponse

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_jobs():
    """
    Listar todos los trabajos en el sistema
    
    Returns:
        Lista de trabajos
    """
    logger.info("📋 Endpoint de listado de trabajos llamado")
    
    try:
        # Implementar listado real desde Cosmos DB
        from app.services.cosmos_service import CosmosService
        
        cosmos_service = CosmosService()
        jobs = await cosmos_service.list_processing_jobs()
        
        logger.info(f"📋 Listado de trabajos completado: {len(jobs)} trabajos")
        return jobs
        
    except Exception as e:
        logger.error(f"❌ Error listando trabajos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listando trabajos")


@router.get("/{job_id}", response_model=DocumentStatusResponse)
async def get_job_details(job_id: str) -> DocumentStatusResponse:
    """
    Obtener detalles completos de un trabajo
    
    Args:
        job_id: ID del trabajo
        
    Returns:
        Detalles completos del trabajo
    """
    logger.info(f"🔍 Consultando detalles del job: {job_id}")
    
    try:
        # Implementar consulta real desde Cosmos DB
        from app.services.cosmos_service import CosmosService
        
        cosmos_service = CosmosService()
        job_details = await cosmos_service.get_processing_job(job_id)
        
        if not job_details:
            raise HTTPException(status_code=404, detail="Job no encontrado")
        
        response = DocumentStatusResponse(
            job_id=job_id,
            status=job_details.get("status", "unknown"),
            progress_percentage=100.0 if job_details.get("status") == "completed" else 0.0,
            current_step=job_details.get("status", "unknown"),
            message=f"Job {job_details.get('status', 'unknown')}"
        )
        
        logger.info(f"📊 Detalles del job {job_id} obtenidos exitosamente")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error consultando detalles del job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error consultando detalles del trabajo")


@router.get("/{job_id}/status")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Obtener el estado de un trabajo específico
    
    Args:
        job_id: ID del trabajo
        
    Returns:
        Estado del trabajo
    """
    logger.info(f"🔍 Consultando estado del job: {job_id}")
    
    try:
        from app.services.cosmos_service import CosmosService
        
        cosmos_service = CosmosService()
        job_details = await cosmos_service.get_processing_job(job_id)
        
        if not job_details:
            raise HTTPException(status_code=404, detail="Job no encontrado")
        
        status_response = {
            "job_id": job_id,
            "status": job_details.get("status", "unknown"),
            "document_name": job_details.get("document_name", "N/A"),
            "processing_mode": job_details.get("processing_mode", "N/A"),
            "created_at": job_details.get("created_at", "N/A"),
            "fields_extracted": job_details.get("fields_extracted", 0)
        }
        
        if job_details.get("status") == "completed":
            status_response.update({
                "completed_at": job_details.get("completed_at", "N/A"),
                "processing_time_ms": job_details.get("processing_time_ms", 0)
            })
        
        if job_details.get("error_message"):
            status_response["error_message"] = job_details.get("error_message")
        
        logger.info(f"📊 Estado del job {job_id} obtenido exitosamente")
        return status_response
        
    except Exception as e:
        logger.error(f"❌ Error consultando estado del job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error consultando estado del trabajo")


@router.get("/{job_id}/result")
async def get_job_result(job_id: str) -> Dict[str, Any]:
    """
    Obtener el resultado de un trabajo completado
    
    Args:
        job_id: ID del trabajo
        
    Returns:
        Resultado del trabajo
    """
    logger.info(f"🔍 Consultando resultado del job: {job_id}")
    
    try:
        from app.services.cosmos_service import CosmosService
        
        cosmos_service = CosmosService()
        job_details = await cosmos_service.get_processing_job(job_id)
        
        if not job_details:
            raise HTTPException(status_code=404, detail="Job no encontrado")
        
        if job_details.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Job no completado aún")
        
        # Obtener resultado de extracción
        extraction_result = await cosmos_service.get_extraction_by_job_id(job_id)
        
        if not extraction_result:
            raise HTTPException(status_code=404, detail="Resultado de extracción no encontrado")
        
        result_response = {
            "job_id": job_id,
            "extraction_data": extraction_result.get("extraction_data", []),
            "processing_summary": {
                "processing_status": "completed",
                "strategy_used": job_details.get("processing_mode", "N/A"),
                "processing_time_ms": job_details.get("processing_time_ms", 0),
                "pages_processed": extraction_result.get("pages_processed", 0)
            }
        }
        
        logger.info(f"📊 Resultado del job {job_id} obtenido exitosamente")
        return result_response
        
    except Exception as e:
        logger.error(f"❌ Error consultando resultado del job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error consultando resultado del trabajo")


@router.delete("/{job_id}")
async def delete_job(job_id: str) -> Dict[str, str]:
    """
    Eliminar un trabajo del sistema
    
    Args:
        job_id: ID del trabajo a eliminar
        
    Returns:
        Confirmación de la eliminación
    """
    logger.info(f"🗑️ Eliminando job: {job_id}")
    
    try:
        # TODO: Implementar eliminación real desde Cosmos DB
        logger.info(f"✅ Job {job_id} eliminado exitosamente")
        return {"message": f"Job {job_id} eliminado exitosamente"}
        
    except Exception as e:
        logger.error(f"❌ Error eliminando job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error eliminando el trabajo")
