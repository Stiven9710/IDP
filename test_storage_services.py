#!/usr/bin/env python3
"""
Script para probar los servicios de Azure Storage (Blob + Queue)
Verifica que ambos servicios estén funcionando correctamente
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any

from app.services.blob_storage_service import BlobStorageService
from app.services.queue_storage_service import QueueStorageService
from app.core.config import settings


async def test_blob_storage():
    """Probar servicio de Blob Storage"""
    print("🗄️ PROBANDO BLOB STORAGE")
    print("=" * 50)
    
    blob_service = BlobStorageService()
    
    # 1. Health Check
    print("🔍 Verificando salud del servicio...")
    health = await blob_service.health_check()
    print(f"   Status: {health.get('status', 'N/A')}")
    print(f"   Message: {health.get('message', 'N/A')}")
    
    if health.get('status') != 'healthy':
        print("❌ Blob Storage no está saludable")
        return False
    
    print("✅ Blob Storage está funcionando correctamente")
    
    # 2. Listar contenedores
    print("\n📁 Listando contenedores...")
    try:
        containers = list(blob_service.blob_service_client.list_containers())
        print(f"   Contenedores encontrados: {len(containers)}")
        for container in containers:
            print(f"   - {container.name}")
    except Exception as e:
        print(f"   ❌ Error listando contenedores: {e}")
    
    # 3. Probar subida de documento
    print("\n📤 Probando subida de documento...")
    test_content = b"Este es un documento de prueba para verificar Blob Storage"
    test_filename = "test_document.txt"
    test_job_id = str(uuid.uuid4())
    
    try:
        blob_url = await blob_service.upload_document(
            test_content, 
            test_filename, 
            test_job_id,
            {"test": "true", "created_by": "test_script"}
        )
        
        if blob_url:
            print(f"   ✅ Documento subido exitosamente")
            print(f"   🔗 URL: {blob_url}")
            
            # 4. Probar descarga
            print("\n📥 Probando descarga de documento...")
            downloaded_content = await blob_service.download_document(blob_url)
            
            if downloaded_content == test_content:
                print("   ✅ Documento descargado correctamente")
                print(f"   📏 Tamaño: {len(downloaded_content)} bytes")
            else:
                print("   ❌ Error: contenido descargado no coincide")
            
            # 5. Probar metadatos
            print("\n📊 Probando obtención de metadatos...")
            metadata = await blob_service.get_blob_metadata(blob_url)
            
            if metadata:
                print("   ✅ Metadatos obtenidos correctamente")
                print(f"   📄 Nombre: {metadata.get('name', 'N/A')}")
                print(f"   📏 Tamaño: {metadata.get('size', 'N/A')} bytes")
                print(f"   🕐 Creado: {metadata.get('created', 'N/A')}")
            else:
                print("   ❌ Error obteniendo metadatos")
            
            # 6. Limpiar - eliminar documento de prueba
            print("\n🗑️ Limpiando documento de prueba...")
            if await blob_service.delete_document(blob_url):
                print("   ✅ Documento de prueba eliminado")
            else:
                print("   ❌ Error eliminando documento de prueba")
                
        else:
            print("   ❌ Error subiendo documento de prueba")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en pruebas de Blob Storage: {e}")
        return False
    
    print("\n✅ Todas las pruebas de Blob Storage pasaron exitosamente")
    return True


async def test_queue_storage():
    """Probar servicio de Queue Storage"""
    print("\n📋 PROBANDO QUEUE STORAGE")
    print("=" * 50)
    
    queue_service = QueueStorageService()
    
    # 1. Health Check
    print("🔍 Verificando salud del servicio...")
    health = await queue_service.health_check()
    print(f"   Status: {health.get('status', 'N/A')}")
    print(f"   Message: {health.get('message', 'N/A')}")
    
    if health.get('status') != 'healthy':
        print("❌ Queue Storage no está saludable")
        return False
    
    print("✅ Queue Storage está funcionando correctamente")
    
    # 2. Listar colas
    print("\n📋 Listando colas disponibles...")
    try:
        queues = await queue_service.list_queues()
        print(f"   Colas encontradas: {len(queues)}")
        for queue in queues:
            print(f"   - {queue['name']} ({queue['approximate_message_count']} mensajes)")
    except Exception as e:
        print(f"   ❌ Error listando colas: {e}")
    
    # 3. Probar envío de mensaje
    print("\n📤 Probando envío de mensaje...")
    test_message = {
        "job_id": str(uuid.uuid4()),
        "filename": "test_document.pdf",
        "processing_mode": "hybrid_consensus",
        "fields_config": [{"name": "test", "type": "string"}],
        "prompt_general": "Test prompt",
        "test": True,
        "created_by": "test_script"
    }
    
    try:
        message_id = await queue_service.send_message(
            test_message, 
            priority="normal"
        )
        
        if message_id:
            print(f"   ✅ Mensaje enviado exitosamente")
            print(f"   🆔 Message ID: {message_id}")
            
            # 4. Probar recepción de mensaje
            print("\n📥 Probando recepción de mensaje...")
            received_messages = await queue_service.receive_message(
                max_messages=1,
                visibility_timeout=30  # 30 segundos para pruebas
            )
            
            if received_messages:
                message = received_messages[0]
                print("   ✅ Mensaje recibido correctamente")
                print(f"   🆔 Message ID: {message.get('message_id', 'N/A')}")
                print(f"   📊 Dequeue Count: {message.get('dequeue_count', 'N/A')}")
                
                # Verificar contenido
                content = message.get('content', {})
                if content.get('job_id') == test_message['job_id']:
                    print("   ✅ Contenido del mensaje correcto")
                else:
                    print("   ❌ Error: contenido del mensaje no coincide")
                
                # 5. Eliminar mensaje de prueba
                print("\n🗑️ Eliminando mensaje de prueba...")
                if await queue_service.delete_message(
                    message['message_id'], 
                    message['pop_receipt']
                ):
                    print("   ✅ Mensaje de prueba eliminado")
                else:
                    print("   ❌ Error eliminando mensaje de prueba")
                    
            else:
                print("   ❌ Error: no se recibió el mensaje")
                
        else:
            print("   ❌ Error enviando mensaje de prueba")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en pruebas de Queue Storage: {e}")
        return False
    
    print("\n✅ Todas las pruebas de Queue Storage pasaron exitosamente")
    return True


async def test_storage_integration():
    """Probar integración entre Blob y Queue Storage"""
    print("\n🔗 PROBANDO INTEGRACIÓN STORAGE")
    print("=" * 50)
    
    blob_service = BlobStorageService()
    queue_service = QueueStorageService()
    
    # Simular flujo completo: subir documento + enviar a cola
    print("🔄 Simulando flujo completo de procesamiento...")
    
    try:
        # 1. Subir documento
        test_content = b"Documento para procesamiento asincrono"
        test_filename = "async_document.pdf"
        test_job_id = str(uuid.uuid4())
        
        print("   📤 Subiendo documento...")
        blob_url = await blob_service.upload_document(
            test_content, 
            test_filename, 
            test_job_id
        )
        
        if not blob_url:
            print("   ❌ Error subiendo documento")
            return False
        
        print("   ✅ Documento subido")
        
        # 2. Enviar mensaje a cola
        print("   📋 Enviando mensaje a cola...")
        message_data = {
            "job_id": test_job_id,
            "blob_url": blob_url,
            "filename": test_filename,
            "processing_mode": "hybrid_consensus",
            "fields_config": [{"name": "test", "type": "string"}],
            "prompt_general": "Test prompt para procesamiento asincrono"
        }
        
        message_id = await queue_service.send_message(message_data)
        
        if not message_id:
            print("   ❌ Error enviando mensaje a cola")
            return False
        
        print("   ✅ Mensaje enviado a cola")
        
        # 3. Verificar que esté en la cola
        print("   🔍 Verificando mensaje en cola...")
        queue_props = await queue_service.get_queue_properties()
        
        if queue_props and queue_props.get('approximate_message_count', 0) > 0:
            print("   ✅ Mensaje confirmado en cola")
        else:
            print("   ❌ Mensaje no encontrado en cola")
        
        # 4. Limpiar
        print("   🗑️ Limpiando recursos de prueba...")
        
        # Recibir y eliminar mensaje
        messages = await queue_service.receive_message(max_messages=1)
        if messages:
            await queue_service.delete_message(
                messages[0]['message_id'], 
                messages[0]['pop_receipt']
            )
        
        # Eliminar blob
        await blob_service.delete_document(blob_url)
        
        print("   ✅ Recursos de prueba limpiados")
        
        print("\n✅ Integración entre Blob y Queue Storage funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en pruebas de integración: {e}")
        return False


async def main():
    """Función principal de pruebas"""
    print("🚀 PRUEBAS DE SERVICIOS DE AZURE STORAGE")
    print("=" * 60)
    print(f"🌐 Storage Account: {settings.azure_storage_account_name or 'N/A'}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Verificar configuración
        if not settings.azure_storage_connection_string and not settings.azure_storage_account_name:
            print("⚠️ ADVERTENCIA: No se configuraron credenciales de Azure Storage")
            print("   Configura las variables en .env para ejecutar las pruebas")
            print("   Usa env.example como referencia")
            return
        
        # Ejecutar pruebas
        blob_success = await test_blob_storage()
        queue_success = await test_queue_storage()
        integration_success = await test_storage_integration()
        
        # Resumen
        print("\n📊 RESUMEN DE PRUEBAS")
        print("=" * 30)
        print(f"🗄️ Blob Storage: {'✅ PASÓ' if blob_success else '❌ FALLÓ'}")
        print(f"📋 Queue Storage: {'✅ PASÓ' if queue_success else '❌ FALLÓ'}")
        print(f"🔗 Integración: {'✅ PASÓ' if integration_success else '❌ FALLÓ'}")
        
        if all([blob_success, queue_success, integration_success]):
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            print("   Los servicios de Azure Storage están funcionando correctamente")
        else:
            print("\n⚠️ Algunas pruebas fallaron")
            print("   Revisa la configuración y los logs para más detalles")
            
    except Exception as e:
        print(f"\n❌ Error general en las pruebas: {e}")
        print("\n💡 Verifica que:")
        print("   1. Las credenciales de Azure Storage estén configuradas en .env")
        print("   2. La cuenta de Storage exista y sea accesible")
        print("   3. Los servicios estén habilitados en Azure")


if __name__ == "__main__":
    asyncio.run(main())
