# core/services/evaluador_abandono.py

from typing import List
from datetime import datetime, time
from app.core.models.evento import Evento, TipoEvento
from app.core.utils.time_utils import minutos_entre


class EvaluadorAbandono:
    """Evalúa la salida final de la jornada (abandono/fuga)"""
    
    @staticmethod
    def evaluar(eventos: List[Evento], hora_salida_clan: time, config) -> dict:
        """
        Evalúa la salida final de la jornada.

        Casos posibles:
        - Sin evento SALIDA registrado → se fue sin marcar = fuga (igual que salida anticipada)
        - Salida dentro de tolerancia (hora_salida - tolerancia a hora_salida) → puntual
        - Salida antes de tolerancia → salida_anticipada
        - Salida después de hora_salida → tiempo_extra (informativo)

        Args:
            eventos: Lista de eventos del día
            hora_salida_clan: Hora oficial de salida del clan (time)
            config: Objeto ConfiguracionClan con tolerancia_salida_min y fuga_minutos_limite
            
        Returns:
            dict con:
                estado: 'puntual' | 'salida_anticipada' | 'tiempo_extra' | 'sin_salida'
                minutos_diferencia: minutos respecto a la hora oficial (None si sin_salida)
                es_fuga: True si salió antes de tolerancia O si no registró salida
                incidencias: lista de strings
        """
        # Tomamos la referencia de fecha del último evento del día
        fecha_ref = eventos[-1].timestamp.date() if eventos else None
        salidas = [e for e in eventos if e.tipo == TipoEvento.SALIDA]
        
        incidencias = []

        # --- Sin registro de salida: se fue sin marcar → fuga ---
        if not salidas:
            incidencias.append("No registró salida al final de la jornada (fuga)")
            return {
                "estado": "sin_salida",
                "minutos_diferencia": None,
                "es_fuga": True,
                "incidencias": incidencias
            }

        ultima_salida = salidas[-1]
        hora_salida_oficial = datetime.combine(
            ultima_salida.timestamp.date(),
            hora_salida_clan
        )

        # Positivo = salió antes, Negativo = salió después
        minutos = minutos_entre(ultima_salida.timestamp, hora_salida_oficial)

        if minutos < 0:
            # Salió después de la hora oficial → tiempo extra
            incidencias.append(
                f"Tiempo extra: salió {abs(minutos)} minutos después de la hora oficial"
            )
            return {
                "estado": "tiempo_extra",
                "minutos_diferencia": abs(minutos),
                "es_fuga": False,
                "incidencias": incidencias
            }

        if minutos <= config.tolerancia_salida_min:
            # Salió dentro de tolerancia → puntual
            return {
                "estado": "puntual",
                "minutos_diferencia": minutos,
                "es_fuga": False,
                "incidencias": incidencias
            }

        # Salió antes de la tolerancia → salida anticipada
        # Verificar si es fuga (supera el límite de minutos para considerar fuga)
        es_fuga = minutos > config.fuga_minutos_limite
        
        if es_fuga:
            incidencias.append(
                f"Fuga: salió {minutos} minutos antes de la hora oficial "
                f"(límite: {config.fuga_minutos_limite} min)"
            )
        else:
            incidencias.append(
                f"Salida anticipada: {minutos} minutos antes de la hora oficial"
            )
        
        return {
            "estado": "salida_anticipada",
            "minutos_diferencia": minutos,
            "es_fuga": es_fuga,
            "incidencias": incidencias
        }