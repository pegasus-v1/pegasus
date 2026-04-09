# API endpoints

from .turnstile import router as turnstile_router
from .procesamiento import router as procesamiento_router
from .reportes import router as reportes_router
from .clanes import router as clanes_router

__all__ = [
    "turnstile_router",
    "procesamiento_router",
    "reportes_router",
    "clanes_router"
]