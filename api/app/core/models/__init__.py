# core/models/__init__.py

from .evento import Evento, TipoEvento
from .persona import Persona
from .resultado import Resultado

__all__ = ["Evento", "TipoEvento", "Persona", "Resultado"]