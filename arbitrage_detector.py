#!/usr/bin/env python3
"""
Arbitrage Detector for Prediction Markets (Polymarket & Kalshi)

Este script detecta oportunidades de arbitraje entre mercados de predicción
comparando probabilidades implícitas en Polymarket y Kalshi.

SOLO USA DATOS REALES - Sin simulaciones ni datos mock.

Autor: Claude
Versión: 2.0
"""

from py_clob_client.client import ClobClient
import requests
import pandas as pd
from rapidfuzz import fuzz
from typing import List, Dict, Tuple, Optional
import time
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
    """Cliente para interactuar con la API de Polymarket usando py-clob-client oficial"""

    def __init__(self):
        """Inicializa el cliente de Polymarket (sin autenticación para datos públicos)"""
        self.client = ClobClient("https://clob.polymarket.com")
        logger.info("✓ Cliente Polymarket inicializado")

    def get_markets(self) -> List[Dict]:
        """
        Obtiene TODOS los mercados activos de Polymarket usando la API real

        Returns:
            Lista de mercados con su información real
        """
        markets_list = []
        next_cursor = None

        try:
            logger.info("Obteniendo mercados reales de Polymarket...")

            while True:
                # Hacer llamada a la API real
                if next_cursor is None:
                    response = self.client.get_markets()
                else:
                    response = self.client.get_markets(next_cursor=next_cursor)

                # Verificar respuesta
                if 'data' not in response or not response['data']:
                    break

                # Agregar mercados
                markets_list.extend(response['data'])
                logger.info(f"  Obtenidos {len(response['data'])} mercados...")

                # Verificar si hay más páginas
                next_cursor = response.get('next_cursor')
                if not next_cursor:
                    break

                time.sleep(0.3)  # Rate limiting respetuoso

            logger.info(f"✓ Polymarket: {len(markets_list)} mercados reales obtenidos")
            return markets_list

        except Exception as e:
            logger.error(f"Error al obtener mercados de Polymarket: {e}")
            raise Exception(f"No se pudieron obtener datos reales de Polymarket: {e}")

    def parse_market(self, market: Dict) -> Optional[Dict]:
        """
        Parsea un mercado de Polymarket al formato estándar

        Args:
            market: Diccionario con datos del mercado real

        Returns:
            Diccionario con formato estándar o None si hay error
        """
        try:
            # Validar campos requeridos
            if not market.get('question') or not market.get('tokens'):
                return None

            # Solo mercados activos y abiertos
            if market.get('closed', True) or not market.get('active', False):
                return None

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

            # Precio del token (ya viene como probabilidad 0-1)
            yes_price = float(yes_token.get('price', 0))

            if yes_price <= 0 or yes_price >= 1:
                return None

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


class KalshiClient:
    """Cliente para interactuar con la API pública de Kalshi"""

    # API pública sin autenticación
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

    def __init__(self):
        """Inicializa el cliente de Kalshi (sin autenticación para datos públicos)"""
        self.session = requests.Session()
        logger.info("✓ Cliente Kalshi inicializado")

    def get_markets(self) -> List[Dict]:
        """
        Obtiene TODOS los mercados activos de Kalshi usando la API pública real

        Returns:
            Lista de mercados con su información real
        """
        markets_list = []
        cursor = None
        limit = 1000  # Máximo permitido

        try:
            logger.info("Obteniendo mercados reales de Kalshi...")

            while True:
                # Preparar parámetros
                params = {
                    'limit': limit,
                    'status': 'open'
                }

                if cursor:
                    params['cursor'] = cursor

                # Llamada a la API real
                url = f"{self.BASE_URL}/markets"
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                # Verificar respuesta
                if 'markets' not in data or not data['markets']:
                    break

                # Agregar mercados
                markets_list.extend(data['markets'])
                logger.info(f"  Obtenidos {len(data['markets'])} mercados...")

                # Verificar si hay más páginas
                cursor = data.get('cursor')
                if not cursor:
                    break

                time.sleep(0.3)  # Rate limiting respetuoso

            logger.info(f"✓ Kalshi: {len(markets_list)} mercados reales obtenidos")
            return markets_list

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener mercados de Kalshi: {e}")
            raise Exception(f"No se pudieron obtener datos reales de Kalshi: {e}")

    def parse_market(self, market: Dict) -> Optional[Dict]:
        """
        Parsea un mercado de Kalshi al formato estándar

        Args:
            market: Diccionario con datos del mercado real

        Returns:
            Diccionario con formato estándar o None si hay error
        """
        try:
            if not market.get('title') or not market.get('ticker'):
                return None

            # Solo mercados abiertos
            if market.get('status') != 'open':
                return None

            # Obtener precio Yes (en centavos, convertir a probabilidad)
            # Kalshi usa yes_bid, yes_ask, last_price
            yes_price_cents = market.get('yes_bid', market.get('last_price', 0))

            if yes_price_cents is None:
                return None

            yes_price = float(yes_price_cents) / 100.0

            if yes_price <= 0 or yes_price >= 1:
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


class ArbitrageDetector:
    """Detector de oportunidades de arbitraje entre plataformas - SOLO DATOS REALES"""

    def __init__(self, similarity_threshold: float = 80.0):
        """
        Inicializa el detector

        Args:
            similarity_threshold: Umbral mínimo de similitud para emparejar mercados (0-100)
        """
        self.similarity_threshold = similarity_threshold
        self.polymarket = PolymarketClient()
        self.kalshi = KalshiClient()

    def fetch_all_markets(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Obtiene todos los mercados REALES de ambas plataformas

        Returns:
            Tupla (mercados_polymarket, mercados_kalshi)
        """
        logger.info("\n" + "="*60)
        logger.info("OBTENIENDO MERCADOS REALES DE AMBAS PLATAFORMAS")
        logger.info("="*60 + "\n")

        # Obtener mercados reales
        poly_markets_raw = self.polymarket.get_markets()
        kalshi_markets_raw = self.kalshi.get_markets()

        # Parsear a formato estándar
        poly_markets = []
        for m in poly_markets_raw:
            parsed = self.polymarket.parse_market(m)
            if parsed:
                poly_markets.append(parsed)

        kalshi_markets = []
        for m in kalshi_markets_raw:
            parsed = self.kalshi.parse_market(m)
            if parsed:
                kalshi_markets.append(parsed)

        logger.info(f"\n✓ Total mercados reales parseados:")
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
                'Mercado': poly['title'][:80],  # Limitar longitud
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
        Ejecuta el detector completo con DATOS REALES ÚNICAMENTE

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
        print(f"{Fore.GREEN}✓ Usando DATOS REALES de APIs en vivo{Style.RESET_ALL}\n")

        try:
            # 1. Obtener mercados REALES
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
            raise


def main():
    """Función principal"""
    # Configuración
    SIMILARITY_THRESHOLD = 80.0  # Umbral de similitud (0-100)
    TOP_N = 20  # Número de mejores oportunidades a mostrar

    # Crear detector (SOLO DATOS REALES)
    detector = ArbitrageDetector(similarity_threshold=SIMILARITY_THRESHOLD)

    # Ejecutar
    detector.run(export_csv=True, export_json=True, top_n=TOP_N)


if __name__ == "__main__":
    main()
