#!/usr/bin/env python3
"""
Script de prueba para el importador de torniquete.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.repositories.turnstile_repository import TurnstileImporter

def test_parse():
    import pathlib
    base_dir = pathlib.Path(__file__).parent.parent.parent
    file_path = base_dir / "data" / "torniquete.xlsx"
    print(f"📂 Leyendo {file_path}")
    
    df = TurnstileImporter.parse_xlsx(file_path)
    print(f"✅ DataFrame shape: {df.shape}")
    print(f"   Columnas: {list(df.columns)}")
    print(f"   Primeras filas:")
    print(df.head())
    
    # Mostrar conteo de estados
    if 'estado' in df.columns:
        print(f"\n📊 Conteo de estados:")
        print(df['estado'].value_counts())
    
    # Mostrar algunos documentos únicos
    if 'documento' in df.columns:
        print(f"\n📋 Documentos únicos: {df['documento'].nunique()}")
        print(df['documento'].head(10).tolist())

if __name__ == "__main__":
    test_parse()