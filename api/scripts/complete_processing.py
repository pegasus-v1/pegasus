#!/usr/bin/env python3
"""
Completa el procesamiento de todas las combinaciones coder-fecha que faltan.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.core.orchestrator.procesador_dia import ProcesadorDia
from app.db.models import Coder, Registro, ResumenDiario

def complete_processing():
    """Procesa combinaciones coder-fecha faltantes"""
    
    print("🔧 COMPLETANDO PROCESAMIENTO DE JORNADAS")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Obtener todas las fechas únicas con registros
        fechas = db.query(Registro.fecha).distinct().all()
        fechas = [f[0] for f in fechas]
        print(f"1. Fechas únicas: {len(fechas)}")
        
        # Obtener todos los coders
        coders = db.query(Coder).all()
        print(f"2. Coders totales: {len(coders)}")
        
        # Combinaciones totales
        total_combinaciones = len(coders) * len(fechas)
        print(f"3. Combinaciones posibles: {total_combinaciones}")
        
        # Contar resúmenes existentes
        resumenes_existentes = db.query(ResumenDiario).count()
        print(f"4. Resúmenes ya existentes: {resumenes_existentes}")
        
        procesador = ProcesadorDia(db)
        procesados = 0
        nuevos_resumenes = 0
        nuevas_incidencias = 0
        
        print("\n5. Procesando combinaciones faltantes...")
        for coder in coders:
            for fecha in fechas:
                # Verificar si ya existe resumen para esta combinación
                existe = db.query(ResumenDiario).filter(
                    ResumenDiario.coder_id == coder.id,
                    ResumenDiario.fecha == fecha
                ).first()
                
                if existe:
                    continue
                
                # Verificar si hay registros para este coder en esta fecha
                tiene_registros = db.query(Registro).filter(
                    Registro.coder_id == coder.id,
                    Registro.fecha == fecha
                ).count() > 0
                
                # Procesar (guardar=True)
                resultado = procesador.procesar_dia(coder.id, fecha, guardar=True)
                procesados += 1
                nuevos_resumenes += 1
                nuevas_incidencias += len(resultado.incidencias)
                
                # Mostrar progreso cada 50 procesamientos
                if procesados % 50 == 0:
                    print(f"   Procesadas {procesados} combinaciones...")
        
        print(f"\n   ✅ Combinaciones procesadas: {procesados}")
        print(f"   📊 Nuevos resúmenes creados: {nuevos_resumenes}")
        print(f"   ⚠️  Nuevas incidencias registradas: {nuevas_incidencias}")
        
        # Estadísticas finales
        total_resumenes = db.query(ResumenDiario).count()
        total_incidencias = db.query(ResumenDiario).count()  # Incidencia count?
        from app.db.models import Incidencia
        total_incidencias = db.query(Incidencia).count()
        print(f"\n6. Totales finales:")
        print(f"   • Resúmenes diarios: {total_resumenes}")
        print(f"   • Incidencias: {total_incidencias}")
        
        # Verificar que todas las combinaciones están cubiertas
        if total_resumenes == total_combinaciones:
            print("\n🎉 ¡Todas las combinaciones han sido procesadas!")
        else:
            print(f"\n⚠️  Aún faltan {total_combinaciones - total_resumenes} combinaciones")
        
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    complete_processing()