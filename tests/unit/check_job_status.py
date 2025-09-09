#!/usr/bin/env python3
"""
Script para consultar el estado de un job de procesamiento asíncrono
"""

import requests
import json
import time
from datetime import datetime


def check_job_status(job_id: str):
    """Consultar el estado de un job específico"""
    print(f"🔍 CONSULTANDO ESTADO DEL JOB")
    print("=" * 50)
    print(f"🆔 Job ID: {job_id}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Endpoint para consultar estado
    status_url = f"http://159.203.149.247:8000/api/v1/jobs/{job_id}/status"
    
    try:
        print(f"🌐 Consultando estado...")
        print(f"   🔗 URL: {status_url}")
        
        response = requests.get(status_url)
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ Estado obtenido exitosamente")
            print()
            
            # Mostrar información del estado
            print("📊 ESTADO DEL JOB:")
            print("-" * 30)
            print(f"🆔 Job ID: {status_data.get('job_id', 'N/A')}")
            print(f"⚙️ Estado: {status_data.get('status', 'N/A')}")
            print(f"📄 Documento: {status_data.get('document_name', 'N/A')}")
            print(f"🎯 Modo: {status_data.get('processing_mode', 'N/A')}")
            print(f"🕐 Creado: {status_data.get('created_at', 'N/A')}")
            
            if 'completed_at' in status_data:
                print(f"✅ Completado: {status_data.get('completed_at', 'N/A')}")
            
            if 'processing_time_ms' in status_data:
                print(f"⏱️ Tiempo: {status_data.get('processing_time_ms', 'N/A')} ms")
            
            if 'fields_extracted' in status_data:
                print(f"🔍 Campos extraídos: {status_data.get('fields_extracted', 'N/A')}")
            
            if 'error_message' in status_data:
                print(f"❌ Error: {status_data.get('error_message', 'N/A')}")
            
            return status_data.get('status', 'unknown')
            
        else:
            print(f"   ❌ Error obteniendo estado: {response.status_code}")
            print(f"   📝 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error en la consulta: {e}")
        return None


def get_job_result(job_id: str):
    """Obtener el resultado de un job completado"""
    print(f"\n🔍 OBTENIENDO RESULTADO DEL JOB")
    print("=" * 50)
    
    # Endpoint para obtener resultado
    result_url = f"http://159.203.149.247:8000/api/v1/jobs/{job_id}/result"
    
    try:
        print(f"🌐 Consultando resultado...")
        print(f"   🔗 URL: {result_url}")
        
        response = requests.get(result_url)
        
        if response.status_code == 200:
            result_data = response.json()
            print(f"   ✅ Resultado obtenido exitosamente")
            print()
            
            # Mostrar información del resultado
            print("📊 RESULTADO DE LA EXTRACCIÓN:")
            print("-" * 40)
            
            if 'extraction_data' in result_data:
                extraction_data = result_data['extraction_data']
                print(f"🔍 Campos extraídos: {len(extraction_data)}")
                print()
                
                for field in extraction_data:
                    field_name = field.get('name', 'N/A')
                    field_value = field.get('value', 'N/A')
                    field_type = field.get('type', 'N/A')
                    confidence = field.get('confidence', 'N/A')
                    
                    print(f"📋 {field_name}:")
                    print(f"   Valor: {field_value}")
                    print(f"   Tipo: {field_type}")
                    if confidence != 'N/A':
                        print(f"   Confianza: {confidence}")
                    print()
            
            if 'processing_summary' in result_data:
                summary = result_data['processing_summary']
                print(f"⚙️ RESUMEN DEL PROCESAMIENTO:")
                print(f"   Estado: {summary.get('processing_status', 'N/A')}")
                print(f"   Estrategia: {summary.get('strategy_used', 'N/A')}")
                print(f"   Tiempo: {summary.get('processing_time_ms', 'N/A')} ms")
                print(f"   Páginas: {summary.get('pages_processed', 'N/A')}")
            
            return result_data
            
        else:
            print(f"   ❌ Error obteniendo resultado: {response.status_code}")
            print(f"   📝 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error en la consulta: {e}")
        return None


def list_all_jobs():
    """Listar todos los jobs disponibles"""
    print(f"\n📋 LISTANDO TODOS LOS JOBS")
    print("=" * 50)
    
    # Endpoint para listar jobs
    jobs_url = "http://159.203.149.247:8000/api/v1/jobs"
    
    try:
        print(f"🌐 Consultando jobs...")
        print(f"   🔗 URL: {jobs_url}")
        
        response = requests.get(jobs_url)
        
        if response.status_code == 200:
            jobs_data = response.json()
            print(f"   ✅ Jobs obtenidos exitosamente")
            print()
            
            if 'jobs' in jobs_data:
                jobs = jobs_data['jobs']
                print(f"📊 Total de jobs: {len(jobs)}")
                print()
                
                for job in jobs:
                    print(f"🆔 Job ID: {job.get('job_id', 'N/A')}")
                    print(f"   📄 Documento: {job.get('document_name', 'N/A')}")
                    print(f"   ⚙️ Estado: {job.get('status', 'N/A')}")
                    print(f"   🎯 Modo: {job.get('processing_mode', 'N/A')}")
                    print(f"   🕐 Creado: {job.get('created_at', 'N/A')}")
                    print()
            
            return jobs_data
            
        else:
            print(f"   ❌ Error obteniendo jobs: {response.status_code}")
            print(f"   📝 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error en la consulta: {e}")
        return None


def monitor_job_completion(job_id: str, max_wait_minutes: int = 10):
    """Monitorear la completación de un job"""
    print(f"⏱️ MONITOREANDO COMPLETACIÓN DEL JOB")
    print("=" * 50)
    print(f"🆔 Job ID: {job_id}")
    print(f"⏰ Tiempo máximo de espera: {max_wait_minutes} minutos")
    print()
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while True:
        # Consultar estado
        status = check_job_status(job_id)
        
        if status == 'completed':
            print(f"\n🎉 ¡JOB COMPLETADO EXITOSAMENTE!")
            # Obtener resultado
            get_job_result(job_id)
            break
        elif status == 'failed':
            print(f"\n❌ JOB FALLÓ")
            break
        elif status == 'processing':
            print(f"   🔄 Procesando...")
        elif status == 'pending':
            print(f"   ⏳ En cola...")
        else:
            print(f"   ❓ Estado desconocido: {status}")
        
        # Verificar timeout
        elapsed_time = time.time() - start_time
        if elapsed_time > max_wait_seconds:
            print(f"\n⏰ TIMEOUT: Tiempo máximo de espera alcanzado")
            break
        
        # Esperar antes de la siguiente consulta
        print(f"   ⏱️ Esperando 10 segundos... (Tiempo transcurrido: {elapsed_time:.0f}s)")
        time.sleep(10)


def main():
    """Función principal"""
    print("🚀 CONSULTA DE ESTADO DE JOBS ASÍNCRONOS")
    print("=" * 60)
    
    # Job ID del test anterior
    job_id = "1b5f1645-c68b-407b-b1ae-98a5d8ef210d"
    
    print(f"🎯 Job ID a consultar: {job_id}")
    print()
    
    try:
        # 1. Consultar estado actual
        current_status = check_job_status(job_id)
        
        # 2. Si está completado, obtener resultado
        if current_status == 'completed':
            get_job_result(job_id)
        elif current_status == 'pending':
            print(f"\n⏳ El job está en cola. ¿Quieres monitorear su completación?")
            print(f"   💡 Usa: monitor_job_completion('{job_id}')")
        
        # 3. Listar todos los jobs
        list_all_jobs()
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")


if __name__ == "__main__":
    main()
