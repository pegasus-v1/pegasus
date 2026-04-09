# app/api/endpoints/reportes.py

from datetime import date, timedelta
from typing import List, Optional
import time as _time
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.api.dependencies import verify_api_key, get_db
from app.db.models import Coder, Clan, Registro, ConfiguracionClan, ResumenDiario, Incidencia

# --------------------------------------------------------------------------- #
# Caché en memoria para endpoints de solo lectura                              #
# Evita ir a Railway (DB remota) en cada petición — TTL de 10 minutos         #
# --------------------------------------------------------------------------- #
_CACHE: dict = {}
_TTL = 600  # segundos (10 min)

def _cache_get(key: str):
    if key in _CACHE:
        data, ts = _CACHE[key]
        if _time.monotonic() - ts < _TTL:
            return data
        del _CACHE[key]
    return None

def _cache_set(key: str, data):
    _CACHE[key] = (data, _time.monotonic())

def _cache_invalidate_prefix(prefix: str):
    """Borra entradas cuya clave empieza con prefix (para invalidar por endpoint)."""
    for k in list(_CACHE.keys()):
        if k.startswith(prefix):
            del _CACHE[k]

router = APIRouter(dependencies=[Depends(verify_api_key)])



@router.get("/resumen-diario", summary="Obtener resumen de asistencia por fecha")
async def get_resumen_diario(
    fecha: date = Query(..., description="Fecha (YYYY-MM-DD)"),
    clan_id: Optional[int] = Query(None, description="Filtrar por clan (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen de asistencia para una fecha específica usando la tabla de resúmenes procesados.
    """
    cache_key = f"resumen_diario:{fecha}:{clan_id}"
    cached_data = _cache_get(cache_key)
    if cached_data:
        return cached_data

    from sqlalchemy.orm import joinedload

    # Obtener clanes
    clanes_query = db.query(Clan)
    if clan_id:
        clanes_query = clanes_query.filter(Clan.id == clan_id)
    clanes = clanes_query.all()

    # Obtener todos los resúmenes de la fecha con coder y clan precargados (evita N+1)
    resumenes = db.query(ResumenDiario).options(
        joinedload(ResumenDiario.coder).joinedload(Coder.clan)
    ).filter(ResumenDiario.fecha == fecha).all()

    # Pre-calcular total de coders por clan desde la BD en una sola query
    coders_por_clan = {
        cid: count
        for cid, count in db.query(Coder.clan_id, func.count(Coder.id))
                                 .group_by(Coder.clan_id).all()
    }

    # Pre-calcular excesos de break por clan para el resumen
    breaks_por_clan = {
        clan_id: count
        for clan_id, count in db.query(Coder.clan_id, func.count(Incidencia.id))
                                 .join(ResumenDiario, ResumenDiario.id == Incidencia.resumen_id)
                                 .join(Coder, Coder.id == ResumenDiario.coder_id)
                                 .filter(ResumenDiario.fecha == fecha, Incidencia.tipo == "break")
                                 .group_by(Coder.clan_id).all()
    }

    # Construir resumen por clan
    por_clan = []
    for clan in clanes:
        resumenes_clan = [r for r in resumenes if r.coder and r.coder.clan_id == clan.id]

        tardes            = len([r for r in resumenes_clan if r.estado_entrada in ["retardo_leve", "retardo_grave", "retardo_critico"]])
        ausentes          = len([r for r in resumenes_clan if r.ausente])
        salidas_anticipadas = len([r for r in resumenes_clan if r.estado_salida == "salida_anticipada"])

        por_clan.append({
            "clan_id": clan.id,
            "clan": clan.nombre,
            "coders_con_registros": len([r for r in resumenes_clan if not r.ausente]),
            "total_coders": coders_por_clan.get(clan.id, 0),
            "con_retardo": tardes,
            "ausentes": ausentes,
            "salidas_anticipadas": salidas_anticipadas,
            "excesos_break": breaks_por_clan.get(clan.id, 0)
        })

    # Estadísticas generales
    total_coders = sum(coders_por_clan.values())
    coders_con_registros = len([r for r in resumenes if not r.ausente])
    total_excesos_break = sum(breaks_por_clan.values())

    result = {
        "fecha": fecha,
        "total_coders": total_coders,
        "coders_con_registros": coders_con_registros,
        "total_excesos_break": total_excesos_break,
        "porcentaje_asistencia_general": round((coders_con_registros / total_coders * 100), 2) if total_coders > 0 else 0,
        "por_clan": por_clan
    }

    _cache_set(cache_key, result)
    return result


def _get_tiempos_registro(db: Session, fecha: date):
    """Retorna dict {coder_id: (primera_hora, ultima_hora)} para optimizar."""
    registros = db.query(
        Registro.coder_id,
        func.min(Registro.hora).label("primera"),
        func.max(Registro.hora).label("ultima")
    ).filter(Registro.fecha == fecha).group_by(Registro.coder_id).all()
    
    return {r.coder_id: (r.primera, r.ultima) for r in registros}


@router.get("/incidencias", summary="Obtener incidencias por rango de fechas")
async def get_incidencias(
    fecha_inicio: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha final (YYYY-MM-DD)"),
    clan_id: Optional[int] = Query(None, description="Filtrar por clan (opcional)"),
    tipo_incidencia: Optional[str] = Query(None, description="Filtrar por tipo de incidencia"),
    db: Session = Depends(get_db)
):
    """
    Obtiene incidencias detectadas en un rango de fechas.
    Nota: Por ahora simulamos procesando los días, en producción se guardarían en tabla 'incidencias'.
    """
    # Validar fechas
    if fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_inicio debe ser anterior o igual a fecha_fin"
        )
    
    # Por ahora, este endpoint requeriría tener incidencias pre-procesadas.
    # Para el MVP, podemos devolver un mensaje indicando que se necesita procesar primero.
    # O podemos procesar on-demand (pero sería lento).
    # Por simplicidad, devolveremos información básica.
    
    return {
        "message": "Este endpoint requiere que las incidencias hayan sido pre-procesadas y guardadas en la base de datos.",
        "suggestion": "Use el endpoint /procesamiento/procesar-rango primero para generar resultados.",
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "clan_id": clan_id,
        "tipo_incidencia": tipo_incidencia
    }


@router.get("/estadisticas-clan", summary="Estadísticas de asistencia por clan")
async def get_estadisticas_clan(
    clan_id: Optional[int] = Query(None, description="ID del clan (opcional, si no se especifica devuelve todos)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de asistencia por clan.
    """
    if clan_id:
        clanes = db.query(Clan).filter_by(id=clan_id).all()
    else:
        clanes = db.query(Clan).all()
    
    estadisticas = []
    
    for clan in clanes:
        # Contar coders en este clan
        total_coders = db.query(Coder).filter_by(clan_id=clan.id).count()
        
        # Contar registros de este clan
        total_registros = db.query(Registro).join(Coder).filter(Coder.clan_id == clan.id).count()
        
        # Última fecha con registros
        ultima_fecha = db.query(Registro.fecha)\
            .join(Coder)\
            .filter(Coder.clan_id == clan.id)\
            .order_by(Registro.fecha.desc())\
            .first()
        
        estadisticas.append({
            "clan_id": clan.id,
            "clan_nombre": clan.nombre,
            "total_coders": total_coders,
            "total_registros": total_registros,
            "registros_por_coder": round(total_registros / total_coders, 2) if total_coders > 0 else 0,
            "ultima_fecha_registro": ultima_fecha[0] if ultima_fecha else None,
            "hora_entrada": clan.hora_entrada.strftime("%H:%M") if clan.hora_entrada else None,
            "hora_salida": clan.hora_salida.strftime("%H:%M") if clan.hora_salida else None
        })
    
    return {
        "clanes": estadisticas,
        "total_clanes": len(estadisticas)
    }


@router.get("/ausentes-hoy", summary="Lista de coders sin registros hoy")
async def get_ausentes_hoy(
    clan_id: Optional[int] = Query(None, description="Filtrar por clan (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de coders que no tienen registros de asistencia hoy.
    Útil para el equipo de notificaciones.
    """
    hoy = date.today()
    
    # Coders con registros hoy
    coders_con_registros = db.query(Coder.id)\
        .join(Registro)\
        .filter(Registro.fecha == hoy)\
        .distinct()\
        .all()
    
    ids_con_registros = [c[0] for c in coders_con_registros]
    
    # Query para coders sin registros
    query = db.query(Coder)
    if ids_con_registros:
        query = query.filter(~Coder.id.in_(ids_con_registros))
    
    if clan_id:
        query = query.filter_by(clan_id=clan_id)
    
    coders_ausentes = query.all()
    
    # Formatear respuesta
    ausentes_formateados = []
    for coder in coders_ausentes:
        ausentes_formateados.append({
            "coder_id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "email": coder.email,
            "clan": coder.clan.nombre if coder.clan else None,
            "team_leader": coder.clan.team_leaders[0].nombre if coder.clan and coder.clan.team_leaders else None
        })
    
    return {
        "fecha": hoy,
        "total_ausentes": len(ausentes_formateados),
        "ausentes": ausentes_formateados
    }


# ============================================================================
# Endpoints compatibles con frontend Infox (nombres exactos)
# ============================================================================

@router.get("/resumen-dia", summary="Resumen del día (compatible con Infox)")
async def resumen_dia(
    fecha: date = Query(..., description="Fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Endpoint compatible con el frontend Infox.
    Devuelve un resumen del día similar al endpoint original.
    """
    # Usar el endpoint existente pero con formato compatible
    from .reportes import get_resumen_diario
    return await get_resumen_diario(fecha, None, db)


@router.get("/tarde", summary="Coders que llegaron tarde (compatible con Infox)")
async def llegaron_tarde(
    fecha: date = Query(..., description="Fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Lista de coders que llegaron tarde en la fecha especificada.
    Compatible con frontend Infox.
    """
    # Buscar resúmenes con estado de entrada de retardo
    from sqlalchemy.orm import joinedload
    resumenes = db.query(ResumenDiario).options(
        joinedload(ResumenDiario.coder).joinedload(Coder.clan)
    ).filter(
        ResumenDiario.fecha == fecha,
        ResumenDiario.estado_entrada.in_(["retardo_leve", "retardo_grave", "retardo_critico"])
    ).all()

    # Precargar tiempos de registros para evitar N+1
    tiempos = _get_tiempos_registro(db, fecha)

    tardios = []
    for resumen in resumenes:
        coder = resumen.coder
        if not coder:
            continue
            
        primera_hora, _ = tiempos.get(coder.id, (None, None))
        
        tardios.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None,
            "estado_entrada": resumen.estado_entrada,
            "minutos_retardo": resumen.minutos_retardo,
            "hora_entrada": primera_hora.strftime("%H:%M:%S") if primera_hora else None,
            "hora_entrada_estimada": None
        })

    return {
        "fecha": fecha,
        "total": len(tardios),
        "estudiantes": tardios
    }


@router.get("/ausentes", summary="Coders ausentes (compatible con Infox)")
async def ausentes(
    fecha: date = Query(..., description="Fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Lista de coders ausentes en la fecha especificada.
    Compatible con frontend Infox.
    """
    from sqlalchemy.orm import joinedload

    # Coders con resúmenes marcados como ausentes (carga eager de coder y clan)
    resumenes_ausentes = db.query(ResumenDiario).options(
        joinedload(ResumenDiario.coder).joinedload(Coder.clan)
    ).filter(
        ResumenDiario.fecha == fecha,
        ResumenDiario.ausente == True
    ).all()

    ids_con_resumen = {r.coder_id for r in db.query(ResumenDiario.coder_id)
                       .filter(ResumenDiario.fecha == fecha).all()}

    # Coders sin resumen (no procesados aún) — una sola query
    query = db.query(Coder).options(joinedload(Coder.clan))
    if ids_con_resumen:
        query = query.filter(~Coder.id.in_(ids_con_resumen))
    coders_sin_procesar = query.all()

    ausentes_lista = []

    for resumen in resumenes_ausentes:
        coder = resumen.coder
        if coder:
            ausentes_lista.append({
                "id": coder.id,
                "nombre": coder.nombre,
                "cedula": coder.cedula,
                "clan": coder.clan.nombre if coder.clan else None,
                "razon": "Sin registros de acceso"
            })

    for coder in coders_sin_procesar:
        ausentes_lista.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None,
            "razon": "No procesado aún"
        })

    return {
        "fecha": fecha,
        "total": len(ausentes_lista),
        "estudiantes": ausentes_lista
    }


@router.get("/fuga-manana", summary="Fugas en clanes de la mañana (compatible con Infox)")
async def fuga_manana(
    fecha: date = Query(..., description="Fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Lista de coders con fuga en clanes de la mañana.
    Compatible con frontend Infox.
    """
    # Identificar clanes de la mañana (horario 06:00-14:00)
    clanes_manana = db.query(Clan).filter(
        Clan.hora_entrada.isnot(None)
    ).all()
    
    # Filtrar por horario típico de mañana (06:00)
    clanes_manana_ids = []
    for clan in clanes_manana:
        if clan.hora_entrada and clan.hora_entrada.hour == 6:  # 06:00 AM
            clanes_manana_ids.append(clan.id)
    
    if not clanes_manana_ids:
        # Si no hay clanes con hora_entrada == 06:00, usar los 3 primeros clanes (Hamilton, Thompson, Nakamoto)
        clanes_manana = db.query(Clan).filter(
            Clan.nombre.in_(["Hamilton", "Thompson", "Nakamoto"])
        ).all()
        clanes_manana_ids = [c.id for c in clanes_manana]
    
    # Buscar incidencias de tipo 'fuga' para estos clanes en la fecha
    incidencias_fuga = db.query(Incidencia)\
        .join(ResumenDiario)\
        .join(Coder)\
        .filter(
            Incidencia.tipo == "fuga",
            ResumenDiario.fecha == fecha,
            Coder.clan_id.in_(clanes_manana_ids)
        ).all()
    
    fugas = []
    for inc in incidencias_fuga:
        resumen = inc.resumen
        coder = resumen.coder if resumen else None
        if not coder:
            continue
            
        fugas.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None,
            "descripcion": inc.descripcion,
            "minutos": inc.minutos
        })
    
    return {
        "fecha": fecha,
        "total": len(fugas),
        "fugas": fugas
    }


@router.get("/exceso-break", summary="Exceso en breaks (compatible con Infox)")
async def exceso_break(
    fecha: date = Query(..., description="Fecha (YYYY-MM-DD)"),
    tipo: str = Query("ambos", description="Tipo de break: 'desayuno', 'almuerzo', 'ambos'"),
    db: Session = Depends(get_db)
):
    """
    Lista de coders con exceso en breaks.
    Compatible con frontend Infox.
    """
    # Filtrar incidencias de tipo 'break'
    query = db.query(Incidencia)\
        .join(ResumenDiario)\
        .filter(
            Incidencia.tipo == "break",
            ResumenDiario.fecha == fecha
        )
    
    # Filtrar por tipo de break si es necesario (basado en descripción)
    breaks = query.all()
    
    excesos = []
    for inc in breaks:
        # Determinar tipo de break basado en descripción
        desc_lower = inc.descripcion.lower()
        es_desayuno = "desayuno" in desc_lower or "break1" in desc_lower or "08" in desc_lower
        es_almuerzo = "almuerzo" in desc_lower or "break2" in desc_lower or "12" in desc_lower or "13" in desc_lower
        
        # Aplicar filtro de tipo
        if tipo == "desayuno" and not es_desayuno:
            continue
        if tipo == "almuerzo" and not es_almuerzo:
            continue
        
        resumen = inc.resumen
        coder = resumen.coder if resumen else None
        if not coder:
            continue
            
        excesos.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None,
            "descripcion": inc.descripcion,
            "minutos": inc.minutos,
            "tipo_break": "desayuno" if es_desayuno else "almuerzo" if es_almuerzo else "desconocido"
        })
    
    return {
        "fecha": fecha,
        "tipo": tipo,
        "total": len(excesos),
        "excesos": excesos
    }


@router.get("/salidas-anticipadas", summary="Salidas anticipadas (compatible con Infox)")
async def salidas_anticipadas(
    fecha: date = Query(..., description="Fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Lista de coders con salidas anticipadas.
    Compatible con frontend Infox.
    """
    # Buscar incidencias de tipo 'salida_anticipada' o resúmenes con estado_salida 'salida_anticipada'
    incidencias_salida = db.query(Incidencia)\
        .join(ResumenDiario)\
        .filter(
            ResumenDiario.fecha == fecha,
            Incidencia.tipo.in_(["salida_anticipada", "fuga"])  # Las fugas también son salidas anticipadas
        ).all()
    
    # Precargar tiempos de registros
    tiempos = _get_tiempos_registro(db, fecha)
    
    salidas_formateadas = []
    for inc in incidencias_salida:
        resumen = inc.resumen
        coder = resumen.coder if resumen else None
        if not coder:
            continue
        
        _, ultima_hora = tiempos.get(coder.id, (None, None))
            
        salidas_formateadas.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None,
            "descripcion": inc.descripcion,
            "minutos": inc.minutos,
            "hora_salida": ultima_hora.strftime("%H:%M:%S") if ultima_hora else None
        })
    
    # También buscar resúmenes con estado_salida 'salida_anticipada' que no tengan incidencia
    resumenes_salida = db.query(ResumenDiario).filter(
        ResumenDiario.fecha == fecha,
        ResumenDiario.estado_salida == "salida_anticipada"
    ).all()
    
    for resumen in resumenes_salida:
        # Verificar si ya está en la lista
        if any(s["id"] == resumen.coder_id for s in salidas_formateadas):
            continue
            
        coder = resumen.coder
        if not coder:
            continue
            
        _, ultima_hora = tiempos.get(coder.id, (None, None))
            
        salidas_formateadas.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None,
            "descripcion": "Salida anticipada",
            "minutos": None,
            "hora_salida": ultima_hora.strftime("%H:%M:%S") if ultima_hora else None
        })
    
    return {
        "fecha": fecha,
        "total": len(salidas_formateadas),
        "estudiantes": salidas_formateadas
    }


@router.get("/asistieron", summary="Coders que asistieron (compatible con Infox)")
async def asistieron(
    fecha: date = Query(..., description="Fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Lista de coders que sí asistieron (tienen ResumenDiario con ausente=False).
    Compatible con frontend Infox.
    """
    from sqlalchemy.orm import joinedload
    resumenes = db.query(ResumenDiario).options(
        joinedload(ResumenDiario.coder).joinedload(Coder.clan)
    ).filter(
        ResumenDiario.fecha == fecha,
        ResumenDiario.ausente == False
    ).all()

    # Precargar tiempos de registros
    tiempos = _get_tiempos_registro(db, fecha)

    presentes = []
    for resumen in resumenes:
        coder = resumen.coder
        if not coder:
            continue
            
        primera_hora, _ = tiempos.get(coder.id, (None, None))

        presentes.append({
            "id": coder.id,
            "nombre": coder.nombre,
            "cedula": coder.cedula,
            "clan": coder.clan.nombre if coder.clan else None,
            "estado_entrada": resumen.estado_entrada,
            "minutos_retardo": resumen.minutos_retardo,
            "hora_entrada": primera_hora.strftime("%H:%M:%S") if primera_hora else None
        })

    return {
        "fecha": fecha,
        "total": len(presentes),
        "estudiantes": presentes
    }