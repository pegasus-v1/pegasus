# app/api/endpoints/turnstile.py

import os
import tempfile
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import verify_api_key, get_db
from app.core.repositories.turnstile_repository import TurnstileImporter

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/import", summary="Importar archivo XLSX del torniquete")
async def import_turnstile(
    file: UploadFile = File(..., description="Archivo XLSX del torniquete"),
    db: Session = Depends(get_db)
):
    """
    Importa un archivo XLSX con datos del torniquete.
    
    El archivo debe tener columnas: Time, Person, ID, Status (o variaciones).
    Los registros se matchearán con coders por cédula (ID).
    """
    # Validar tipo de archivo
    if not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se aceptan archivos .xlsx"
        )
    
    # Guardar archivo temporalmente
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Guardar archivo subido
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Importar usando TurnstileImporter
        total, matched, errors = TurnstileImporter.import_and_save(temp_path, db_session=db)
        
        # Limpiar archivo temporal
        os.unlink(temp_path)
        
        return {
            "message": "Importación completada",
            "filename": file.filename,
            "total_registros": total,
            "registros_matcheados": matched,
            "registros_sin_match": total - matched,
            "errores": errors
        }
        
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la importación: {str(e)}"
        )


@router.get("/stats", summary="Estadísticas de registros del torniquete")
async def get_turnstile_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas de los registros del torniquete en la base de datos.
    """
    from app.db.models import Registro, Coder, Clan
    
    total_registros = db.query(Registro).count()
    
    # Registros por clan
    registros_por_clan = []
    clanes = db.query(Clan).all()
    for clan in clanes:
        count = db.query(Registro).join(Coder).filter(Coder.clan_id == clan.id).count()
        registros_por_clan.append({
            "clan": clan.nombre,
            "registros": count
        })
    
    return {
        "total_registros": total_registros,
        "registros_por_clan": registros_por_clan
    }