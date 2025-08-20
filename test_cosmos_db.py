#!/usr/bin/env python3
"""
Script de prueba para Azure Cosmos DB
Verifica la conexión y operaciones básicas
"""

import asyncio
import json
import logging
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.cosmos_service import CosmosService
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cosmos_connection():
    """Probar conexión básica a Cosmos DB"""
    print("🔍 Probando conexión a Azure Cosmos DB...")
    
    try:
        # Crear servicio
        cosmos_service = CosmosService()
        
        # Verificar salud
        health_status = await cosmos_service.health_check()
        print(f"📊 Estado de salud: {health_status['status']}")
        print(f"💬 Mensaje: {health_status['message']}")
        
        if health_status['status'] == 'healthy':
            print("✅ Cosmos DB está funcionando correctamente")
            return True
        else:
            print(f"❌ Cosmos DB no está disponible: {health_status['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando conexión: {str(e)}")
        return False

async def test_document_operations():
    """Probar operaciones básicas con documentos"""
    print("\n📄 Probando operaciones con documentos...")
    
    try:
        cosmos_service = CosmosService()
        
        # Crear documento de prueba
        test_document = {
            "filename": "test_document.pdf",
            "file_size_mb": 0.1,
            "file_type": "pdf",
            "status": "test",
            "processing_mode": "gpt_vision_only",
            "correlation_id": "test-123"
        }
        
        # Guardar documento
        doc_id = await cosmos_service.save_document(test_document)
        if doc_id:
            print(f"✅ Documento guardado con ID: {doc_id}")
            
            # Recuperar documento
            retrieved_doc = await cosmos_service.get_document(doc_id)
            if retrieved_doc:
                print(f"✅ Documento recuperado: {retrieved_doc['filename']}")
                
                # Actualizar estado
                success = await cosmos_service.update_document_status(
                    doc_id, 
                    "processed", 
                    processing_time_ms=1500
                )
                if success:
                    print("✅ Estado del documento actualizado")
                else:
                    print("❌ Error actualizando estado")
            else:
                print("❌ Error recuperando documento")
        else:
            print("❌ Error guardando documento")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error en operaciones de documentos: {str(e)}")
        return False

async def test_extraction_operations():
    """Probar operaciones con extracciones"""
    print("\n🔍 Probando operaciones con extracciones...")
    
    try:
        cosmos_service = CosmosService()
        
        # Crear extracción de prueba
        test_extraction = {
            "document_id": "doc_test_123",
            "extraction_date": datetime.utcnow().isoformat(),
            "processing_time_ms": 2500,
            "strategy_used": "hybrid_consensus",
            "extraction_data": [
                {
                    "name": "numero_factura",
                    "value": "TEST-001",
                    "confidence": "high",
                    "source": "consensus"
                },
                {
                    "name": "total_a_pagar",
                    "value": 100.50,
                    "confidence": "high",
                    "source": "consensus"
                }
            ],
            "processing_summary": {
                "processing_status": "completed",
                "pages_processed": 1,
                "review_flags": []
            }
        }
        
        # Guardar extracción
        ext_id = await cosmos_service.save_extraction_result(test_extraction)
        if ext_id:
            print(f"✅ Extracción guardada con ID: {ext_id}")
            
            # Buscar extracciones
            search_results = await cosmos_service.search_extractions("TEST-001")
            if search_results:
                print(f"✅ Búsqueda exitosa: {len(search_results)} resultados")
            else:
                print("⚠️ No se encontraron resultados en la búsqueda")
                
        else:
            print("❌ Error guardando extracción")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error en operaciones de extracciones: {str(e)}")
        return False

async def test_job_operations():
    """Probar operaciones con trabajos de procesamiento"""
    print("\n⚙️ Probando operaciones con trabajos...")
    
    try:
        cosmos_service = CosmosService()
        
        # Crear trabajo de prueba
        test_job = {
            "document_id": "doc_test_123",
            "job_type": "extraction",
            "priority": "normal",
            "estimated_duration_minutes": 5
        }
        
        # Crear trabajo
        job_id = await cosmos_service.create_processing_job(test_job)
        if job_id:
            print(f"✅ Trabajo creado con ID: {job_id}")
            
            # Actualizar progreso
            success = await cosmos_service.update_job_status(
                job_id, 
                "processing", 
                progress=50,
                current_step="AI processing"
            )
            if success:
                print("✅ Progreso del trabajo actualizado")
                
                # Obtener estado
                job_status = await cosmos_service.get_job_status(job_id)
                if job_status:
                    print(f"✅ Estado del trabajo: {job_status['status']} - {job_status['progress']}%")
                else:
                    print("❌ Error obteniendo estado del trabajo")
            else:
                print("❌ Error actualizando progreso del trabajo")
                
        else:
            print("❌ Error creando trabajo")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error en operaciones de trabajos: {str(e)}")
        return False

async def test_database_stats():
    """Probar obtención de estadísticas de la base de datos"""
    print("\n📊 Probando estadísticas de la base de datos...")
    
    try:
        cosmos_service = CosmosService()
        
        stats = await cosmos_service.get_database_stats()
        if stats:
            print("✅ Estadísticas obtenidas:")
            print(f"   📁 Database: {stats.get('database_name', 'N/A')}")
            print(f"   📦 Containers: {list(stats.get('containers', {}).keys())}")
            print(f"   📄 Documentos: {stats.get('documents_count', 'N/A')}")
            print(f"   🔍 Extracciones: {stats.get('extractions_count', 'N/A')}")
            print(f"   ⚙️ Trabajos: {stats.get('jobs_count', 'N/A')}")
        else:
            print("❌ Error obteniendo estadísticas")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {str(e)}")
        return False

async def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de Azure Cosmos DB")
    print("=" * 50)
    
    # Verificar configuración
    print("🔧 Verificando configuración...")
    if not settings.azure_cosmos_endpoint or not settings.azure_cosmos_key:
        print("❌ Cosmos DB no configurado en .env")
        print("   Asegúrate de tener:")
        print("   - AZURE_COSMOS_ENDPOINT")
        print("   - AZURE_COSMOS_KEY")
        return
    
    print("✅ Configuración encontrada")
    
    # Ejecutar pruebas
    tests = [
        ("Conexión", test_cosmos_connection),
        ("Documentos", test_document_operations),
        ("Extracciones", test_extraction_operations),
        ("Trabajos", test_job_operations),
        ("Estadísticas", test_database_stats)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en prueba {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {total} | Pasaron: {passed} | Fallaron: {total - passed}")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! Cosmos DB está funcionando correctamente")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa la configuración y los logs")

if __name__ == "__main__":
    asyncio.run(main())
