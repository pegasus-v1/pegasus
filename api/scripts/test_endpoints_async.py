#!/usr/bin/env python3
"""
Prueba endpoints usando httpx AsyncClient directamente con la app ASGI.
"""

import asyncio
import sys
import os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from main import app

API_KEY = "mvp-test-key-123"

async def test_endpoint(client, endpoint, params=None):
    """Prueba un endpoint GET"""
    if params:
        # Construir query string
        from urllib.parse import urlencode
        endpoint = f"{endpoint}?{urlencode(params)}"
    
    print(f"Testing {endpoint}...")
    
    try:
        response = await client.get(endpoint, headers={"X-API-Key": API_KEY})
        
        if response.status_code != 200:
            print(f"  ❌ Failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
        
        print(f"  ✅ Success")
        data = response.json()
        
        # Imprimir resumen básico
        if isinstance(data, list):
            print(f"  Items: {len(data)}")
        elif isinstance(data, dict):
            if "total" in data:
                print(f"  Total: {data['total']}")
            elif "fecha" in data:
                print(f"  Fecha: {data['fecha']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

async def run_tests():
    print("🧪 PRUEBAS DE ENDPOINTS CON ASYNC CLIENT")
    print("=" * 60)
    
    # Crear cliente ASGI
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Obtener una fecha con datos (usar ayer)
        test_date = date.today() - timedelta(days=1)
        test_date_str = test_date.strftime("%Y-%m-%d")
        
        tests = [
            # Endpoints básicos
            ("/health", None),
            ("/", None),
            ("/api/v1/turnstile/stats", None),
            ("/api/v1/clanes", None),
            
            # Endpoints de reportes
            ("/api/v1/reportes/resumen-diario", {"fecha": test_date_str}),
            ("/api/v1/reportes/ausentes-hoy", None),
            
            # Endpoints compatibles
            ("/api/reportes/resumen-dia", {"fecha": test_date_str}),
            ("/api/reportes/tarde", {"fecha": test_date_str}),
            ("/api/reportes/ausentes", {"fecha": test_date_str}),
            ("/api/reportes/fuga-manana", {"fecha": test_date_str}),
            ("/api/reportes/exceso-break", {"fecha": test_date_str, "tipo": "ambos"}),
            ("/api/reportes/salidas-anticipadas", {"fecha": test_date_str}),
            
            # Endpoints de coders
            ("/api/coders/estudiantes", None),
            ("/api/coders/buscar", {"q": "a"}),
        ]
        
        passed = 0
        total = len(tests)
        
        for endpoint, params in tests:
            if await test_endpoint(client, endpoint, params):
                passed += 1
            print()
        
        # Probar endpoint de detalle (necesita un ID de coder existente)
        print("Testing /api/coders/buscar/detalle...")
        # Primero obtener un coder
        response = await client.get("/api/coders/estudiantes", headers={"X-API-Key": API_KEY})
        if response.status_code == 200:
            coders = response.json()
            if coders:
                coder_id = coders[0]["id"]
                params = {"id": coder_id, "fecha": test_date_str}
                if await test_endpoint(client, "/api/coders/buscar/detalle", params):
                    passed += 1
                total += 1
        
        # Probar historial de coder
        if coders:
            coder_id = coders[0]["id"]
            params = {"dias": 7}
            if await test_endpoint(client, f"/api/coders/estudiantes/{coder_id}/historial", params):
                passed += 1
            total += 1
        
        print(f"\n✅ Resultado: {passed}/{total} pruebas pasadas")
        
        if passed == total:
            print("🎉 ¡Todas las pruebas pasaron!")
            return 0
        else:
            print("⚠️  Algunas pruebas fallaron")
            return 1

def main():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_tests())

if __name__ == "__main__":
    sys.exit(main())