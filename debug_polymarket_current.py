#!/usr/bin/env python3
"""
Buscar API actual de Polymarket para mercados 2025
"""

import requests
import json
from datetime import datetime

def test_different_polymarket_apis():
    """Probar diferentes endpoints de Polymarket"""
    
    apis = [
        {
            "name": "Gamma API (original)", 
            "url": "https://gamma-api.polymarket.com/markets",
            "params": {"limit": 10, "active": True}
        },
        {
            "name": "Gamma API (sin filtro active)",
            "url": "https://gamma-api.polymarket.com/markets", 
            "params": {"limit": 10}
        },
        {
            "name": "CLOB API (actual)",
            "url": "https://clob.polymarket.com/markets",
            "params": {"limit": 10}
        },
        {
            "name": "CLOB API (filtro activos)",
            "url": "https://clob.polymarket.com/markets", 
            "params": {"limit": 10, "active": True}
        },
        {
            "name": "CLOB API (filtro no cerrados)",
            "url": "https://clob.polymarket.com/markets",
            "params": {"limit": 10, "closed": False}
        }
    ]
    
    for api in apis:
        print(f"\n🔍 Probando: {api['name']}")
        print(f"URL: {api['url']}")
        
        try:
            response = requests.get(api['url'], params=api['params'], timeout=5)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Determinar formato
                if isinstance(data, list):
                    markets = data
                    print(f"Formato: Lista directa - {len(markets)} mercados")
                elif isinstance(data, dict) and 'data' in data:
                    markets = data['data']
                    print(f"Formato: {{data: [...]}} - {len(markets)} mercados")
                else:
                    print(f"Formato desconocido: {type(data)}")
                    continue
                
                # Analizar fechas y estado
                if markets:
                    current_year = 2025
                    recent_markets = []
                    
                    for market in markets[:5]:
                        question = market.get('question', 'Sin título')
                        closed = market.get('closed', 'N/A')
                        active = market.get('active', 'N/A')
                        end_date = market.get('end_date', market.get('endDate', ''))
                        
                        # Extraer año de la pregunta o fecha
                        year_in_question = None
                        if '2025' in question or '2025' in str(end_date):
                            year_in_question = 2025
                        elif '2024' in question or '2024' in str(end_date):
                            year_in_question = 2024
                        elif '2023' in question or '2023' in str(end_date):
                            year_in_question = 2023
                            
                        if year_in_question and year_in_question >= 2024:
                            recent_markets.append({
                                'question': question[:60] + "...",
                                'year': year_in_question,
                                'closed': closed,
                                'active': active,
                                'tokens': len(market.get('tokens', []))
                            })
                    
                    print(f"Mercados 2024-2025 encontrados: {len(recent_markets)}")
                    for m in recent_markets[:3]:
                        print(f"  • {m['question']} ({m['year']}) - closed:{m['closed']}, active:{m['active']}, tokens:{m['tokens']}")
                        
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_different_polymarket_apis()