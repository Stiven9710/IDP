#!/usr/bin/env python3
"""
Servicio para manejar Azure Blob Storage
Gestiona el almacenamiento de documentos grandes y procesados
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import AzureError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class BlobStorageService:
    """Servicio para manejar Azure Blob Storage"""
    
    def __init__(self):
        """Inicializar servicio de Blob Storage"""
        from app.core.config import settings
        
        self.connection_string = settings.azure_storage_connection_string
        self.account_name = settings.azure_storage_account_name
        self.account_key = settings.azure_storage_account_key
        
        # Nombres de contenedores
        self.documents_container = "documents"
        self.processed_container = "processed"
        self.temp_container = "temp"
        
        # Inicializar cliente
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar cliente de Blob Storage"""
        try:
            if self.connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
                logger.info("✅ Cliente de Blob Storage inicializado con connection string")
            else:
                logger.warning("⚠️ No se configuró connection string de Blob Storage")
                self.blob_service_client = None
                return
            
            # Crear contenedores si no existen
            self._ensure_containers_exist()
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Blob Storage: {e}")
            self.blob_service_client = None
    
    def _ensure_containers_exist(self):
        """Asegurar que los contenedores existan"""
        if not self.blob_service_client:
            return
            
        containers = [self.documents_container, self.processed_container, self.temp_container]
        
        for container_name in containers:
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client.create_container()
                    logger.info(f"📁 Contenedor creado: {container_name}")
                else:
                    logger.info(f"📁 Contenedor ya existe: {container_name}")
            except Exception as e:
                logger.error(f"❌ Error creando contenedor {container_name}: {e}")
    
    def _is_available(self) -> bool:
        """Verificar si el servicio está disponible"""
        return self.blob_service_client is not None
    
    async def upload_document(
        self, 
        file_content: bytes, 
        filename: str, 
        job_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Subir documento a Blob Storage
        
        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre del archivo
            job_id: ID del trabajo de procesamiento
            metadata: Metadatos adicionales
            
        Returns:
            URL del blob o None si falla
        """
        if not self._is_available():
            logger.error("❌ Blob Storage no está disponible")
            return None
        
        try:
            # Generar nombre único del blob
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            blob_name = f"{job_id}/{timestamp}_{filename}"
            
            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.documents_container,
                blob=blob_name
            )
            
            # Preparar metadatos
            blob_metadata = {
                "job_id": job_id,
                "filename": filename,
                "upload_timestamp": timestamp,
                "file_size_bytes": str(len(file_content)),
                "content_type": "application/octet-stream"
            }
            
            if metadata:
                blob_metadata.update(metadata)
            
            # Subir archivo
            logger.info(f"📤 Subiendo documento a Blob Storage...")
            logger.info(f"   📁 Contenedor: {self.documents_container}")
            logger.info(f"   📄 Nombre: {blob_name}")
            logger.info(f"   📏 Tamaño: {len(file_content)} bytes")
            
            blob_client.upload_blob(
                file_content,
                metadata=blob_metadata,
                overwrite=True
            )
            
            # Generar URL del blob
            blob_url = blob_client.url
            
            logger.info(f"✅ Documento subido exitosamente a Blob Storage")
            logger.info(f"   🔗 URL: {blob_url}")
            logger.info(f"   🆔 Job ID: {job_id}")
            
            return blob_url
            
        except Exception as e:
            logger.error(f"❌ Error subiendo documento a Blob Storage: {e}")
            return None
    
    async def download_document(self, blob_url: str) -> Optional[bytes]:
        """
        Descargar documento desde Blob Storage
        
        Args:
            blob_url: URL del blob a descargar
            
        Returns:
            Contenido del archivo o None si falla
        """
        if not self._is_available():
            logger.error("❌ Blob Storage no está disponible")
            return None
        
        try:
            logger.info(f"📥 Descargando documento desde Blob Storage...")
            logger.info(f"   🔗 URL: {blob_url}")
            
            # Extraer container y blob name de la URL
            # URL format: https://account.blob.core.windows.net/container/blob_name
            try:
                # Usar urllib.parse para manejar URLs correctamente
                from urllib.parse import urlparse
                parsed_url = urlparse(blob_url)
                
                # La ruta será: /container/blob_name
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) < 2:
                    logger.error(f"❌ URL de blob inválida: {blob_url}")
                    return None
                
                container_name = path_parts[0]  # container name
                blob_name = '/'.join(path_parts[1:])  # blob name (puede tener /)
                
                # 🔧 DECODIFICAR EL NOMBRE DEL BLOB (eliminar %20, %2F, etc.)
                from urllib.parse import unquote
                decoded_blob_name = unquote(blob_name)
                
                logger.info(f"   🔍 Parsing de URL:")
                logger.info(f"      🔗 URL original: {blob_url}")
                logger.info(f"      📁 Container extraído: {container_name}")
                logger.info(f"      📄 Blob extraído (codificado): {blob_name}")
                logger.info(f"      📄 Blob extraído (decodificado): {decoded_blob_name}")
                
            except Exception as parse_error:
                logger.error(f"❌ Error parseando URL: {parse_error}")
                # Fallback al método anterior
                url_parts = blob_url.split('/')
                if len(url_parts) < 6:
                    logger.error(f"❌ URL de blob inválida: {blob_url}")
                    return None
                
                container_name = url_parts[3]  # container name
                blob_name = '/'.join(url_parts[4:])  # blob name (puede tener /)
                
                # 🔧 DECODIFICAR EL NOMBRE DEL BLOB EN EL FALLBACK TAMBIÉN
                from urllib.parse import unquote
                decoded_blob_name = unquote(blob_name)
            
            logger.info(f"   📁 Container: {container_name}")
            logger.info(f"   📄 Blob (codificado): {blob_name}")
            logger.info(f"   📄 Blob (decodificado): {decoded_blob_name}")
            
            # Usar el cliente autenticado para descargar
            # 🔧 USAR EL NOMBRE DECODIFICADO PARA EVITAR CODIFICACIÓN DOBLE
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=decoded_blob_name
            )
            
            # 🔍 VERIFICAR EXISTENCIA DEL BLOB ANTES DE DESCARGAR
            logger.info(f"   🔍 Verificando existencia del blob...")
            try:
                properties = blob_client.get_blob_properties()
                logger.info(f"   ✅ Blob existe: {properties.size} bytes")
                logger.info(f"   📅 Última modificación: {properties.last_modified}")
            except Exception as existence_error:
                logger.error(f"   ❌ Blob no existe o no es accesible: {existence_error}")
                logger.error(f"   🔍 Detalles del error: {type(existence_error).__name__}")
                raise Exception(f"Blob no existe o no es accesible: {str(existence_error)}")
            
            # Descargar contenido
            logger.info(f"   📥 Iniciando descarga del contenido...")
            blob_data = blob_client.download_blob()
            content = blob_data.readall()
            
            logger.info(f"✅ Documento descargado exitosamente")
            logger.info(f"   📏 Tamaño: {len(content)} bytes")
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Error descargando documento: {e}")
            logger.error(f"   🔍 Detalles del error: {type(e).__name__}")
            raise Exception(f"Error descargando documento desde Blob Storage: {str(e)}")
    
    async def move_to_processed(
        self, 
        source_blob_url: str, 
        job_id: str,
        processing_result: Dict[str, Any]
    ) -> Optional[str]:
        """
        Mover documento procesado al contenedor de procesados
        
        Args:
            source_blob_url: URL del blob original
            job_id: ID del trabajo
            processing_result: Resultado del procesamiento
            
        Returns:
            Nueva URL del blob o None si falla
        """
        if not self._is_available():
            logger.error("❌ Blob Storage no está disponible")
            return None
        
        try:
            # Extraer container y blob name de la URL original
            try:
                # Usar urllib.parse para manejar URLs correctamente
                from urllib.parse import urlparse
                parsed_url = urlparse(source_blob_url)
                
                # La ruta será: /container/blob_name
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) < 2:
                    logger.error(f"❌ URL de blob inválida: {source_blob_url}")
                    return None
                
                container_name = path_parts[0]  # container name
                blob_name = '/'.join(path_parts[1:])  # blob name (puede tener /)
                
            except Exception as parse_error:
                logger.error(f"❌ Error parseando URL: {parse_error}")
                # Fallback al método anterior
                url_parts = source_blob_url.split('/')
                if len(url_parts) < 6:
                    logger.error(f"❌ URL de blob inválida: {source_blob_url}")
                    return None
                
                container_name = url_parts[3]  # container name
                blob_name = '/'.join(url_parts[4:])  # blob name (puede tener /)
            
            # 🔧 DECODIFICAR EL NOMBRE DEL BLOB PARA EVITAR CODIFICACIÓN DOBLE
            from urllib.parse import unquote
            decoded_blob_name = unquote(blob_name)
            
            # Obtener cliente del blob original usando el cliente autenticado
            source_blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=decoded_blob_name
            )
            
            # Generar nombre para el blob procesado
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            processed_blob_name = f"{job_id}/processed_{timestamp}_{blob_name.split('/')[-1]}"
            
            # Obtener cliente del blob de destino
            dest_blob_client = self.blob_service_client.get_blob_client(
                container=self.processed_container,
                blob=processed_blob_name
            )
            
            # Copiar blob con metadatos actualizados
            logger.info(f"🔄 Moviendo documento procesado...")
            logger.info(f"   📁 Desde: {container_name}")
            logger.info(f"   📁 Hacia: {self.processed_container}")
            logger.info(f"   📄 Nombre: {processed_blob_name}")
            
            # Leer contenido del blob original
            blob_data = source_blob_client.download_blob()
            content = blob_data.readall()
            
            # Metadatos del procesamiento
            processed_metadata = {
                "job_id": job_id,
                "processing_timestamp": timestamp,
                "original_blob_url": source_blob_url,
                "processing_status": "completed",
                "extraction_fields_count": str(len(processing_result.get("extraction_data", []))),
                "processing_mode": processing_result.get("processing_summary", {}).get("strategy_used", "unknown")
            }
            
            # Subir al contenedor de procesados
            dest_blob_client.upload_blob(
                content,
                metadata=processed_metadata,
                overwrite=True
            )
            
            # Eliminar del contenedor original
            try:
                source_blob_client.delete_blob()
                logger.info(f"   ✅ Blob original eliminado exitosamente")
            except Exception as delete_error:
                logger.warning(f"   ⚠️ No se pudo eliminar blob original: {delete_error}")
                # Continuar aunque falle la eliminación
            
            new_blob_url = dest_blob_client.url
            
            logger.info(f"✅ Documento movido exitosamente a procesados")
            logger.info(f"   🔗 Nueva URL: {new_blob_url}")
            
            return new_blob_url
            
        except Exception as e:
            logger.error(f"❌ Error moviendo documento procesado: {e}")
            logger.error(f"   🔍 Detalles del error: {type(e).__name__}")
            # No lanzar excepción, solo retornar None para que el worker maneje el error
            return None
    
    async def delete_document(self, blob_url: str) -> bool:
        """
        Eliminar documento de Blob Storage
        
        Args:
            blob_url: URL del blob a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if not self._is_available():
            logger.error("❌ Blob Storage no está disponible")
            return False
        
        try:
            blob_client = BlobClient.from_blob_url(blob_url)
            
            logger.info(f"🗑️ Eliminando documento de Blob Storage...")
            logger.info(f"   🔗 URL: {blob_url}")
            
            blob_client.delete_blob()
            
            logger.info(f"✅ Documento eliminado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando documento: {e}")
            return False
    
    async def list_documents(self, container_name: str = None, prefix: str = None) -> List[Dict[str, Any]]:
        """
        Listar documentos en un contenedor
        
        Args:
            container_name: Nombre del contenedor (por defecto documents)
            prefix: Prefijo para filtrar blobs
            
        Returns:
            Lista de documentos con metadatos
        """
        if not self._is_available():
            logger.error("❌ Blob Storage no está disponible")
            return []
        
        try:
            container = container_name or self.documents_container
            container_client = self.blob_service_client.get_container_client(container)
            
            logger.info(f"📋 Listando documentos en contenedor: {container}")
            
            documents = []
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blobs:
                doc_info = {
                    "name": blob.name,
                    "size": blob.size,
                    "created": blob.creation_time,
                    "last_modified": blob.last_modified,
                    "url": f"{container_client.url}/{blob.name}",
                    "metadata": blob.metadata or {}
                }
                documents.append(doc_info)
            
            logger.info(f"✅ Encontrados {len(documents)} documentos en {container}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error listando documentos: {e}")
            return []
    
    async def get_blob_metadata(self, blob_url: str) -> Optional[Dict[str, Any]]:
        """
        Obtener metadatos de un blob
        
        Args:
            blob_url: URL del blob
            
        Returns:
            Metadatos del blob o None si falla
        """
        if not self._is_available():
            logger.error("❌ Blob Storage no está disponible")
            return None
        
        try:
            blob_client = BlobClient.from_blob_url(blob_url)
            properties = blob_client.get_blob_properties()
            
            return {
                "name": properties.name,
                "size": properties.size,
                "created": properties.creation_time,
                "last_modified": properties.last_modified,
                "content_type": properties.content_settings.content_type,
                "metadata": properties.metadata or {}
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo metadatos: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar salud del servicio de Blob Storage
        
        Returns:
            Estado de salud del servicio
        """
        try:
            if not self._is_available():
                return {
                    "status": "unhealthy",
                    "message": "Blob Storage no está configurado",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Intentar listar contenedores
            containers = list(self.blob_service_client.list_containers())
            
            return {
                "status": "healthy",
                "message": "Blob Storage funcionando correctamente",
                "timestamp": datetime.utcnow().isoformat(),
                "account_name": self.account_name,
                "containers_count": len(containers),
                "containers": [c.name for c in containers]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Error en Blob Storage: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def list_blobs_in_container(
        self, 
        container_name: str, 
        name_starts_with: Optional[str] = None
    ) -> List[Any]:
        """
        🆕 MÉTODO NATIVO: Listar blobs en un contenedor específico
        
        Args:
            container_name: Nombre del contenedor
            name_starts_with: Prefijo para filtrar nombres de blobs
            
        Returns:
            Lista de blobs de Azure
        """
        if not self._is_available():
            logger.error("❌ Blob Storage no está disponible")
            return []
        
        try:
            logger.info(f"📋 Listando blobs en contenedor: {container_name}")
            if name_starts_with:
                logger.info(f"   🔍 Filtro: name_starts_with='{name_starts_with}'")
            
            container_client = self.blob_service_client.get_container_client(container_name)
            
            # Listar blobs usando el método nativo de Azure
            blobs = list(container_client.list_blobs(name_starts_with=name_starts_with))
            
            logger.info(f"✅ Encontrados {len(blobs)} blobs en contenedor {container_name}")
            for blob in blobs:
                logger.info(f"   📄 Blob: {blob.name} ({blob.size} bytes)")
            
            return blobs
            
        except Exception as e:
            logger.error(f"❌ Error listando blobs en contenedor {container_name}: {e}")
            logger.error(f"🔍 Tipo de error: {type(e).__name__}")
            return []
    
    async def delete_blob_native(
        self, 
        container_name: str, 
        blob_name: str
    ) -> bool:
        """
        🆕 MÉTODO NATIVO: Eliminar un blob usando métodos nativos de Azure
        
        Args:
            container_name: Nombre del contenedor
            blob_name: Nombre del blob
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        if not self._is_available():
            logger.error("❌ Blob Storage no está disponible")
            return False
        
        try:
            logger.info(f"🗑️ Eliminando blob usando método nativo de Azure...")
            logger.info(f"   📁 Contenedor: {container_name}")
            logger.info(f"   📄 Blob: {blob_name}")
            
            # Obtener cliente del contenedor
            container_client = self.blob_service_client.get_container_client(container_name)
            
            # Obtener cliente del blob
            blob_client = container_client.get_blob_client(blob_name)
            
            # Verificar que el blob existe antes de eliminarlo
            if not blob_client.exists():
                logger.warning(f"⚠️ Blob {blob_name} no existe en contenedor {container_name}")
                return False
            
            # Eliminar el blob usando el método nativo de Azure
            blob_client.delete_blob()
            
            logger.info(f"✅ Blob eliminado exitosamente usando método nativo de Azure")
            logger.info(f"   🗑️ Blob eliminado: {blob_name}")
            logger.info(f"   📁 Contenedor: {container_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando blob con método nativo: {e}")
            logger.error(f"🔍 Tipo de error: {type(e).__name__}")
            logger.error(f"📁 Contenedor: {container_name}")
            logger.error(f"📄 Blob: {blob_name}")
            return False
