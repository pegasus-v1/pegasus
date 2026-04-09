# core/models/evento.py

from datetime import datetime
from enum import Enum


class TipoEvento(Enum):
    ENTRADA                = "ENTRADA"
    SALIDA                 = "SALIDA"
    SALIDA_BREAK_DESAYUNO  = "SALIDA_BREAK_DESAYUNO"
    ENTRADA_BREAK_DESAYUNO = "ENTRADA_BREAK_DESAYUNO"
    SALIDA_BREAK_ALMUERZO  = "SALIDA_BREAK_ALMUERZO"
    ENTRADA_BREAK_ALMUERZO = "ENTRADA_BREAK_ALMUERZO"

    @property
    def nombre_break(self):
        mapping = {
            "SALIDA_BREAK_DESAYUNO":  "desayuno",
            "ENTRADA_BREAK_DESAYUNO": "desayuno",
            "SALIDA_BREAK_ALMUERZO":  "almuerzo",
            "ENTRADA_BREAK_ALMUERZO": "almuerzo",
        }
        return mapping.get(self.value)

    @property
    def es_entrada(self) -> bool:
        return self.value in ("ENTRADA", "ENTRADA_BREAK_DESAYUNO", "ENTRADA_BREAK_ALMUERZO")

    @property
    def es_salida(self) -> bool:
        return self.value in ("SALIDA", "SALIDA_BREAK_DESAYUNO", "SALIDA_BREAK_ALMUERZO")

    @property
    def es_entrada_jornada(self) -> bool:
        return self == TipoEvento.ENTRADA

    @property
    def es_salida_jornada(self) -> bool:
        return self == TipoEvento.SALIDA


class Evento:
    def __init__(
        self,
        persona_id: str,
        tipo: TipoEvento,
        timestamp: datetime,
        nombre: str = "",
        departamento: str = "",
        dispositivo: str = "",
    ):
        self.persona_id   = persona_id
        self.tipo         = tipo
        self.timestamp    = timestamp
        self.nombre       = nombre
        self.departamento = departamento
        self.dispositivo  = dispositivo

    def __repr__(self):
        return f"Evento({self.tipo.value}, {self.timestamp.strftime('%Y-%m-%d %H:%M')})"