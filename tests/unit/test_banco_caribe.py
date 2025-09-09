#!/usr/bin/env python3
"""
Script para probar el sistema IDP con el documento de Banco Caribe
Usa la API completa para procesar el documento y extraer información específica
"""

import asyncio
import json
import requests
import time
from pathlib import Path
from datetime import datetime


def test_banco_caribe_document():
    """Probar procesamiento del documento de Banco Caribe usando la API"""
    print("🚀 PRUEBA COMPLETA DEL SISTEMA IDP")
    print("=" * 60)
    print(f"📄 Documento: Banco Caribe - Propuesta Perfil Transaccional IB Final.pptx")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Verificar que el documento existe
    document_path = Path("tests/Documentos/Banco Caribe - Propuesta Perfil Transaccional IB Final.pptx")
    if not document_path.exists():
        print(f"❌ Error: Documento no encontrado en {document_path}")
        return False
    
    file_size_mb = document_path.stat().st_size / (1024 * 1024)
    print(f"📏 Tamaño del documento: {file_size_mb:.2f} MB")
    
    # 2. Cargar configuración
    try:
        with open("test_banco_caribe_config.json", "r") as f:
            config = json.load(f)
        print("✅ Configuración cargada exitosamente")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False
    
    # 3. Preparar datos para la API
    print("\n📋 Preparando datos para la API...")
    
    # Convertir campos a formato JSON string para la API
    fields_config = json.dumps(config["fields"])
    prompt_general = config["prompt_general"]
    processing_mode = config["processing_mode"]
    
    print(f"   🎯 Modo de procesamiento: {processing_mode}")
    print(f"   📝 Prompt general: {prompt_general[:50]}...")
    print(f"   🔍 Campos a extraer: {len(config['fields'])}")
    
    # 4. Preparar archivo para upload
    print("\n📤 Preparando archivo para upload...")
    
    try:
        with open(document_path, "rb") as f:
            file_content = f.read()
        print(f"   ✅ Archivo leído: {len(file_content)} bytes")
    except Exception as e:
        print(f"   ❌ Error leyendo archivo: {e}")
        return False
    
    # 5. Llamar a la API
    print("\n🌐 Llamando a la API del sistema IDP...")
    
    api_url = "http://159.203.149.247:8000/api/v1/documents/process-upload"
    
    # Preparar datos multipart
    files = {
        'file': (document_path.name, file_content, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
    }
    
    data = {
        'fields_config': fields_config,
        'prompt_general': prompt_general,
        'processing_mode': processing_mode
    }
    
    try:
        print(f"   🔗 URL: {api_url}")
        print(f"   📊 Enviando request...")
        
        start_time = time.time()
        response = requests.post(api_url, files=files, data=data)
        processing_time = time.time() - start_time
        
        print(f"   ⏱️ Tiempo de respuesta: {processing_time:.2f} segundos")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API respondió exitosamente")
            
            # Procesar respuesta
            try:
                result = response.json()
                print("\n📊 RESULTADO DE LA EXTRACCIÓN:")
                print("=" * 40)
                
                # Mostrar información del trabajo
                if "job_id" in result:
                    print(f"🆔 Job ID: {result['job_id']}")
                
                if "processing_summary" in result:
                    summary = result["processing_summary"]
                    print(f"⚙️ Estado: {summary.get('processing_status', 'N/A')}")
                    print(f"⏱️ Tiempo: {summary.get('processing_time_ms', 'N/A')} ms")
                    print(f"🎯 Estrategia: {summary.get('strategy_used', 'N/A')}")
                
                # Mostrar datos extraídos
                if "extraction_data" in result:
                    extraction_data = result["extraction_data"]
                    print(f"\n🔍 DATOS EXTRAÍDOS ({len(extraction_data)} campos):")
                    print("-" * 30)
                    
                    for field in extraction_data:
                        field_name = field.get("name", "N/A")
                        field_value = field.get("value", "N/A")
                        field_type = field.get("type", "N/A")
                        confidence = field.get("confidence", "N/A")
                        
                        print(f"📋 {field_name}:")
                        print(f"   Valor: {field_value}")
                        print(f"   Tipo: {field_type}")
                        if confidence != "N/A":
                            print(f"   Confianza: {confidence}")
                        print()
                
                # Mostrar mensaje
                if "message" in result:
                    print(f"💬 Mensaje: {result['message']}")
                
                print("\n🎉 ¡EXTRACCIÓN COMPLETADA EXITOSAMENTE!")
                return True
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Error parseando respuesta JSON: {e}")
                print(f"   📝 Respuesta raw: {response.text[:200]}...")
                return False
                
        else:
            print(f"   ❌ API respondió con error: {response.status_code}")
            print(f"   📝 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error de conexión: La API no está ejecutándose")
        print("   💡 Ejecuta 'python main.py' en otra terminal")
        return False
    except Exception as e:
        print(f"   ❌ Error en la llamada a la API: {e}")
        return False


def show_test_summary():
    """Mostrar resumen de la prueba"""
    print("\n📋 RESUMEN DE LA PRUEBA")
    print("=" * 40)
    print("🎯 Objetivo: Probar extracción de propuesta de Banco Caribe")
    print("📄 Documento: Presentación PowerPoint (.pptx)")
    print("🔍 Campos a extraer:")
    print("   • Nombre de la Propuesta")
    print("   • Resumen de la propuesta (< 30 palabras)")
    print("   • Tecnología a implementar")
    print("   • Requisitos de infraestructura de Software")
    print("   • Total de horas")
    print("⚙️ Modo: hybrid_consensus (máxima precisión)")
    print("🌐 Servicios: API + Azure Storage + Cosmos DB")


def main():
    """Función principal"""
    print("🚀 PRUEBA DEL SISTEMA IDP - BANCO CARIBE")
    print("=" * 60)
    
    # Mostrar resumen
    show_test_summary()
    
    print("\n" + "="*60)
    
    # Ejecutar prueba
    success = test_banco_caribe_document()
    
    if success:
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("   El sistema IDP procesó correctamente el documento de Banco Caribe")
    else:
        print("\n❌ LA PRUEBA FALLÓ")
        print("   Revisa los logs para identificar el problema")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
