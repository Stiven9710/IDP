"""
Servicio principal de procesamiento de documentos IDP
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import httpx

from app.core.config import settings
from app.models.request import DocumentProcessingRequest
from app.models.response import (
    DocumentProcessingResponse, 
    ProcessingStatus, 
    ProcessingMode,
    ExtractionField,
    ProcessingSummary
)
from app.services.ai_orchestrator import AIOrchestratorService
from app.services.storage_service import StorageService
from app.services.queue_service import QueueService
from app.services.cosmos_service import CosmosService
from app.utils.helpers import get_file_size_from_url, is_supported_format

# Configurar logging
logger = logging.getLogger(__name__)


class DocumentService:
    """Servicio principal para el procesamiento de documentos"""
    
    def __init__(self):
        """Inicializar el servicio de documentos"""
        self.ai_orchestrator = AIOrchestratorService()
        self.storage_service = StorageService()
        self.queue_service = QueueService()
        self.cosmos_service = CosmosService()
        
        # Umbral para procesamiento asíncrono (10MB según requerimiento)
        self.async_threshold_mb = 10.0
        
        logger.info("🚀 DocumentService inicializado correctamente")
    
    async def process_document(
        self, 
        request: DocumentProcessingRequest
    ) -> DocumentProcessingResponse:
        """
        Procesar un documento de forma síncrona o asíncrona según su tamaño
        
        Args:
            request: Request de procesamiento del documento
            
        Returns:
            Response con el resultado del procesamiento
        """
        start_time = time.time()
        job_id = str(uuid.uuid4())
        
        logger.info(f"📄 Iniciando procesamiento del documento: {job_id}")
        logger.info(f"🔗 URL del documento: {request.document_path}")
        logger.info(f"🎯 Modo de procesamiento: {request.processing_mode}")
        logger.info(f"📝 Número de campos a extraer: {len(request.fields)}")
        
        try:
            # Validar formato del documento
            if not self._validate_document_format(str(request.document_path)):
                raise ValueError(f"Formato de documento no soportado: {request.document_path}")
            
            # Obtener tamaño del archivo
            file_size_mb = await self._get_document_size(str(request.document_path))
            logger.info(f"📏 Tamaño del documento: {file_size_mb:.2f} MB")
            
            # Decidir si procesar de forma síncrona o asíncrona
            if file_size_mb <= self.async_threshold_mb:
                logger.info("⚡ Procesamiento SÍNCRONO (documento pequeño)")
                return await self._process_synchronously(
                    job_id, request, file_size_mb, start_time
                )
            else:
                logger.info("🔄 Procesamiento ASÍNCRONO (documento grande)")
                return await self._process_asynchronously(
                    job_id, request, file_size_mb, start_time
                )
                
        except Exception as e:
            logger.error(f"❌ Error en el procesamiento del documento {job_id}: {str(e)}")
            raise
    
    async def _process_synchronously(
        self,
        job_id: str,
        request: DocumentProcessingRequest,
        file_size_mb: float,
        start_time: float
    ) -> DocumentProcessingResponse:
        """Procesar documento de forma síncrona"""
        logger.info(f"⚡ Iniciando procesamiento síncrono para job {job_id}")
        logger.info(f"📊 Tamaño del documento: {file_size_mb:.2f} MB")
        logger.info(f"🎯 Modo de procesamiento: {request.processing_mode}")
        logger.info(f"📋 Campos a extraer: {len(request.fields)}")
        
        try:
            # Descargar documento temporalmente
            document_content = await self._download_document(str(request.document_path))
            logger.info(f"📥 Documento descargado: {len(document_content)} bytes")
            
            # Procesar con IA
            logger.info(f"🤖 Iniciando procesamiento con IA...")
            extraction_result = await self.ai_orchestrator.process_document(
                document_content=document_content,
                fields=request.fields,
                prompt_general=request.prompt_general,
                processing_mode=request.processing_mode
            )
            logger.info(f"✅ Procesamiento con IA completado")
            logger.info(f"📊 Campos extraídos: {len(extraction_result.extraction_data)}")
            
            # Calcular tiempo de procesamiento
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.info(f"⏱️ Tiempo total de procesamiento: {processing_time_ms}ms")
            
            # Crear response
            response = DocumentProcessingResponse(
                job_id=job_id,
                extraction_data=extraction_result.extraction_data,
                processing_summary=ProcessingSummary(
                    processing_status=ProcessingStatus.COMPLETED,
                    processing_time_ms=processing_time_ms,
                    file_size_mb=file_size_mb,
                    strategy_used=ProcessingMode(request.processing_mode),
                    timestamp=datetime.utcnow(),
                    pages_processed=extraction_result.pages_processed,
                    review_flags=extraction_result.review_flags
                ),
                message="Documento procesado exitosamente de forma síncrona",
                correlation_id=request.metadata.get("correlation_id") if request.metadata else None
            )
            
            # ===== INICIO: GUARDADO EN COSMOS DB =====
            logger.info(f"🗄️ Iniciando guardado en Azure Cosmos DB...")
            
            # Guardar información del documento en Cosmos DB
            document_info = {
                "filename": request.document_path.split("/")[-1] if "/" in request.document_path else request.document_path,
                "file_size_mb": file_size_mb,
                "file_type": request.document_path.split(".")[-1] if "." in request.document_path else "unknown",
                "status": "processed",
                "processing_mode": request.processing_mode,
                "correlation_id": request.metadata.get("correlation_id") if request.metadata else None,
                "job_id": job_id,
                "created_at": datetime.utcnow().isoformat(),
                "ai_processing_time_ms": processing_time_ms
            }
            
            logger.info(f"📄 Guardando información del documento en Cosmos DB...")
            logger.info(f"   📁 Nombre: {document_info['filename']}")
            logger.info(f"   📏 Tamaño: {document_info['file_size_mb']:.2f} MB")
            logger.info(f"   🎯 Modo: {document_info['processing_mode']}")
            
            doc_id = await self.cosmos_service.save_document(document_info)
            if doc_id:
                logger.info(f"✅ Documento guardado exitosamente en Cosmos DB")
                logger.info(f"   🆔 Document ID: {doc_id}")
                logger.info(f"   📍 Container: documents")
                
                # Guardar resultado de extracción
                extraction_data = {
                    "document_id": doc_id,
                    "extraction_date": datetime.utcnow().isoformat(),
                    "processing_time_ms": processing_time_ms,
                    "strategy_used": request.processing_mode,
                    "extraction_data": [field.dict() for field in extraction_result.extraction_data],
                    "processing_summary": {
                        "processing_status": "completed",
                        "pages_processed": extraction_result.pages_processed,
                        "review_flags": extraction_result.review_flags
                    },
                    "job_id": job_id,
                    "filename": document_info['filename'],
                    "fields_extracted": len(extraction_result.extraction_data)
                }
                
                logger.info(f"🔍 Guardando resultado de extracción en Cosmos DB...")
                logger.info(f"   📊 Campos extraídos: {extraction_data['fields_extracted']}")
                logger.info(f"   🎯 Estrategia: {extraction_data['strategy_used']}")
                
                ext_id = await self.cosmos_service.save_extraction_result(extraction_data)
                if ext_id:
                    logger.info(f"✅ Extracción guardada exitosamente en Cosmos DB")
                    logger.info(f"   🆔 Extraction ID: {ext_id}")
                    logger.info(f"   📍 Container: extractions")
                    logger.info(f"   🔗 Vinculada al documento: {doc_id}")
                else:
                    logger.error(f"❌ ERROR: No se pudo guardar la extracción en Cosmos DB")
                    logger.error(f"   📄 Document ID: {doc_id}")
                    logger.error(f"   🔍 Datos de extracción: {len(extraction_data)} campos")
            else:
                logger.error(f"❌ ERROR: No se pudo guardar el documento en Cosmos DB")
                logger.error(f"   📁 Nombre: {document_info['filename']}")
                logger.error(f"   📏 Tamaño: {document_info['file_size_mb']:.2f} MB")
            
            # ===== FIN: GUARDADO EN COSMOS DB =====
            
            # Crear trabajo de procesamiento
            job_info = {
                "job_id": job_id,
                "document_name": document_info['filename'],
                "processing_mode": request.processing_mode,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "processing_time_ms": processing_time_ms,
                "fields_extracted": len(extraction_result.extraction_data),
                "document_id": doc_id if doc_id else None,
                "extraction_id": ext_id if 'ext_id' in locals() else None
            }
            
            logger.info(f"⚙️ Guardando información del trabajo en Cosmos DB...")
            job_db_id = await self.cosmos_service.create_processing_job(job_info)
            if job_db_id:
                logger.info(f"✅ Trabajo guardado exitosamente en Cosmos DB")
                logger.info(f"   🆔 Job DB ID: {job_db_id}")
                logger.info(f"   📍 Container: processing_jobs")
            else:
                logger.warning(f"⚠️ No se pudo guardar el trabajo en Cosmos DB")
            
            # Resumen final
            logger.info(f"🎉 RESUMEN FINAL - Job {job_id}:")
            logger.info(f"   📄 Documento: {document_info['filename']} ({file_size_mb:.2f} MB)")
            logger.info(f"   🤖 IA: {request.processing_mode} - {len(extraction_result.extraction_data)} campos")
            logger.info(f"   ⏱️ Tiempo: {processing_time_ms}ms")
            logger.info(f"   🗄️ Cosmos DB: Document={doc_id}, Extraction={ext_id if 'ext_id' in locals() else 'N/A'}, Job={job_db_id if 'job_db_id' in locals() else 'N/A'}")
            
            logger.info(f"✅ Procesamiento síncrono completado exitosamente para job {job_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento síncrono {job_id}: {str(e)}")
            raise
    
    async def _process_asynchronously(
        self,
        job_id: str,
        request: DocumentProcessingRequest,
        file_size_mb: float,
        start_time: float
    ) -> DocumentProcessingResponse:
        """Procesar documento de forma asíncrona"""
        logger.info(f"🔄 Iniciando procesamiento asíncrono para job {job_id}")
        
        try:
            # Guardar documento en Blob Storage (Capa Bronce)
            blob_path = await self.storage_service.upload_document_to_blob(
                document_url=str(request.document_path),
                job_id=job_id
            )
            logger.info(f"📦 Documento guardado en Blob Storage: {blob_path}")
            
            # Crear mensaje en la cola
            queue_message = {
                "job_id": job_id,
                "document_path": str(request.document_path),
                "blob_path": blob_path,
                "processing_mode": request.processing_mode,
                "prompt_general": request.prompt_general,
                "fields": [field.dict() for field in request.fields],
                "metadata": request.metadata,
                "file_size_mb": file_size_mb,
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.queue_service.enqueue_message(
                queue_name=settings.azure_storage_queue_name,
                message=queue_message
            )
            logger.info(f"📬 Mensaje encolado para job {job_id}")
            
            # Crear response de aceptación
            response = DocumentProcessingResponse(
                job_id=job_id,
                extraction_data=[],  # Vacío para procesamiento asíncrono
                processing_summary=ProcessingSummary(
                    processing_status=ProcessingStatus.PENDING,
                    processing_time_ms=0,
                    file_size_mb=file_size_mb,
                    strategy_used=ProcessingMode(request.processing_mode),
                    timestamp=datetime.utcnow(),
                    pages_processed=0,
                    review_flags=[]
                ),
                message="Documento aceptado para procesamiento asíncrono",
                correlation_id=request.metadata.get("correlation_id") if request.metadata else None
            )
            
            # Guardar estado inicial en Cosmos DB
            await self.storage_service.save_job_status(job_id, ProcessingStatus.PENDING)
            logger.info(f"💾 Estado inicial guardado en Cosmos DB para job {job_id}")
            
            logger.info(f"✅ Procesamiento asíncrono iniciado para job {job_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento asíncrono {job_id}: {str(e)}")
            raise
    
    async def get_document_status(self, job_id: str) -> Dict[str, Any]:
        """Obtener el estado de un documento en procesamiento"""
        logger.info(f"🔍 Consultando estado del job: {job_id}")
        
        try:
            status = await self.storage_service.get_job_status(job_id)
            logger.info(f"📊 Estado del job {job_id}: {status}")
            return status
        except Exception as e:
            logger.error(f"❌ Error consultando estado del job {job_id}: {str(e)}")
            raise
    
    async def get_document_result(self, job_id: str) -> Dict[str, Any]:
        """Obtener el resultado de un documento procesado"""
        logger.info(f"🔍 Consultando resultado del job: {job_id}")
        
        try:
            result = await self.storage_service.get_extraction_result(job_id)
            logger.info(f"📊 Resultado del job {job_id} obtenido exitosamente")
            return result
        except Exception as e:
            logger.error(f"❌ Error consultando resultado del job {job_id}: {str(e)}")
            raise
    
    def _validate_document_format(self, document_url: str) -> bool:
        """Validar si el formato del documento es soportado"""
        parsed_url = urlparse(document_url)
        file_path = parsed_url.path.lower()
        
        supported_formats = [
            '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp',
            '.docx', '.doc', '.txt', '.rtf'
        ]
        
        is_supported = any(file_path.endswith(fmt) for fmt in supported_formats)
        logger.info(f"🔍 Validación de formato: {file_path} - {'✅ Soportado' if is_supported else '❌ No soportado'}")
        
        return is_supported
    
    async def _get_document_size(self, document_url: str) -> float:
        """Obtener el tamaño del documento desde la URL"""
        try:
            file_size_mb = await get_file_size_from_url(document_url)
            logger.info(f"📏 Tamaño del documento obtenido: {file_size_mb:.2f} MB")
            return file_size_mb
        except Exception as e:
            logger.warning(f"⚠️ No se pudo obtener el tamaño del documento: {str(e)}")
            # Valor por defecto para continuar el procesamiento
            return 5.0
    
    async def _download_document(self, document_url: str) -> bytes:
        """Descargar el documento desde la URL"""
        logger.info(f"📥 Descargando documento desde: {document_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(document_url)
            response.raise_for_status()
            
            content = response.content
            logger.info(f"📥 Documento descargado: {len(content)} bytes")
            return content
