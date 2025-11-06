#!/usr/bin/env python3
"""
Debug del emparejamiento de mercados
"""

from arbitrage_detector_quick import QuickArbitrageDetector
import logging

logging.basicConfig(level=logging.INFO)

def debug_market_matching():
    """Debug del proceso de emparejamiento"""
    print("🔍 DEBUG EMPAREJAMIENTO DE MERCADOS")
    print("=" * 50)
    
    # Crear detector con umbral bajo
    detector = QuickArbitrageDetector(similarity_threshold=50.0)  # Umbral bajo
    
    # Obtener mercados
    poly_markets, kalshi_markets = detector.fetch_all_markets()
    
    print(f"\n📊 Mercados obtenidos:")
    print(f"  - Polymarket: {len(poly_markets)}")
    print(f"  - Kalshi: {len(kalshi_markets)}")
    
    # Mostrar muestra de títulos
    print(f"\n📝 Muestra de títulos Polymarket:")
    for i, market in enumerate(poly_markets[:5]):
        print(f"  {i+1}. {market['title'][:60]}...")
        
    print(f"\n📝 Muestra de títulos Kalshi:")
    for i, market in enumerate(kalshi_markets[:5]):
        print(f"  {i+1}. {market['title'][:60]}...")
    
    # Intentar emparejamiento
    print(f"\n🔗 Intentando emparejamiento (umbral: 50%)...")
    matches = detector.match_markets(poly_markets, kalshi_markets)
    
    print(f"✓ {len(matches)} pares encontrados")
    
    if matches:
        print(f"\n📋 Primeros 3 emparejamientos:")
        for i, match in enumerate(matches[:3]):
            poly = match['polymarket']
            kalshi = match['kalshi']
            similarity = match['similarity']
            print(f"  {i+1}. Similitud: {similarity:.1f}%")
            print(f"     Poly:   {poly['title'][:50]}...")
            print(f"     Kalshi: {kalshi['title'][:50]}...")
            print()
    else:
        # Intentar con umbral aún más bajo
        print(f"\n🔗 Intentando con umbral 30%...")
        detector.similarity_threshold = 30.0
        matches = detector.match_markets(poly_markets, kalshi_markets)
        print(f"✓ {len(matches)} pares encontrados con umbral 30%")

if __name__ == "__main__":
    debug_market_matching()