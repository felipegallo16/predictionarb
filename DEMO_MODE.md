# 🎭 Modo Demostración

## ⚠️ Aviso Importante

Las APIs públicas de Polymarket y Kalshi están protegidas por **Cloudflare** y pueden devolver errores 403 Forbidden cuando se acceden directamente sin autenticación o desde ciertos entornos.

## 🔄 Soluciones Implementadas

Este script incluye **modo demostración automático** que:

1. ✅ **Intenta conectarse a las APIs reales** primero
2. ✅ **Si falla (403)**, cambia automáticamente a datos de demostración
3. ✅ **Mantiene toda la funcionalidad** intacta (matching, cálculos, exportación)
4. ✅ **Usa datos realistas** basados en mercados reales

## 📊 Datos de Demostración

Los datos incluidos son **realistas** y basados en mercados reales:

- **Elección Trump 2024**: Con precios típicos del mercado
- **Recesión US 2025**: Probabilidades actuales del mercado
- **Bitcoin $100K**: Predicción cripto popular
- **AGI 2026**: Especulación sobre IA
- **Mars 2030**: Misión SpaceX
- **Tasa de interés Fed**: Decisión monetaria

## 🚀 Uso del Script

### Modo Demostración (Por Defecto)
```bash
python arbitrage_detector.py
```

### Modo En Vivo (Intentar APIs Reales)
```bash
python arbitrage_detector.py --live
```

## 🔧 Cómo Usar APIs Reales

Para acceder a las APIs reales sin restricciones:

### Opción 1: Cliente Oficial de Polymarket
```bash
pip install py-clob-client
```

```python
from py_clob_client.client import ClobClient

client = ClobClient("https://clob.polymarket.com")
markets = client.get_markets()
```

### Opción 2: Kalshi SDK Oficial
```bash
pip install kalshi-python
```

```python
import KalshiClientsBaseV2

kalshi_client = KalshiClientsBaseV2.ExchangeClient(
    exchange_api_base="https://trading-api.kalshi.com/trade-api/v2"
)
```

### Opción 3: Bypass Cloudflare

Usar servicios como:
- **Selenium** con navegador real
- **Playwright** para automatización
- **Proxies rotativos** (ScraperAPI, Bright Data)
- **Cloudflare Scraper** libraries

### Opción 4: API Keys (Para Trading)

Si necesitas hacer trading real:

**Polymarket**: Requiere wallet Ethereum + firma de transacciones
```python
client = ClobClient(
    "https://clob.polymarket.com",
    key="YOUR_PRIVATE_KEY",
    chain_id=137
)
```

**Kalshi**: Requiere cuenta + API credentials
```python
client = ExchangeClient(
    exchange_api_base="https://trading-api.kalshi.com/trade-api/v2",
    email="your@email.com",
    password="your_password"
)
client.login()
```

## 📝 Limitaciones del Modo Demo

- ❌ Datos NO actualizados en tiempo real
- ❌ Solo ~6 mercados por plataforma
- ❌ No puede ejecutar trades reales
- ✅ Perfecto para testing y demostración
- ✅ Algoritmos funcionan idénticamente

## 🎯 Resultados del Demo

El modo demo detecta correctamente:
- **1 oportunidad de arbitraje positiva** (Trump 2024: +5% spread)
- **3 pares de mercados** emparejados
- **Exportación completa** a CSV y JSON

## 💡 Recomendación

Para **producción real**:
1. Usa los clientes oficiales (py-clob-client, kalshi-python)
2. Obtén API credentials si vas a hacer trading
3. Implementa rate limiting apropiado
4. Considera costos de transacción (fees ~1-2%)
5. Verifica liquidez antes de operar

---

**Nota**: El script funciona perfectamente en modo demo para:
- Entender el concepto de arbitraje
- Probar la lógica de matching
- Validar cálculos de spread
- Aprender sobre mercados de predicción
