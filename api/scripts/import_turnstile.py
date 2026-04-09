#!/usr/bin/env python3
"""
Script para importar datos del torniquete desde XLSX a la base de datos.
"""

import sys
import os
import pathlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.repositories.turnstile_repository import TurnstileImporter
from app.db.session import SessionLocal

def import_turnstile():
    """Importar archivo de torniquete"""
    
    # Ruta al archivo
    base_dir = pathlib.Path(__file__).parent.parent.parent
    file_path = base_dir / "data" / "torniquete.xlsx"
    
    if not file_path.exists():
        print(f"❌ Archivo {file_path} no encontrado")
        sys.exit(1)
    
    print(f"📂 Importando {file_path}")
    
    db = SessionLocal()
    
    try:
        total, matched, errors = TurnstileImporter.import_and_save(
            str(file_path), db_session=db
        )
        
        print(f"\n📈 Resultado:")
        print(f"  • Registros en archivo: {total}")
        print(f"  • Registros matcheados y guardados: {matched}")
        print(f"  • Registros sin match: {total - matched}")
        print(f"  • Errores: {len(errors)}")
        
        if matched > 0:
            # Verificar conteo en base de datos
            from app.db.models import Registro
            count = db.query(Registro).count()
            print(f"  • Total registros en DB: {count}")
        
        print("\n✅ Importación completada")
        
    except Exception as e:
        print(f"\n❌ Error durante la importación: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import_turnstile()