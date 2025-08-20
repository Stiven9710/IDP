"""
Servicio para interactuar con Azure Cosmos DB
Maneja operaciones CRUD para documentos, extracciones y trabajos de procesamiento
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError

from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

class CosmosService:
    """Servicio para interactuar con Azure Cosmos DB"""
    
    def __init__(self):
        """Inicializar el servicio de Cosmos DB"""
        try:
            # Verificar configuración
            if not all([
                settings.azure_cosmos_endpoint,
                settings.azure_cosmos_key,
                settings.azure_cosmos_database_name
            ]):
                logger.warning("⚠️ Cosmos DB no configurado completamente")
                self.client = None
                self.database = None
                return
            
            # Crear cliente de Cosmos DB
            self.client = CosmosClient(
                url=settings.azure_cosmos_endpoint,
                credential=settings.azure_cosmos_key
            )
            
            # Obtener o crear database
            self.database = self.client.get_database_client(settings.azure_cosmos_database_name)
            
            # Obtener o crear containers
            self.documents_container = self.database.get_container_client(
                settings.azure_cosmos_container_documents
            )
            self.extractions_container = self.database.get_container_client(
                settings.azure_cosmos_container_extractions
            )
            self.jobs_container = self.database.get_container_client(
                settings.azure_cosmos_container_jobs
            )
            
            logger.info("🗄️ CosmosService inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando CosmosService: {str(e)}")
            self.client = None
            self.database = None
    
    def _is_available(self) -> bool:
        """Verificar si el servicio está disponible"""
        return self.client is not None and self.database is not None
    
    # ==================== DOCUMENTS ====================
    
    async def save_document(self, document_info: Dict[str, Any]) -> str:
        """Guardar información de un documento en Cosmos DB"""
        if not self._is_available():
            logger.error("❌ Cosmos DB no está disponible")
            return None
            
        try:
            # Generar ID único
            doc_id = f"doc_{str(uuid.uuid4())}"
            document_info["id"] = doc_id
            
            logger.info(f"🗄️ Guardando documento en Cosmos DB...")
            logger.info(f"   🆔 ID generado: {doc_id}")
            logger.info(f"   📁 Nombre: {document_info.get('filename', 'N/A')}")
            logger.info(f"   📏 Tamaño: {document_info.get('file_size_mb', 0):.2f} MB")
            logger.info(f"   🎯 Modo: {document_info.get('processing_mode', 'N/A')}")
            
            # Insertar en Cosmos DB
            self.documents_container.create_item(body=document_info)
            
            logger.info(f"✅ Documento guardado exitosamente en Cosmos DB")
            logger.info(f"   🆔 Document ID: {doc_id}")
            logger.info(f"   📍 Container: {self.documents_container.id}")
            logger.info(f"   📊 Campos guardados: {len(document_info)}")
            
            return doc_id
            
        except CosmosHttpResponseError as e:
            logger.error(f"❌ Error de Cosmos DB al guardar documento: {e.status_code} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado al guardar documento: {str(e)}")
            return None
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener documento por ID
        
        Args:
            document_id: ID del documento
            
        Returns:
            Documento o None si no se encuentra
        """
        if not self._is_available():
            logger.warning("⚠️ Cosmos DB no disponible")
            return None
        
        try:
            result = self.documents_container.read_item(
                item=document_id,
                partition_key=document_id
            )
            
            logger.info(f"✅ Documento recuperado: {document_id}")
            return result
            
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                logger.info(f"📄 Documento no encontrado: {document_id}")
                return None
            else:
                logger.error(f"❌ Error de Cosmos DB obteniendo documento: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo documento: {str(e)}")
            return None
    
    async def update_document_status(self, document_id: str, status: str, **kwargs) -> bool:
        """
        Actualizar estado del documento
        
        Args:
            document_id: ID del documento
            status: Nuevo estado
            **kwargs: Otros campos a actualizar
            
        Returns:
            True si se actualizó correctamente
        """
        if not self._is_available():
            logger.warning("⚠️ Cosmos DB no disponible")
            return False
        
        try:
            # Obtener documento actual
            document = await self.get_document(document_id)
            if not document:
                return False
            
            # Actualizar campos
            document['status'] = status
            document['updated_at'] = datetime.utcnow().isoformat()
            
            for key, value in kwargs.items():
                document[key] = value
            
            # Guardar cambios
            self.documents_container.replace_item(
                item=document_id,
                body=document
            )
            
            logger.info(f"✅ Estado del documento actualizado: {document_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando estado del documento: {str(e)}")
            return False
    
    # ==================== EXTRACTIONS ====================
    
    async def save_extraction_result(self, extraction_data: Dict[str, Any]) -> str:
        """Guardar resultado de extracción en Cosmos DB"""
        if not self._is_available():
            logger.error("❌ Cosmos DB no está disponible")
            return None
            
        try:
            # Generar ID único
            ext_id = f"ext_{str(uuid.uuid4())}"
            extraction_data["id"] = ext_id
            
            logger.info(f"🔍 Guardando resultado de extracción en Cosmos DB...")
            logger.info(f"   🆔 ID generado: {ext_id}")
            logger.info(f"   📄 Document ID: {extraction_data.get('document_id', 'N/A')}")
            logger.info(f"   🎯 Estrategia: {extraction_data.get('strategy_used', 'N/A')}")
            logger.info(f"   📊 Campos extraídos: {extraction_data.get('fields_extracted', 0)}")
            logger.info(f"   ⏱️ Tiempo: {extraction_data.get('processing_time_ms', 0)}ms")
            
            # Insertar en Cosmos DB
            self.extractions_container.create_item(body=extraction_data)
            
            logger.info(f"✅ Extracción guardada exitosamente en Cosmos DB")
            logger.info(f"   🆔 Extraction ID: {ext_id}")
            logger.info(f"   📍 Container: {self.extractions_container.id}")
            logger.info(f"   📊 Datos guardados: {len(extraction_data)} campos")
            
            return ext_id
            
        except CosmosHttpResponseError as e:
            logger.error(f"❌ Error de Cosmos DB al guardar extracción: {e.status_code} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado al guardar extracción: {str(e)}")
            return None
    
    async def get_extraction_history(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Obtener historial de extracciones de un documento
        
        Args:
            document_id: ID del documento
            
        Returns:
            Lista de extracciones
        """
        if not self._is_available():
            logger.warning("⚠️ Cosmos DB no disponible")
            return []
        
        try:
            # Consultar extracciones por document_id
            query = "SELECT * FROM c WHERE c.document_id = @document_id ORDER BY c.created_at DESC"
            parameters = [{"name": "@document_id", "value": document_id}]
            
            results = list(self.extractions_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=False
            ))
            
            logger.info(f"✅ Historial de extracciones obtenido: {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial de extracciones: {str(e)}")
            return []
    
    async def search_extractions(self, query_text: str, field_name: str = None) -> List[Dict[str, Any]]:
        """
        Buscar extracciones por texto
        
        Args:
            query_text: Texto a buscar
            field_name: Campo específico donde buscar (opcional)
            
        Returns:
            Lista de extracciones que coinciden
        """
        if not self._is_available():
            logger.warning("⚠️ Cosmos DB no disponible")
            return []
        
        try:
            if field_name:
                # Búsqueda en campo específico
                query = f"SELECT * FROM c WHERE CONTAINS(c.{field_name}, @query_text)"
            else:
                # Búsqueda en todos los campos de texto
                query = """
                SELECT * FROM c 
                WHERE CONTAINS(c.numero_factura, @query_text) 
                   OR CONTAINS(c.proveedor_nombre, @query_text)
                   OR CONTAINS(c.cliente_nombre, @query_text)
                """
            
            parameters = [{"name": "@query_text", "value": query_text}]
            
            results = list(self.extractions_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            logger.info(f"✅ Búsqueda completada: {len(results)} resultados para '{query_text}'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {str(e)}")
            return []
    
    # ==================== PROCESSING JOBS ====================
    
    async def create_processing_job(self, job_info: Dict[str, Any]) -> str:
        """Crear un trabajo de procesamiento en Cosmos DB"""
        if not self._is_available():
            logger.error("❌ Cosmos DB no está disponible")
            return None
            
        try:
            # Generar ID único
            job_db_id = f"job_{str(uuid.uuid4())}"
            job_info["id"] = job_db_id
            
            logger.info(f"⚙️ Creando trabajo de procesamiento en Cosmos DB...")
            logger.info(f"   🆔 ID generado: {job_db_id}")
            logger.info(f"   📄 Documento: {job_info.get('document_name', 'N/A')}")
            logger.info(f"   🎯 Modo: {job_info.get('processing_mode', 'N/A')}")
            logger.info(f"   📊 Estado: {job_info.get('status', 'N/A')}")
            
            # Insertar en Cosmos DB
            self.jobs_container.create_item(body=job_info)
            
            logger.info(f"✅ Trabajo de procesamiento creado exitosamente en Cosmos DB")
            logger.info(f"   🆔 Job DB ID: {job_db_id}")
            logger.info(f"   📍 Container: {self.jobs_container.id}")
            logger.info(f"   📊 Campos guardados: {len(job_info)}")
            
            return job_db_id
            
        except CosmosHttpResponseError as e:
            logger.error(f"❌ Error de Cosmos DB al crear trabajo: {e.status_code} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado al crear trabajo: {str(e)}")
            return None
    
    async def update_job_status(self, job_id: str, status: str, progress: int = None, **kwargs) -> bool:
        """
        Actualizar estado de un trabajo de procesamiento
        
        Args:
            job_id: ID del trabajo
            status: Nuevo estado
            progress: Progreso (0-100)
            **kwargs: Otros campos a actualizar
            
        Returns:
            True si se actualizó correctamente
        """
        if not self._is_available():
            logger.warning("⚠️ Cosmos DB no disponible")
            return False
        
        try:
            # Obtener trabajo actual
            query = "SELECT * FROM c WHERE c.id = @job_id"
            parameters = [{"name": "@job_id", "value": job_id}]
            
            results = list(self.jobs_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=False
            ))
            
            if not results:
                logger.warning(f"⚠️ Trabajo no encontrado: {job_id}")
                return False
            
            job = results[0]
            
            # Actualizar campos
            job['status'] = status
            job['updated_at'] = datetime.utcnow().isoformat()
            
            if progress is not None:
                job['progress'] = progress
            
            for key, value in kwargs.items():
                job[key] = value
            
            # Guardar cambios
            self.jobs_container.replace_item(
                item=job_id,
                body=job
            )
            
            logger.info(f"✅ Estado del trabajo actualizado: {job_id} -> {status} ({progress}%)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando estado del trabajo: {str(e)}")
            return False
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener estado de un trabajo de procesamiento
        
        Args:
            job_id: ID del trabajo
            
        Returns:
            Información del trabajo o None si no se encuentra
        """
        if not self._is_available():
            logger.warning("⚠️ Cosmos DB no disponible")
            return None
        
        try:
            query = "SELECT * FROM c WHERE c.id = @job_id"
            parameters = [{"name": "@job_id", "value": job_id}]
            
            results = list(self.jobs_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=False
            ))
            
            if results:
                logger.info(f"✅ Estado del trabajo obtenido: {job_id}")
                return results[0]
            else:
                logger.info(f"📄 Trabajo no encontrado: {job_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del trabajo: {str(e)}")
            return None
    
    # ==================== UTILITIES ====================
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la base de datos
        
        Returns:
            Estadísticas de Cosmos DB
        """
        if not self._is_available():
            logger.warning("⚠️ Cosmos DB no disponible")
            return {}
        
        try:
            stats = {
                'database_name': settings.azure_cosmos_database_name,
                'containers': {
                    'documents': self.documents_container.id,
                    'extractions': self.extractions_container.id,
                    'jobs': self.jobs_container.id
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Contar documentos en cada container
            try:
                docs_count = len(list(self.documents_container.read_all_items()))
                stats['documents_count'] = docs_count
            except:
                stats['documents_count'] = 'N/A'
            
            try:
                extractions_count = len(list(self.extractions_container.read_all_items()))
                stats['extractions_count'] = extractions_count
            except:
                stats['extractions_count'] = 'N/A'
            
            try:
                jobs_count = len(list(self.jobs_container.read_all_items()))
                stats['jobs_count'] = jobs_count
            except:
                stats['jobs_count'] = 'N/A'
            
            logger.info("✅ Estadísticas de la base de datos obtenidas")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar salud del servicio de Cosmos DB
        
        Returns:
            Estado de salud del servicio
        """
        try:
            if not self._is_available():
                return {
                    'status': 'unavailable',
                    'message': 'Cosmos DB no configurado',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Intentar una operación simple
            stats = await self.get_database_stats()
            
            return {
                'status': 'healthy',
                'message': 'Cosmos DB funcionando correctamente',
                'timestamp': datetime.utcnow().isoformat(),
                'stats': stats
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Error en Cosmos DB: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
