#!/usr/bin/env python3
"""
Script para verificar mensajes en la cola de fallidos
"""

import asyncio
from app.services.queue_storage_service import QueueStorageService


async def check_failed_messages():
    """Verificar mensajes en la cola de fallidos"""
    print("🔍 VERIFICANDO MENSAJES EN COLA DE FALLIDOS")
    print("=" * 60)
    
    try:
        queue_service = QueueStorageService()
        
        # Verificar cola de fallidos
        print(f"📋 Verificando cola de fallidos...")
        
        # Recibir todos los mensajes de la cola de fallidos
        failed_messages = await queue_service.receive_message(
            queue_name="failed-processing",
            max_messages=10,
            visibility_timeout=30
        )
        
        if failed_messages:
            print(f"✅ Encontrados {len(failed_messages)} mensajes fallidos")
            print()
            
            for i, msg in enumerate(failed_messages):
                print(f"📄 Mensaje Fallido {i+1}:")
                print(f"   🆔 ID: {msg.get('message_id')}")
                print(f"   📄 Contenido: {msg.get('content', {}).get('filename', 'N/A')}")
                print(f"   🎯 Job ID: {msg.get('content', {}).get('job_id', 'N/A')}")
                print(f"   ❌ Error: {msg.get('content', {}).get('error_message', 'N/A')}")
                print(f"   🕐 Falló: {msg.get('content', {}).get('failed_at', 'N/A')}")
                print()
                
                # Buscar específicamente el documento de Banco Caribe
                filename = msg.get('content', {}).get('filename', '')
                if 'Banco Caribe' in filename or 'Propuesta Perfil Transaccional' in filename:
                    print(f"🎯 ¡ENCONTRADO! Documento de Banco Caribe:")
                    print(f"   📄 Filename: {filename}")
                    print(f"   🆔 Job ID: {msg.get('content', {}).get('job_id')}")
                    print(f"   ❌ Error: {msg.get('content', {}).get('error_message')}")
                    print(f"   🎯 Processing Mode: {msg.get('content', {}).get('processing_mode')}")
                    print()
        else:
            print(f"⚠️ No se encontraron mensajes en la cola de fallidos")
        
        # Verificar cola principal
        print(f"\n📋 Verificando cola principal...")
        health = await queue_service.health_check()
        main_queue_count = health.get('main_queue', {}).get('message_count', 0)
        print(f"📊 Mensajes en cola principal: {main_queue_count}")
        
        if main_queue_count == 0:
            print(f"✅ Cola principal vacía (todos los mensajes procesados)")
        else:
            print(f"⚠️ Hay mensajes pendientes en la cola principal")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_failed_messages())
