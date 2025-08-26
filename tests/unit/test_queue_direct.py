#!/usr/bin/env python3
"""
Script simple para probar directamente la funcionalidad de la cola
"""

import asyncio
from app.services.queue_storage_service import QueueStorageService


async def test_queue():
    """Probar la funcionalidad de la cola directamente"""
    print("🧪 PROBANDO COLA DIRECTAMENTE")
    print("=" * 40)
    
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
        
        # Intentar recibir mensaje
        print(f"\n📥 Intentando recibir mensaje...")
        messages = await queue_service.receive_message(
            max_messages=1,
            visibility_timeout=30
        )
        
        if messages:
            print(f"✅ Mensaje recibido: {len(messages)}")
            for msg in messages:
                print(f"   🆔 Message ID: {msg.get('message_id')}")
                print(f"   📄 Contenido: {msg.get('content', {}).get('filename', 'N/A')}")
        else:
            print(f"⚠️ No se recibieron mensajes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_queue())
