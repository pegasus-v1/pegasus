# app/api/endpoints/procesamiento.py

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.dependencies import verify_api_key, get_db
from app.core.orchestrator.procesador_dia import ProcesadorDia
from app.db.models import Coder

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/procesar-dia", summary="Procesar jornada de un coder en una fecha específica")
async def procesar_dia(
    coder_id: int = Query(..., description="ID del coder"),
    fecha: date = Query(..., description="Fecha a procesar (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Procesa la jornada de un coder en una fecha específica.
    
    Evalúa retardos, breaks, fugas y calcula tiempo total trabajado.
    """
    # Verificar que el coder existe
    coder = db.query(Coder).filter_by(id=coder_id).first()
    if not coder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coder con ID {coder_id} no encontrado"
        )
    
    try:
        procesador = ProcesadorDia(db)
        resultado = procesador.procesar_dia(coder_id, fecha)
        
        return {
            "coder_id": coder_id,
            "coder_nombre": coder.nombre,
            "fecha": fecha,
            "estado": resultado.estado,
            "tiempo_total_minutos": resultado.tiempo_total,
            "tiempo_total_formato": f"{resultado.tiempo_total // 60}h {resultado.tiempo_total % 60}m",
            "incidencias": resultado.incidencias,
            "clan": coder.clan.nombre if coder.clan else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar: {str(e)}"
        )


@router.post("/procesar-rango", summary="Procesar rango de fechas para un coder")
async def procesar_rango(
    coder_id: int = Query(..., description="ID del coder"),
    fecha_inicio: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha final (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Procesa un rango de fechas para un coder.
    """
    # Validar fechas
    if fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_inicio debe ser anterior o igual a fecha_fin"
        )
    
    # Verificar que el coder existe
    coder = db.query(Coder).filter_by(id=coder_id).first()
    if not coder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coder con ID {coder_id} no encontrado"
        )
    
    try:
        procesador = ProcesadorDia(db)
        resultados = procesador.procesar_rango(coder_id, fecha_inicio, fecha_fin)
        
        # Formatear resultados
        resultados_formateados = []
        for fecha, resultado in resultados.items():
            resultados_formateados.append({
                "fecha": fecha,
                "estado": resultado.estado,
                "tiempo_total_minutos": resultado.tiempo_total,
                "incidencias": resultado.incidencias
            })
        
        # Calcular estadísticas
        total_dias = len(resultados)
        dias_con_incidencias = sum(1 for r in resultados.values() if r.incidencias)
        estados = [r.estado for r in resultados.values()]
        
        return {
            "coder_id": coder_id,
            "coder_nombre": coder.nombre,
            "rango": {"inicio": fecha_inicio, "fin": fecha_fin},
            "total_dias": total_dias,
            "dias_con_incidencias": dias_con_incidencias,
            "estados_distribucion": {
                estado: estados.count(estado) for estado in set(estados)
            },
            "resultados": resultados_formateados
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar rango: {str(e)}"
        )


@router.post("/procesar-lote", summary="Procesar múltiples coders en una fecha")
async def procesar_lote(
    coder_ids: List[int] = Query(..., description="Lista de IDs de coders"),
    fecha: date = Query(..., description="Fecha a procesar"),
    db: Session = Depends(get_db)
):
    """
    Procesa múltiples coders en una fecha específica (procesamiento por lote).
    """
    if not coder_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere al menos un coder_id"
        )
    
    resultados = []
    errores = []
    
    for coder_id in coder_ids:
        try:
            coder = db.query(Coder).filter_by(id=coder_id).first()
            if not coder:
                errores.append({
                    "coder_id": coder_id,
                    "error": "Coder no encontrado"
                })
                continue
            
            procesador = ProcesadorDia(db)
            resultado = procesador.procesar_dia(coder_id, fecha)
            
            resultados.append({
                "coder_id": coder_id,
                "coder_nombre": coder.nombre,
                "clan": coder.clan.nombre if coder.clan else None,
                "estado": resultado.estado,
                "tiempo_total_minutos": resultado.tiempo_total,
                "incidencias_count": len(resultado.incidencias),
                "incidencias": resultado.incidencias[:5]  # Mostrar primeras 5
            })
            
        except Exception as e:
            errores.append({
                "coder_id": coder_id,
                "error": str(e)
            })
    
    return {
        "fecha": fecha,
        "total_coders": len(coder_ids),
        "procesados_exitosamente": len(resultados),
        "errores": len(errores),
        "resultados": resultados,
        "errores_detalle": errores[:10]  # Limitar a 10 errores
    }