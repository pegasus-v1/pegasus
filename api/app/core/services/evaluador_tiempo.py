# core/services/evaluador_tiempo.py

from typing import List
from app.core.models.evento import Evento
from app.core.utils.time_utils import minutos_entre


class CalculadorTiempo:
    """Calcula el tiempo total trabajado"""
    
    @staticmethod
    def calcular(eventos: List[Evento]) -> dict:
        """
        Calcula el tiempo total trabajado sumando los intervalos
        entre cada entrada y su salida correspondiente.
        Funciona con todos los tipos de entrada/salida (incluyendo breaks).
        
        Args:
            eventos: Lista de eventos del día ordenados por tiempo
            
        Returns:
            dict con:
                total_minutos: int
                horas: int
                minutos: int
                incidencias: lista de strings (vacía por defecto)
        """
        tiempo_total = 0
        entrada_actual = None
        
        incidencias = []

        for evento in eventos:
            if evento.tipo.es_entrada:
                if entrada_actual is not None:
                    incidencias.append(
                        f"Entrada registrada sin salida previa a las {evento.timestamp.strftime('%H:%M')}"
                    )
                entrada_actual = evento.timestamp
            elif evento.tipo.es_salida and entrada_actual:
                tiempo_total += minutos_entre(entrada_actual, evento.timestamp)
                entrada_actual = None
            elif evento.tipo.es_salida and not entrada_actual:
                incidencias.append(
                    f"Salida sin entrada previa a las {evento.timestamp.strftime('%H:%M')}"
                )

        return {
            "total_minutos": tiempo_total,
            "horas": tiempo_total // 60,
            "minutos": tiempo_total % 60,
            "incidencias": incidencias
        }