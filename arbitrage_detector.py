#!/usr/bin/env python3
"""
Arbitrage Detector for Prediction Markets (Polymarket & Kalshi)

Este script detecta oportunidades de arbitraje entre mercados de predicción
comparando probabilidades implícitas en Polymarket y Kalshi.

Autor: Claude
Versión: 1.0
"""

import httpx
import pandas as pd
from rapidfuzz import fuzz
from typing import List, Dict, Tuple, Optional
import time
import json
from datetime import datetime
from tabulate import tabulate
import logging
from colorama import Fore, Style, init

# Inicializar colorama para salida con colores
init(autoreset=True)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Cliente para interactuar con la API de Polymarket"""

    BASE_URL = "https://gamma-api.polymarket.com"

    def __init__(self, use_demo_data: bool = False):
        self.client = httpx.Client(timeout=30.0, follow_redirects=True)
        self.use_demo_data = use_demo_data

    def get_demo_markets(self) -> List[Dict]:
        """
        Retorna datos de demostración realistas basados en mercados reales
        """
        logger.info("Usando datos de demostración de Polymarket...")
        return [
            {
                "id": "pm_trump_2024",
                "question": "Will Donald Trump win the 2024 US Presidential Election?",
                "slug": "trump-2024-election",
                "tokens": [{"outcome": "Yes", "price": 0.58}],
                "volume": 8450230.0,
                "liquidity": 1250000.0,
                "endDate": "2024-11-06T00:00:00Z"
            },
            {
                "id": "pm_recession_2025",
                "question": "Will the US enter a recession by December 31, 2025?",
                "slug": "us-recession-2025",
                "tokens": [{"outcome": "Yes", "price": 0.32}],
                "volume": 2100450.0,
                "liquidity": 450000.0,
                "endDate": "2025-12-31T23:59:59Z"
            },
            {
                "id": "pm_bitcoin_100k",
                "question": "Will Bitcoin reach $100,000 by end of 2025?",
                "slug": "bitcoin-100k-2025",
                "tokens": [{"outcome": "Yes", "price": 0.45}],
                "volume": 5200000.0,
                "liquidity": 890000.0,
                "endDate": "2025-12-31T23:59:59Z"
            },
            {
                "id": "pm_ai_breakthrough",
                "question": "Will AGI be achieved by end of 2026?",
                "slug": "agi-2026",
                "tokens": [{"outcome": "Yes", "price": 0.15}],
                "volume": 890000.0,
                "liquidity": 120000.0,
                "endDate": "2026-12-31T23:59:59Z"
            },
            {
                "id": "pm_mars_mission",
                "question": "Will SpaceX land humans on Mars by 2030?",
                "slug": "spacex-mars-2030",
                "tokens": [{"outcome": "Yes", "price": 0.28}],
                "volume": 1200000.0,
                "liquidity": 350000.0,
                "endDate": "2030-12-31T23:59:59Z"
            },
            {
                "id": "pm_rate_cut",
                "question": "Will the Fed cut interest rates in Q1 2026?",
                "slug": "fed-rate-cut-q1-2026",
                "tokens": [{"outcome": "Yes", "price": 0.67}],
                "volume": 3400000.0,
                "liquidity": 680000.0,
                "endDate": "2026-03-31T23:59:59Z"
            }
        ]

    def get_markets(self, limit: int = 100) -> List[Dict]:
        """
        Obtiene todos los mercados activos de Polymarket

        Returns:
            Lista de mercados con su información
        """
        if self.use_demo_data:
            return self.get_demo_markets()

        markets = []
        offset = 0

        try:
            while True:
                url = f"{self.BASE_URL}/markets"
                params = {
                    'limit': limit,
                    'offset': offset,
                    'closed': 'false',  # Solo mercados abiertos
                    'active': 'true'
                }

                logger.info(f"Fetching Polymarket markets (offset: {offset})...")
                response = self.client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if not data:
                    break

                markets.extend(data)

                # Si recibimos menos del límite, no hay más páginas
                if len(data) < limit:
                    break

                offset += limit
                time.sleep(0.5)  # Rate limiting

            logger.info(f"✓ Polymarket: {len(markets)} mercados activos encontrados")
            return markets

        except httpx.HTTPError as e:
            logger.warning(f"No se pudo conectar a Polymarket API: {e.response.status_code if hasattr(e, 'response') else 'Error'}")
            logger.info("Cambiando a modo demostración...")
            return self.get_demo_markets()

    def parse_market(self, market: Dict) -> Optional[Dict]:
        """
        Parsea un mercado de Polymarket al formato estándar

        Args:
            market: Diccionario con datos del mercado

        Returns:
            Diccionario con formato estándar o None si hay error
        """
        try:
            # Polymarket puede tener múltiples outcomes, nos enfocamos en binarios
            if not market.get('question') or not market.get('tokens'):
                return None

            # Para mercados binarios, buscamos el outcome "Yes"
            yes_price = None
            volume = 0

            # Los tokens contienen la información de precio
            for token in market.get('tokens', []):
                if token.get('outcome', '').lower() in ['yes', 'y']:
                    yes_price = float(token.get('price', 0))

            # Si no encontramos precio Yes, intentar con el primer token
            if yes_price is None and len(market.get('tokens', [])) > 0:
                yes_price = float(market['tokens'][0].get('price', 0))

            if yes_price is None:
                return None

            # Volume y liquidez
            volume = float(market.get('volume', 0))
            liquidity = float(market.get('liquidity', 0))

            return {
                'platform': 'Polymarket',
                'title': market['question'].strip(),
                'prob_yes': yes_price,  # Ya viene como probabilidad (0-1)
                'prob_no': 1 - yes_price,
                'volume': volume,
                'liquidity': liquidity,
                'end_date': market.get('endDate', market.get('end_date_iso', 'N/A')),
                'market_id': market.get('id', ''),
                'url': f"https://polymarket.com/event/{market.get('slug', '')}"
            }

        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Error parseando mercado Polymarket: {e}")
            return None


class KalshiClient:
    """Cliente para interactuar con la API de Kalshi"""

    BASE_URL = "https://trading-api.kalshi.com/trade-api/v2"

    def __init__(self, use_demo_data: bool = False):
        self.client = httpx.Client(timeout=30.0, follow_redirects=True)
        self.use_demo_data = use_demo_data

    def get_demo_markets(self) -> List[Dict]:
        """
        Retorna datos de demostración realistas basados en mercados reales
        """
        logger.info("Usando datos de demostración de Kalshi...")
        return [
            {
                "ticker": "TRUMP2024",
                "title": "Will Donald Trump win the 2024 Presidential Election?",
                "yes_bid": 53,  # En centavos
                "last_price": 53,
                "volume": 6230000.0,
                "open_interest": 980000.0,
                "expiration_time": "2024-11-06T00:00:00Z"
            },
            {
                "ticker": "USRECESSION-25",
                "title": "Will there be a US recession by the end of 2025?",
                "yes_bid": 29,
                "last_price": 29,
                "volume": 1890000.0,
                "open_interest": 420000.0,
                "expiration_time": "2025-12-31T23:59:59Z"
            },
            {
                "ticker": "BTC100K-25",
                "title": "Will Bitcoin reach $100,000 by end of 2025?",
                "yes_bid": 51,
                "last_price": 51,
                "volume": 4100000.0,
                "open_interest": 750000.0,
                "expiration_time": "2025-12-31T23:59:59Z"
            },
            {
                "ticker": "AGI-2026",
                "title": "Will Artificial General Intelligence be achieved by 2026?",
                "yes_bid": 8,
                "last_price": 8,
                "volume": 520000.0,
                "open_interest": 85000.0,
                "expiration_time": "2026-12-31T23:59:59Z"
            },
            {
                "ticker": "MARS-2030",
                "title": "Will humans land on Mars by 2030?",
                "yes_bid": 35,
                "last_price": 35,
                "volume": 980000.0,
                "open_interest": 280000.0,
                "expiration_time": "2030-12-31T23:59:59Z"
            },
            {
                "ticker": "FEDCUT-Q126",
                "title": "Will the Federal Reserve cut rates in Q1 2026?",
                "yes_bid": 72,
                "last_price": 72,
                "volume": 2800000.0,
                "open_interest": 590000.0,
                "expiration_time": "2026-03-31T23:59:59Z"
            }
        ]

    def get_markets(self, limit: int = 200) -> List[Dict]:
        """
        Obtiene todos los mercados activos de Kalshi

        Returns:
            Lista de mercados con su información
        """
        if self.use_demo_data:
            return self.get_demo_markets()

        markets = []
        cursor = None

        try:
            while True:
                url = f"{self.BASE_URL}/markets"
                params = {
                    'limit': limit,
                    'status': 'open'
                }

                if cursor:
                    params['cursor'] = cursor

                logger.info(f"Fetching Kalshi markets (cursor: {cursor})...")
                response = self.client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if 'markets' in data:
                    markets.extend(data['markets'])

                # Verificar si hay más páginas
                cursor = data.get('cursor')
                if not cursor:
                    break

                time.sleep(0.5)  # Rate limiting

            logger.info(f"✓ Kalshi: {len(markets)} mercados activos encontrados")
            return markets

        except httpx.HTTPError as e:
            logger.warning(f"No se pudo conectar a Kalshi API: {e.response.status_code if hasattr(e, 'response') else 'Error'}")
            logger.info("Cambiando a modo demostración...")
            return self.get_demo_markets()

    def parse_market(self, market: Dict) -> Optional[Dict]:
        """
        Parsea un mercado de Kalshi al formato estándar

        Args:
            market: Diccionario con datos del mercado

        Returns:
            Diccionario con formato estándar o None si hay error
        """
        try:
            if not market.get('title'):
                return None

            # Kalshi usa centavos (0-100), convertir a probabilidad (0-1)
            yes_price_cents = market.get('yes_bid', market.get('last_price', 0))
            yes_price = float(yes_price_cents) / 100.0

            volume = float(market.get('volume', 0))
            liquidity = float(market.get('open_interest', 0))

            return {
                'platform': 'Kalshi',
                'title': market['title'].strip(),
                'prob_yes': yes_price,
                'prob_no': 1 - yes_price,
                'volume': volume,
                'liquidity': liquidity,
                'end_date': market.get('expiration_time', market.get('close_time', 'N/A')),
                'market_id': market.get('ticker', market.get('id', '')),
                'url': f"https://kalshi.com/markets/{market.get('ticker', '')}"
            }

        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Error parseando mercado Kalshi: {e}")
            return None


class ArbitrageDetector:
    """Detector de oportunidades de arbitraje entre plataformas"""

    def __init__(self, similarity_threshold: float = 80.0, use_demo_data: bool = False):
        """
        Inicializa el detector

        Args:
            similarity_threshold: Umbral mínimo de similitud para emparejar mercados (0-100)
            use_demo_data: Si True, usa datos de demostración en lugar de APIs reales
        """
        self.similarity_threshold = similarity_threshold
        self.use_demo_data = use_demo_data
        self.polymarket = PolymarketClient(use_demo_data=use_demo_data)
        self.kalshi = KalshiClient(use_demo_data=use_demo_data)

    def fetch_all_markets(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Obtiene todos los mercados de ambas plataformas

        Returns:
            Tupla (mercados_polymarket, mercados_kalshi)
        """
        logger.info("\n" + "="*60)
        logger.info("OBTENIENDO MERCADOS DE AMBAS PLATAFORMAS")
        logger.info("="*60 + "\n")

        # Obtener mercados raw
        poly_markets_raw = self.polymarket.get_markets()
        kalshi_markets_raw = self.kalshi.get_markets()

        # Parsear a formato estándar
        poly_markets = [
            self.polymarket.parse_market(m) for m in poly_markets_raw
        ]
        poly_markets = [m for m in poly_markets if m is not None]

        kalshi_markets = [
            self.kalshi.parse_market(m) for m in kalshi_markets_raw
        ]
        kalshi_markets = [m for m in kalshi_markets if m is not None]

        logger.info(f"\n✓ Total mercados parseados:")
        logger.info(f"  - Polymarket: {len(poly_markets)}")
        logger.info(f"  - Kalshi: {len(kalshi_markets)}\n")

        return poly_markets, kalshi_markets

    def calculate_similarity(self, title1: str, title2: str) -> float:
        """
        Calcula la similitud entre dos títulos de mercados

        Args:
            title1: Primer título
            title2: Segundo título

        Returns:
            Score de similitud (0-100)
        """
        # Usar token_sort_ratio que es más robusto a orden de palabras
        return fuzz.token_sort_ratio(title1.lower(), title2.lower())

    def match_markets(
        self,
        poly_markets: List[Dict],
        kalshi_markets: List[Dict]
    ) -> List[Dict]:
        """
        Empareja mercados similares entre plataformas

        Args:
            poly_markets: Lista de mercados de Polymarket
            kalshi_markets: Lista de mercados de Kalshi

        Returns:
            Lista de pares de mercados con alta similitud
        """
        logger.info("="*60)
        logger.info("EMPAREJANDO MERCADOS SIMILARES")
        logger.info("="*60 + "\n")

        matches = []

        for poly_market in poly_markets:
            best_match = None
            best_score = 0

            for kalshi_market in kalshi_markets:
                score = self.calculate_similarity(
                    poly_market['title'],
                    kalshi_market['title']
                )

                if score > best_score:
                    best_score = score
                    best_match = kalshi_market

            # Solo emparejar si supera el umbral
            if best_score >= self.similarity_threshold and best_match:
                matches.append({
                    'poly_market': poly_market,
                    'kalshi_market': best_match,
                    'similarity_score': best_score
                })

        logger.info(f"✓ {len(matches)} pares de mercados encontrados (similitud >= {self.similarity_threshold}%)\n")
        return matches

    def calculate_arbitrage(self, matches: List[Dict]) -> pd.DataFrame:
        """
        Calcula oportunidades de arbitraje para cada par de mercados

        Estrategia:
        - Comprar "Yes" en Polymarket a precio pP
        - Comprar "No" en Kalshi a precio (1 - pK)
        - Arbitraje existe si: pP + (1 - pK) < 1 (ganancia garantizada)

        Args:
            matches: Lista de pares de mercados emparejados

        Returns:
            DataFrame con oportunidades de arbitraje ordenadas
        """
        logger.info("="*60)
        logger.info("CALCULANDO OPORTUNIDADES DE ARBITRAJE")
        logger.info("="*60 + "\n")

        opportunities = []

        for match in matches:
            poly = match['poly_market']
            kalshi = match['kalshi_market']

            # Probabilidad implícita "Yes" en Polymarket
            prob_yes_poly = poly['prob_yes']

            # Probabilidad implícita "No" en Kalshi
            prob_no_kalshi = kalshi['prob_no']

            # Suma de probabilidades (si > 1, hay arbitraje)
            total_prob = prob_yes_poly + prob_no_kalshi

            # Spread de arbitraje (beneficio potencial)
            spread = total_prob - 1.0
            spread_pct = spread * 100

            # Volumen y liquidez combinados
            total_volume = poly['volume'] + kalshi['volume']
            total_liquidity = poly['liquidity'] + kalshi['liquidity']

            opportunities.append({
                'Mercado': poly['title'][:60],  # Limitar longitud
                'Similitud (%)': f"{match['similarity_score']:.1f}",
                'Prob Yes Poly': f"{prob_yes_poly:.3f}",
                'Prob No Kalshi': f"{prob_no_kalshi:.3f}",
                'Suma Probs': f"{total_prob:.3f}",
                'Spread (%)': f"{spread_pct:.2f}",
                'Vol Total ($)': f"{total_volume:,.0f}",
                'Liquidez ($)': f"{total_liquidity:,.0f}",
                'Expira Poly': str(poly['end_date'])[:10] if poly['end_date'] != 'N/A' else 'N/A',
                'Expira Kalshi': str(kalshi['end_date'])[:10] if kalshi['end_date'] != 'N/A' else 'N/A',
                'URL Poly': poly['url'],
                'URL Kalshi': kalshi['url'],
                # Para ordenamiento
                '_spread_numeric': spread_pct,
                '_volume_numeric': total_volume
            })

        # Crear DataFrame
        df = pd.DataFrame(opportunities)

        if df.empty:
            logger.warning("No se encontraron oportunidades de arbitraje")
            return df

        # Ordenar por spread (mayor primero)
        df = df.sort_values('_spread_numeric', ascending=False)

        return df

    def display_opportunities(self, df: pd.DataFrame, top_n: int = 20):
        """
        Muestra las oportunidades de arbitraje en consola

        Args:
            df: DataFrame con oportunidades
            top_n: Número de mejores oportunidades a mostrar
        """
        if df.empty:
            print(f"\n{Fore.YELLOW}⚠ No se encontraron oportunidades de arbitraje{Style.RESET_ALL}\n")
            return

        # Filtrar solo spreads positivos (verdaderas oportunidades)
        positive_arb = df[df['_spread_numeric'] > 0]

        print(f"\n{Fore.GREEN}{'='*80}")
        print(f"OPORTUNIDADES DE ARBITRAJE DETECTADAS")
        print(f"{'='*80}{Style.RESET_ALL}\n")

        if positive_arb.empty:
            print(f"{Fore.YELLOW}⚠ No hay oportunidades de arbitraje positivas en este momento{Style.RESET_ALL}\n")
            print(f"Total de pares analizados: {len(df)}\n")
        else:
            print(f"{Fore.GREEN}✓ {len(positive_arb)} oportunidades con spread positivo encontradas{Style.RESET_ALL}\n")

            # Mostrar top N
            display_df = positive_arb.head(top_n).copy()

            # Seleccionar columnas para display
            display_cols = [
                'Mercado', 'Similitud (%)', 'Prob Yes Poly', 'Prob No Kalshi',
                'Spread (%)', 'Vol Total ($)', 'Expira Poly'
            ]

            print(tabulate(
                display_df[display_cols],
                headers='keys',
                tablefmt='grid',
                showindex=False
            ))

            print(f"\n{Fore.CYAN}Mostrando top {min(top_n, len(positive_arb))} de {len(positive_arb)} oportunidades{Style.RESET_ALL}\n")

        # Estadísticas
        print(f"{Fore.BLUE}ESTADÍSTICAS:{Style.RESET_ALL}")
        print(f"  • Spread promedio: {df['_spread_numeric'].mean():.2f}%")
        print(f"  • Spread máximo: {df['_spread_numeric'].max():.2f}%")
        print(f"  • Spread mínimo: {df['_spread_numeric'].min():.2f}%")
        print(f"  • Volumen total combinado: ${df['_volume_numeric'].sum():,.0f}\n")

    def export_to_csv(self, df: pd.DataFrame, filename: str = "arbitrage_opportunities.csv"):
        """
        Exporta oportunidades a CSV

        Args:
            df: DataFrame con oportunidades
            filename: Nombre del archivo de salida
        """
        if df.empty:
            logger.warning("No hay datos para exportar")
            return

        # Remover columnas auxiliares
        export_df = df.drop(columns=['_spread_numeric', '_volume_numeric'], errors='ignore')

        export_df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"✓ Datos exportados a {filename}")

    def export_to_json(self, df: pd.DataFrame, filename: str = "arbitrage_opportunities.json"):
        """
        Exporta oportunidades a JSON

        Args:
            df: DataFrame con oportunidades
            filename: Nombre del archivo de salida
        """
        if df.empty:
            logger.warning("No hay datos para exportar")
            return

        # Remover columnas auxiliares
        export_df = df.drop(columns=['_spread_numeric', '_volume_numeric'], errors='ignore')

        export_df.to_json(filename, orient='records', indent=2, force_ascii=False)
        logger.info(f"✓ Datos exportados a {filename}")

    def run(self, export_csv: bool = True, export_json: bool = True, top_n: int = 20):
        """
        Ejecuta el detector completo

        Args:
            export_csv: Si exportar resultados a CSV
            export_json: Si exportar resultados a JSON
            top_n: Número de mejores oportunidades a mostrar
        """
        start_time = time.time()

        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"DETECTOR DE ARBITRAJE - POLYMARKET vs KALSHI")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if self.use_demo_data:
            print(f"{Fore.YELLOW}⚠ MODO DEMOSTRACIÓN: Usando datos simulados{Style.RESET_ALL}")
            print(f"  (Las APIs tienen protección Cloudflare activa)\n")
        else:
            print(f"{Fore.GREEN}✓ Intentando conectar a APIs en vivo...{Style.RESET_ALL}\n")

        try:
            # 1. Obtener mercados
            poly_markets, kalshi_markets = self.fetch_all_markets()

            if not poly_markets or not kalshi_markets:
                logger.error("No se pudieron obtener mercados de una o ambas plataformas")
                return

            # 2. Emparejar mercados
            matches = self.match_markets(poly_markets, kalshi_markets)

            if not matches:
                logger.warning("No se encontraron mercados emparejados")
                return

            # 3. Calcular arbitraje
            df = self.calculate_arbitrage(matches)

            # 4. Mostrar resultados
            self.display_opportunities(df, top_n)

            # 5. Exportar
            if export_csv:
                self.export_to_csv(df)

            if export_json:
                self.export_to_json(df)

            elapsed = time.time() - start_time
            print(f"{Fore.GREEN}✓ Análisis completado en {elapsed:.2f} segundos{Style.RESET_ALL}\n")

        except Exception as e:
            logger.error(f"Error durante la ejecución: {e}", exc_info=True)


def main():
    """Función principal"""
    import sys

    # Configuración
    SIMILARITY_THRESHOLD = 80.0  # Umbral de similitud (0-100)
    TOP_N = 20  # Número de mejores oportunidades a mostrar

    # Detectar si usar modo demo
    # Las APIs están protegidas por Cloudflare, por lo que usaremos modo demo por defecto
    USE_DEMO = True

    # Para intentar usar APIs reales (requiere bypass de Cloudflare o credenciales):
    # USE_DEMO = False
    # O ejecutar: python arbitrage_detector.py --live

    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        USE_DEMO = False

    # Crear detector
    detector = ArbitrageDetector(
        similarity_threshold=SIMILARITY_THRESHOLD,
        use_demo_data=USE_DEMO
    )

    # Ejecutar
    detector.run(export_csv=True, export_json=True, top_n=TOP_N)


if __name__ == "__main__":
    main()
