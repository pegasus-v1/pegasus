#!/usr/bin/env python3
"""
Importar una muestra de registros del torniquete (primeras 1000 filas) para pruebas.
"""

import sys
import os
import pandas as pd
import pathlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import Coder, Registro

def import_sample(n_rows=1000):
    """Importar muestra de registros"""
    
    base_dir = pathlib.Path(__file__).parent.parent.parent
    file_path = base_dir / "data" / "torniquete.xlsx"
    
    if not file_path.exists():
        print(f"❌ Archivo {file_path} no encontrado")
        sys.exit(1)
    
    print(f"📂 Leyendo primeras {n_rows} filas de {file_path}")
    
    # Leer solo n_rows filas
    df = pd.read_excel(file_path, nrows=n_rows)
    
    # Normalizar nombres de columnas
    column_map = {}
    for col in df.columns:
        col_lower = col.strip().lower()
        if 'time' in col_lower:
            column_map[col] = 'timestamp'
        elif 'person' in col_lower:
            column_map[col] = 'nombre'
        elif 'id' in col_lower:
            column_map[col] = 'documento'
        elif 'status' in col_lower or 'entered/exited' in col_lower:
            column_map[col] = 'estado'
    
    df = df.rename(columns=column_map)
    
    # Asegurar que timestamp sea datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Limpiar documento
    if 'documento' in df.columns:
        df['documento'] = df['documento'].astype(str).str.strip()
    
    # Normalizar estado
    if 'estado' in df.columns:
        df['estado'] = df['estado'].astype(str).str.strip().str.lower()
        df['estado'] = df['estado'].map({
            'in': 'entrada',
            'out': 'salida',
            'entered': 'entrada',
            'exited': 'salida'
        })
    
    print(f"📊 {len(df)} registros leídos")
    
    db = SessionLocal()
    
    try:
        # Obtener todos los coders y crear diccionario
        coders = db.query(Coder).all()
        coder_dict = {str(c.cedula).strip(): c for c in coders}
        print(f"🔍 {len(coder_dict)} coders en diccionario")
        
        # Preparar registros para bulk insert
        registros_dicts = []
        matched = 0
        
        for _, row in df.iterrows():
            documento = str(row.get('documento', '')).strip()
            if not documento:
                continue
            
            coder = coder_dict.get(documento)
            if not coder:
                continue
            
            dt = row['timestamp']
            registros_dicts.append({
                'coder_id': coder.id,
                'fecha': dt.date(),
                'hora': dt.time(),
                'estado_acceso': row.get('estado', 'entrada'),
                'tipo_evento': None,
                'dispositivo': 'torniquete'
            })
            matched += 1
        
        print(f"🔍 {matched} registros matcheados con coders")
        
        # Bulk insert
        if registros_dicts:
            db.bulk_insert_mappings(Registro, registros_dicts)
            db.commit()
            print(f"💾 {matched} registros guardados (bulk insert)")
        else:
            print("⚠️  No hay registros para guardar")
        
        # Verificar
        total_registros = db.query(Registro).count()
        print(f"📊 Total registros en DB después de importación: {total_registros}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import_sample(1000)  # Importar primeras 1000 filas