from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.api.router import api_router

load_dotenv()

app = FastAPI(
    title="Pegasus API",
    description="Sistema de gestión de asistencia para coders",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de la API
app.include_router(api_router, prefix="/api/v1")
# También incluir en /api para compatibilidad con frontend Infox
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Pegasus API - Sistema de gestión de asistencia",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "turnstile": "/api/v1/turnstile",
            "procesamiento": "/api/v1/procesamiento",
            "reportes": "/api/v1/reportes",
            "clanes": "/api/v1/clanes"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pegasus-api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )