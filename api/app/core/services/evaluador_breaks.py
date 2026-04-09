# core/services/evaluador_breaks.py

from typing import List
from app.core.models.evento import Evento, TipoEvento
from app.core.utils.time_utils import minutos_entre

# Mapa: tipo de salida → tipo de entrada correspondiente
_PARES_BREAK = {
    TipoEvento.SALIDA_BREAK_DESAYUNO:  TipoEvento.ENTRADA_BREAK_DESAYUNO,
    TipoEvento.SALIDA_BREAK_ALMUERZO:  TipoEvento.ENTRADA_BREAK_ALMUERZO,
}


class EvaluadorBreaks:
    """Evalúa breaks basado en configuración del clan"""
    
    @staticmethod
    def evaluar(eventos: List[Evento], config) -> List[str]:
        """
        Evalúa si cada break excedió su tiempo permitido.
        Usa los tipos explícitos del CSV en lugar de rangos de hora.
        Retorna lista de incidencias.
        
        Args:
            eventos: Lista de eventos del día (ya tipificados)
            config: Objeto ConfiguracionClan con break1_inicio, break1_fin, etc.
            
        Returns:
            Lista de strings con incidencias
        """
        incidencias = []

        # Indexamos los eventos por tipo para buscar rápido
        por_tipo = {}
        for e in eventos:
            por_tipo.setdefault(e.tipo, []).append(e)

        for tipo_salida, tipo_entrada in _PARES_BREAK.items():
            salidas  = por_tipo.get(tipo_salida, [])
            entradas = por_tipo.get(tipo_entrada, [])

            if not salidas:
                continue  # No salió a este break

            salida = salidas[0]  # Tomamos el primero (un break por jornada)

            # Obtener configuración del break desde config del clan
            # Necesitamos mapear tipo_salida a break1 o break2
            # Por ahora asumimos: DESAYUNO -> break1, ALMUERZO -> break2
            if "DESAYUNO" in tipo_salida.value:
                inicio_break = config.break1_inicio
                fin_break = config.break1_fin
                tolerancia = config.break1_tolerancia
                nombre_break = "desayuno"
            else:  # ALMUERZO
                inicio_break = config.break2_inicio
                fin_break = config.break2_fin
                tolerancia = config.break2_tolerancia
                nombre_break = "almuerzo"

            tiempo_permitido = (
                (fin_break.hour * 60 + fin_break.minute)
                - (inicio_break.hour * 60 + inicio_break.minute)
                + tolerancia
            )

            if not entradas:
                # Salió al break y nunca regresó
                incidencias.append(f"No regresó del break de {nombre_break}")
                continue

            entrada = entradas[0]
            duracion = minutos_entre(salida.timestamp, entrada.timestamp)

            if duracion > tiempo_permitido:
                exceso = duracion - tiempo_permitido
                incidencias.append(
                    f"Exceso en break ({nombre_break}): {duracion} min tomados, "
                    f"permitidos {tiempo_permitido} min (+{exceso} min)"
                )

        return incidencias