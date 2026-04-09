# core/models/persona.py

class Persona:
    def __init__(self, id: int, nombre: str):
        self.id = id
        self.nombre = nombre

    def __repr__(self):
        return f"Persona(id={self.id}, nombre='{self.nombre}')"