# core/models/resultado.py

class Resultado:
    def __init__(self, persona_id: int):
        self.persona_id = persona_id
        self.estado = None
        self.incidencias = []
        self.tiempo_total = 0  # en minutos

    def agregar_incidencia(self, incidencia: str):
        self.incidencias.append(incidencia)

    def __repr__(self):
        return (
            f"Resultado(persona_id={self.persona_id}, "
            f"estado={self.estado}, "
            f"incidencias={self.incidencias}, "
            f"tiempo_total={self.tiempo_total})"
        )