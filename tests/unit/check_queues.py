#!/usr/bin/env python3
"""
Script para verificar el estado de todas las colas
"""

import asyncio
from app.services.queue_storage_service import QueueStorageService


async def check_all_queues():
    """Verificar estado de todas las colas"""
    print("🔍 VERIFICANDO ESTADO DE TODAS LAS COLAS")
    print("=" * 50)
    
    try:
        queue_service = QueueStorageService()
        
        # Listar todas las colas
        queues = await queue_service.list_queues()
        
        print(f"📋 Total de colas: {len(queues)}")
        print()
        
        for queue in queues:
            name = queue['name']
            count = queue['approximate_message_count']
            
            print(f"📋 Cola: {name}")
            print(f"   📊 Mensajes: {count}")
            
            if count > 0:
                print(f"   ⚠️ ¡Hay mensajes en esta cola!")
                
                # Intentar recibir un mensaje de muestra
                if name == "failed-processing":
                    print(f"   🔍 Verificando mensajes de fallidos...")
                    try:
                        messages = await queue_service.receive_message(
                            queue_name=name,
                            max_messages=1,
                            visibility_timeout=5
                        )
                        if messages:
                            print(f"   ✅ Mensaje de muestra recibido")
                            msg = messages[0]
                            print(f"      🆔 ID: {msg.get('message_id')}")
                            print(f"      📄 Contenido: {msg.get('content', {}).get('filename', 'N/A')}")
                        else:
                            print(f"   ⚠️ No se pudieron recibir mensajes")
                    except Exception as e:
                        print(f"   ❌ Error recibiendo mensaje: {e}")
            
            print()
        
        # Verificar salud general
        health = await queue_service.health_check()
        print(f"📊 Estado general: {health.get('status')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_all_queues())
