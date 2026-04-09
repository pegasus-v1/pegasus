# app/api/endpoints/clanes.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from datetime import time
from app.api.dependencies import verify_api_key, get_db
from app.db.models import Clan, ConfiguracionClan, Coder

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/", summary="Listar todos los clanes")
async def list_clanes(
    incluir_configuracion: bool = Query(False, description="Incluir configuración detallada"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de todos los clanes en el sistema.
    """
    clanes = db.query(Clan).all()
    
    resultado = []
    for clan in clanes:
        clan_data = {
            "id": clan.id,
            "nombre": clan.nombre,
            "hora_entrada": clan.hora_entrada.strftime("%H:%M") if clan.hora_entrada else None,
            "hora_salida": clan.hora_salida.strftime("%H:%M") if clan.hora_salida else None,
            "tiempo_alimentacion_minutos": clan.tiempo_alimentacion_minutos,
            "total_coders": db.query(Coder).filter_by(clan_id=clan.id).count()
        }
        
        if incluir_configuracion:
            config = db.query(ConfiguracionClan).filter_by(clan_id=clan.id).first()
            if config:
                clan_data["configuracion"] = {
                    "tolerancia_entrada_min": config.tolerancia_entrada_min,
                    "tolerancia_retardo_leve": config.tolerancia_retardo_leve,
                    "tolerancia_retardo_grave": config.tolerancia_retardo_grave,
                    "tolerancia_salida_min": config.tolerancia_salida_min,
                    "break1_inicio": config.break1_inicio.strftime("%H:%M") if config.break1_inicio else None,
                    "break1_fin": config.break1_fin.strftime("%H:%M") if config.break1_fin else None,
                    "break1_tolerancia": config.break1_tolerancia,
                    "break2_inicio": config.break2_inicio.strftime("%H:%M") if config.break2_inicio else None,
                    "break2_fin": config.break2_fin.strftime("%H:%M") if config.break2_fin else None,
                    "break2_tolerancia": config.break2_tolerancia,
                    "fuga_minutos_limite": config.fuga_minutos_limite
                }
        
        resultado.append(clan_data)
    
    return {
        "total_clanes": len(resultado),
        "clanes": resultado
    }


@router.get("/{clan_id}", summary="Obtener clan por ID")
async def get_clan(
    clan_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene información detallada de un clan específico.
    """
    clan = db.query(Clan).filter_by(id=clan_id).first()
    if not clan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clan con ID {clan_id} no encontrado"
        )
    
    config = db.query(ConfiguracionClan).filter_by(clan_id=clan_id).first()
    
    # Obtener coders de este clan
    coders = db.query(Coder).filter_by(clan_id=clan_id).all()
    
    return {
        "id": clan.id,
        "nombre": clan.nombre,
        "hora_entrada": clan.hora_entrada.strftime("%H:%M") if clan.hora_entrada else None,
        "hora_salida": clan.hora_salida.strftime("%H:%M") if clan.hora_salida else None,
        "tiempo_alimentacion_minutos": clan.tiempo_alimentacion_minutos,
        "configuracion": {
            "tolerancia_entrada_min": config.tolerancia_entrada_min if config else 20,
            "tolerancia_retardo_leve": config.tolerancia_retardo_leve if config else 40,
            "tolerancia_retardo_grave": config.tolerancia_retardo_grave if config else 60,
            "tolerancia_salida_min": config.tolerancia_salida_min if config else 10,
            "break1_inicio": config.break1_inicio.strftime("%H:%M") if config and config.break1_inicio else None,
            "break1_fin": config.break1_fin.strftime("%H:%M") if config and config.break1_fin else None,
            "break1_tolerancia": config.break1_tolerancia if config else 5,
            "break2_inicio": config.break2_inicio.strftime("%H:%M") if config and config.break2_inicio else None,
            "break2_fin": config.break2_fin.strftime("%H:%M") if config and config.break2_fin else None,
            "break2_tolerancia": config.break2_tolerancia if config else 5,
            "fuga_minutos_limite": config.fuga_minutos_limite if config else 30
        } if config else None,
        "coders": [
            {
                "id": coder.id,
                "nombre": coder.nombre,
                "cedula": coder.cedula,
                "email": coder.email
            }
            for coder in coders
        ],
        "total_coders": len(coders)
    }


@router.put("/{clan_id}/configuracion", summary="Actualizar configuración de un clan")
async def update_configuracion_clan(
    clan_id: int,
    tolerancia_entrada_min: Optional[int] = Body(None, description="Tolerancia entrada (minutos)"),
    tolerancia_retardo_leve: Optional[int] = Body(None, description="Tolerancia retardo leve (minutos)"),
    tolerancia_retardo_grave: Optional[int] = Body(None, description="Tolerancia retardo grave (minutos)"),
    tolerancia_salida_min: Optional[int] = Body(None, description="Tolerancia salida anticipada (minutos)"),
    break1_inicio: Optional[str] = Body(None, description="Break 1 inicio (HH:MM)"),
    break1_fin: Optional[str] = Body(None, description="Break 1 fin (HH:MM)"),
    break1_tolerancia: Optional[int] = Body(None, description="Tolerancia break 1 (minutos)"),
    break2_inicio: Optional[str] = Body(None, description="Break 2 inicio (HH:MM)"),
    break2_fin: Optional[str] = Body(None, description="Break 2 fin (HH:MM)"),
    break2_tolerancia: Optional[int] = Body(None, description="Tolerancia break 2 (minutos)"),
    fuga_minutos_limite: Optional[int] = Body(None, description="Límite minutos para considerar fuga"),
    db: Session = Depends(get_db)
):
    """
    Actualiza la configuración de un clan (tolerancias, breaks, etc.).
    """
    # Verificar que el clan existe
    clan = db.query(Clan).filter_by(id=clan_id).first()
    if not clan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clan con ID {clan_id} no encontrado"
        )
    
    # Obtener o crear configuración
    config = db.query(ConfiguracionClan).filter_by(clan_id=clan_id).first()
    if not config:
        config = ConfiguracionClan(clan_id=clan_id)
        db.add(config)
    
    # Actualizar campos proporcionados
    if tolerancia_entrada_min is not None:
        config.tolerancia_entrada_min = tolerancia_entrada_min
    if tolerancia_retardo_leve is not None:
        config.tolerancia_retardo_leve = tolerancia_retardo_leve
    if tolerancia_retardo_grave is not None:
        config.tolerancia_retardo_grave = tolerancia_retardo_grave
    if tolerancia_salida_min is not None:
        config.tolerancia_salida_min = tolerancia_salida_min
    if break1_tolerancia is not None:
        config.break1_tolerancia = break1_tolerancia
    if break2_tolerancia is not None:
        config.break2_tolerancia = break2_tolerancia
    if fuga_minutos_limite is not None:
        config.fuga_minutos_limite = fuga_minutos_limite
    
    # Convertir strings time a objetos time
    if break1_inicio is not None:
        try:
            h, m = map(int, break1_inicio.split(":"))
            config.break1_inicio = time(h, m)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato inválido para break1_inicio. Use HH:MM"
            )
    
    if break1_fin is not None:
        try:
            h, m = map(int, break1_fin.split(":"))
            config.break1_fin = time(h, m)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato inválido para break1_fin. Use HH:MM"
            )
    
    if break2_inicio is not None:
        try:
            h, m = map(int, break2_inicio.split(":"))
            config.break2_inicio = time(h, m)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato inválido para break2_inicio. Use HH:MM"
            )
    
    if break2_fin is not None:
        try:
            h, m = map(int, break2_fin.split(":"))
            config.break2_fin = time(h, m)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato inválido para break2_fin. Use HH:MM"
            )
    
    db.commit()
    
    return {
        "message": "Configuración actualizada exitosamente",
        "clan_id": clan_id,
        "clan_nombre": clan.nombre,
        "configuracion": {
            "tolerancia_entrada_min": config.tolerancia_entrada_min,
            "tolerancia_retardo_leve": config.tolerancia_retardo_leve,
            "tolerancia_retardo_grave": config.tolerancia_retardo_grave,
            "tolerancia_salida_min": config.tolerancia_salida_min,
            "break1_inicio": config.break1_inicio.strftime("%H:%M") if config.break1_inicio else None,
            "break1_fin": config.break1_fin.strftime("%H:%M") if config.break1_fin else None,
            "break1_tolerancia": config.break1_tolerancia,
            "break2_inicio": config.break2_inicio.strftime("%H:%M") if config.break2_inicio else None,
            "break2_fin": config.break2_fin.strftime("%H:%M") if config.break2_fin else None,
            "break2_tolerancia": config.break2_tolerancia,
            "fuga_minutos_limite": config.fuga_minutos_limite
        }
    }


@router.get("/{clan_id}/horario", summary="Obtener horario detallado de un clan")
async def get_horario_clan(
    clan_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el horario detallado de un clan (jornada, breaks, tolerancias).
    """
    clan = db.query(Clan).filter_by(id=clan_id).first()
    if not clan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clan con ID {clan_id} no encontrado"
        )
    
    config = db.query(ConfiguracionClan).filter_by(clan_id=clan_id).first()
    if not config:
        # Crear configuración por defecto
        config = ConfiguracionClan(clan_id=clan_id)
        db.add(config)
        db.commit()
    
    return {
        "clan_id": clan.id,
        "clan_nombre": clan.nombre,
        "jornada": {
            "entrada": clan.hora_entrada.strftime("%H:%M") if clan.hora_entrada else None,
            "salida": clan.hora_salida.strftime("%H:%M") if clan.hora_salida else None,
            "duracion_horas": (
                (clan.hora_salida.hour - clan.hora_entrada.hour) +
                (clan.hora_salida.minute - clan.hora_entrada.minute) / 60
            ) if clan.hora_entrada and clan.hora_salida else None
        },
        "breaks": [
            {
                "nombre": "break1",
                "descripcion": "Desayuno (mañana) o Break 1 (tarde)",
                "inicio": config.break1_inicio.strftime("%H:%M"),
                "fin": config.break1_fin.strftime("%H:%M"),
                "duracion_minutos": (
                    (config.break1_fin.hour * 60 + config.break1_fin.minute) -
                    (config.break1_inicio.hour * 60 + config.break1_inicio.minute)
                ),
                "tolerancia_minutos": config.break1_tolerancia
            },
            {
                "nombre": "break2",
                "descripcion": "Almuerzo (mañana) o Break 2 (tarde)",
                "inicio": config.break2_inicio.strftime("%H:%M"),
                "fin": config.break2_fin.strftime("%H:%M"),
                "duracion_minutos": (
                    (config.break2_fin.hour * 60 + config.break2_fin.minute) -
                    (config.break2_inicio.hour * 60 + config.break2_inicio.minute)
                ),
                "tolerancia_minutos": config.break2_tolerancia
            }
        ],
        "tolerancias": {
            "entrada_min": config.tolerancia_entrada_min,
            "retardo_leve_min": config.tolerancia_retardo_leve,
            "retardo_grave_min": config.tolerancia_retardo_grave,
            "salida_anticipada_min": config.tolerancia_salida_min,
            "fuga_limite_min": config.fuga_minutos_limite
        }
    }