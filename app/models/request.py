"""
Modelos Pydantic para las requests del sistema IDP
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Literal, Any
from datetime import datetime
import re


class FieldDefinition(BaseModel):
    """Definición de un campo a extraer del documento"""
    
    name: str = Field(
        ..., 
        description="Nombre del campo a extraer",
        min_length=1,
        max_length=100
    )
    
    type: Literal["string", "date", "number", "boolean", "array"] = Field(
        ..., 
        description="Tipo de dato esperado para el campo"
    )
    
    description: str = Field(
        ..., 
        description="Descripción detallada del campo con instrucciones específicas",
        min_length=10,
        max_length=1000
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validar que el nombre del campo sea válido"""
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError('El nombre del campo debe ser un identificador válido (letras, números, guiones bajos)')
        return v


class DocumentProcessingRequest(BaseModel):
    """Request para procesar un documento con IDP"""
    
    document_path: str = Field(
        ..., 
        description="URL del documento a procesar (SharePoint, OneDrive, etc.) o ruta de archivo local"
    )
    
    processing_mode: Literal["dual_service", "gpt_vision_only", "hybrid_consensus"] = Field(
        ..., 
        description="Modo de procesamiento a utilizar"
    )
    
    prompt_general: str = Field(
        ..., 
        description="Prompt general para la extracción de datos del documento",
        min_length=20,
        max_length=2000
    )
    
    fields: List[FieldDefinition] = Field(
        ..., 
        description="Lista de campos a extraer del documento",
        min_items=1,
        max_items=50
    )
    
    metadata: Optional[dict] = Field(
        default=None, 
        description="Metadatos adicionales del documento"
    )
    
    @validator('document_path')
    def validate_document_path(cls, v):
        """Validar que document_path sea una URL válida o una ruta de archivo local"""
        # Si es una ruta de archivo local (comienza con / o contiene caracteres de ruta)
        if v.startswith('/') or '\\' in v or '/' in v:
            return v
        
        # Si es una URL, validar formato
        if v.startswith(('http://', 'https://', 'ftp://')):
            # Validar formato básico de URL
            if not re.match(r'^https?://[^\s/$.?#].[^\s]*$', v):
                raise ValueError('Formato de URL inválido')
            return v
        
        # Si no es ninguno de los anteriores, asumir que es una ruta relativa
        return v
    
    @validator('fields')
    def validate_fields(cls, v):
        """Validar que no haya nombres de campos duplicados"""
        names = [field.name for field in v]
        if len(names) != len(set(names)):
            raise ValueError('No puede haber nombres de campos duplicados')
        return v


class DocumentStatusRequest(BaseModel):
    """Request para consultar el estado de un documento"""
    
    job_id: str = Field(
        ..., 
        description="ID del trabajo de procesamiento"
    )


class DocumentSearchRequest(BaseModel):
    """Request para buscar documentos procesados"""
    
    correlation_id: Optional[str] = Field(
        default=None, 
        description="ID de correlación para buscar documentos específicos"
    )
    
    processing_mode: Optional[str] = Field(
        default=None, 
        description="Filtrar por modo de procesamiento"
    )
    
    start_date: Optional[datetime] = Field(
        default=None, 
        description="Fecha de inicio para la búsqueda"
    )
    
    end_date: Optional[datetime] = Field(
        default=None, 
        description="Fecha de fin para la búsqueda"
    )
    
    limit: int = Field(
        default=100, 
        description="Número máximo de resultados",
        ge=1,
        le=1000
    )
