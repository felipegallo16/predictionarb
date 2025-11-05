#!/usr/bin/env python3
"""
Script de diagnóstico rápido para probar APIs

Este script prueba las APIs con timeouts MUY cortos para
identificar exactamente dónde se está trabando.
"""

import requests
import time

def test_polymarket():
    """Test rápido de Polymarket"""
    print("🧪 Probando Polymarket...")
    print("URL: https://gamma-api.polymarket.com/markets")

    try:
        start = time.time()
        response = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={'limit': 5, 'closed': 'false'},
            timeout=5
        )
        elapsed = time.time() - start

        print(f"✅ Respuesta: {response.status_code} ({elapsed:.2f}s)")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mercados obtenidos: {len(data)}")
            if data:
                print(f"✅ Primer mercado: {data[0].get('question', 'N/A')[:50]}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text[:200]}")

    except requests.exceptions.Timeout:
        print(f"⏱️ TIMEOUT después de 5 segundos")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()

def test_kalshi():
    """Test rápido de Kalshi"""
    print("🧪 Probando Kalshi...")
    print("URL: https://api.elections.kalshi.com/trade-api/v2/markets")

    try:
        start = time.time()
        response = requests.get(
            "https://api.elections.kalshi.com/trade-api/v2/markets",
            params={'limit': 5, 'status': 'open'},
            timeout=5
        )
        elapsed = time.time() - start

        print(f"✅ Respuesta: {response.status_code} ({elapsed:.2f}s)")
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            print(f"✅ Mercados obtenidos: {len(markets)}")
            if markets:
                print(f"✅ Primer mercado: {markets[0].get('title', 'N/A')[:50]}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text[:200]}")

    except requests.exceptions.Timeout:
        print(f"⏱️ TIMEOUT después de 5 segundos")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()

def main():
    print("="*60)
    print("DIAGNÓSTICO RÁPIDO DE APIs")
    print("="*60)
    print()
    print("Este script prueba ambas APIs con timeout de 5 segundos.")
    print("Si tarda más, sabrás exactamente cuál API se está trabando.")
    print()
    print("="*60)
    print()

    # Test 1: Polymarket
    test_polymarket()

    # Test 2: Kalshi
    test_kalshi()

    print("="*60)
    print("DIAGNÓSTICO COMPLETO")
    print("="*60)
    print()
    print("Si ambas dieron ✅, las APIs funcionan correctamente.")
    print("Si alguna dio ⏱️ TIMEOUT, esa API está bloqueada o muy lenta.")
    print("Si dio ❌ 403, necesitas VPN o cambiar de ubicación.")
    print()

if __name__ == "__main__":
    main()
