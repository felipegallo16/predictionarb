#!/usr/bin/env python3
"""
Buscar mercados actuales de Polymarket con filtros avanzados
"""

import requests
import json
from datetime import datetime, timedelta

def test_advanced_filters():
    """Probar filtros avanzados en APIs de Polymarket"""
    
    # Fecha actual y futuras
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    next_month = now + timedelta(days=30)
    
    # Formato ISO
    tomorrow_iso = tomorrow.strftime('%Y-%m-%dT%H:%M:%SZ')
    next_month_iso = next_month.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    tests = [
        {
            "name": "CLOB - Solo mercados abiertos (closed=false)",
            "url": "https://clob.polymarket.com/markets",
            "params": {"limit": 50, "closed": "false"}
        },
        {
            "name": "CLOB - Mercados activos (active=true)",
            "url": "https://clob.polymarket.com/markets", 
            "params": {"limit": 50, "active": "true", "closed": "false"}
        },
        {
            "name": "CLOB - Ordenar por fecha final",
            "url": "https://clob.polymarket.com/markets",
            "params": {"limit": 50, "order": "end_date_iso", "order_direction": "DESC"}
        },
        {
            "name": "Gamma - Buscar por términos actuales",
            "url": "https://gamma-api.polymarket.com/markets",
            "params": {"limit": 20, "search": "2025"}
        },
        {
            "name": "Gamma - Buscar elecciones",
            "url": "https://gamma-api.polymarket.com/markets", 
            "params": {"limit": 20, "search": "election"}
        },
        {
            "name": "Gamma - Buscar Trump",
            "url": "https://gamma-api.polymarket.com/markets",
            "params": {"limit": 20, "search": "Trump"}
        }
    ]
    
    for test in tests:
        print(f"\n🔍 {test['name']}")
        
        try:
            response = requests.get(test['url'], params=test['params'], timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Manejar diferentes formatos
                if isinstance(data, list):
                    markets = data
                elif isinstance(data, dict) and 'data' in data:
                    markets = data['data']
                else:
                    print("Formato no reconocido")
                    continue
                
                print(f"Mercados encontrados: {len(markets)}")
                
                # Buscar mercados recientes con tokens y precios válidos
                valid_markets = []
                for market in markets:
                    question = market.get('question', '')
                    tokens = market.get('tokens', [])
                    closed = market.get('closed', True)
                    active = market.get('active', False)
                    end_date = market.get('end_date_iso', market.get('endDate', ''))
                    
                    # Verificar si tiene tokens con precios válidos
                    has_valid_prices = False
                    if tokens:
                        for token in tokens:
                            price = token.get('price', 0)
                            if isinstance(price, (int, float)) and 0 < price < 1:
                                has_valid_prices = True
                                break
                    
                    # Filtrar por criterios de calidad
                    if (not closed and active and tokens and has_valid_prices and 
                        ('2024' in question or '2025' in question or 'election' in question.lower() or 'trump' in question.lower())):
                        valid_markets.append({
                            'question': question[:80],
                            'tokens': len(tokens),
                            'closed': closed,
                            'active': active,
                            'end_date': end_date,
                            'sample_price': tokens[0].get('price') if tokens else None
                        })
                
                print(f"✅ Mercados válidos (abiertos, con precios): {len(valid_markets)}")
                for market in valid_markets[:3]:
                    print(f"  • {market['question']} - Precio: {market['sample_price']}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_advanced_filters()