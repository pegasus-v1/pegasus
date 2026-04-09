# core/services/procesador_eventos.py

from typing import List
from app.core.models.evento import Evento


class ProcesadorEventos:
    """Utilidades para procesar eventos"""
    
    @staticmethod
    def ordenar_eventos(eventos: List[Evento]) -> List[Evento]:
        """Ordena eventos por timestamp"""
        return sorted(eventos, key=lambda e: e.timestamp)
    
    @staticmethod
    def validar_secuencia_eventos(eventos: List[Evento]) -> List[str]:
        """
        Detecta registros consecutivos del mismo tipo de dirección
        (dos entradas seguidas o dos salidas seguidas) lo que indica
        un error del sensor o marcación duplicada.
        """
        advertencias = []
        if not eventos:
            return advertencias

        eventos_ordenados = ProcesadorEventos.ordenar_eventos(eventos)
        dir_anterior = None  # "entrada" o "salida"

        for evento in eventos_ordenados:
            dir_actual = "entrada" if evento.tipo.es_entrada else "salida"
            if dir_actual == dir_anterior:
                advertencias.append(
                    f"Anomalía: doble '{dir_actual}' registrada a las "
                    f"{evento.timestamp.strftime('%H:%M')} ({evento.tipo.value})"
                )
            dir_anterior = dir_actual

        return advertencias