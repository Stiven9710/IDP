"""
Router principal de la API v1 para IDP Expert System
"""

from fastapi import APIRouter
from app.api.v1.endpoints import documents, health, jobs

# Crear router principal de la API v1
api_router = APIRouter()

# Incluir routers de endpoints específicos
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

api_router.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["jobs"]
)
