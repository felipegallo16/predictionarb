#!/usr/bin/env python3
"""
Script para verificar información de traders
"""

import requests
import json
from datetime import datetime

DATA_API_BASE = "https://data-api.polymarket.com"

def verify_trader(wallet):
    """Verifica información de un trader"""

    print(f"\n{'='*70}")
    print(f"Verificando: {wallet}")
    print(f"{'='*70}")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json'
    })

    # 1. Obtener valor total
    try:
        response = session.get(f"{DATA_API_BASE}/value", params={'user': wallet}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            value = data.get('value', 0)
            print(f"💰 Valor Total: ${value:,.2f} USD")
        else:
            print(f"⚠️  No se pudo obtener valor (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Error obteniendo valor: {e}")

    # 2. Obtener posiciones actuales
    try:
        response = session.get(f"{DATA_API_BASE}/positions", params={'user': wallet, 'limit': 5}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            positions = data if isinstance(data, list) else data.get('data', [])

            print(f"\n📊 Posiciones Actuales: {len(positions)}")

            if positions:
                for i, pos in enumerate(positions[:3], 1):
                    market = pos.get('market', 'Unknown')
                    outcome = pos.get('outcome', 'N/A')
                    current_value = pos.get('currentValue', 0)
                    pnl = pos.get('cashPnl', 0)

                    pnl_symbol = "📈" if pnl >= 0 else "📉"
                    print(f"  {i}. {market[:50]}")
                    print(f"     Outcome: {outcome} | Valor: ${current_value:,.2f} | PnL: {pnl_symbol} ${pnl:,.2f}")
        else:
            print(f"⚠️  No se pudieron obtener posiciones (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Error obteniendo posiciones: {e}")

    # 3. Obtener actividad reciente
    try:
        response = session.get(f"{DATA_API_BASE}/activity", params={'user': wallet, 'limit': 5}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            activities = data if isinstance(data, list) else data.get('data', [])

            print(f"\n📈 Actividad Reciente: {len(activities)} transacciones")

            if activities:
                latest = activities[0]
                timestamp = latest.get('timestamp', 0)
                if timestamp:
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"   Última actividad: {time_str}")
                    print(f"   Tipo: {latest.get('type', 'N/A')}")

                    # Intentar obtener username desde la respuesta
                    user_data = latest.get('user', {})
                    if isinstance(user_data, dict):
                        username = user_data.get('name') or user_data.get('pseudonym') or user_data.get('username')
                        if username:
                            print(f"   Username: {username}")
        else:
            print(f"⚠️  No se pudo obtener actividad (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Error obteniendo actividad: {e}")

    print()

def main():
    """Verifica todos los traders"""

    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║           🔍 VERIFICACIÓN DE TRADERS - POLYMARKET 🔍                 ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    # Cargar traders.json
    with open('traders.json', 'r') as f:
        data = json.load(f)
        traders = data.get('traders', [])

    print(f"Total traders a verificar: {len(traders)}\n")

    for trader in traders:
        wallet = trader['wallet']
        verify_trader(wallet)

    print(f"{'='*70}")
    print("✅ Verificación completada")
    print(f"{'='*70}\n")
    print("Para iniciar el monitoreo continuo, ejecuta:")
    print("  python3 trader_tracker.py")

if __name__ == "__main__":
    main()
