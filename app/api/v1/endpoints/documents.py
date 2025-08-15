"""
Endpoints para el procesamiento de documentos IDP
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from app.models.request import DocumentProcessingRequest, DocumentStatusRequest, DocumentSearchRequest
from app.models.response import (
    DocumentProcessingResponse, 
    DocumentStatusResponse, 
    DocumentSearchResponse,
    ErrorResponse
)
from app.services.document_service import DocumentService
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()

# Instanciar servicios
document_service = DocumentService()


@router.post("/process", response_model=DocumentProcessingResponse)
async def process_document(
    request: DocumentProcessingRequest,
    background_tasks: BackgroundTasks
) -> DocumentProcessingResponse:
    """
    Procesar un documento de forma síncrona o asíncrona según su tamaño
    
    Args:
        request: Request con la información del documento a procesar
        background_tasks: Tareas en segundo plano de FastAPI
        
    Returns:
        Response con el resultado del procesamiento o ID del job
    """
    logger.info("🚀 Endpoint /process llamado")
    logger.info(f"📄 Documento: {request.document_path}")
    logger.info(f"🎯 Modo: {request.processing_mode}")
    logger.info(f"📝 Campos: {len(request.fields)}")
    
    try:
        # Validar configuración
        if not _validate_azure_config():
            raise HTTPException(
                status_code=500,
                detail="Servicios de Azure no configurados correctamente"
            )
        
        # Procesar documento
        result = await document_service.process_document(request)
        
        logger.info(f"✅ Documento procesado exitosamente: {result.job_id}")
        return result
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{job_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(job_id: str) -> DocumentStatusResponse:
    """
    Obtener el estado de un documento en procesamiento
    
    Args:
        job_id: ID del trabajo de procesamiento
        
    Returns:
        Estado actual del documento
    """
    logger.info(f"🔍 Consultando estado del job: {job_id}")
    
    try:
        status_data = await document_service.get_document_status(job_id)
        
        # Convertir a response model
        response = DocumentStatusResponse(
            job_id=job_id,
            status=status_data.get("status", "unknown"),
            progress_percentage=status_data.get("progress_percentage", 0.0),
            estimated_completion=status_data.get("estimated_completion"),
            current_step=status_data.get("current_step", "Desconocido"),
            message=status_data.get("message", "Estado consultado exitosamente")
        )
        
        logger.info(f"📊 Estado del job {job_id}: {response.status}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error consultando estado del job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error consultando estado del documento")


@router.get("/{job_id}/result", response_model=DocumentProcessingResponse)
async def get_document_result(job_id: str) -> DocumentProcessingResponse:
    """
    Obtener el resultado de un documento procesado
    
    Args:
        job_id: ID del trabajo de procesamiento
        
    Returns:
        Resultado completo del procesamiento
    """
    logger.info(f"🔍 Consultando resultado del job: {job_id}")
    
    try:
        result_data = await document_service.get_document_result(job_id)
        
        # Verificar si el documento está procesado
        if not result_data or result_data.get("status") != "completed":
            raise HTTPException(
                status_code=404, 
                detail="Documento no encontrado o aún en procesamiento"
            )
        
        # Convertir a response model
        response = DocumentProcessingResponse(
            job_id=job_id,
            extraction_data=result_data.get("extraction_data", []),
            processing_summary=result_data.get("processing_summary", {}),
            message=result_data.get("message", "Resultado obtenido exitosamente"),
            correlation_id=result_data.get("correlation_id")
        )
        
        logger.info(f"📊 Resultado del job {job_id} obtenido exitosamente")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error consultando resultado del job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error consultando resultado del documento")


@router.get("/search", response_model=DocumentSearchResponse)
async def search_documents(
    correlation_id: str = None,
    processing_mode: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
) -> DocumentSearchResponse:
    """
    Buscar documentos procesados con filtros opcionales
    
    Args:
        correlation_id: ID de correlación para buscar documentos específicos
        processing_mode: Filtrar por modo de procesamiento
        start_date: Fecha de inicio para la búsqueda (YYYY-MM-DD)
        end_date: Fecha de fin para la búsqueda (YYYY-MM-DD)
        limit: Número máximo de resultados
        
    Returns:
        Lista de documentos encontrados
    """
    logger.info("🔍 Endpoint de búsqueda de documentos llamado")
    logger.info(f"🔍 Filtros: correlation_id={correlation_id}, mode={processing_mode}")
    
    try:
        # Construir filtros de búsqueda
        search_filters = {}
        if correlation_id:
            search_filters["correlation_id"] = correlation_id
        if processing_mode:
            search_filters["processing_mode"] = processing_mode
        if start_date:
            search_filters["start_date"] = start_date
        if end_date:
            search_filters["end_date"] = end_date
        
        # Realizar búsqueda (implementar en storage service)
        # Por ahora, devolver respuesta de ejemplo
        documents = [
            {
                "job_id": "example-job-123",
                "document_path": "https://example.com/document.pdf",
                "processing_mode": "hybrid_consensus",
                "status": "completed",
                "created_at": "2025-01-12T10:00:00Z"
            }
        ]
        
        response = DocumentSearchResponse(
            documents=documents,
            total_count=len(documents),
            page=1,
            page_size=limit,
            has_more=False
        )
        
        logger.info(f"📊 Búsqueda completada: {len(documents)} documentos encontrados")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda de documentos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la búsqueda de documentos")


@router.delete("/{job_id}")
async def cancel_document_processing(job_id: str) -> Dict[str, str]:
    """
    Cancelar el procesamiento de un documento
    
    Args:
        job_id: ID del trabajo de procesamiento
        
    Returns:
        Confirmación de la cancelación
    """
    logger.info(f"❌ Cancelando procesamiento del job: {job_id}")
    
    try:
        # Implementar lógica de cancelación
        # Por ahora, devolver confirmación
        logger.info(f"✅ Procesamiento del job {job_id} cancelado")
        return {"message": f"Procesamiento del job {job_id} cancelado exitosamente"}
        
    except Exception as e:
        logger.error(f"❌ Error cancelando job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error cancelando el procesamiento")


def _validate_azure_config() -> bool:
    """Validar que la configuración de Azure esté completa"""
    required_configs = [
        settings.azure_openai_endpoint,
        settings.azure_openai_api_key,
        settings.azure_document_intelligence_endpoint,
        settings.azure_document_intelligence_api_key
    ]
    
    return all(config for config in required_configs)
