#!/usr/bin/env python3
"""
Test directo del Background Worker para verificar si puede procesar mensajes
"""

import asyncio
import json
import uuid
from datetime import datetime
from app.services.background_worker import BackgroundWorker
from app.services.queue_storage_service import QueueStorageService


async def test_worker_direct():
    """Test directo del Background Worker"""
    print("🧪 TEST DIRECTO DEL BACKGROUND WORKER")
    print("=" * 60)
    
    try:
        # 1. Crear un mensaje de prueba
        test_job_id = str(uuid.uuid4())
        test_message = {
            "job_id": test_job_id,
            "filename": "test_worker_document.pdf",
            "blob_url": "https://almacenamientoidp.blob.core.windows.net/documents/test/test_document.pdf",
            "file_size_mb": 1.5,
            "processing_mode": "dual_service",
            "prompt_general": "Extrae información básica del documento",
            "fields": [
                {
                    "name": "test_field",
                    "type": "string",
                    "description": "Campo de prueba"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"📋 Mensaje de prueba creado:")
        print(f"   🆔 Job ID: {test_job_id}")
        print(f"   📄 Filename: {test_message['filename']}")
        print(f"   🎯 Mode: {test_message['processing_mode']}")
        
        # 2. Enviar mensaje a la cola
        print(f"\n📤 Enviando mensaje a la cola...")
        queue_service = QueueStorageService()
        
        message_id = await queue_service.send_message(
            message_data=test_message,
            queue_name="document-processing"
        )
        
        if message_id:
            print(f"✅ Mensaje enviado exitosamente: {message_id}")
        else:
            print(f"❌ Error enviando mensaje")
            return False
        
        # 3. Verificar que el mensaje está en la cola
        print(f"\n🔍 Verificando mensaje en la cola...")
        health = await queue_service.health_check()
        message_count = health.get('main_queue', {}).get('message_count', 0)
        print(f"📊 Mensajes en cola: {message_count}")
        
        if message_count == 0:
            print(f"⚠️ No hay mensajes en la cola")
            return False
        
        # 4. Crear worker y procesar un mensaje
        print(f"\n🔄 Creando Background Worker...")
        worker = BackgroundWorker()
        
        # 5. Procesar un ciclo del worker
        print(f"🔄 Ejecutando un ciclo del worker...")
        await worker._process_queue()
        
        # 6. Verificar si el mensaje fue procesado
        print(f"\n🔍 Verificando si el mensaje fue procesado...")
        health_after = await queue_service.health_check()
        message_count_after = health_after.get('main_queue', {}).get('message_count', 0)
        print(f"📊 Mensajes en cola después: {message_count_after}")
        
        if message_count_after < message_count:
            print(f"✅ Mensaje procesado exitosamente")
            
            # Verificar si el job se creó en Cosmos DB
            print(f"\n🗄️ Verificando job en Cosmos DB...")
            from app.services.cosmos_service import CosmosService
            cosmos_service = CosmosService()
            
            job_details = await cosmos_service.get_processing_job(test_job_id)
            if job_details:
                print(f"✅ Job encontrado en Cosmos DB:")
                print(f"   🆔 Job ID: {job_details.get('job_id')}")
                print(f"   📊 Estado: {job_details.get('status')}")
                print(f"   📄 Documento: {job_details.get('document_name')}")
            else:
                print(f"⚠️ Job no encontrado en Cosmos DB")
            
            return True
        else:
            print(f"⚠️ Mensaje no fue procesado")
            return False
        
    except Exception as e:
        print(f"❌ Error en test directo: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Función principal"""
    print("🚀 TEST DIRECTO DEL BACKGROUND WORKER")
    print("=" * 60)
    
    success = await test_worker_direct()
    
    if success:
        print(f"\n✅ TEST EXITOSO")
        print(f"   El Background Worker está funcionando correctamente")
    else:
        print(f"\n❌ TEST FALLIDO")
        print(f"   Hay un problema con el Background Worker")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())
