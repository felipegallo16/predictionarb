#!/usr/bin/env python3
"""
🧪 Script de Diagnóstico - APIs Polymarket y Kalshi
Prueba rápida para verificar conectividad sin bloqueos
"""

import requests
import time
import json

def test_polymarket():
    """Prueba la API de Polymarket (Gamma)"""
    print("🧪 Probando Polymarket...")
    
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        'limit': 10,
        'offset': 0,
        'active': True
    }
    
    start_time = time.time()
    try:
        response = requests.get(url, params=params, timeout=5)
        elapsed = time.time() - start_time
        
        print(f"✅ Respuesta: {response.status_code} ({elapsed:.2f}s)")
        
        if response.status_code == 200:
            data = response.json()
            # Polymarket devuelve una lista directamente
            if isinstance(data, list):
                markets_count = len(data)
            else:
                markets_count = len(data.get('data', []))
            print(f"✅ Éxito: {markets_count} mercados obtenidos")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text[:100]}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏱️ Timeout: >5 segundos ({elapsed:.2f}s)")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error: {str(e)} ({elapsed:.2f}s)")
        return False

def test_kalshi():
    """Prueba la API de Kalshi"""
    print("\n🧪 Probando Kalshi...")
    
    url = "https://api.elections.kalshi.com/trade-api/v2/markets"
    params = {
        'limit': 10,
        'status': 'open'
    }
    
    start_time = time.time()
    try:
        response = requests.get(url, params=params, timeout=5)
        elapsed = time.time() - start_time
        
        print(f"✅ Respuesta: {response.status_code} ({elapsed:.2f}s)")
        
        if response.status_code == 200:
            data = response.json()
            markets_count = len(data.get('markets', []))
            print(f"✅ Éxito: {markets_count} mercados obtenidos")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text[:100]}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏱️ Timeout: >5 segundos ({elapsed:.2f}s)")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error: {str(e)} ({elapsed:.2f}s)")
        return False

def main():
    print("🚀 Test de Diagnóstico - APIs de Predicción")
    print("=" * 50)
    
    poly_ok = test_polymarket()
    kalshi_ok = test_kalshi()
    
    print("\n📊 Resumen:")
    print(f"Polymarket: {'✅ OK' if poly_ok else '❌ FALLO'}")
    print(f"Kalshi: {'✅ OK' if kalshi_ok else '❌ FALLO'}")
    
    if poly_ok and kalshi_ok:
        print("\n🎉 ¡Ambas APIs funcionan! Puedes ejecutar el detector completo.")
        print("Ejecutar: python3 arbitrage_detector.py")
    elif poly_ok or kalshi_ok:
        print("\n⚠️ Solo una API funciona. Revisa tu conexión/VPN.")
    else:
        print("\n🚫 Ninguna API funciona. Verifica:")
        print("• Conexión a internet")
        print("• VPN/Proxy si estás en región bloqueada")
        print("• Firewall corporativo")

if __name__ == "__main__":
    main()
