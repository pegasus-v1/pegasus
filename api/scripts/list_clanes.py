#!/usr/bin/env python3
"""
Script para listar clanes en la base de datos.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import Clan, Coder, ConfiguracionClan

def list_clanes():
    db = SessionLocal()
    try:
        clanes = db.query(Clan).all()
        print("📋 Clanes en la base de datos:")
        print("ID | Nombre | Hora Entrada | Hora Salida | Coders Asociados")
        print("-" * 80)
        
        for clan in clanes:
            # Contar coders en este clan
            coder_count = db.query(Coder).filter_by(clan_id=clan.id).count()
            
            # Obtener configuración si existe
            config = db.query(ConfiguracionClan).filter_by(clan_id=clan.id).first()
            
            print(f"{clan.id:2d} | {clan.nombre:15s} | "
                  f"{clan.hora_entrada if clan.hora_entrada else 'N/A':10s} | "
                  f"{clan.hora_salida if clan.hora_salida else 'N/A':10s} | "
                  f"{coder_count:3d} coders")
        
        print(f"\nTotal: {len(clanes)} clanes")
        
    finally:
        db.close()

if __name__ == "__main__":
    list_clanes()