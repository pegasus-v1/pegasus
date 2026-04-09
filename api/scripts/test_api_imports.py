#!/usr/bin/env python3
"""
Verifica que todos los imports de la API funcionen correctamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.api.dependencies import verify_api_key, get_db
    from app.api.router import api_router
    from app.api.endpoints import turnstile_router, procesamiento_router, reportes_router, clanes_router
    
    print("✅ Importes de API exitosos")
    print(f"  • API Router: {api_router}")
    print(f"  • Turnstile Router: {turnstile_router}")
    print(f"  • Procesamiento Router: {procesamiento_router}")
    print(f"  • Reportes Router: {reportes_router}")
    print(f"  • Clanes Router: {clanes_router}")
    
    # Verificar modelos
    from app.db.models import Clan, Coder, Registro, ConfiguracionClan
    print("✅ Importes de modelos exitosos")
    
    # Verificar servicios
    from app.core.orchestrator.procesador_dia import ProcesadorDia
    from app.core.repositories.turnstile_repository import TurnstileImporter
    print("✅ Importes de servicios exitosos")
    
    print("\n✅ Todos los imports funcionan correctamente")
    
except Exception as e:
    print(f"❌ Error en imports: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)