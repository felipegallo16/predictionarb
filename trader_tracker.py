#!/usr/bin/env python3
"""
Tracker de Actividad de Traders - Polymarket

Script para monitorear la actividad de traders específicos en Polymarket
usando la Data API oficial.

Autor: Claude
Versión: 1.0
Fecha: 2025-11-07
"""

import requests
import time
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trader_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PolymarketTraderTracker:
    """Cliente para trackear actividad de traders en Polymarket"""

    DATA_API_BASE = "https://data-api.polymarket.com"

    def __init__(self, traders_file: str = "traders.json"):
        """
        Inicializa el tracker

        Args:
            traders_file: Ruta al archivo JSON con mapping username → wallet
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        })

        self.traders = self.load_traders(traders_file)
        self.last_activity_timestamps = {}  # wallet → last_timestamp

        logger.info(f"✓ Tracker inicializado con {len(self.traders)} traders")

    def load_traders(self, traders_file: str) -> List[Dict]:
        """
        Carga la lista de traders desde archivo JSON

        Args:
            traders_file: Ruta al archivo

        Returns:
            Lista de traders con username y wallet
        """
        path = Path(traders_file)

        if not path.exists():
            # Intentar copiar desde traders.json.example si existe
            example_path = Path(f"{traders_file}.example")
            if example_path.exists():
                logger.info(f"Copiando {example_path} a {traders_file}...")
                import shutil
                shutil.copy(example_path, path)
                logger.info(f"✓ Archivo {traders_file} creado desde ejemplo")
                logger.warning(f"⚠️  EDITA {traders_file} y agrega wallet addresses reales")
            else:
                logger.warning(f"Archivo {traders_file} no existe, creando ejemplo...")
                self.create_example_traders_file(traders_file)
            return []

        try:
            with open(traders_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                traders = data.get('traders', [])

            logger.info(f"✓ Cargados {len(traders)} traders desde {traders_file}")
            return traders

        except Exception as e:
            logger.error(f"Error cargando {traders_file}: {e}")
            return []

    def create_example_traders_file(self, filename: str):
        """Crea un archivo de ejemplo con el formato correcto"""

        example = {
            "traders": [
                {
                    "name": "Example Trader 1",
                    "username": "example_trader_1",
                    "wallet": "0x0000000000000000000000000000000000000000",
                    "tracked_since": datetime.now().isoformat(),
                    "notes": "Reemplaza con wallet address real"
                }
            ]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(example, f, indent=2)

        logger.info(f"✓ Archivo de ejemplo creado: {filename}")
        logger.info(f"  → Edita el archivo y agrega wallet addresses reales")

    def get_trader_activity(
        self,
        wallet: str,
        limit: int = 100,
        since_timestamp: Optional[int] = None
    ) -> List[Dict]:
        """
        Obtiene la actividad de un trader específico

        Args:
            wallet: Wallet address del trader (0x...)
            limit: Número máximo de actividades a obtener
            since_timestamp: Timestamp en ms, obtener solo actividad posterior

        Returns:
            Lista de actividades
        """
        url = f"{self.DATA_API_BASE}/activity"

        params = {
            'user': wallet,
            'limit': limit
        }

        if since_timestamp:
            params['start'] = since_timestamp

        try:
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 403:
                logger.error(f"403 Forbidden para {wallet} - Verifica acceso a API")
                return []

            response.raise_for_status()
            data = response.json()

            # La respuesta puede ser una lista directamente o un dict con 'data'
            if isinstance(data, list):
                activities = data
            else:
                activities = data.get('data', [])

            return activities

        except requests.exceptions.Timeout:
            logger.error(f"Timeout obteniendo actividad de {wallet}")
            return []
        except Exception as e:
            logger.error(f"Error obteniendo actividad de {wallet}: {e}")
            return []

    def get_trader_positions(self, wallet: str, limit: int = 100) -> List[Dict]:
        """
        Obtiene las posiciones actuales de un trader

        Args:
            wallet: Wallet address
            limit: Número máximo de posiciones

        Returns:
            Lista de posiciones
        """
        url = f"{self.DATA_API_BASE}/positions"

        params = {
            'user': wallet,
            'limit': limit
        }

        try:
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 403:
                logger.error(f"403 Forbidden para {wallet}")
                return []

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                return data
            else:
                return data.get('data', [])

        except Exception as e:
            logger.error(f"Error obteniendo posiciones de {wallet}: {e}")
            return []

    def get_trader_value(self, wallet: str) -> Optional[float]:
        """
        Obtiene el valor total en USD de las holdings de un trader

        Args:
            wallet: Wallet address

        Returns:
            Valor en USD o None si hay error
        """
        url = f"{self.DATA_API_BASE}/value"

        params = {'user': wallet}

        try:
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 403:
                return None

            response.raise_for_status()
            data = response.json()

            return data.get('value', 0.0)

        except Exception as e:
            logger.error(f"Error obteniendo valor de {wallet}: {e}")
            return None

    def format_activity(self, activity: Dict, trader_name: str) -> str:
        """
        Formatea una actividad para display

        Args:
            activity: Dict con datos de actividad
            trader_name: Nombre del trader

        Returns:
            String formateado
        """
        activity_type = activity.get('type', 'UNKNOWN')
        market_title = activity.get('market', {}).get('title', 'Unknown Market')

        # Timestamp
        timestamp = activity.get('timestamp', 0)
        if timestamp:
            dt = datetime.fromtimestamp(timestamp / 1000)
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = 'Unknown time'

        # Amounts
        usdc_amount = activity.get('usdcAmount', 0)
        token_amount = activity.get('tokenAmount', 0)

        # Side y outcome
        side = activity.get('side', 'N/A')
        outcome_index = activity.get('outcomeIndex', None)
        outcome = 'YES' if outcome_index == 0 else 'NO' if outcome_index == 1 else 'N/A'

        # Transaction hash
        tx_hash = activity.get('transactionHash', 'N/A')

        output = f"""
╔═══════════════════════════════════════════════════════════════
║ 🔔 NUEVA ACTIVIDAD DETECTADA
╠═══════════════════════════════════════════════════════════════
║ Trader:       {trader_name}
║ Tipo:         {activity_type}
║ Mercado:      {market_title[:60]}
║ Lado:         {side}
║ Outcome:      {outcome}
║ USDC:         ${usdc_amount:,.2f}
║ Tokens:       {token_amount:,.2f}
║ Timestamp:    {time_str}
║ TX Hash:      {tx_hash[:20]}...
╚═══════════════════════════════════════════════════════════════
"""
        return output

    def format_position(self, position: Dict) -> str:
        """Formatea una posición para display"""

        market = position.get('market', 'Unknown')
        outcome = position.get('outcome', 'N/A')
        size = position.get('size', 0)
        current_value = position.get('currentValue', 0)
        pnl = position.get('cashPnl', 0)
        pnl_percent = position.get('percentPnl', 0)

        pnl_symbol = "📈" if pnl >= 0 else "📉"

        return f"""
  • Market: {market[:50]}
    Outcome: {outcome} | Size: {size:,.2f} tokens
    Valor: ${current_value:,.2f} | PnL: {pnl_symbol} ${pnl:,.2f} ({pnl_percent:.1f}%)
"""

    def check_new_activity(self, trader: Dict) -> List[Dict]:
        """
        Verifica si hay actividad nueva para un trader

        Args:
            trader: Dict con info del trader (username, wallet)

        Returns:
            Lista de nuevas actividades
        """
        wallet = trader['wallet']

        # Obtener timestamp de última actividad conocida
        last_timestamp = self.last_activity_timestamps.get(wallet)

        # Obtener actividades (solo posteriores a last_timestamp si existe)
        activities = self.get_trader_activity(
            wallet,
            limit=100,
            since_timestamp=last_timestamp
        )

        if not activities:
            return []

        # Filtrar actividades nuevas
        new_activities = []

        for activity in activities:
            activity_timestamp = activity.get('timestamp', 0)

            if last_timestamp is None or activity_timestamp > last_timestamp:
                new_activities.append(activity)

        # Actualizar timestamp de última actividad
        if activities:
            latest_timestamp = max(a.get('timestamp', 0) for a in activities)
            self.last_activity_timestamps[wallet] = latest_timestamp

        return new_activities

    def display_trader_summary(self, trader: Dict):
        """
        Muestra resumen de un trader (posiciones y valor)

        Args:
            trader: Dict con info del trader
        """
        wallet = trader['wallet']
        name = trader.get('name', trader.get('username', 'Unknown'))

        logger.info(f"\n{'='*70}")
        logger.info(f"👤 TRADER: {name}")
        logger.info(f"   Wallet: {wallet}")
        logger.info(f"{'='*70}")

        # Obtener valor total
        total_value = self.get_trader_value(wallet)
        if total_value is not None:
            logger.info(f"💰 Valor Total: ${total_value:,.2f} USD")

        # Obtener posiciones actuales
        positions = self.get_trader_positions(wallet, limit=10)

        if positions:
            logger.info(f"\n📊 Posiciones Actuales ({len(positions)}):")
            for pos in positions[:5]:  # Mostrar top 5
                logger.info(self.format_position(pos))
        else:
            logger.info("   (Sin posiciones abiertas)")

        logger.info(f"{'='*70}\n")

    def monitor_once(self):
        """
        Ejecuta un ciclo de monitoreo (revisa todos los traders una vez)
        """
        if not self.traders:
            logger.warning("⚠️  No hay traders configurados en traders.json")
            logger.warning("   Edita el archivo y agrega wallet addresses reales")
            return

        logger.info(f"\n🔍 Monitoreando {len(self.traders)} traders...")

        new_activity_found = False

        for trader in self.traders:
            wallet = trader['wallet']
            name = trader.get('name', trader.get('username', 'Unknown'))

            # Saltar wallets de ejemplo (0x000...)
            if wallet.startswith('0x00000000'):
                continue

            logger.info(f"  Verificando: {name} ({wallet[:10]}...)")

            # Verificar nueva actividad
            new_activities = self.check_new_activity(trader)

            if new_activities:
                new_activity_found = True
                logger.info(f"  ✓ {len(new_activities)} nueva(s) actividad(es)")

                for activity in new_activities:
                    print(self.format_activity(activity, name))
            else:
                logger.info(f"  - Sin actividad nueva")

            time.sleep(1)  # Rate limiting

        if not new_activity_found:
            logger.info("\n✓ Monitoreo completado - Sin actividad nueva")

    def monitor_continuous(self, interval: int = 300):
        """
        Monitoreo continuo (ejecuta ciclos cada X segundos)

        Args:
            interval: Segundos entre ciclos (default: 300 = 5 minutos)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 INICIANDO MONITOREO CONTINUO")
        logger.info(f"   Intervalo: {interval} segundos ({interval/60:.1f} minutos)")
        logger.info(f"   Traders: {len(self.traders)}")
        logger.info(f"{'='*70}\n")

        # Mostrar resumen inicial de cada trader
        for trader in self.traders:
            if not trader['wallet'].startswith('0x00000000'):
                self.display_trader_summary(trader)
                time.sleep(2)

        cycle = 0

        try:
            while True:
                cycle += 1
                logger.info(f"\n{'─'*70}")
                logger.info(f"📊 CICLO #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'─'*70}")

                self.monitor_once()

                logger.info(f"\n⏳ Esperando {interval} segundos hasta próximo ciclo...")
                logger.info(f"   (Presiona Ctrl+C para detener)\n")

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\n\n🛑 Monitoreo detenido por usuario")
            logger.info(f"   Total ciclos ejecutados: {cycle}")


def main():
    """Función principal"""

    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║               🔍 POLYMARKET TRADER TRACKER 🔍                        ║
║                                                                       ║
║   Monitorea la actividad de traders específicos en tiempo real      ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    # Inicializar tracker
    tracker = PolymarketTraderTracker(traders_file="traders.json")

    print("\nOpciones:")
    print("  1. Monitoreo continuo (cada 5 minutos)")
    print("  2. Verificación única (una vez)")
    print("  3. Ver resumen de traders")
    print()

    try:
        choice = input("Selecciona opción [1/2/3]: ").strip()

        if choice == "1":
            interval = input("Intervalo en segundos (default 300 = 5 min): ").strip()
            interval = int(interval) if interval else 300
            tracker.monitor_continuous(interval=interval)

        elif choice == "2":
            tracker.monitor_once()

        elif choice == "3":
            for trader in tracker.traders:
                if not trader['wallet'].startswith('0x00000000'):
                    tracker.display_trader_summary(trader)
                    time.sleep(2)

        else:
            print("Opción inválida")

    except KeyboardInterrupt:
        print("\n\n👋 Hasta luego!")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
