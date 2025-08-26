#!/usr/bin/env python3
"""
Script de debug para identificar el problema con receive_messages
"""

import asyncio
from app.services.queue_storage_service import QueueStorageService


async def debug_queue():
    """Debug detallado de la funcionalidad de la cola"""
    print("🔍 DEBUG DETALLADO DE LA COLA")
    print("=" * 50)
    
    try:
        # Crear servicio de cola
        queue_service = QueueStorageService()
        
        # Verificar salud
        health = await queue_service.health_check()
        print(f"📊 Estado de salud: {health.get('status')}")
        print(f"📋 Cola principal: {health.get('main_queue', {}).get('name')}")
        print(f"📊 Mensajes en cola: {health.get('main_queue', {}).get('message_count')}")
        
        # Listar colas
        queues = await queue_service.list_queues()
        print(f"\n📋 Colas disponibles: {len(queues)}")
        for queue in queues:
            print(f"   - {queue['name']}: {queue['approximate_message_count']} mensajes")
        
        # Debug directo con Azure SDK
        print(f"\n🔍 DEBUG DIRECTO CON AZURE SDK")
        print("-" * 40)
        
        try:
            from azure.storage.queue import QueueServiceClient
            
            # Usar la misma connection string
            from app.core.config import settings
            connection_string = settings.azure_storage_connection_string
            
            if connection_string:
                print(f"✅ Connection string disponible")
                
                # Crear cliente directo
                queue_service_client = QueueServiceClient.from_connection_string(connection_string)
                queue_client = queue_service_client.get_queue_client("document-processing")
                
                print(f"📋 Cliente de cola creado: {queue_client.queue_name}")
                
                # Obtener propiedades
                properties = queue_client.get_queue_properties()
                print(f"📊 Propiedades de la cola:")
                print(f"   - Nombre: {properties.name}")
                print(f"   - Mensajes aproximados: {properties.approximate_message_count}")
                
                # Intentar recibir mensajes directamente
                print(f"\n📥 Intentando recibir mensajes directamente...")
                messages = queue_client.receive_messages(
                    max_messages=1,
                    visibility_timeout=30
                )
                
                print(f"📊 Mensajes recibidos (raw): {messages}")
                
                # Convertir a lista
                message_list = list(messages)
                print(f"📊 Mensajes convertidos a lista: {len(message_list)}")
                
                if message_list:
                    for i, msg in enumerate(message_list):
                        print(f"\n📄 Mensaje {i+1}:")
                        print(f"   🆔 ID: {msg.id}")
                        print(f"   📝 Contenido: {msg.content[:100]}...")
                        print(f"   🔑 Pop Receipt: {msg.pop_receipt}")
                        print(f"   🔄 Dequeue Count: {getattr(msg, 'dequeue_count', 'N/A')}")
                        
                        # Intentar parsear JSON
                        try:
                            import json
                            content = msg.content
                            if hasattr(msg, 'encoding_policy') and msg.encoding_policy:
                                import base64
                                content = base64.b64decode(content).decode('utf-8')
                            
                            parsed_content = json.loads(content)
                            print(f"   ✅ JSON parseado correctamente")
                            print(f"   📄 Filename: {parsed_content.get('filename', 'N/A')}")
                            print(f"   🎯 Processing Mode: {parsed_content.get('processing_mode', 'N/A')}")
                            
                        except Exception as e:
                            print(f"   ❌ Error parseando JSON: {e}")
                else:
                    print(f"⚠️ No se recibieron mensajes")
                
            else:
                print(f"❌ Connection string no disponible")
                
        except Exception as e:
            print(f"❌ Error en debug directo: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_queue())
