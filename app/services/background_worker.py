#!/usr/bin/env python3
"""
Background Worker para procesar la cola de Azure Storage
Procesa documentos de forma asíncrona usando Document Intelligence + GPT-4o
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.queue_storage_service import QueueStorageService
from app.services.blob_storage_service import BlobStorageService
from app.services.cosmos_service import CosmosService
from app.services.ai_orchestrator import AIOrchestratorService
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


class BackgroundWorker:
    """Worker para procesar documentos de forma asíncrona"""
    
    def __init__(self):
        """Inicializar el Background Worker"""
        self.queue_service = QueueStorageService()
        self.blob_service = BlobStorageService()
        self.cosmos_service = CosmosService()
        self.ai_orchestrator = AIOrchestratorService()
        
        # Configuración del worker
        self.polling_interval = 5  # segundos entre consultas a la cola
        self.max_processing_time = 300  # segundos máximo por documento
        self.is_running = False
        
        logger.info("🚀 BackgroundWorker inicializado correctamente")
    
    async def start(self):
        """Iniciar el worker"""
        logger.info("🚀 Iniciando Background Worker...")
        self.is_running = True
        
        try:
            while self.is_running:
                await self._process_queue()
                await asyncio.sleep(self.polling_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Background Worker detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error en Background Worker: {str(e)}")
        finally:
            self.is_running = False
    
    async def stop(self):
        """Detener el worker"""
        logger.info("🛑 Deteniendo Background Worker...")
        self.is_running = False
    
    async def _process_queue(self):
        """Procesar mensajes de la cola"""
        try:
            # Recibir mensaje de la cola específica
            logger.info(f"📥 Intentando recibir mensaje de la cola: {settings.azure_storage_queue_name}")
            messages = await self.queue_service.receive_message(
                queue_name=settings.azure_storage_queue_name,  # Especificar cola correcta
                max_messages=1,
                visibility_timeout=60  # 1 minuto de visibilidad
            )
            
            if not messages:
                logger.info(f"📭 No hay mensajes en la cola {settings.azure_storage_queue_name}")
                return  # No hay mensajes para procesar
            
            logger.info(f"✅ Mensaje recibido exitosamente de la cola {settings.azure_storage_queue_name}")
            
            message = messages[0]
            message_id = message.get('message_id')
            pop_receipt = message.get('pop_receipt')
            content = message.get('content', {})
            
            logger.info(f"📥 Procesando mensaje: {message_id}")
            logger.info(f"   📄 Documento: {content.get('filename', 'N/A')}")
            logger.info(f"   🎯 Modo: {content.get('processing_mode', 'N/A')}")
            
            try:
                # Procesar el documento
                await self._process_document(message_id, content)
                
                # Eliminar mensaje de la cola (procesado exitosamente)
                await self.queue_service.delete_message(message_id, pop_receipt)
                logger.info(f"✅ Mensaje procesado y eliminado de la cola: {message_id}")
                
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje {message_id}: {str(e)}")
                
                # Mover mensaje a cola de fallidos
                await self.queue_service.move_to_failed_queue(content, str(e))
                
                # Eliminar mensaje de la cola principal
                await self.queue_service.delete_message(message_id, pop_receipt)
                
                # Actualizar estado del job en Cosmos DB
                await self._update_job_status(content.get('job_id'), 'failed', str(e))
                
        except Exception as e:
            logger.error(f"❌ Error en _process_queue: {str(e)}")
    
    async def _process_document(self, message_id: str, content: Dict[str, Any]):
        """Procesar un documento específico"""
        job_id = content.get('job_id')
        blob_path = content.get('blob_path')  # Cambiar blob_url por blob_path
        processing_mode = content.get('processing_mode', 'dual_service')
        prompt_general = content.get('prompt_general', '')
        fields = content.get('fields', [])
        
        logger.info(f"🔄 INICIANDO PROCESAMIENTO DEL DOCUMENTO")
        logger.info(f"   🆔 Job ID: {job_id}")
        logger.info(f"   📄 Filename: {content.get('filename', 'unknown')}")
        logger.info(f"   🎯 Processing Mode: {processing_mode}")
        logger.info(f"   📏 File Size: {content.get('file_size_mb', 0)} MB")
        logger.info(f"   🔗 Blob Path: {blob_path}")
        logger.info(f"   📝 Prompt Length: {len(prompt_general)} chars")
        logger.info(f"   🔍 Fields Count: {len(fields)}")
        logger.info(f"   🆔 Message ID: {message_id}")
        logger.info(f"   🕐 Timestamp: {datetime.utcnow().isoformat()}")
        logger.info(f"   " + "="*80)
        
        try:
            # 0. VERIFICAR ESTADO DEL JOB ANTES DE PROCESAR
            logger.info(f"🔒 PASO 0: VERIFICANDO ESTADO DEL JOB")
            job_status = await self._get_job_status(job_id)
            
            if job_status in ['completed', 'failed']:
                logger.warning(f"   ⚠️ Job {job_id} ya está en estado '{job_status}', saltando procesamiento")
                return
            
            if job_status == 'processing':
                logger.warning(f"   ⚠️ Job {job_id} ya está siendo procesado, saltando procesamiento")
                return
            
            if job_status != 'pending':
                logger.warning(f"   ⚠️ Job {job_id} tiene estado inesperado '{job_status}', saltando procesamiento")
                return
            
            logger.info(f"   ✅ Job {job_id} está en estado 'pending', procediendo con el procesamiento")
            
            # 1. Actualizar estado del job a 'processing'
            await self._update_job_status(job_id, 'processing')
            
            # 2. Descargar documento desde Blob Storage
            logger.info(f"📥 PASO 2: DESCARGANDO DOCUMENTO DESDE BLOB STORAGE")
            logger.info(f"   🔗 Blob Path: {blob_path}")
            logger.info(f"   🕐 Inicio descarga: {datetime.utcnow().isoformat()}")
            
            # ⏱️ RETRASO OPTIMIZADO: Solo esperar estabilidad mínima
            from app.core.config import settings
            logger.info(f"   ⏱️ RETRASO OPTIMIZADO: Esperando {settings.azure_blob_retry_delay_seconds} segundos para estabilidad...")
            logger.info(f"   📊 Configuración optimizada:")
            logger.info(f"      ⏱️ Retraso inicial: {settings.azure_blob_retry_delay_seconds}s")
            logger.info(f"      🔄 Máximo reintentos: {settings.azure_blob_max_retries}")
            logger.info(f"      📈 Factor backoff: {settings.azure_blob_retry_backoff_factor}x")
            logger.info(f"      ⏰ Tiempo total máximo estimado: ~{settings.azure_blob_retry_delay_seconds * (1 + sum(settings.azure_blob_retry_backoff_factor ** i for i in range(settings.azure_blob_max_retries - 1)))}s")
            
            import asyncio
            await asyncio.sleep(settings.azure_blob_retry_delay_seconds)
            logger.info(f"   ✅ Retraso inicial completado, iniciando descarga del documento...")
            
            # 📥 DESCARGAR DOCUMENTO DEL CONTAINER ORIGINAL
            document_content = None
            total_wait_time = 0
            
            for attempt in range(settings.azure_blob_max_retries):
                logger.info(f"   🔄 INTENTO {attempt + 1}/{settings.azure_blob_max_retries}")
                logger.info(f"      ⏰ Tiempo total esperado hasta ahora: {total_wait_time}s")
                
                # Intentar descargar del container original
                logger.info(f"   📥 Intentando descargar del container original...")
                try:
                    document_content = await self.blob_service.download_document(blob_path)
                    
                    if document_content:
                        logger.info(f"   ✅ Descarga exitosa del container original en intento {attempt + 1}")
                        logger.info(f"      🎯 Tiempo total de espera: {total_wait_time}s")
                        break
                    else:
                        logger.warning(f"   ⚠️ Descarga retornó None del container original en intento {attempt + 1}")
                        
                except Exception as download_error:
                    logger.warning(f"   ⚠️ Error en intento {attempt + 1}: {str(download_error)}")
                    
                    if attempt < settings.azure_blob_max_retries - 1:
                        # Calcular retraso exponencial
                        delay = int(settings.azure_blob_retry_delay_seconds * (settings.azure_blob_retry_backoff_factor ** attempt))
                        total_wait_time += delay
                        
                        logger.info(f"   ⏱️ Esperando {delay} segundos antes del siguiente intento...")
                        logger.info(f"      📊 Próximo intento en: {delay}s")
                        logger.info(f"      ⏰ Tiempo total de espera: {total_wait_time}s")
                        
                        await asyncio.sleep(delay)
                    else:
                        # Último intento falló
                        logger.error(f"   ❌ Todos los intentos fallaron después de {total_wait_time}s de espera")
                        raise download_error
                

                
            # Verificar que se descargó correctamente
            if not document_content:
                logger.error(f"   ❌ Documento descargado está vacío o es None")
                raise Exception("Documento descargado está vacío o es None")
            
            logger.info(f"   ✅ Descarga completada: {len(document_content)} bytes")
            logger.info(f"   🕐 Fin descarga: {datetime.utcnow().isoformat()}")
            logger.info(f"   📊 Tamaño del documento: {len(document_content)} bytes")
            logger.info(f"   " + "="*80)
            
            # 3. Procesar con IA
            logger.info(f"🤖 PASO 3: PROCESANDO DOCUMENTO CON IA")
            logger.info(f"   🎯 Processing Mode: {processing_mode}")
            logger.info(f"   📝 Prompt Length: {len(prompt_general)} chars")
            logger.info(f"   🔍 Fields Count: {len(fields)}")
            logger.info(f"   🕐 Inicio IA: {datetime.utcnow().isoformat()}")
            
            start_time = time.time()
            
            # Convertir campos de diccionario a objetos FieldDefinition
            from app.models.request import FieldDefinition
            logger.info(f"   🔄 Convirtiendo campos a FieldDefinition...")
            field_definitions = [
                FieldDefinition(
                    name=field.get('name', ''),
                    type=field.get('type', 'string'),
                    description=field.get('description', '')
                )
                for field in fields
            ]
            logger.info(f"   ✅ Campos convertidos: {len(field_definitions)}")
            
            # Procesar con AI Orchestrator
            logger.info(f"   🚀 Llamando a AI Orchestrator...")
            try:
                extraction_result = await self.ai_orchestrator.process_document(
                    document_content=document_content,
                    fields=field_definitions,
                    prompt_general=prompt_general,
                    processing_mode=processing_mode
                )
                logger.info(f"   ✅ AI Orchestrator completado exitosamente")
            except Exception as ai_error:
                logger.error(f"   ❌ Error en AI Orchestrator: {str(ai_error)}")
                logger.error(f"   🔍 Detalles del error: {type(ai_error).__name__}")
                raise Exception(f"Error en AI Orchestrator: {str(ai_error)}")
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.info(f"   ⏱️ Tiempo de procesamiento IA: {processing_time_ms}ms")
            logger.info(f"   📊 Campos extraídos: {len(extraction_result.extraction_data)}")
            logger.info(f"   📄 Páginas procesadas: {extraction_result.pages_processed or 0}")
            logger.info(f"   🕐 Fin IA: {datetime.utcnow().isoformat()}")
            logger.info(f"   " + "="*80)
            
            # 4. Guardar resultado en Cosmos DB
            logger.info(f"🗄️ PASO 4: GUARDANDO RESULTADO EN COSMOS DB")
            logger.info(f"   🕐 Inicio guardado: {datetime.utcnow().isoformat()}")
            
            # Guardar información del documento
            logger.info(f"   📄 Preparando información del documento...")
            document_info = {
                "filename": content.get('filename', 'unknown'),
                "file_size_mb": content.get('file_size_mb', 0),
                "file_type": content.get('filename', '').split('.')[-1] if '.' in content.get('filename', '') else 'unknown',
                "status": "processed",
                "processing_mode": processing_mode,
                "job_id": job_id,
                "created_at": datetime.utcnow().isoformat(),
                "ai_processing_time_ms": processing_time_ms
            }
            logger.info(f"   ✅ Información del documento preparada")
            logger.info(f"   📊 Campos del documento: {len(document_info)}")
            
            logger.info(f"   🗄️ Guardando documento en Cosmos DB...")
            try:
                doc_id = await self.cosmos_service.save_document(document_info)
                if doc_id:
                    logger.info(f"   ✅ Documento guardado en Cosmos DB: {doc_id}")
                else:
                    logger.error(f"   ❌ Error: save_document retornó None")
                    raise Exception("Error guardando documento en Cosmos DB")
            except Exception as doc_error:
                logger.error(f"   ❌ Error guardando documento: {str(doc_error)}")
                logger.error(f"   🔍 Detalles del error: {type(doc_error).__name__}")
                raise Exception(f"Error guardando documento en Cosmos DB: {str(doc_error)}")
            
            logger.info(f"   " + "="*80)
            
            # Guardar resultado de extracción
            logger.info(f"   🔍 Preparando resultado de extracción...")
            extraction_data = {
                "document_id": doc_id if doc_id else None,
                "job_id": job_id,
                "extraction_date": datetime.utcnow().isoformat(),
                "processing_time_ms": processing_time_ms,
                "strategy_used": processing_mode,
                "extraction_data": [field.dict() for field in extraction_result.extraction_data],
                "processing_summary": {
                    "processing_status": "completed",
                    "strategy_used": processing_mode,
                    "processing_time_ms": processing_time_ms,
                    "pages_processed": extraction_result.pages_processed or 0
                }
            }
            logger.info(f"   ✅ Resultado de extracción preparado")
            logger.info(f"   📊 Campos de extracción: {len(extraction_data)}")
            logger.info(f"   🔍 Datos extraídos: {len(extraction_data['extraction_data'])} campos")
            
            logger.info(f"   🗄️ Guardando resultado de extracción en Cosmos DB...")
            try:
                ext_id = await self.cosmos_service.save_extraction_result(extraction_data)
                if ext_id:
                    logger.info(f"   ✅ Resultado de extracción guardado en Cosmos DB: {ext_id}")
                else:
                    logger.error(f"   ❌ Error: save_extraction_result retornó None")
                    raise Exception("Error guardando resultado de extracción en Cosmos DB")
            except Exception as ext_error:
                logger.error(f"   ❌ Error guardando extracción: {str(ext_error)}")
                logger.error(f"   🔍 Detalles del error: {type(ext_error).__name__}")
                raise Exception(f"Error guardando resultado de extracción en Cosmos DB: {str(ext_error)}")
            
            logger.info(f"   " + "="*80)
            
            # 5. Actualizar estado del job a 'completed'
            logger.info(f"🔄 PASO 5: ACTUALIZANDO ESTADO DEL JOB A 'COMPLETED'")
            logger.info(f"   🆔 Job ID: {job_id}")
            logger.info(f"   ⏱️ Processing Time: {processing_time_ms}ms")
            logger.info(f"   🔍 Fields Extracted: {len(extraction_result.extraction_data)}")
            logger.info(f"   🗄️ Document ID: {doc_id}")
            logger.info(f"   🔍 Extraction ID: {ext_id}")
            
            try:
                await self._update_job_status(
                    job_id, 
                    'completed', 
                    processing_time_ms=processing_time_ms,
                    fields_extracted=len(extraction_result.extraction_data),
                    document_id=doc_id,
                    extraction_id=ext_id
                )
                logger.info(f"   ✅ Estado del job actualizado exitosamente")
            except Exception as status_error:
                logger.error(f"   ❌ Error actualizando estado del job: {str(status_error)}")
                logger.error(f"   🔍 Detalles del error: {type(status_error).__name__}")
                raise Exception(f"Error actualizando estado del job: {str(status_error)}")
            
            # 6. Mover documento procesado al contenedor de procesados
            logger.info(f"📁 PASO 6: MOVIENDO DOCUMENTO A CONTENEDOR PROCESADO")
            logger.info(f"   🔗 Blob Path: {blob_path}")
            logger.info(f"   🆔 Job ID: {job_id}")
            
            move_successful = False
            try:
                await self.blob_service.move_to_processed(blob_path, job_id, {
                    "status": "completed",
                    "processing_time_ms": processing_time_ms,
                    "fields_extracted": len(extraction_result.extraction_data)
                })
                logger.info(f"   ✅ Documento movido a contenedor procesado exitosamente")
                move_successful = True
            except Exception as move_error:
                logger.error(f"   ❌ Error moviendo documento: {str(move_error)}")
                logger.error(f"   🔍 Detalles del error: {type(move_error).__name__}")
                logger.warning(f"   ⚠️ Continuando sin mover documento")
                # No marcar como failed si solo falló el movimiento
            
            # 7. Actualizar estado final del job
            logger.info(f"🔄 PASO 7: ACTUALIZANDO ESTADO FINAL DEL JOB")
            try:
                if move_successful:
                    # Si el movimiento fue exitoso, marcar como completed
                    await self._update_job_status(
                        job_id, 
                        'completed', 
                        processing_time_ms=processing_time_ms,
                        fields_extracted=len(extraction_result.extraction_data),
                        document_id=doc_id,
                        extraction_id=ext_id
                    )
                    logger.info(f"   ✅ Job marcado como 'completed'")
                else:
                    # Si el movimiento falló pero el procesamiento fue exitoso, marcar como completed con warning
                    await self._update_job_status(
                        job_id, 
                        'completed', 
                        processing_time_ms=processing_time_ms,
                        fields_extracted=len(extraction_result.extraction_data),
                        document_id=doc_id,
                        extraction_id=ext_id
                    )
                    logger.warning(f"   ⚠️ Job marcado como 'completed' (movimiento falló pero procesamiento exitoso)")
            except Exception as status_error:
                logger.error(f"   ❌ Error actualizando estado final del job: {str(status_error)}")
            
            # 8. Resumen final
            logger.info(f"🎉 PROCESAMIENTO COMPLETADO EXITOSAMENTE")
            logger.info(f"   🆔 Job ID: {job_id}")
            logger.info(f"   📄 Filename: {content.get('filename', 'unknown')}")
            logger.info(f"   📊 Campos extraídos: {len(extraction_result.extraction_data)}")
            logger.info(f"   ⏱️ Tiempo total: {processing_time_ms}ms")
            logger.info(f"   🗄️ Document ID: {doc_id}")
            logger.info(f"   🔍 Extraction ID: {ext_id}")
            logger.info(f"   📁 Movimiento a processed: {'✅ Exitoso' if move_successful else '⚠️ Falló pero continuó'}")
            logger.info(f"   🕐 Timestamp final: {datetime.utcnow().isoformat()}")
            logger.info(f"   " + "="*80)
            
        except Exception as e:
            logger.error(f"❌ ERROR PROCESANDO DOCUMENTO")
            logger.error(f"   🆔 Job ID: {job_id}")
            logger.error(f"   📄 Filename: {content.get('filename', 'unknown')}")
            logger.error(f"   ❌ Error: {str(e)}")
            logger.error(f"   🔍 Tipo de error: {type(e).__name__}")
            logger.error(f"   🕐 Timestamp del error: {datetime.utcnow().isoformat()}")
            logger.error(f"   " + "="*80)
            
            # Actualizar estado del job a 'failed'
            logger.info(f"🔄 Actualizando estado del job a 'failed'...")
            try:
                await self._update_job_status(job_id, 'failed', str(e))
                logger.info(f"   ✅ Estado del job actualizado a 'failed'")
            except Exception as update_error:
                logger.error(f"   ❌ Error actualizando estado del job: {str(update_error)}")
            
            # Re-lanzar excepción para que se maneje en _process_queue
            raise
    
    async def _get_job_status(self, job_id: str) -> str:
        """Obtener el estado actual de un job desde Cosmos DB"""
        try:
            logger.info(f"   🔍 Consultando estado del job {job_id} en Cosmos DB...")
            
            # Obtener el job desde Cosmos DB
            job = await self.cosmos_service.get_processing_job(job_id)
            
            if job:
                status = job.get('status', 'unknown')
                logger.info(f"   ✅ Estado del job {job_id}: {status}")
                logger.info(f"      📊 Datos del job: {list(job.keys())}")
                return status
            else:
                logger.warning(f"   ⚠️ Job {job_id} no encontrado en Cosmos DB")
                return 'not_found'
                
        except Exception as e:
            logger.error(f"   ❌ Error consultando estado del job {job_id}: {str(e)}")
            return 'error'
    
    async def _update_job_status(
        self, 
        job_id: str, 
        status: str, 
        error_message: str = None,
        processing_time_ms: int = None,
        fields_extracted: int = None,
        document_id: str = None,
        extraction_id: str = None
    ):
        """Actualizar el estado de un job en Cosmos DB"""
        try:
            # Buscar el job existente
            existing_job = await self.cosmos_service.get_processing_job(job_id)
            
            if existing_job:
                # Actualizar job existente
                update_data = {
                    "status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                if status == "completed":
                    update_data.update({
                        "completed_at": datetime.utcnow().isoformat(),
                        "processing_time_ms": processing_time_ms or 0,
                        "fields_extracted": fields_extracted or 0,
                        "document_id": document_id,
                        "extraction_id": extraction_id
                    })
                elif status == "failed":
                    update_data.update({
                        "failed_at": datetime.utcnow().isoformat(),
                        "error_message": error_message
                    })
                elif status == "processing":
                    update_data.update({
                        "started_at": datetime.utcnow().isoformat()
                    })
                
                # Actualizar en Cosmos DB
                logger.info(f"   🔄 Llamando a CosmosService.update_job_status...")
                logger.info(f"      📊 Parámetros: job_id={job_id}, status={status}, update_data={update_data}")
                
                result = await self.cosmos_service.update_job_status(job_id, status, update_data)
                
                if result:
                    logger.info(f"✅ Estado del job actualizado exitosamente: {job_id} -> {status}")
                else:
                    logger.error(f"❌ CosmosService.update_job_status retornó False para job: {job_id}")
                    raise Exception(f"Error actualizando estado del job en Cosmos DB: {job_id}")
                
            else:
                # Crear nuevo job si no existe
                job_info = {
                    "job_id": job_id,
                    "document_name": "unknown",
                    "processing_mode": "dual_service",
                    "status": status,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                if status == "completed":
                    job_info.update({
                        "completed_at": datetime.utcnow().isoformat(),
                        "processing_time_ms": processing_time_ms or 0,
                        "fields_extracted": fields_extracted or 0
                    })
                
                await self.cosmos_service.create_processing_job(job_info)
                logger.info(f"✅ Nuevo job creado: {job_id} con estado {status}")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando estado del job {job_id}: {str(e)}")


async def start_worker():
    """Función para iniciar el worker desde el main"""
    worker = BackgroundWorker()
    await worker.start()


if __name__ == "__main__":
    # Para pruebas independientes
    asyncio.run(start_worker())
