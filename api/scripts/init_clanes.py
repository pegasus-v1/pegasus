#!/usr/bin/env python3
"""
Script para inicializar los 5 clanes en la base de datos.
Ejecutar: python scripts/init_clanes.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import time
from app.db.session import SessionLocal
from app.db.models import Clan, ConfiguracionClan

def init_clanes():
    """Inicializar los 5 clanes con sus configuraciones"""
    
    # Configuración de los clanes
    CLANES_CONFIG = {
        "Hamilton": {
            "hora_entrada": time(6, 0, 0),    # 06:00
            "hora_salida": time(14, 0, 0),    # 14:00
            "break1_inicio": time(8, 0, 0),   # 08:00
            "break1_fin": time(8, 30, 0),     # 08:30
            "break2_inicio": time(12, 0, 0),  # 12:00
            "break2_fin": time(13, 0, 0),     # 13:00
            "jornada_mañana": True
        },
        "Thompson": {
            "hora_entrada": time(6, 0, 0),
            "hora_salida": time(14, 0, 0),
            "break1_inicio": time(8, 0, 0),
            "break1_fin": time(8, 30, 0),
            "break2_inicio": time(12, 0, 0),
            "break2_fin": time(13, 0, 0),
            "jornada_mañana": True
        },
        "Nakamoto": {
            "hora_entrada": time(6, 0, 0),
            "hora_salida": time(14, 0, 0),
            "break1_inicio": time(8, 0, 0),
            "break1_fin": time(8, 30, 0),
            "break2_inicio": time(12, 0, 0),
            "break2_fin": time(13, 0, 0),
            "jornada_mañana": True
        },
        "Tesla": {
            "hora_entrada": time(14, 0, 0),    # 14:00
            "hora_salida": time(22, 0, 0),     # 22:00
            "break1_inicio": time(15, 30, 0),  # 15:30
            "break1_fin": time(16, 0, 0),      # 16:00
            "break2_inicio": time(18, 0, 0),   # 18:00
            "break2_fin": time(19, 0, 0),      # 19:00
            "jornada_mañana": False
        },
        "McCarty": {
            "hora_entrada": time(14, 0, 0),
            "hora_salida": time(22, 0, 0),
            "break1_inicio": time(15, 30, 0),
            "break1_fin": time(16, 0, 0),
            "break2_inicio": time(18, 0, 0),
            "break2_fin": time(19, 0, 0),
            "jornada_mañana": False
        }
    }
    
    db = SessionLocal()
    
    try:
        for nombre, config in CLANES_CONFIG.items():
            # Verificar si el clan ya existe
            clan_existente = db.query(Clan).filter_by(nombre=nombre).first()
            
            if clan_existente:
                print(f"Clan {nombre} ya existe, actualizando...")
                clan = clan_existente
            else:
                print(f"Creando clan {nombre}...")
                clan = Clan(nombre=nombre)
                db.add(clan)
                db.flush()  # Para obtener el ID
            
            # Actualizar horas
            clan.hora_entrada = config["hora_entrada"]
            clan.hora_salida = config["hora_salida"]
            clan.tiempo_alimentacion_minutos = 60  # Valor por defecto
            
            # Crear o actualizar configuración
            config_existente = db.query(ConfiguracionClan).filter_by(clan_id=clan.id).first()
            
            if config_existente:
                config_clan = config_existente
            else:
                config_clan = ConfiguracionClan(clan_id=clan.id)
                db.add(config_clan)
            
            # Actualizar configuración
            config_clan.break1_inicio = config["break1_inicio"]
            config_clan.break1_fin = config["break1_fin"]
            config_clan.break2_inicio = config["break2_inicio"]
            config_clan.break2_fin = config["break2_fin"]
            
            print(f"  • Entrada: {config['hora_entrada'].strftime('%H:%M')}")
            print(f"  • Salida: {config['hora_salida'].strftime('%H:%M')}")
            print(f"  • Break 1: {config['break1_inicio'].strftime('%H:%M')} - {config['break1_fin'].strftime('%H:%M')}")
            print(f"  • Break 2: {config['break2_inicio'].strftime('%H:%M')} - {config['break2_fin'].strftime('%H:%M')}")
        
        db.commit()
        print("\n✅ Clanes inicializados exitosamente")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error al inicializar clanes: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_clanes()