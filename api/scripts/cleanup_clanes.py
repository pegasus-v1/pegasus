#!/usr/bin/env python3
"""
Script para eliminar los clanes de prueba y sus datos asociados.
Elimina: Gosling, Lovelace, Berners-Lee, Borg, Dijkstra
Mantiene: Hamilton, Thompson, Nakamoto, Tesla, McCarty
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import Clan, Coder, Registro, CorreoEnviado, ConfiguracionClan

def cleanup_clanes():
    """Eliminar clanes de prueba y sus datos asociados"""
    
    clanes_a_eliminar = ["Gosling", "Lovelace", "Berners-Lee", "Borg", "Dijkstra"]
    clanes_a_mantener = ["Hamilton", "Thompson", "Nakamoto", "Tesla", "McCarty"]
    
    db = SessionLocal()
    
    try:
        print("🧹 Limpieza de clanes de prueba")
        print(f"Clanes a eliminar: {', '.join(clanes_a_eliminar)}")
        print(f"Clanes a mantener: {', '.join(clanes_a_mantener)}")
        print("-" * 60)
        
        # 1. Obtener IDs de clanes a eliminar
        clanes_eliminar = db.query(Clan).filter(Clan.nombre.in_(clanes_a_eliminar)).all()
        clanes_eliminar_ids = [c.id for c in clanes_eliminar]
        
        if not clanes_eliminar_ids:
            print("✅ No hay clanes a eliminar")
            return
        
        print(f"📋 Encontrados {len(clanes_eliminar)} clanes a eliminar")
        
        # 2. Obtener coders de estos clanes
        coders_a_eliminar = db.query(Coder).filter(Coder.clan_id.in_(clanes_eliminar_ids)).all()
        coder_ids = [c.id for c in coders_a_eliminar]
        
        print(f"📋 {len(coders_a_eliminar)} coders asociados a eliminar")
        
        # 3. Eliminar registros de estos coders
        if coder_ids:
            registros_eliminados = db.query(Registro).filter(Registro.coder_id.in_(coder_ids)).delete(synchronize_session=False)
            print(f"🗑️  Eliminados {registros_eliminados} registros de torniquete")
        
        # 4. Eliminar correos enviados de estos coders
        if coder_ids:
            correos_eliminados = db.query(CorreoEnviado).filter(CorreoEnviado.coder_id.in_(coder_ids)).delete(synchronize_session=False)
            print(f"🗑️  Eliminados {correos_eliminados} correos enviados")
        
        # 5. Eliminar configuraciones de clan
        configs_eliminadas = db.query(ConfiguracionClan).filter(ConfiguracionClan.clan_id.in_(clanes_eliminar_ids)).delete(synchronize_session=False)
        print(f"🗑️  Eliminadas {configs_eliminadas} configuraciones de clan")
        
        # 6. Eliminar los coders
        if coder_ids:
            coders_eliminados = db.query(Coder).filter(Coder.id.in_(coder_ids)).delete(synchronize_session=False)
            print(f"🗑️  Eliminados {coders_eliminados} coders")
        
        # 7. Eliminar los clanes
        clanes_eliminados = db.query(Clan).filter(Clan.id.in_(clanes_eliminar_ids)).delete(synchronize_session=False)
        print(f"🗑️  Eliminados {clanes_eliminados} clanes")
        
        # 8. Verificar estado final
        db.commit()
        
        print("\n✅ Limpieza completada")
        print("-" * 60)
        
        # Verificar clanes restantes
        clanes_restantes = db.query(Clan).all()
        print(f"📊 Clanes restantes ({len(clanes_restantes)}):")
        for clan in clanes_restantes:
            coder_count = db.query(Coder).filter_by(clan_id=clan.id).count()
            print(f"  • {clan.nombre}: {coder_count} coders")
        
        # Verificar total de coders
        total_coders = db.query(Coder).count()
        print(f"\n📊 Total coders en sistema: {total_coders}")
        
        # Verificar que sean exactamente 99
        if total_coders == 99:
            print("✅ Correcto: 99 coders (los importados desde users.json)")
        else:
            print(f"⚠️  Atención: {total_coders} coders (se esperaban 99)")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la limpieza: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_clanes()