# app/api/dependencies.py

import os
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

# API Key configuration
API_KEY = os.getenv("API_KEY", "mvp-test-key-123")
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(x_api_key: str = Header(None)):
    """
    Verifica la API key proporcionada en el header.
    Para el MVP, usamos una clave simple.
    """
    if x_api_key == API_KEY:
        return x_api_key
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
        headers={"WWW-Authenticate": "APIKey"},
    )


def get_db() -> Session:
    """
    Dependencia para obtener sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()