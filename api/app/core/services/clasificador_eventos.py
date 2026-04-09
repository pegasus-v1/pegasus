# core/services/clasificador_eventos.py

from datetime import datetime, time
from app.core.models.evento import TipoEvento
from app.core.utils.time_utils import convertir_a_minutos


class ClasificadorEventos:
    """Clasifica eventos de entrada/salida en tipos específicos basado en horarios del clan"""
    
    @staticmethod
    def clasificar(
        timestamp: datetime,
        estado: str,  # "entrada" o "salida"
        config
    ) -> TipoEvento:
        """
        Determina el TipoEvento basado en la hora del evento y configuración del clan.
        
        Args:
            timestamp: Fecha y hora del evento
            estado: "entrada" o "salida"
            config: Objeto ConfiguracionClan con horarios de breaks
            
        Returns:
            TipoEvento apropiado (ENTRADA, SALIDA, ENTRADA_BREAK_DESAYUNO, etc.)
        """
        hora_evento = timestamp.time()
        minutos_evento = convertir_a_minutos(hora_evento)
        
        # Verificar si está dentro de break1
        break1_inicio_min = convertir_a_minutos(config.break1_inicio)
        break1_fin_min = convertir_a_minutos(config.break1_fin)
        
        # Verificar si está dentro de break2
        break2_inicio_min = convertir_a_minutos(config.break2_inicio)
        break2_fin_min = convertir_a_minutos(config.break2_fin)
        
        # Determinar a qué break pertenece (si alguno)
        # Considerar margen de tolerancia? Por ahora exacto.
        if break1_inicio_min <= minutos_evento <= break1_fin_min:
            # Está dentro del primer break
            if estado == "entrada":
                return TipoEvento.ENTRADA_BREAK_DESAYUNO
            else:  # salida
                return TipoEvento.SALIDA_BREAK_DESAYUNO
                
        elif break2_inicio_min <= minutos_evento <= break2_fin_min:
            # Está dentro del segundo break
            if estado == "entrada":
                return TipoEvento.ENTRADA_BREAK_ALMUERZO
            else:  # salida
                return TipoEvento.SALIDA_BREAK_ALMUERZO
        
        # No está dentro de ningún break → evento de jornada normal
        if estado == "entrada":
            return TipoEvento.ENTRADA
        else:  # salida
            return TipoEvento.SALIDA
    
    @staticmethod
    def clasificar_registros(registros_db, config):
        """
        Convierte registros de la base de datos (tabla 'registros') a objetos Evento.
        
        Args:
            registros_db: Lista de objetos Registro (SQLAlchemy)
            config: ConfiguracionClan del coder
            
        Returns:
            Lista de objetos Evento clasificados
        """
        from app.core.models.evento import Evento
        
        eventos = []
        for registro in registros_db:
            # Crear datetime combinando fecha y hora
            timestamp = datetime.combine(registro.fecha, registro.hora)
            
            # Clasificar el evento
            tipo = ClasificadorEventos.clasificar(
                timestamp=timestamp,
                estado=registro.estado_acceso,
                config=config
            )
            
            # Crear objeto Evento
            evento = Evento(
                persona_id=registro.coder_id,
                tipo=tipo,
                timestamp=timestamp,
                nombre=registro.coder.nombre if registro.coder else "",
                dispositivo=registro.dispositivo or "torniquete"
            )
            eventos.append(evento)
        
        return eventos