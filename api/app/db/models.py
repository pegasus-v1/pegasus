from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Time, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .session import Base

class Clan(Base):
    __tablename__ = "clanes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    hora_entrada = Column(Time)  # Time
    hora_salida = Column(Time)
    tiempo_alimentacion_minutos = Column(Integer)
    
    # Relaciones
    configuracion = relationship("ConfiguracionClan", back_populates="clan", uselist=False)
    coders = relationship("Coder", back_populates="clan")
    team_leaders = relationship("TeamLeader", back_populates="clan")

class ConfiguracionClan(Base):
    __tablename__ = "configuraciones_clan"
    
    id = Column(Integer, primary_key=True, index=True)
    clan_id = Column(Integer, ForeignKey("clanes.id"), unique=True)
    
    # Tolerancias (minutos)
    tolerancia_entrada_min = Column(Integer, default=20)
    tolerancia_retardo_leve = Column(Integer, default=40)
    tolerancia_retardo_grave = Column(Integer, default=60)
    tolerancia_salida_min = Column(Integer, default=10)
    
    # Breaks
    break1_inicio = Column(Time, nullable=False)
    break1_fin = Column(Time, nullable=False)
    break1_tolerancia = Column(Integer, default=5)
    
    break2_inicio = Column(Time, nullable=False)
    break2_fin = Column(Time, nullable=False)
    break2_tolerancia = Column(Integer, default=5)
    
    # Reglas de fuga
    fuga_minutos_limite = Column(Integer, default=30)
    
    # Relación
    clan = relationship("Clan", back_populates="configuracion")

class Coder(Base):
    __tablename__ = "coder"
    
    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    moodle_id = Column(Integer, unique=True)
    clan_id = Column(Integer, ForeignKey("clanes.id"))
    
    # Relaciones
    clan = relationship("Clan", back_populates="coders")
    registros = relationship("Registro", back_populates="coder")
    correos_enviados = relationship("CorreoEnviado", back_populates="coder")

class Registro(Base):
    __tablename__ = "registros"
    
    id = Column(Integer, primary_key=True, index=True)
    coder_id = Column(Integer, ForeignKey("coder.id"))
    fecha = Column(Date)  # Date
    hora = Column(Time)   # Time
    estado_acceso = Column(String(20))
    tipo_evento = Column(String(30), nullable=True)
    dispositivo = Column(String(50), nullable=True)
    
    # Relación
    coder = relationship("Coder", back_populates="registros")

class CorreoEnviado(Base):
    __tablename__ = "correos_enviados"
    
    id = Column(Integer, primary_key=True, index=True)
    coder_id = Column(Integer, ForeignKey("coder.id"))
    tipo_correo = Column(String(50), default="ausencia")
    estado = Column(String(20))
    fecha_envio = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    coder = relationship("Coder", back_populates="correos_enviados")

class TeamLeader(Base):
    __tablename__ = "team_leaders"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)
    clan_id = Column(Integer, ForeignKey("clanes.id"))
    
    # Relación
    clan = relationship("Clan", back_populates="team_leaders")

# Modelos para procesamiento (no persistentes en BD)
class ResumenDiario(Base):
    __tablename__ = "resumenes_diarios"
    
    id = Column(Integer, primary_key=True, index=True)
    coder_id = Column(Integer, ForeignKey("coder.id"))
    fecha = Column(Date)  # Date
    estado_entrada = Column(String(50))
    minutos_retardo = Column(Integer)
    estado_salida = Column(String(50))
    salida_inferida = Column(Boolean, default=False)
    tiempo_trabajado_min = Column(Integer)
    ausente = Column(Boolean, default=False)
    
    # Relación
    coder = relationship("Coder")

class Incidencia(Base):
    __tablename__ = "incidencias"
    
    id = Column(Integer, primary_key=True, index=True)
    resumen_id = Column(Integer, ForeignKey("resumenes_diarios.id"))
    tipo = Column(String(50))
    descripcion = Column(String(255))
    minutos = Column(Integer)
    
    # Relación
    resumen = relationship("ResumenDiario")