"""
IDP Expert System - Aplicación principal FastAPI
"""

import asyncio
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings, get_cors_origins
from app.api.v1.router import api_router
from app.services.background_worker import BackgroundWorker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando IDP Expert System...")
    
    # Iniciar Background Worker en un hilo separado
    print("🔄 Iniciando Background Worker...")
    background_worker = BackgroundWorker()
    
    def run_worker():
        """Ejecutar el worker en un hilo separado"""
        try:
            asyncio.run(background_worker.start())
        except Exception as e:
            print(f"❌ Error en Background Worker: {e}")
    
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()
    print("✅ Background Worker iniciado en segundo plano")
    
    yield
    
    # Shutdown
    print("🛑 Cerrando IDP Expert System...")
    print("🔄 Deteniendo Background Worker...")
    try:
        # Crear un nuevo event loop para detener el worker
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(background_worker.stop())
        loop.close()
        print("✅ Background Worker detenido")
    except Exception as e:
        print(f"❌ Error deteniendo Background Worker: {e}")


# Crear instancia de FastAPI
app = FastAPI(
    title="IDP Expert System",
    description="Sistema de Procesamiento Inteligente de Documentos con FastAPI y Azure",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar hosts confiables
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # En producción, especificar hosts específicos
)

# Incluir routers de la API
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Endpoint raíz de la aplicación"""
    return {
        "message": "IDP Expert System - API de Procesamiento Inteligente de Documentos",
        "version": "2.0.0",
        "status": "active",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {
        "status": "healthy",
        "service": "IDP Expert System",
        "version": "2.0.0"
    }
