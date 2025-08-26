#!/usr/bin/env python3
"""
Script para ejecutar el Background Worker de forma independiente
Procesa documentos de la cola de Azure Storage de forma asíncrona
"""

import asyncio
import signal
import sys
from app.services.background_worker import BackgroundWorker


async def main():
    """Función principal"""
    print("🚀 INICIANDO BACKGROUND WORKER")
    print("=" * 50)
    print("📋 Funcionalidades:")
    print("   • Procesa cola de Azure Storage")
    print("   • Ejecuta Document Intelligence + GPT-4o")
    print("   • Guarda resultados en Cosmos DB")
    print("   • Actualiza estados de jobs")
    print()
    
    # Crear worker
    worker = BackgroundWorker()
    
    # Configurar manejo de señales para detener gracefully
    def signal_handler(signum, frame):
        print(f"\n🛑 Señal recibida: {signum}")
        asyncio.create_task(worker.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🔄 Iniciando worker...")
        print("   💡 Presiona Ctrl+C para detener")
        print()
        
        # Iniciar worker
        await worker.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Worker detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el worker: {e}")
    finally:
        print("🔄 Cerrando worker...")
        await worker.stop()
        print("✅ Worker cerrado correctamente")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Worker detenido")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)
