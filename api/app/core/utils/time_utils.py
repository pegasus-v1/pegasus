# core/utils/time_utils.py

from datetime import datetime, time

def minutos_entre(inicio: datetime, fin: datetime) -> int:
    """
    Retorna la diferencia en minutos entre dos timestamps
    """
    delta = fin - inicio
    return int(delta.total_seconds() / 60)


def convertir_a_minutos(hora: time) -> int:
    """
    Convierte un objeto time a minutos desde 00:00
    """
    return hora.hour * 60 + hora.minute