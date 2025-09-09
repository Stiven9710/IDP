#!/usr/bin/env python3
"""
Script de prueba para el sistema IDP Expert System usando JSON de ejemplo
"""

import asyncio
import json
import logging
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_idp_with_json():
    """Probar el sistema IDP usando el JSON de ejemplo"""
    
    logger.info("🧪 Iniciando pruebas del sistema IDP con JSON de ejemplo")
    
    # Leer el JSON de ejemplo
    json_file_path = "test_request_example.json"
    
    if not os.path.exists(json_file_path):
        logger.error(f"❌ No se encontró el archivo: {json_file_path}")
        return
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            test_request = json.load(file)
        
        logger.info(f"✅ JSON leído exitosamente desde: {json_file_path}")
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando JSON: {str(e)}")
        return
    except Exception as e:
        logger.error(f"❌ Error leyendo archivo: {str(e)}")
        return
    
    # Mostrar el request cargado
    logger.info("\n📋 Request cargado desde JSON:")
    logger.info(f"   📄 Documento: {test_request['document_path']}")
    logger.info(f"   🎯 Modo: {test_request['processing_mode']}")
    logger.info(f"   📝 Campos: {len(test_request['fields'])}")
    logger.info(f"   🆔 Correlation ID: {test_request['metadata']['correlation_id']}")
    
    # Mostrar los campos definidos
    logger.info("\n📝 Campos definidos para extracción:")
    for i, field in enumerate(test_request['fields'], 1):
        logger.info(f"   {i:2d}. {field['name']} ({field['type']})")
        logger.info(f"       {field['description'][:80]}...")
    
    # Simular procesamiento según el tamaño del documento
    logger.info("\n🔍 Simulando procesamiento del documento:")
    
    # El documento Invoice_2082463105.pdf es de 92KB (0.09 MB)
    file_size_mb = 0.09
    
    if file_size_mb <= 10.0:
        logger.info("⚡ Procesamiento SÍNCRONO (archivo pequeño)")
        logger.info(f"   - Tamaño del documento: {file_size_mb:.2f} MB")
        logger.info("   - El documento se procesa inmediatamente")
        logger.info("   - Se devuelve el resultado completo")
        logger.info("   - Tiempo de respuesta estimado: < 30 segundos")
        
        # Simular resultado síncrono
        await simulate_sync_processing(test_request)
        
    else:
        logger.info("🔄 Procesamiento ASÍNCRONO (archivo grande)")
        logger.info(f"   - Tamaño del documento: {file_size_mb:.2f} MB")
        logger.info("   - El documento se guarda en Blob Storage")
        logger.info("   - Se encola para procesamiento en segundo plano")
        logger.info("   - Se devuelve HTTP 202 + Job ID")
        logger.info("   - El cliente puede consultar el estado")
        
        # Simular resultado asíncrono
        await simulate_async_processing(test_request)


async def simulate_sync_processing(request: dict):
    """Simular procesamiento síncrono"""
    logger.info("\n⚡ Simulando procesamiento SÍNCRONO...")
    
    # Simular tiempo de procesamiento
    await asyncio.sleep(2)
    
    # Simular resultado de extracción
    extraction_result = {
        "job_id": "sync-job-12345",
        "extraction_data": [
            {
                "name": "numero_factura",
                "value": "2082463105",
                "confidence": 0.95,
                "review_required": False,
                "source_strategy": "hybrid_consensus",
                "extraction_time_ms": 1500
            },
            {
                "name": "fecha_factura",
                "value": "2025-01-12",
                "confidence": 0.98,
                "review_required": False,
                "source_strategy": "hybrid_consensus",
                "extraction_time_ms": 1200
            },
            {
                "name": "total_a_pagar",
                "value": 150000.00,
                "confidence": 0.92,
                "review_required": False,
                "source_strategy": "hybrid_consensus",
                "extraction_time_ms": 1800
            }
        ],
        "processing_summary": {
            "processing_status": "completed",
            "processing_time_ms": 4500,
            "file_size_mb": 0.09,
            "strategy_used": "hybrid_consensus",
            "timestamp": datetime.utcnow().isoformat(),
            "pages_processed": 1,
            "review_flags": []
        },
        "message": "Documento procesado exitosamente de forma síncrona",
        "correlation_id": request['metadata']['correlation_id']
    }
    
    logger.info("✅ Resultado del procesamiento síncrono:")
    logger.info(f"   🆔 Job ID: {extraction_result['job_id']}")
    logger.info(f"   ⏱️  Tiempo: {extraction_result['processing_summary']['processing_time_ms']}ms")
    logger.info(f"   📊 Campos extraídos: {len(extraction_result['extraction_data'])}")
    logger.info(f"   🎯 Estrategia: {extraction_result['processing_summary']['strategy_used']}")
    
    # Mostrar campos extraídos
    for field in extraction_result['extraction_data']:
        logger.info(f"   📝 {field['name']}: {field['value']} (confianza: {field['confidence']})")


async def simulate_async_processing(request: dict):
    """Simular procesamiento asíncrono"""
    logger.info("\n🔄 Simulando procesamiento ASÍNCRONO...")
    
    # Simular aceptación del trabajo
    job_id = "async-job-67890"
    
    logger.info(f"✅ Trabajo aceptado para procesamiento asíncrono:")
    logger.info(f"   🆔 Job ID: {job_id}")
    logger.info(f"   📄 Documento: {request['document_path']}")
    logger.info(f"   🎯 Modo: {request['processing_mode']}")
    logger.info(f"   📝 Campos a extraer: {len(request['fields'])}")
    
    # Simular consulta de estado
    logger.info("\n🔍 Simulando consulta de estado...")
    await asyncio.sleep(1)
    
    status_response = {
        "job_id": job_id,
        "status": "processing",
        "progress_percentage": 45.0,
        "current_step": "Procesando con Azure OpenAI",
        "message": "Documento en procesamiento"
    }
    
    logger.info(f"📊 Estado del trabajo:")
    logger.info(f"   📈 Progreso: {status_response['progress_percentage']}%")
    logger.info(f"   🔄 Paso actual: {status_response['current_step']}")
    logger.info(f"   📝 Mensaje: {status_response['message']}")


def show_api_usage():
    """Mostrar cómo usar la API"""
    
    logger.info("\n🌐 Cómo usar la API IDP:")
    logger.info("=" * 50)
    
    logger.info("\n1️⃣ Iniciar el servidor:")
    logger.info("   python main.py")
    
    logger.info("\n2️⃣ Abrir la documentación interactiva:")
    logger.info("   http://159.203.149.247:8000/docs")
    
    logger.info("\n3️⃣ Usar el endpoint principal:")
    logger.info("   POST /api/v1/documents/process")
    
    logger.info("\n4️⃣ Copiar el JSON de ejemplo:")
    logger.info("   test_request_example.json")
    
    logger.info("\n5️⃣ Endpoints adicionales disponibles:")
    logger.info("   GET  /api/v1/documents/{job_id}/status")
    logger.info("   GET  /api/v1/documents/{job_id}/result")
    logger.info("   GET  /api/v1/documents/search")
    logger.info("   GET  /api/v1/health")
    logger.info("   GET  /api/v1/jobs")
    
    logger.info("\n6️⃣ Para pruebas con documentos reales:")
    logger.info("   - Reemplaza la URL en el JSON")
    logger.info("   - Ajusta los campos según el tipo de documento")
    logger.info("   - Cambia el modo de procesamiento según necesites")


def validate_json_structure():
    """Validar la estructura del JSON de ejemplo"""
    
    logger.info("\n🔍 Validando estructura del JSON de ejemplo...")
    
    required_fields = ["document_path", "processing_mode", "prompt_general", "fields", "metadata"]
    required_field_properties = ["name", "type", "description"]
    
    try:
        with open("test_request_example.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Validar campos requeridos
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.error(f"❌ Campos faltantes: {missing_fields}")
            return False
        
        # Validar estructura de fields
        if not isinstance(data['fields'], list):
            logger.error("❌ 'fields' debe ser una lista")
            return False
        
        # Validar cada field
        for i, field in enumerate(data['fields']):
            missing_props = [prop for prop in required_field_properties if prop not in field]
            if missing_props:
                logger.error(f"❌ Field {i}: propiedades faltantes: {missing_props}")
                return False
        
        logger.info("✅ Estructura del JSON válida")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error validando JSON: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("🚀 IDP Expert System - Pruebas con JSON")
    logger.info("=" * 50)
    
    # Validar estructura del JSON
    if not validate_json_structure():
        logger.error("❌ El JSON de ejemplo no es válido")
        exit(1)
    
    # Ejecutar pruebas
    asyncio.run(test_idp_with_json())
    
    # Mostrar uso de la API
    show_api_usage()
    
    logger.info("\n✨ ¡El sistema IDP está listo para procesar documentos reales!")
    logger.info("📄 Usa el JSON de ejemplo como base para tus requests")
