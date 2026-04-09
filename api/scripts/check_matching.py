#!/usr/bin/env python3
"""
Script para verificar matching entre documentos en XLSX y coders en DB.
"""

import sys
import os
import pandas as pd
import pathlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import Coder

def check_matching():
    # Ruta al archivo
    base_dir = pathlib.Path(__file__).parent.parent.parent
    file_path = base_dir / "data" / "torniquete.xlsx"
    
    if not file_path.exists():
        print(f"❌ Archivo {file_path} no encontrado")
        return
    
    print(f"📂 Analizando {file_path}")
    
    # Leer archivo
    df = pd.read_excel(file_path)
    
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
    
    # Limpiar documento
    if 'documento' in df.columns:
        df['documento'] = df['documento'].astype(str).str.strip()
    
    # Obtener documentos únicos del archivo
    documentos_xlsx = set(df['documento'].unique())
    print(f"📋 Documentos únicos en XLSX: {len(documentos_xlsx)}")
    
    # Obtener cédulas de coders en DB
    db = SessionLocal()
    try:
        coders = db.query(Coder.cedula).all()
        documentos_db = set(str(c[0]) for c in coders)
        print(f"📋 Cédulas en base de datos: {len(documentos_db)}")
        
        # Calcular intersección
        matching = documentos_xlsx.intersection(documentos_db)
        no_match_xlsx = documentos_xlsx - documentos_db
        no_match_db = documentos_db - documentos_xlsx
        
        print(f"\n🔍 Resultados del matching:")
        print(f"   • Coincidencias: {len(matching)}")
        print(f"   • Documentos en XLSX sin coder en DB: {len(no_match_xlsx)}")
        print(f"   • Coders en DB sin registros en XLSX: {len(no_match_db)}")
        
        if matching:
            print(f"\n✅ Matching exitoso para {len(matching)} coders")
            # Mostrar algunos ejemplos
            print("   Ejemplos de documentos que coinciden:")
            for doc in list(matching)[:10]:
                coder = db.query(Coder).filter_by(cedula=doc).first()
                print(f"   • {doc}: {coder.nombre if coder else 'N/A'}")
        
        if no_match_xlsx:
            print(f"\n⚠️  Documentos en XLSX sin coder en DB (primeros 10):")
            for doc in list(no_match_xlsx)[:10]:
                print(f"   • {doc}")
        
        if no_match_db:
            print(f"\n⚠️  Coders en DB sin registros en XLSX (primeros 10):")
            for doc in list(no_match_db)[:10]:
                coder = db.query(Coder).filter_by(cedula=doc).first()
                print(f"   • {doc}: {coder.nombre if coder else 'N/A'}")
        
        # Calcular registros potenciales a importar
        if 'documento' in df.columns:
            total_registros = len(df)
            registros_con_match = df[df['documento'].isin(matching)]
            print(f"\n📊 Registros en archivo: {total_registros}")
            print(f"📊 Registros con matching: {len(registros_con_match)}")
            print(f"📊 Registros sin matching: {total_registros - len(registros_con_match)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_matching()