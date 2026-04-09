# app/api/endpoints/coders.py
# Endpoints para gestión de coders/estudiantes

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api.dependencies import verify_api_key, get_db
from app.db.models import Coder, Clan, Registro, ResumenDiario, Incidencia

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/estudiantes", summary="Lista de todos los coders/estudiantes")
async def get_estudiantes(
    clan_id: Optional[int] = Query(None, description="Filtrar por clan"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de todos los coders (estudiantes) en el sistema.
    Compatible con el frontend original de Infox.
    """
    query = db.query(Coder)
    
    if clan_id:
        query = query.filter_by(clan_id=clan_id)
    
    coders = query.order_by(Coder.nombre).all()
    
    estudiantes = []
    for coder in coders:
        # Obtener estadísticas básicas
        total_registros = db.query(Registro).filter_by(coder_id=coder.id).count()
        ultima_fecha = db.query(Registro.fecha)\
            .filter_by(coder_id=coder.id)\
            .order_by(Registro.fecha.desc())\
            .first()
        
        estudiantes.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "email": coder.email,
            "clan_id": coder.clan_id,
            "clan_nombre": coder.clan.nombre if coder.clan else None,
            "total_registros": total_registros,
            "ultima_fecha": ultima_fecha[0] if ultima_fecha else None
        })
    
    return estudiantes


@router.get("/estudiantes/{coder_id}/historial", summary="Historial de asistencia de un coder")
async def get_historial_coder(
    coder_id: int,
    dias: Optional[int] = Query(30, description="Número de días hacia atrás (default: 30)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de asistencia de un coder.
    Compatible con el frontend original de Infox.
    """
    from datetime import date, timedelta
    
    coder = db.query(Coder).filter_by(id=coder_id).first()
    if not coder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coder con ID {coder_id} no encontrado"
        )
    
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=dias)
    
    # Obtener resúmenes en el rango
    resumenes = db.query(ResumenDiario).filter(
        ResumenDiario.coder_id == coder_id,
        ResumenDiario.fecha >= fecha_inicio,
        ResumenDiario.fecha <= fecha_fin
    ).order_by(ResumenDiario.fecha.desc()).all()
    
    historial = []
    for resumen in resumenes:
        # Obtener incidencias para este resumen
        incidencias = db.query(Incidencia).filter_by(resumen_id=resumen.id).all()
        
        historial.append({
            "fecha": resumen.fecha,
            "estado_entrada": resumen.estado_entrada,
            "minutos_retardo": resumen.minutos_retardo,
            "estado_salida": resumen.estado_salida,
            "tiempo_trabajado_min": resumen.tiempo_trabajado_min,
            "ausente": resumen.ausente,
            "incidencias": [
                {
                    "tipo": inc.tipo,
                    "descripcion": inc.descripcion,
                    "minutos": inc.minutos
                }
                for inc in incidencias
            ]
        })
    
    return {
        "coder": {
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None
        },
        "historial": historial,
        "rango": {
            "inicio": fecha_inicio,
            "fin": fecha_fin,
            "dias": dias
        }
    }


@router.get("/buscar", summary="Buscar coders por nombre o cédula")
async def buscar_coders(
    q: str = Query(..., description="Término de búsqueda (nombre o cédula)"),
    db: Session = Depends(get_db)
):
    """
    Busca coders por nombre o cédula.
    Compatible con el frontend original de Infox.
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El término de búsqueda debe tener al menos 2 caracteres"
        )
    
    term = f"%{q.strip()}%"
    
    coders = db.query(Coder).filter(
        or_(
            Coder.nombre.ilike(term),
            Coder.cedula.ilike(term)
        )
    ).order_by(Coder.nombre).limit(50).all()
    
    resultados = []
    for coder in coders:
        resultados.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "email": coder.email,
            "clan": coder.clan.nombre if coder.clan else None
        })
    
    return {
        "query": q,
        "resultados": resultados,
        "total": len(resultados)
    }


@router.get("/buscar/detalle", summary="Detalle de un coder en una fecha específica")
async def detalle_coder_fecha(
    id: int = Query(..., description="ID del coder"),
    fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de asistencia de un coder en una fecha específica.
    Compatible con el frontend original de Infox.
    """
    from datetime import datetime
    
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )
    
    coder = db.query(Coder).filter_by(id=id).first()
    if not coder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coder con ID {id} no encontrado"
        )
    
    # Obtener resumen del día
    resumen = db.query(ResumenDiario).filter(
        ResumenDiario.coder_id == id,
        ResumenDiario.fecha == fecha_obj
    ).first()
    
    if not resumen:
        # No hay resumen procesado para esta fecha
        return {
            "coder": {
                "id": coder.id,
                "nombre": coder.nombre,
                "cedula": coder.cedula,
                "clan": coder.clan.nombre if coder.clan else None
            },
            "fecha": fecha_obj,
            "procesado": False,
            "mensaje": "No hay datos procesados para esta fecha"
        }
    
    # Obtener incidencias
    incidencias = db.query(Incidencia).filter_by(resumen_id=resumen.id).all()
    
    # Obtener registros originales del torniquete
    registros = db.query(Registro).filter(
        Registro.coder_id == id,
        Registro.fecha == fecha_obj
    ).order_by(Registro.hora).all()
    
    return {
        "coder": {
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None
        },
        "fecha": fecha_obj,
        "procesado": True,
        "resumen": {
            "estado_entrada": resumen.estado_entrada,
            "minutos_retardo": resumen.minutos_retardo,
            "estado_salida": resumen.estado_salida,
            "salida_inferida": resumen.salida_inferida,
            "tiempo_trabajado_min": resumen.tiempo_trabajado_min,
            "ausente": resumen.ausente
        },
        "incidencias": [
            {
                "tipo": inc.tipo,
                "descripcion": inc.descripcion,
                "minutos": inc.minutos
            }
            for inc in incidencias
        ],
        "registros": [
            {
                "id": reg.id,
                "hora": reg.hora.strftime("%H:%M:%S") if reg.hora else None,
                "estado_acceso": reg.estado_acceso,
                "tipo_evento": reg.tipo_evento,
                "dispositivo": reg.dispositivo
            }
            for reg in registros
        ]
    }