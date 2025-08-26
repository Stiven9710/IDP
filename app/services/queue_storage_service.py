#!/usr/bin/env python3
"""
Servicio para manejar Azure Queue Storage
Gestiona la cola de procesamiento asíncrono de documentos
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from azure.storage.queue import QueueServiceClient, QueueClient, TextBase64EncodePolicy
from azure.core.exceptions import AzureError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class QueueStorageService:
    """Servicio para manejar Azure Queue Storage"""
    
    def __init__(self):
        """Inicializar servicio de Queue Storage"""
        from app.core.config import settings
        
        self.connection_string = settings.azure_storage_connection_string
        self.account_name = settings.azure_storage_account_name
        self.account_key = settings.azure_storage_account_key
        
        # Nombres de colas
        self.document_processing_queue = "document-processing-queue"
        self.high_priority_queue = "high-priority-processing"
        self.failed_processing_queue = "failed-processing"
        
        # Configuración de la cola
        self.visibility_timeout = 300  # 5 minutos
        self.max_message_size = 65536  # 64KB
        
        # Inicializar cliente
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar cliente de Queue Storage"""
        try:
            if self.connection_string:
                self.queue_service_client = QueueServiceClient.from_connection_string(
                    self.connection_string
                )
                logger.info("✅ Cliente de Queue Storage inicializado con connection string")
            else:
                logger.warning("⚠️ No se configuró connection string de Queue Storage")
                self.queue_service_client = None
                return
            
            # Crear colas si no existen
            self._ensure_queues_exist()
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Queue Storage: {e}")
            self.queue_service_client = None
    
    def _ensure_queues_exist(self):
        """Asegurar que las colas existan"""
        if not self.queue_service_client:
            return
            
        queues = [
            self.document_processing_queue,
            self.high_priority_queue,
            self.failed_processing_queue
        ]
        
        for queue_name in queues:
            try:
                queue_client = self.queue_service_client.get_queue_client(queue_name)
                # Verificar si la cola existe usando try/except en lugar de .exists()
                try:
                    # Intentar obtener propiedades para verificar si existe
                    queue_client.get_queue_properties()
                    logger.info(f"📋 Cola ya existe: {queue_name}")
                except ResourceNotFoundError:
                    # La cola no existe, crearla
                    queue_client.create_queue()
                    logger.info(f"📋 Cola creada: {queue_name}")
                    
            except Exception as e:
                logger.error(f"❌ Error creando cola {queue_name}: {e}")
    
    def _is_available(self) -> bool:
        """Verificar si el servicio está disponible"""
        return self.queue_service_client is not None
    
    async def send_message(
        self, 
        message_data: Dict[str, Any], 
        queue_name: str = None,
        priority: str = "normal"
    ) -> Optional[str]:
        """
        Enviar mensaje a la cola
        
        Args:
            message_data: Datos del mensaje a enviar
            queue_name: Nombre de la cola (por defecto document-processing)
            priority: Prioridad del mensaje (normal, high)
            
        Returns:
            ID del mensaje o None si falla
        """
        if not self._is_available():
            logger.error("❌ Queue Storage no está disponible")
            return None
        
        try:
            # Seleccionar cola según prioridad
            if priority == "high":
                queue = queue_name or self.high_priority_queue
            else:
                queue = queue_name or self.document_processing_queue
            
            queue_client = self.queue_service_client.get_queue_client(queue)
            
            # Generar ID único del mensaje
            message_id = str(uuid.uuid4())
            message_data["message_id"] = message_id
            message_data["timestamp"] = datetime.utcnow().isoformat()
            message_data["priority"] = priority
            
            # Convertir a JSON
            message_json = json.dumps(message_data, ensure_ascii=False)
            
            # Verificar tamaño del mensaje
            if len(message_json.encode('utf-8')) > self.max_message_size:
                logger.error(f"❌ Mensaje demasiado grande: {len(message_json)} caracteres")
                return None
            
            # Enviar mensaje
            logger.info(f"📤 Enviando mensaje a la cola...")
            logger.info(f"   📋 Cola: {queue}")
            logger.info(f"   🆔 Message ID: {message_id}")
            logger.info(f"   🎯 Prioridad: {priority}")
            logger.info(f"   📏 Tamaño: {len(message_json)} caracteres")
            
            # Enviar mensaje sin encoding_policy (causaba error)
            result = queue_client.send_message(message_json)
            
            logger.info(f"✅ Mensaje enviado exitosamente a la cola")
            logger.info(f"   🆔 Message ID: {message_id}")
            logger.info(f"   📋 Cola: {queue}")
            logger.info(f"   🕐 Timestamp: {message_data['timestamp']}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje a la cola: {e}")
            return None
    
    async def receive_message(
        self, 
        queue_name: str = None,
        max_messages: int = 1,
        visibility_timeout: int = None
    ) -> List[Dict[str, Any]]:
        """
        Recibir mensajes de la cola
        
        Args:
            queue_name: Nombre de la cola (por defecto document-processing)
            max_messages: Número máximo de mensajes a recibir
            visibility_timeout: Tiempo de visibilidad en segundos
            
        Returns:
            Lista de mensajes recibidos
        """
        if not self._is_available():
            logger.error("❌ Queue Storage no está disponible")
            return []
        
        try:
            queue = queue_name or self.document_processing_queue
            queue_client = self.queue_service_client.get_queue_client(queue)
            
            timeout = visibility_timeout or self.visibility_timeout
            
            logger.info(f"📥 Recibiendo mensajes de la cola...")
            logger.info(f"   📋 Cola: {queue}")
            logger.info(f"   📊 Máximo: {max_messages} mensajes")
            logger.info(f"   ⏱️ Timeout: {timeout} segundos")
            
            # Recibir mensajes
            messages = queue_client.receive_messages(
                max_messages=max_messages,
                visibility_timeout=timeout
            )
            
            received_messages = []
            for message in messages:
                try:
                    # Decodificar mensaje
                    message_content = message.content
                    if hasattr(message, 'encoding_policy') and message.encoding_policy:
                        # Decodificar si está en base64
                        import base64
                        message_content = base64.b64decode(message_content).decode('utf-8')
                    
                    # Parsear JSON
                    message_data = json.loads(message_content)
                    
                    # Agregar metadatos del mensaje (manejar atributos que pueden no existir)
                    message_info = {
                        "message_id": message.id,
                        "pop_receipt": message.pop_receipt,
                        "dequeue_count": getattr(message, 'dequeue_count', 0),
                        "content": message_data
                    }
                    
                    # Agregar atributos opcionales si existen
                    if hasattr(message, 'insertion_time'):
                        message_info["insertion_time"] = message.insertion_time
                    if hasattr(message, 'expiration_time'):
                        message_info["expiration_time"] = message.expiration_time
                    if hasattr(message, 'next_visible_time'):
                        message_info["next_visible_time"] = message.next_visible_time
                    
                    received_messages.append(message_info)
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando mensaje {message.id}: {e}")
                    continue
            
            logger.info(f"✅ Recibidos {len(received_messages)} mensajes de la cola {queue}")
            return received_messages
            
        except Exception as e:
            logger.error(f"❌ Error recibiendo mensajes: {e}")
            return []
    
    async def delete_message(
        self, 
        message_id: str, 
        pop_receipt: str, 
        queue_name: str = None
    ) -> bool:
        """
        Eliminar mensaje de la cola
        
        Args:
            message_id: ID del mensaje
            pop_receipt: Pop receipt del mensaje
            queue_name: Nombre de la cola
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if not self._is_available():
            logger.error("❌ Queue Storage no está disponible")
            return False
        
        try:
            queue = queue_name or self.document_processing_queue
            queue_client = self.queue_service_client.get_queue_client(queue)
            
            logger.info(f"🗑️ Eliminando mensaje de la cola...")
            logger.info(f"   📋 Cola: {queue}")
            logger.info(f"   🆔 Message ID: {message_id}")
            
            queue_client.delete_message(message_id, pop_receipt)
            
            logger.info(f"✅ Mensaje eliminado exitosamente de la cola")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando mensaje: {e}")
            return False
    
    async def update_message_visibility(
        self, 
        message_id: str, 
        pop_receipt: str, 
        visibility_timeout: int,
        queue_name: str = None
    ) -> bool:
        """
        Actualizar tiempo de visibilidad de un mensaje
        
        Args:
            message_id: ID del mensaje
            pop_receipt: Pop receipt del mensaje
            visibility_timeout: Nuevo timeout en segundos
            queue_name: Nombre de la cola
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if not self._is_available():
            logger.error("❌ Queue Storage no está disponible")
            return False
        
        try:
            queue = queue_name or self.document_processing_queue
            queue_client = self.queue_service_client.get_queue_client(queue)
            
            logger.info(f"⏱️ Actualizando visibilidad del mensaje...")
            logger.info(f"   📋 Cola: {queue}")
            logger.info(f"   🆔 Message ID: {message_id}")
            logger.info(f"   ⏱️ Nuevo timeout: {visibility_timeout} segundos")
            
            queue_client.update_message(
                message_id,
                pop_receipt,
                visibility_timeout=visibility_timeout
            )
            
            logger.info(f"✅ Visibilidad del mensaje actualizada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando visibilidad: {e}")
            return False
    
    async def move_to_failed_queue(
        self, 
        message_data: Dict[str, Any], 
        error_message: str,
        original_queue: str = None
    ) -> Optional[str]:
        """
        Mover mensaje fallido a la cola de fallidos
        
        Args:
            message_data: Datos del mensaje original
            error_message: Mensaje de error
            original_queue: Cola original del mensaje
            
        Returns:
            ID del mensaje en la cola de fallidos o None si falla
        """
        if not self._is_available():
            logger.error("❌ Queue Storage no está disponible")
            return None
        
        try:
            # Agregar información del error
            failed_message = {
                **message_data,
                "failed_at": datetime.utcnow().isoformat(),
                "error_message": error_message,
                "original_queue": original_queue or self.document_processing_queue,
                "retry_count": message_data.get("retry_count", 0) + 1
            }
            
            # Enviar a cola de fallidos
            failed_queue_client = self.queue_service_client.get_queue_client(
                self.failed_processing_queue
            )
            
            logger.info(f"⚠️ Moviendo mensaje fallido a cola de fallidos...")
            logger.info(f"   📋 Cola original: {original_queue}")
            logger.info(f"   📋 Cola de fallidos: {self.failed_processing_queue}")
            logger.info(f"   ❌ Error: {error_message}")
            
            # Enviar mensaje sin encoding_policy
            result = failed_queue_client.send_message(json.dumps(failed_message, ensure_ascii=False))
            
            logger.info(f"✅ Mensaje fallido movido a cola de fallidos")
            return result.id
            
        except Exception as e:
            logger.error(f"❌ Error moviendo mensaje fallido: {e}")
            return None
    
    async def get_queue_properties(self, queue_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Obtener propiedades de una cola
        
        Args:
            queue_name: Nombre de la cola
            
        Returns:
            Propiedades de la cola o None si falla
        """
        if not self._is_available():
            logger.error("❌ Queue Storage no está disponible")
            return None
        
        try:
            queue = queue_name or self.document_processing_queue
            queue_client = self.queue_service_client.get_queue_client(queue)
            
            properties = queue_client.get_queue_properties()
            
            return {
                "name": queue,
                "approximate_message_count": properties.approximate_message_count,
                "metadata": properties.metadata or {}
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo propiedades de la cola: {e}")
            return None
    
    async def list_queues(self) -> List[Dict[str, Any]]:
        """
        Listar todas las colas disponibles
        
        Returns:
            Lista de colas con sus propiedades
        """
        if not self._is_available():
            logger.error("❌ Queue Storage no está disponible")
            return []
        
        try:
            logger.info("📋 Listando colas disponibles...")
            
            queues = []
            queue_list = self.queue_service_client.list_queues()
            
            for queue in queue_list:
                try:
                    queue_client = self.queue_service_client.get_queue_client(queue.name)
                    properties = queue_client.get_queue_properties()
                    
                    queue_info = {
                        "name": queue.name,
                        "approximate_message_count": properties.approximate_message_count,
                        "metadata": properties.metadata or {}
                    }
                    queues.append(queue_info)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error obteniendo propiedades de cola {queue.name}: {e}")
                    continue
            
            logger.info(f"✅ Encontradas {len(queues)} colas")
            return queues
            
        except Exception as e:
            logger.error(f"❌ Error listando colas: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar salud del servicio de Queue Storage
        
        Returns:
            Estado de salud del servicio
        """
        try:
            if not self._is_available():
                return {
                    "status": "unhealthy",
                    "message": "Queue Storage no está configurado",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Intentar listar colas
            queues = await self.list_queues()
            
            # Obtener propiedades de la cola principal
            main_queue_props = await self.get_queue_properties(self.document_processing_queue)
            
            return {
                "status": "healthy",
                "message": "Queue Storage funcionando correctamente",
                "timestamp": datetime.utcnow().isoformat(),
                "account_name": self.account_name,
                "queues_count": len(queues),
                "main_queue": {
                    "name": self.document_processing_queue,
                    "message_count": main_queue_props.get("approximate_message_count", 0) if main_queue_props else 0
                },
                "queues": [q["name"] for q in queues]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Error en Queue Storage: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
