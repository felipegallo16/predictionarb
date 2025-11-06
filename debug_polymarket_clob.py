#!/usr/bin/env python3
"""
Debug de API CLOB de Polymarket
"""

import requests
import json

def debug_clob_markets():
    """Probar API CLOB de Polymarket"""
    print("=== POLYMARKET CLOB API ===")
    
    url = "https://clob.polymarket.com/markets"
    params = {
        'limit': 10,
        'offset': 0
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo: {type(data)}")
            
            if 'data' in data:
                markets = data['data']
                print(f"Cantidad: {len(markets)}")
                
                for i, market in enumerate(markets[:3]):
                    print(f"\n--- MERCADO {i+1} ---")
                    print(f"Question: {market.get('question')}")
                    print(f"Active: {market.get('active')}")
                    print(f"Closed: {market.get('closed')}")
                    print(f"Tokens: {len(market.get('tokens', []))}")
                    
                    if market.get('tokens'):
                        print("Tokens:")
                        for token in market.get('tokens', []):
                            print(f"  - {token.get('outcome')}: {token.get('price')}")
                            
    except Exception as e:
        print(f"Error: {e}")

def debug_book_api():
    """Probar API Book de Polymarket"""
    print("\n=== POLYMARKET BOOK API ===")
    
    url = "https://clob.polymarket.com/book"
    params = {
        'token_id': '21742633143463906290569050155826241533067272736897614950488156847949938836455'
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_clob_markets()
    debug_book_api()