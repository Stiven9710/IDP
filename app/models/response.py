"""
Modelos Pydantic para las responses del sistema IDP
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """Estados posibles del procesamiento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingMode(str, Enum):
    """Modos de procesamiento disponibles"""
    DUAL_SERVICE = "dual_service"
    GPT_VISION_ONLY = "gpt_vision_only"
    HYBRID_CONSENSUS = "hybrid_consensus"


class ExtractionField(BaseModel):
    """Campo extraído del documento"""
    
    name: str = Field(..., description="Nombre del campo extraído")
    value: Any = Field(..., description="Valor extraído del campo")
    confidence: float = Field(
        ..., 
        description="Nivel de confianza de la extracción (0.0 a 1.0)",
        ge=0.0,
        le=1.0
    )
    review_required: bool = Field(
        default=False, 
        description="Indica si el campo requiere revisión humana"
    )
    source_strategy: str = Field(
        ..., 
        description="Estrategia utilizada para la extracción"
    )
    extraction_time_ms: int = Field(
        ..., 
        description="Tiempo de extracción en milisegundos"
    )


class ProcessingSummary(BaseModel):
    """Resumen del procesamiento del documento"""
    
    processing_status: ProcessingStatus = Field(
        ..., 
        description="Estado actual del procesamiento"
    )
    
    processing_time_ms: int = Field(
        ..., 
        description="Tiempo total de procesamiento en milisegundos"
    )
    
    file_size_mb: float = Field(
        ..., 
        description="Tamaño del archivo en MB"
    )
    
    strategy_used: ProcessingMode = Field(
        ..., 
        description="Estrategia de procesamiento utilizada"
    )
    
    review_flags: List[str] = Field(
        default_factory=list, 
        description="Banderas de revisión identificadas"
    )
    
    timestamp: datetime = Field(
        ..., 
        description="Timestamp del procesamiento"
    )
    
    pages_processed: int = Field(
        ..., 
        description="Número de páginas procesadas"
    )
    
    errors: List[str] = Field(
        default_factory=list, 
        description="Errores encontrados durante el procesamiento"
    )


class DocumentProcessingResponse(BaseModel):
    """Response del procesamiento de documentos"""
    
    job_id: str = Field(..., description="ID único del trabajo de procesamiento")
    extraction_data: List[ExtractionField] = Field(
        ..., 
        description="Datos extraídos del documento"
    )
    processing_summary: ProcessingSummary = Field(
        ..., 
        description="Resumen del procesamiento"
    )
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    correlation_id: Optional[str] = Field(
        default=None, 
        description="ID de correlación del cliente"
    )


class DocumentStatusResponse(BaseModel):
    """Response del estado de un documento"""
    
    job_id: str = Field(..., description="ID del trabajo")
    status: ProcessingStatus = Field(..., description="Estado actual")
    progress_percentage: float = Field(
        ..., 
        description="Porcentaje de progreso (0.0 a 100.0)",
        ge=0.0,
        le=100.0
    )
    estimated_completion: Optional[datetime] = Field(
        default=None, 
        description="Tiempo estimado de finalización"
    )
    current_step: str = Field(..., description="Paso actual del procesamiento")
    message: str = Field(..., description="Mensaje descriptivo del estado")


class DocumentSearchResponse(BaseModel):
    """Response de búsqueda de documentos"""
    
    documents: List[Dict[str, Any]] = Field(
        ..., 
        description="Lista de documentos encontrados"
    )
    total_count: int = Field(..., description="Total de documentos encontrados")
    page: int = Field(..., description="Página actual de resultados")
    page_size: int = Field(..., description="Tamaño de la página")
    has_more: bool = Field(..., description="Indica si hay más páginas")


class ErrorResponse(BaseModel):
    """Response de error estándar"""
    
    error_code: str = Field(..., description="Código de error")
    error_message: str = Field(..., description="Mensaje descriptivo del error")
    details: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Detalles adicionales del error"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Timestamp del error"
    )
    request_id: Optional[str] = Field(
        default=None, 
        description="ID de la request para tracking"
    )
