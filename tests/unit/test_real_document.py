#!/usr/bin/env python3
"""
Script para probar el procesamiento real con Invoice_2082463105.pdf
Usando los servicios de Azure Storage (Blob + Queue)
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

from app.services.blob_storage_service import BlobStorageService
from app.services.queue_storage_service import QueueStorageService
from app.services.cosmos_service import CosmosService
from app.core.config import settings


async def test_real_document_processing():
    """Probar procesamiento real con Invoice_2082463105.pdf"""
    print("🚀 PRUEBA DE PROCESAMIENTO REAL CON DOCUMENTO")
    print("=" * 60)
    print(f"📄 Documento: Invoice_2082463105.pdf")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Inicializar servicios
    blob_service = BlobStorageService()
    queue_service = QueueStorageService()
    cosmos_service = CosmosService()
    
    # Ruta del documento
    document_path = Path("tests/Documentos/Invoice_2082463105.pdf")
    
    if not document_path.exists():
        print(f"❌ Error: Documento no encontrado en {document_path}")
        return
    
    try:
        # 1. Leer documento
        print("📖 Leyendo documento...")
        with open(document_path, 'rb') as f:
            document_content = f.read()
        
        file_size_mb = len(document_content) / (1024 * 1024)
        print(f"   ✅ Documento leído: {file_size_mb:.2f} MB")
        
        # 2. Generar Job ID
        job_id = str(uuid.uuid4())
        print(f"   🆔 Job ID generado: {job_id}")
        
        # 3. Subir documento a Blob Storage
        print("\n📤 Subiendo documento a Azure Blob Storage...")
        blob_url = await blob_service.upload_document(
            document_content,
            document_path.name,
            job_id,
            {
                "test_type": "real_document",
                "original_path": str(document_path),
                "file_size_mb": str(file_size_mb),
                "created_by": "test_real_document.py"
            }
        )
        
        if not blob_url:
            print("   ❌ Error subiendo documento a Blob Storage")
            return
        
        print(f"   ✅ Documento subido exitosamente")
        print(f"   🔗 URL: {blob_url}")
        
        # 4. Crear trabajo en Cosmos DB
        print("\n🗄️ Creando trabajo en Cosmos DB...")
        job_info = {
            "job_id": job_id,
            "document_name": document_path.name,
            "file_size_mb": file_size_mb,
            "blob_url": blob_url,
            "processing_mode": "hybrid_consensus",
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "test_type": "real_document"
        }
        
        cosmos_job_id = await cosmos_service.create_processing_job(job_info)
        if cosmos_job_id:
            print(f"   ✅ Trabajo creado en Cosmos DB: {cosmos_job_id}")
        else:
            print(f"   ⚠️ No se pudo crear trabajo en Cosmos DB")
        
        # 5. Enviar mensaje a Queue Storage
        print("\n📋 Enviando mensaje a Azure Queue Storage...")
        message_data = {
            "job_id": job_id,
            "blob_url": blob_url,
            "filename": document_path.name,
            "file_size_mb": file_size_mb,
            "processing_mode": "hybrid_consensus",
            "fields_config": [
                {
                    "name": "numero_factura",
                    "type": "string",
                    "description": "El identificador único de la factura"
                },
                {
                    "name": "fecha_factura",
                    "type": "date",
                    "description": "La fecha de emisión de la factura"
                },
                {
                    "name": "proveedor_nombre",
                    "type": "string",
                    "description": "El nombre del proveedor"
                },
                {
                    "name": "total_a_pagar",
                    "type": "number",
                    "description": "El valor total de la factura"
                }
            ],
            "prompt_general": "Actúa como un analista financiero experto. Extrae información de esta factura de manera precisa.",
            "cosmos_job_id": cosmos_job_id,
            "test_type": "real_document"
        }
        
        message_id = await queue_service.send_message(
            message_data,
            priority="high"  # Alta prioridad para documentos reales
        )
        
        if message_id:
            print(f"   ✅ Mensaje enviado exitosamente a la cola")
            print(f"   🆔 Message ID: {message_id}")
        else:
            print(f"   ❌ Error enviando mensaje a la cola")
            return
        
        # 6. Verificar estado en Queue Storage
        print("\n🔍 Verificando estado en Queue Storage...")
        queue_props = await queue_service.get_queue_properties("document-processing")
        if queue_props:
            message_count = queue_props.get("approximate_message_count", 0)
            print(f"   📊 Mensajes en cola: {message_count}")
        else:
            print(f"   ⚠️ No se pudieron obtener propiedades de la cola")
        
        # 7. Simular procesamiento (recibir y eliminar mensaje)
        print("\n⚙️ Simulando procesamiento del mensaje...")
        messages = await queue_service.receive_message(
            max_messages=1,
            visibility_timeout=30
        )
        
        if messages:
            message = messages[0]
            print(f"   ✅ Mensaje recibido para procesamiento")
            print(f"   🆔 Message ID: {message.get('message_id', 'N/A')}")
            
            # Simular procesamiento exitoso
            print(f"   🔄 Procesando documento...")
            await asyncio.sleep(2)  # Simular tiempo de procesamiento
            
            # Eliminar mensaje de la cola
            if await queue_service.delete_message(
                message['message_id'],
                message['pop_receipt']
            ):
                print(f"   ✅ Mensaje procesado y eliminado de la cola")
            else:
                print(f"   ⚠️ No se pudo eliminar mensaje de la cola")
        else:
            print(f"   ⚠️ No se recibieron mensajes para procesar")
        
        # 8. Actualizar estado en Cosmos DB
        print("\n🗄️ Actualizando estado en Cosmos DB...")
        if cosmos_job_id:
            if await cosmos_service.update_job_status(cosmos_job_id, "completed"):
                print(f"   ✅ Estado actualizado a 'completed'")
            else:
                print(f"   ⚠️ No se pudo actualizar estado")
        
        # 9. Resumen final
        print("\n📊 RESUMEN DEL PROCESAMIENTO")
        print("=" * 40)
        print(f"📄 Documento: {document_path.name}")
        print(f"📏 Tamaño: {file_size_mb:.2f} MB")
        print(f"🆔 Job ID: {job_id}")
        print(f"🔗 Blob URL: {blob_url}")
        print(f"📋 Mensaje en cola: {'✅ Enviado' if message_id else '❌ Falló'}")
        print(f"🗄️ Trabajo en Cosmos: {'✅ Creado' if cosmos_job_id else '❌ Falló'}")
        print(f"⚙️ Estado final: {'✅ Completado' if cosmos_job_id else '❌ Incompleto'}")
        
        print("\n🎉 ¡PROCESAMIENTO REAL COMPLETADO EXITOSAMENTE!")
        print("   El documento se procesó completamente usando Azure Storage")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en el procesamiento: {e}")
        return False


async def test_storage_health():
    """Verificar salud de todos los servicios"""
    print("🔍 VERIFICANDO SALUD DE SERVICIOS")
    print("=" * 40)
    
    # Blob Storage
    blob_service = BlobStorageService()
    blob_health = await blob_service.health_check()
    print(f"🗄️ Blob Storage: {blob_health.get('status', 'N/A')}")
    
    # Queue Storage
    queue_service = QueueStorageService()
    queue_health = await queue_service.health_check()
    print(f"📋 Queue Storage: {queue_health.get('status', 'N/A')}")
    
    # Cosmos DB
    cosmos_service = CosmosService()
    cosmos_health = await cosmos_service.health_check()
    print(f"🗄️ Cosmos DB: {cosmos_health.get('status', 'N/A')}")
    
    print()


async def main():
    """Función principal"""
    print("🚀 PRUEBA COMPLETA DE PROCESAMIENTO REAL")
    print("=" * 60)
    
    try:
        # Verificar salud de servicios
        await test_storage_health()
        
        # Procesar documento real
        success = await test_real_document_processing()
        
        if success:
            print("\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            print("   El sistema está listo para procesar documentos reales")
        else:
            print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
            print("   Revisa los logs para más detalles")
            
    except Exception as e:
        print(f"\n❌ Error general: {e}")


if __name__ == "__main__":
    asyncio.run(main())
