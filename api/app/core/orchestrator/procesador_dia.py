# core/orchestrator/procesador_dia.py

from typing import List
from datetime import date
from app.core.models.evento import Evento, TipoEvento
from app.core.models.resultado import Resultado
from app.core.services.procesador_eventos import ProcesadorEventos
from app.core.services.evaluador_retardos import EvaluadorRetardos
from app.core.services.evaluador_breaks import EvaluadorBreaks
from app.core.services.evaluador_abandono import EvaluadorAbandono
from app.core.services.evaluador_tiempo import CalculadorTiempo
from app.core.services.clasificador_eventos import ClasificadorEventos


class ProcesadorDia:
    """Orquestador principal para procesar la jornada de un coder en un día"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def procesar_dia(self, coder_id: int, fecha: date, guardar: bool = True):
        """
        Procesa la jornada de un coder en una fecha específica.
        
        Args:
            coder_id: ID del coder en la base de datos
            fecha: Fecha a procesar
            guardar: Si True, guarda el resumen e incidencias en la base de datos
            
        Returns:
            Objeto Resultado con evaluación completa
        """
        from app.db.models import Coder, Clan, ConfiguracionClan, Registro, ResumenDiario, Incidencia
        
        # 1. Obtener coder y su clan
        coder = self.db.query(Coder).filter_by(id=coder_id).first()
        if not coder:
            raise ValueError(f"Coder con ID {coder_id} no encontrado")
        
        clan = self.db.query(Clan).filter_by(id=coder.clan_id).first()
        if not clan:
            raise ValueError(f"Clan del coder {coder_id} no encontrado")
        
        # 2. Obtener configuración del clan
        config = self.db.query(ConfiguracionClan).filter_by(clan_id=clan.id).first()
        if not config:
            # Crear configuración por defecto si no existe
            config = ConfiguracionClan(clan_id=clan.id)
            self.db.add(config)
            self.db.flush()
        
        # 3. Obtener registros del torniquete para este coder en esta fecha
        registros = self.db.query(Registro).filter(
            Registro.coder_id == coder_id,
            Registro.fecha == fecha
        ).all()
        
        if not registros:
            # Sin registros → ausente
            resultado = Resultado(persona_id=coder_id)
            resultado.estado = "ausente"
            resultado.agregar_incidencia("Sin registros de acceso en el día")
            if guardar:
                self._guardar_resumen_ausente(coder_id, fecha, resultado)
            return resultado
        
        # 4. Clasificar registros en eventos tipados
        eventos = ClasificadorEventos.clasificar_registros(registros, config)
        
        # 5. Ordenar y validar secuencia
        eventos = ProcesadorEventos.ordenar_eventos(eventos)
        resultado = Resultado(persona_id=coder_id)
        
        for adv in ProcesadorEventos.validar_secuencia_eventos(eventos):
            resultado.agregar_incidencia(adv)
        
        # 6. Evaluar retardo de entrada
        retardo = EvaluadorRetardos.evaluar(
            eventos=eventos,
            hora_entrada_clan=clan.hora_entrada,
            config=config
        )
        resultado.estado = retardo["estado"]
        resultado.incidencias.extend(retardo["incidencias"])
        
        # 7. Evaluar breaks
        breaks_incidencias = EvaluadorBreaks.evaluar(eventos, config)
        resultado.incidencias.extend(breaks_incidencias)
        
        # 8. Evaluar salida/abandono
        abandono = EvaluadorAbandono.evaluar(
            eventos=eventos,
            hora_salida_clan=clan.hora_salida,
            config=config
        )
        resultado.incidencias.extend(abandono["incidencias"])
        
        # Si hay fuga, actualizar estado
        if abandono["es_fuga"]:
            resultado.estado = "fuga"
        
        # 9. Calcular tiempo total trabajado
        tiempo = CalculadorTiempo.calcular(eventos)
        resultado.tiempo_total = tiempo["total_minutos"]
        resultado.incidencias.extend(tiempo["incidencias"])
        
        # 10. Guardar en base de datos si se solicita
        if guardar:
            self._guardar_resumen(coder_id, fecha, resultado, retardo, abandono, tiempo)
        
        return resultado
    
    def _guardar_resumen_ausente(self, coder_id: int, fecha: date, resultado):
        """Guarda un resumen diario para un coder ausente"""
        from app.db.models import ResumenDiario, Incidencia
        
        # Eliminar resumen existente para evitar duplicados
        self.db.query(ResumenDiario).filter(
            ResumenDiario.coder_id == coder_id,
            ResumenDiario.fecha == fecha
        ).delete()
        
        # Crear resumen
        resumen = ResumenDiario(
            coder_id=coder_id,
            fecha=fecha,
            estado_entrada="ausente",
            minutos_retardo=None,
            estado_salida=None,
            salida_inferida=False,
            tiempo_trabajado_min=0,
            ausente=True
        )
        self.db.add(resumen)
        self.db.flush()  # Para obtener el ID
        
        # Guardar incidencias
        for incidencia_text in resultado.incidencias:
            incidencia = Incidencia(
                resumen_id=resumen.id,
                tipo="ausente",
                descripcion=incidencia_text,
                minutos=None
            )
            self.db.add(incidencia)
        
        self.db.commit()
    
    def _guardar_resumen(self, coder_id: int, fecha: date, resultado, retardo, abandono, tiempo):
        """Guarda el resumen diario y sus incidencias en la base de datos"""
        from app.db.models import ResumenDiario, Incidencia
        
        # Eliminar resumen existente para evitar duplicados
        self.db.query(ResumenDiario).filter(
            ResumenDiario.coder_id == coder_id,
            ResumenDiario.fecha == fecha
        ).delete()
        
        # Determinar estado de salida
        estado_salida = abandono["estado"]
        salida_inferida = (abandono["estado"] == "sin_salida")
        
        # Crear resumen
        resumen = ResumenDiario(
            coder_id=coder_id,
            fecha=fecha,
            estado_entrada=retardo["estado"],
            minutos_retardo=retardo["minutos_retardo"],
            estado_salida=estado_salida,
            salida_inferida=salida_inferida,
            tiempo_trabajado_min=resultado.tiempo_total,
            ausente=False
        )
        self.db.add(resumen)
        self.db.flush()  # Para obtener el ID
        
        # Guardar incidencias
        # Incidencias de retardo (ya incluidas en resultado.incidencias)
        # Pero podemos agregar también las específicas
        todas_incidencias = resultado.incidencias
        
        for incidencia_text in todas_incidencias:
            # Determinar tipo basado en contenido
            tipo = "general"
            minutos = None
            if "Retardo" in incidencia_text:
                tipo = "retardo"
                minutos = retardo.get("minutos_retardo")
            elif "Break" in incidencia_text or "break" in incidencia_text:
                tipo = "break"
            elif "Fuga" in incidencia_text or "fuga" in incidencia_text:
                tipo = "fuga"
                minutos = abandono.get("minutos_diferencia")
            elif "Salida anticipada" in incidencia_text:
                tipo = "salida_anticipada"
                minutos = abandono.get("minutos_diferencia")
            elif "Tiempo extra" in incidencia_text:
                tipo = "tiempo_extra"
                minutos = abandono.get("minutos_diferencia")
            
            incidencia = Incidencia(
                resumen_id=resumen.id,
                tipo=tipo,
                descripcion=incidencia_text,
                minutos=minutos
            )
            self.db.add(incidencia)
        
        self.db.commit()

    def procesar_rango(self, coder_id: int, fecha_inicio: date, fecha_fin: date, guardar: bool = True):
        """
        Procesa un rango de fechas para un coder.

        Args:
            coder_id: ID del coder
            fecha_inicio: Fecha inicial (inclusive)
            fecha_fin: Fecha final (inclusive)
            guardar: Si True, guarda los resúmenes en la base de datos

        Returns:
            Dict con fecha -> Resultado
        """
        resultados = {}
        current = fecha_inicio

        while current <= fecha_fin:
            resultado = self.procesar_dia(coder_id, current, guardar=guardar)
            resultados[current] = resultado
            # Avanzar un día
            from datetime import timedelta
            current += timedelta(days=1)

        return resultados