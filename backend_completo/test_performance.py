#!/usr/bin/env python3
"""
Script de prueba para demostrar las mejoras de rendimiento
Test the caching and connection pooling improvements
"""
import time
import requests
import sys

def test_cache_performance():
    """Prueba el rendimiento del caché comparando primera llamada vs segunda"""
    
    # Configurar la URL del servidor (cambiar si es necesario)
    BASE_URL = "http://localhost:5000"
    
    print("=" * 60)
    print("Test de Rendimiento - Sistema de Caché")
    print("=" * 60)
    
    endpoints = [
        "/api/categorias",
        "/api/marcas",
    ]
    
    for endpoint in endpoints:
        print(f"\n📊 Probando endpoint: {endpoint}")
        print("-" * 60)
        
        # Primera llamada (sin caché)
        print("🔵 Primera llamada (SIN caché)...")
        start = time.time()
        try:
            response1 = requests.get(f"{BASE_URL}{endpoint}", timeout=15)
            time1 = (time.time() - start) * 1000
            print(f"   ✅ Tiempo: {time1:.2f}ms")
            print(f"   📦 Items recibidos: {len(response1.json())}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
        
        # Esperar un poco
        time.sleep(0.5)
        
        # Segunda llamada (con caché)
        print("🟢 Segunda llamada (CON caché)...")
        start = time.time()
        try:
            response2 = requests.get(f"{BASE_URL}{endpoint}", timeout=15)
            time2 = (time.time() - start) * 1000
            print(f"   ✅ Tiempo: {time2:.2f}ms")
            print(f"   📦 Items recibidos: {len(response2.json())}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
        
        # Calcular mejora
        if time1 > 0:
            improvement = ((time1 - time2) / time1) * 100
            print(f"\n   🚀 Mejora de rendimiento: {improvement:.1f}%")
            print(f"   ⚡ Reducción de tiempo: {time1 - time2:.2f}ms")
    
    print("\n" + "=" * 60)
    print("Test completado")
    print("=" * 60)
    print("\n💡 Nota: Para ver el máximo beneficio, ejecuta este script")
    print("   cuando el servidor esté recibiendo tráfico real.")
    print("   El caché tiene un TTL de 5 minutos (300 segundos).")

if __name__ == "__main__":
    print("\n⚠️  Asegúrate de que el servidor Flask esté corriendo en localhost:5000")
    print("   Puedes iniciarlo con: python3 server.py\n")
    
    input("Presiona Enter para continuar con el test...")
    
    test_cache_performance()
