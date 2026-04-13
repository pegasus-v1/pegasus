#!/usr/bin/env python3
"""
Script para importar coders desde users.json (Moodle) a la base de datos.
Ejecutar: python scripts/import_moodle.py
"""

import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import Coder, Clan

def import_coders():
    """Importar coders desde users.json"""
    
    # Ruta al archivo users.json
    users_path = Path(__file__).parent.parent.parent / "data" / "users.json"
    
    if not users_path.exists():
        print(f" Archivo {users_path} no encontrado")
        sys.exit(1)
    
    with open(users_path, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    print(f" Leyendo {len(users)} coders desde {users_path}")
    
    db = SessionLocal()
    
    try:
        # Obtener mapeo de nombre de clan a ID
        clanes = db.query(Clan).all()
        clan_map = {clan.nombre: clan.id for clan in clanes}
        
        print("🔍 Clanes encontrados:", list(clan_map.keys()))
        
        nuevos = 0
        actualizados = 0
        errores = []
        
        for user in users:
            # Extraer datos
            moodle_id = user.get("id")
            clan_nombre = user.get("group")
            firstname = user.get("firstname", "").strip()
            lastname = user.get("lastname", "").strip()
            document = user.get("document")
            email = user.get("email", "").strip()
            
            # Validaciones básicas
            if not clan_nombre:
                errores.append(f"Usuario {moodle_id} sin clan")
                continue
            
            if clan_nombre not in clan_map:
                errores.append(f"Clan '{clan_nombre}' no encontrado para usuario {moodle_id}")
                continue
            
            if not document:
                errores.append(f"Usuario {moodle_id} sin documento")
                continue
            
            # Formatear nombre completo
            nombre_completo = f"{firstname} {lastname}".strip()
            if not nombre_completo:
                nombre_completo = f"Usuario {moodle_id}"
            
            # Buscar coder por cédula o moodle_id
            coder_existente = db.query(Coder).filter(
                (Coder.cedula == str(document)) | (Coder.moodle_id == moodle_id)
            ).first()
            
            if coder_existente:
                # Actualizar
                coder_existente.nombre = nombre_completo
                coder_existente.email = email
                coder_existente.moodle_id = moodle_id
                coder_existente.clan_id = clan_map[clan_nombre]
                actualizados += 1
                print(f"   Actualizado: {nombre_completo} ({document}) - Clan {clan_nombre}")
            else:
                # Crear nuevo
                nuevo_coder = Coder(
                    cedula=str(document),
                    nombre=nombre_completo,
                    email=email,
                    moodle_id=moodle_id,
                    clan_id=clan_map[clan_nombre]
                )
                db.add(nuevo_coder)
                nuevos += 1
                print(f"   Nuevo: {nombre_completo} ({document}) - Clan {clan_nombre}")
        
        db.commit()
        
        print(f"\n Resumen:")
        print(f"  • Nuevos coders: {nuevos}")
        print(f"  • Coders actualizados: {actualizados}")
        print(f"  • Total en DB: {nuevos + actualizados}")
        
        if errores:
            print(f"\n  Errores ({len(errores)}):")
            for error in errores[:10]:  # Mostrar primeros 10
                print(f"  • {error}")
            if len(errores) > 10:
                print(f"  • ... y {len(errores) - 10} más")
        
        print("\n Importación completada")
        
    except Exception as e:
        db.rollback()
        print(f"\n Error durante la importación: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import_coders()