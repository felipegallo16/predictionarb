#!/usr/bin/env python3
"""
Arbitrage Detector RÁPIDO - Solo primeras 200 mercados para testing
Versión optimizada para pruebas rápidas y demostraciones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from arbitrage_detector import PolymarketClient, KalshiClient, ArbitrageDetector
import logging

# Configurar logging para versión rápida
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class QuickPolymarketClient(PolymarketClient):
    """Versión rápida que obtiene solo 200 mercados"""
    
    def get_markets(self):
        """Obtiene solo 200 mercados usando API CLOB"""
        markets_list = []
        limit = 100
        
        try:
            logger.info("🚀 MODO RÁPIDO: Obteniendo solo 200 mercados de Polymarket (CLOB API)...")
            
            for page in [1, 2]:  # Solo 2 páginas
                offset = (page - 1) * limit
                params = {
                    'limit': limit,
                    'offset': offset
                }
                
                logger.info(f"  📄 Página {page}/2...")
                import requests
                url = "https://clob.polymarket.com/markets"
                response = requests.get(url, params=params, timeout=self.timeout)
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                # CLOB API devuelve {data: [...]}
                markets = data.get('data', [])
                if not markets:
                    break
                    
                markets_list.extend(markets)
                
                if len(markets) < limit:
                    break
                    
            logger.info(f"✅ Polymarket: {len(markets_list)} mercados obtenidos")
            return markets_list
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
            
    def parse_market(self, market):
        """Parsea un mercado de Polymarket al formato estándar"""
        try:
            # Validar campos requeridos
            if not market.get('question') or not market.get('tokens'):
                return None

            # Solo mercados activos
            if not market.get('active', False):
                return None
                
            # Temporal: permitir mercados cerrados para debug
            # if market.get('closed', False):
            #     return None

            # Para mercados binarios, buscamos el outcome "Yes"
            yes_token = None
            for token in market.get('tokens', []):
                if token.get('outcome', '').lower() in ['yes', 'y']:
                    yes_token = token
                    break

            # Si no hay token Yes, usar el primero
            if not yes_token and len(market.get('tokens', [])) > 0:
                yes_token = market['tokens'][0]

            if not yes_token:
                return None

            # Precio del token (puede ser 0-1 para mercados cerrados)
            yes_price = float(yes_token.get('price', 0))

            # Permitir 0 y 1 para mercados resueltos temporalmente
            if yes_price < 0 or yes_price > 1:
                return None
                
            # Si es exactamente 0 o 1, usar valor intermedio para testing
            if yes_price == 0:
                yes_price = 0.1
            elif yes_price == 1:
                yes_price = 0.9

            # Extraer volumen y liquidez
            volume = float(market.get('volume', 0))
            liquidity = float(market.get('liquidity', 0))

            return {
                'platform': 'Polymarket',
                'title': market['question'].strip(),
                'prob_yes': yes_price,
                'prob_no': 1 - yes_price,
                'volume': volume,
                'liquidity': liquidity,
                'end_date': market.get('end_date_iso', market.get('endDate', 'N/A')),
                'market_id': market.get('condition_id', market.get('id', '')),
                'url': f"https://polymarket.com/event/{market.get('slug', '')}"
            }

        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Error parseando mercado Polymarket: {e}")
            return None

class QuickKalshiClient(KalshiClient):
    """Versión rápida que obtiene solo 200 mercados"""
    
    def get_markets(self):
        """Obtiene solo 200 mercados para testing rápido"""
        try:
            logger.info("🚀 MODO RÁPIDO: Obteniendo solo 200 mercados de Kalshi...")
            
            url = f"{self.BASE_URL}/markets"
            params = {
                'limit': 200,
                'status': 'open'
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            markets = data.get('markets', [])
            
            logger.info(f"✅ Kalshi: {len(markets)} mercados obtenidos")
            return markets
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
            
    def parse_market(self, market):
        """Parsea un mercado de Kalshi al formato estándar"""
        try:
            if not market.get('title') or not market.get('ticker'):
                return None

            # Solo mercados abiertos o activos
            if market.get('status') not in ['open', 'active']:
                return None

            # Obtener precio Yes (en centavos, convertir a probabilidad)
            # Kalshi usa yes_bid, yes_ask, last_price
            yes_price_cents = market.get('yes_bid', market.get('last_price', 0))

            if yes_price_cents is None:
                return None

            yes_price = float(yes_price_cents) / 100.0

            # Permitir precios de 0 temporalmente para debug
            if yes_price < 0 or yes_price > 1:
                return None

            # Volumen y open interest
            volume = float(market.get('volume', 0))
            open_interest = float(market.get('open_interest', 0))

            return {
                'platform': 'Kalshi',
                'title': market['title'].strip(),
                'prob_yes': yes_price,
                'prob_no': 1 - yes_price,
                'volume': volume,
                'liquidity': open_interest,
                'end_date': market.get('expiration_time', market.get('close_time', 'N/A')),
                'market_id': market['ticker'],
                'url': f"https://kalshi.com/markets/{market['ticker']}"
            }

        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Error parseando mercado Kalshi: {e}")
            return None

class QuickArbitrageDetector(ArbitrageDetector):
    """Detector rápido que usa clientes limitados"""
    
    def __init__(self, similarity_threshold: float = 80.0):
        """Inicializa con clientes rápidos"""
        self.similarity_threshold = similarity_threshold
        self.polymarket = QuickPolymarketClient()
        self.kalshi = QuickKalshiClient()

def main():
    """Ejecuta detector rápido con límite de mercados"""
    print("🚀 DETECTOR DE ARBITRAJE - MODO RÁPIDO")
    print("=" * 50)
    print("📊 Límite: 200 mercados por plataforma")
    print("⚡ Tiempo estimado: 30-60 segundos")
    print("=" * 50)
    
    # Crear detector rápido
    detector = QuickArbitrageDetector()
    
    # Ejecutar detección
    detector.run()

if __name__ == "__main__":
    main()