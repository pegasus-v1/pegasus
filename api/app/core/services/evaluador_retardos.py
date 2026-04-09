# core/services/evaluador_retardos.py

from typing import List
from datetime import datetime, time
from app.core.models.evento import Evento, TipoEvento
from app.core.utils.time_utils import minutos_entre


class EvaluadorRetardos:
    """Evalúa retardos basado en configuración del clan"""
    
    @staticmethod
    def obtener_primera_entrada(eventos: List[Evento]) -> Evento:
        for evento in eventos:
            if evento.tipo.es_entrada_jornada:
                return evento
        return None
    
    @staticmethod
    def evaluar(
        eventos: List[Evento], 
        hora_entrada_clan: time, 
        config
    ) -> dict:
        """
        Evalúa retardos para un conjunto de eventos.
        
        Args:
            eventos: Lista de eventos del día
            hora_entrada_clan: Hora oficial de entrada del clan (time)
            config: Objeto ConfiguracionClan con tolerancias
            
        Returns:
            dict con keys:
                estado: "puntual", "retardo_leve", "retardo_grave", "retardo_critico", "ausente"
                minutos_retardo: int o None
                incidencias: lista de strings
        """
        primera_entrada = EvaluadorRetardos.obtener_primera_entrada(eventos)
        
        if not primera_entrada:
            return {
                "estado": "ausente",
                "minutos_retardo": None,
                "incidencias": []
            }
        
        # Construir datetime de hora oficial de entrada para el día
        hora_oficial = datetime.combine(
            primera_entrada.timestamp.date(),
            hora_entrada_clan
        )
        
        minutos_retardo = minutos_entre(hora_oficial, primera_entrada.timestamp)
        
        if minutos_retardo <= 0:
            return {
                "estado": "puntual",
                "minutos_retardo": 0,
                "incidencias": []
            }
        
        # Aplicar tolerancias configurables
        if minutos_retardo <= config.tolerancia_entrada_min:
            estado = "puntual"
        elif minutos_retardo <= config.tolerancia_retardo_leve:
            estado = "retardo_leve"
        elif minutos_retardo <= config.tolerancia_retardo_grave:
            estado = "retardo_grave"
        else:
            estado = "retardo_critico"
        
        incidencias = []
        if estado != "puntual":
            incidencias.append(
                f"Retardo ({estado}): llegada a las {primera_entrada.timestamp.strftime('%H:%M')}, "
                f"{minutos_retardo} minutos tarde"
            )
        
        return {
            "estado": estado,
            "minutos_retardo": minutos_retardo,
            "incidencias": incidencias
        }