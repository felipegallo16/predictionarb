#!/usr/bin/env python3
"""
Debug de datos de APIs para entender formato
"""

import requests
import json

def debug_polymarket():
    """Ver formato real de datos de Polymarket"""
    print("=== POLYMARKET DEBUG ===")
    
    url = "https://gamma-api.polymarket.com/markets"
    # Probar sin filtro active para ver mercados más recientes
    params = {
        'limit': 20,
        'offset': 0
        # Removido: 'active': True
    }
    
    response = requests.get(url, params=params, timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Tipo: {type(data)}")
        print(f"Cantidad: {len(data) if isinstance(data, list) else 'No es lista'}")
        
        if isinstance(data, list) and len(data) > 0:
            # Buscar un mercado con tokens
            valid_market = None
            for i, market in enumerate(data):
                tokens = market.get('tokens', [])
                if len(tokens) > 0:
                    valid_market = market
                    print(f"\n--- MERCADO {i+1} (CON TOKENS) ---")
                    break
                else:
                    print(f"Mercado {i+1}: sin tokens, closed={market.get('closed')}, active={market.get('active')}")
            
            if valid_market:
                print(json.dumps(valid_market, indent=2)[:1000] + "...")
                
                print(f"\nCampos principales:")
                print(f"- question: {valid_market.get('question')}")
                print(f"- tokens: {len(valid_market.get('tokens', []))} tokens")
                print(f"- closed: {valid_market.get('closed')}")
                print(f"- active: {valid_market.get('active')}")
                
                if valid_market.get('tokens'):
                    print(f"- primer token: {valid_market['tokens'][0]}")
            else:
                print("❌ No encontramos mercados con tokens")

def debug_kalshi():
    """Ver formato real de datos de Kalshi"""
    print("\n=== KALSHI DEBUG ===")
    
    url = "https://api.elections.kalshi.com/trade-api/v2/markets"
    params = {
        'limit': 3,
        'status': 'open'
    }
    
    response = requests.get(url, params=params, timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Tipo: {type(data)}")
        
        markets = data.get('markets', [])
        print(f"Cantidad: {len(markets)}")
        
        if len(markets) > 0:
            print("\n--- PRIMER MERCADO ---")
            market = markets[0]
            print(json.dumps(market, indent=2)[:1000] + "...")
            
            print(f"\nCampos principales:")
            print(f"- title: {market.get('title')}")
            print(f"- ticker: {market.get('ticker')}")
            print(f"- status: {market.get('status')}")
            print(f"- yes_bid: {market.get('yes_bid')}")
            print(f"- last_price: {market.get('last_price')}")

if __name__ == "__main__":
    debug_polymarket()
    debug_kalshi()