# app/api/router.py

from fastapi import APIRouter
from .endpoints import turnstile, procesamiento, reportes, clanes, coders

# Crear routers individuales
turnstile_router = APIRouter(prefix="/turnstile", tags=["Turnstile"])
procesamiento_router = APIRouter(prefix="/procesamiento", tags=["Procesamiento"])
reportes_router = APIRouter(prefix="/reportes", tags=["Reportes"])
clanes_router = APIRouter(prefix="/clanes", tags=["Clanes"])
coders_router = APIRouter(prefix="/coders", tags=["Coders"])

# Incluir endpoints en routers
turnstile_router.include_router(turnstile.router)
procesamiento_router.include_router(procesamiento.router)
reportes_router.include_router(reportes.router)
clanes_router.include_router(clanes.router)
coders_router.include_router(coders.router)

# Router principal que incluye todos los routers
api_router = APIRouter()
api_router.include_router(turnstile_router)
api_router.include_router(procesamiento_router)
api_router.include_router(reportes_router)
api_router.include_router(clanes_router)
api_router.include_router(coders_router)