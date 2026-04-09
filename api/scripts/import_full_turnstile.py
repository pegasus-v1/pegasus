#!/usr/bin/env python3
"""
Importa todos los registros del archivo torniquete.xlsx y procesa todas las fechas.
"""

import sys
import os
import pathlib
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.core.repositories.turnstile_repository import TurnstileImporter
from app.core.orchestrator.procesador_dia import ProcesadorDia
from app.db.models import Registro, Coder, ResumenDiario, Incidencia

def import_full_turnstile():
    """Importa todos los registros del torniquete y procesa todas las fechas"""
    
    print("🚀 IMPORTACIÓN COMPLETA DEL TORNIQUETE")
    print("=" * 60)
    
    # Ruta al archivo
    base_dir = pathlib.Path(__file__).parent.parent.parent
    file_path = base_dir / "data" / "torniquete.xlsx"
    
    if not file_path.exists():
        print(f"❌ Archivo {file_path} no encontrado")
        sys.exit(1)
    
    db = SessionLocal()
    
    try:
        # 1. Limpiar tablas dependientes (incidencias, resúmenes, registros)
        print("1. Limpiando tablas existentes...")
        db.query(Incidencia).delete()
        db.query(ResumenDiario).delete()
        db.query(Registro).delete()
        db.commit()
        print("   ✅ Tablas limpiadas")
        
        # 2. Importar todos los registros del archivo
        print("\n2. Importando registros del torniquete...")
        total, matched, errors = TurnstileImporter.import_and_save(str(file_path), db_session=db)
        print(f"   ✅ Importados {matched}/{total} registros")
        if errors:
            print(f"   ⚠️  Errores: {errors}")
        
        # 3. Obtener estadísticas
        total_registros = db.query(Registro).count()
        total_coders = db.query(Coder).count()
        print(f"\n3. Estadísticas:")
        print(f"   • Coders en sistema: {total_coders}")
        print(f"   • Registros de torniquete: {total_registros}")
        
        # 4. Obtener fechas únicas con registros
        fechas = db.query(Registro.fecha).distinct().all()
        fechas = [f[0] for f in fechas]
        print(f"\n4. Fechas únicas con registros: {len(fechas)}")
        for f in sorted(fechas)[:10]:  # Mostrar primeras 10
            print(f"   • {f}")
        if len(fechas) > 10:
            print(f"   • ... y {len(fechas) - 10} más")
        
        # 5. Procesar cada coder para cada fecha
        print("\n5. Procesando jornadas...")
        procesador = ProcesadorDia(db)
        total_procesados = 0
        incidencias_totales = 0
        
        coders = db.query(Coder).all()
        for coder in coders:
            for fecha in fechas:
                # Verificar si hay registros para este coder en esta fecha
                tiene_registros = db.query(Registro).filter(
                    Registro.coder_id == coder.id,
                    Registro.fecha == fecha
                ).count() > 0
                
                if tiene_registros:
                    resultado = procesador.procesar_dia(coder.id, fecha, guardar=True)
                    total_procesados += 1
                    incidencias_totales += len(resultado.incidencias)
                    
                    # Mostrar progreso cada 50 procesamientos
                    if total_procesados % 50 == 0:
                        print(f"   Procesados {total_procesados} jornadas...")
        
        print(f"\n   ✅ Total jornadas procesadas: {total_procesados}")
        print(f"   📊 Total incidencias detectadas: {incidencias_totales}")
        
        # 6. Estadísticas finales
        print("\n6. Estadísticas finales:")
        total_resumenes = db.query(ResumenDiario).count()
        total_incidencias = db.query(Incidencia).count()
        print(f"   • Resúmenes diarios guardados: {total_resumenes}")
        print(f"   • Incidencias guardadas: {total_incidencias}")
        
        # Resúmenes por clan
        from app.db.models import Clan
        clanes = db.query(Clan).all()
        print(f"\n   • Resúmenes por clan:")
        for clan in clanes:
            count = db.query(ResumenDiario).join(Coder).filter(Coder.clan_id == clan.id).count()
            coder_count = db.query(Coder).filter_by(clan_id=clan.id).count()
            print(f"     • {clan.nombre}: {coder_count} coders, {count} resúmenes")
        
        print("\n🎉 IMPORTACIÓN Y PROCESAMIENTO COMPLETADOS")
        
    except Exception as e:
        print(f"\n❌ Error durante la importación: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    import_full_turnstile()