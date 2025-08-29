#!/usr/bin/env python3
"""
Script para consultar datos almacenados en Azure Cosmos DB
Muestra documentos, extracciones y trabajos almacenados
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

from app.services.cosmos_service import CosmosService
from app.core.config import settings


async def mostrar_documentos_almacenados():
    """Mostrar todos los documentos almacenados"""
    print("📄 DOCUMENTOS ALMACENADOS")
    print("=" * 50)
    
    cosmos_service = CosmosService()
    
    try:
        # Obtener estadísticas
        stats = await cosmos_service.get_database_stats()
        print(f"📊 Total documentos: {stats.get('documents_count', 0)}")
        print(f"📊 Total extracciones: {stats.get('extractions_count', 0)}")
        print(f"📊 Total trabajos: {stats.get('jobs_count', 0)}")
        print()
        
        # Listar documentos
        print("📋 LISTADO DE DOCUMENTOS:")
        print("-" * 30)
        
        # Simular consulta de documentos (necesitamos implementar list_documents)
        # Por ahora usamos las estadísticas
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")


async def consultar_extracciones_por_documento():
    """Consultar extracciones de un documento específico"""
    print("\n🔍 CONSULTA DE EXTACCIONES")
    print("=" * 50)
    
    cosmos_service = CosmosService()
    
    # Ejemplo: buscar extracciones que contengan "2082463105"
    try:
        print("🔍 Buscando extracciones con '2082463105'...")
        results = await cosmos_service.search_extractions("2082463105")
        
        if results:
            print(f"✅ Encontradas {len(results)} extracciones:")
            for i, result in enumerate(results, 1):
                print(f"\n📋 Extracción {i}:")
                print(f"   ID: {result.get('id', 'N/A')}")
                print(f"   Documento ID: {result.get('document_id', 'N/A')}")
                print(f"   Fecha: {result.get('extraction_date', 'N/A')}")
                print(f"   Estrategia: {result.get('strategy_used', 'N/A')}")
                
                # Mostrar campos extraídos
                extraction_data = result.get('extraction_data', [])
                if extraction_data:
                    print(f"   📊 Campos extraídos ({len(extraction_data)}):")
                    for field in extraction_data[:3]:  # Solo primeros 3 campos
                        field_name = field.get('name', 'N/A')
                        field_value = field.get('value', 'N/A')
                        if isinstance(field_value, str) and len(field_value) > 100:
                            field_value = field_value[:100] + "..."
                        print(f"      • {field_name}: {field_value}")
                    
                    if len(extraction_data) > 3:
                        print(f"      ... y {len(extraction_data) - 3} campos más")
        else:
            print("⚠️ No se encontraron extracciones")
            
    except Exception as e:
        print(f"❌ Error consultando extracciones: {e}")


async def consultar_trabajos_de_procesamiento():
    """Consultar trabajos de procesamiento"""
    print("\n⚙️ TRABAJOS DE PROCESAMIENTO")
    print("=" * 50)
    
    cosmos_service = CosmosService()
    
    try:
        # Crear un trabajo de prueba para consultar
        job_info = {
            "document_name": "test_query_job.pdf",
            "processing_mode": "test",
            "status": "created",
            "created_at": datetime.utcnow().isoformat()
        }
        
        job_id = await cosmos_service.create_processing_job(job_info)
        print(f"✅ Trabajo de prueba creado: {job_id}")
        
        # Consultar el trabajo
        job_status = await cosmos_service.get_job_status(job_id)
        if job_status:
            print(f"📋 Estado del trabajo {job_id}:")
            print(f"   Status: {job_status.get('status', 'N/A')}")
            print(f"   Documento: {job_status.get('document_name', 'N/A')}")
            print(f"   Modo: {job_status.get('processing_mode', 'N/A')}")
            print(f"   Creado: {job_status.get('created_at', 'N/A')}")
        
        # Limpiar trabajo de prueba
        await cosmos_service.update_job_status(job_id, "deleted")
        print(f"🗑️ Trabajo de prueba eliminado")
        
    except Exception as e:
        print(f"❌ Error consultando trabajos: {e}")


async def mostrar_estadisticas_detalladas():
    """Mostrar estadísticas detalladas de la base de datos"""
    print("\n📊 ESTADÍSTICAS DETALLADAS")
    print("=" * 50)
    
    cosmos_service = CosmosService()
    
    try:
        stats = await cosmos_service.get_database_stats()
        
        print("🗄️ Base de Datos:")
        print(f"   Nombre: {stats.get('database_name', 'N/A')}")
        print(f"   Containers: {', '.join(stats.get('containers', []))}")
        
        print("\n📈 Conteos:")
        print(f"   Documentos: {stats.get('documents_count', 0)}")
        print(f"   Extracciones: {stats.get('extractions_count', 0)}")
        print(f"   Trabajos: {stats.get('jobs_count', 0)}")
        
        print("\n🔧 Estado:")
        print(f"   Salud: {stats.get('health_status', 'N/A')}")
        print(f"   Mensaje: {stats.get('health_message', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")


async def main():
    """Función principal"""
    print("🚀 CONSULTA DE DATOS EN AZURE COSMOS DB")
    print("=" * 60)
    print(f"🌐 Endpoint: {settings.azure_cosmos_endpoint}")
    print(f"🗄️ Database: {settings.azure_cosmos_database_name}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Verificar conexión
        cosmos_service = CosmosService()
        health = await cosmos_service.health_check()
        
        if health.get('status') == 'healthy':
            print("✅ Conexión a Cosmos DB exitosa")
            print()
            
            # Ejecutar consultas
            await mostrar_documentos_almacenados()
            await consultar_extracciones_por_documento()
            await consultar_trabajos_de_procesamiento()
            await mostrar_estadisticas_detalladas()
            
        else:
            print(f"❌ Cosmos DB no está saludable: {health.get('message', 'Error desconocido')}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        print("\n💡 Verifica que:")
        print("   1. La API esté ejecutándose")
        print("   2. Las credenciales de Cosmos DB sean correctas")
        print("   3. Los contenedores existan")


if __name__ == "__main__":
    asyncio.run(main())
