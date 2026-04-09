#!/usr/bin/env python3
"""
Script de prueba del pipeline completo:
1. Importa registros del torniquete
2. Procesa algunos coders de ejemplo
3. Muestra resultados
"""

import sys
import os
import pathlib
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.core.repositories.turnstile_repository import TurnstileImporter
from app.core.orchestrator.procesador_dia import ProcesadorDia
from app.db.models import Coder, Registro

def test_pipeline():
    """Probar pipeline completo"""
    
    print("🧪 TEST DEL PIPELINE COMPLETO")
    print("=" * 60)
    
    # Ruta al archivo de torniquete
    base_dir = pathlib.Path(__file__).parent.parent.parent
    file_path = base_dir / "data" / "torniquete.xlsx"
    
    if not file_path.exists():
        print(f"❌ Archivo {file_path} no encontrado")
        sys.exit(1)
    
    db = SessionLocal()
    
    try:
        # 1. Verificar estado inicial
        registros_count = db.query(Registro).count()
        print(f"1. Estado inicial:")
        print(f"   • Registros en DB: {registros_count}")
        
        if registros_count == 0:
            print("   • Importando registros del torniquete...")
            
            # Importar registros
            total, matched, errors = TurnstileImporter.import_and_save(
                str(file_path), db_session=db
            )
            print(f"   • Registros importados: {matched}/{total}")
        
        # 2. Obtener algunos coders para probar
        coders = db.query(Coder).limit(5).all()
        print(f"\n2. Procesando {len(coders)} coders de prueba:")
        
        for coder in coders:
            print(f"\n   👤 Coder: {coder.nombre} (ID: {coder.id})")
            print(f"     Clan: {coder.clan.nombre if coder.clan else 'N/A'}")
            
            # Obtener fechas con registros para este coder
            fechas = db.query(Registro.fecha).filter_by(coder_id=coder.id).distinct().all()
            fechas = [f[0] for f in fechas][:3]  # Tomar primeras 3 fechas
            
            if not fechas:
                print(f"     ⚠️  Sin registros para procesar")
                continue
            
            # Procesar cada fecha
            procesador = ProcesadorDia(db)
            
            for fecha in fechas:
                print(f"\n     📅 Fecha: {fecha}")
                try:
                    resultado = procesador.procesar_dia(coder.id, fecha)
                    
                    print(f"       Estado: {resultado.estado}")
                    print(f"       Tiempo total: {resultado.tiempo_total} min "
                          f"({resultado.tiempo_total // 60}h {resultado.tiempo_total % 60}m)")
                    
                    if resultado.incidencias:
                        print(f"       Incidencias ({len(resultado.incidencias)}):")
                        for inc in resultado.incidencias[:3]:  # Mostrar primeras 3
                            print(f"         • {inc}")
                        if len(resultado.incidencias) > 3:
                            print(f"         • ... y {len(resultado.incidencias) - 3} más")
                    else:
                        print(f"       ✅ Sin incidencias")
                        
                except Exception as e:
                    print(f"       ❌ Error al procesar: {e}")
        
        # 3. Estadísticas finales
        print(f"\n3. Estadísticas finales:")
        total_registros = db.query(Registro).count()
        total_coders = db.query(Coder).count()
        print(f"   • Coders en sistema: {total_coders}")
        print(f"   • Registros de torniquete: {total_registros}")
        
        # Contar registros por clan
        from app.db.models import Clan
        clanes = db.query(Clan).all()
        print(f"\n   • Registros por clan:")
        for clan in clanes:
            count = db.query(Registro).join(Coder).filter(Coder.clan_id == clan.id).count()
            coder_count = db.query(Coder).filter_by(clan_id=clan.id).count()
            print(f"     • {clan.nombre}: {coder_count} coders, {count} registros")
        
        print("\n✅ Prueba completada")
        
    except Exception as e:
        print(f"\n❌ Error en el pipeline: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_pipeline()