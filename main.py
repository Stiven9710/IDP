#!/usr/bin/env python3
"""
IDP Expert System - Sistema de Procesamiento Inteligente de Documentos
Punto de entrada principal de la aplicación FastAPI
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
