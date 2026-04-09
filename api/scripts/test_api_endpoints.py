#!/usr/bin/env python3
"""
Prueba de endpoints de la API Pegasus usando TestClient.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

# Clave API para pruebas (debe coincidir con .env)
API_KEY = "mvp-test-key-123"

client = TestClient(app)

def test_health_endpoint():
    """Prueba el endpoint de salud"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ GET /health")

def test_root_endpoint():
    """Prueba el endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    print("✅ GET /")

def test_turnstile_stats_without_auth():
    """Prueba endpoint protegido sin API key (debe fallar)"""
    response = client.get("/api/v1/turnstile/stats")
    # Debería devolver 403 o 401 (depende de implementación)
    # Nuestra implementación devuelve 403 si no se proporciona API key
    assert response.status_code == 403
    print("✅ GET /api/v1/turnstile/stats sin API key (rechazado)")

def test_turnstile_stats_with_auth():
    """Prueba endpoint protegido con API key"""
    response = client.get("/api/v1/turnstile/stats", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert "total_registros" in data
    print(f"✅ GET /api/v1/turnstile/stats con API key: {data['total_registros']} registros")

def test_clanes_endpoint():
    """Prueba endpoint de clanes"""
    response = client.get("/api/v1/clanes", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ GET /api/v1/clanes: {len(data)} clanes")

def test_reportes_endpoint():
    """Prueba endpoint de reportes (lista de resúmenes)"""
    response = client.get("/api/v1/reportes", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ GET /api/v1/reportes: {len(data)} resúmenes")

def run_all_tests():
    print("🧪 EJECUTANDO PRUEBAS DE ENDPOINTS API")
    print("=" * 60)
    
    try:
        test_health_endpoint()
        test_root_endpoint()
        test_turnstile_stats_without_auth()
        test_turnstile_stats_with_auth()
        test_clanes_endpoint()
        test_reportes_endpoint()
        
        print("\n✅ Todas las pruebas pasaron")
        return 0
    except Exception as e:
        print(f"\n❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())