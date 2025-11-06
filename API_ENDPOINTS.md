# 📚 Endpoints Oficiales - Polymarket & Kalshi

Referencia completa de los endpoints oficiales utilizados en este proyecto.

---

## 🎯 Polymarket - CLOB API

### Documentación Oficial
- **Docs**: https://docs.polymarket.com/
- **API Reference**: https://docs.polymarket.com/developers/CLOB/endpoints
- **GitHub**: https://github.com/Polymarket/py-clob-client

### Base URL
```
https://clob.polymarket.com
```

### Endpoints Utilizados

#### GET /markets
Obtiene todos los mercados activos con paginación.

**Sin autenticación** (para datos públicos de solo lectura)

```bash
curl https://clob.polymarket.com/markets
```

**Respuesta:**
```json
{
  "data": [
    {
      "condition_id": "...",
      "question": "Will Trump win the 2024 Presidential Election?",
      "tokens": [
        {
          "outcome": "Yes",
          "price": 0.58
        }
      ],
      "volume": 8450230.0,
      "liquidity": 1250000.0,
      "closed": false,
      "active": true,
      "end_date_iso": "2024-11-06T00:00:00Z",
      "slug": "trump-2024-election"
    }
  ],
  "next_cursor": "eyJza2lwIjoxMDB9"
}
```

**Paginación:**
- Usa `next_cursor` del response anterior
- `GET /markets?next_cursor=eyJza2lwIjoxMDB9`

**Límites:**
- Rate limit: ~1000 requests/hora para consultas públicas
- No requiere API key para lectura
- Requiere autenticación para trading

### Ejemplo Python
```python
import requests

response = requests.get(
    "https://clob.polymarket.com/markets",
    headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    },
    timeout=8
)

data = response.json()
markets = data['data']
next_cursor = data.get('next_cursor', '')
```

---

## 📊 Kalshi - Public API

### Documentación Oficial
- **Docs**: https://docs.kalshi.com/
- **Quick Start**: https://docs.kalshi.com/getting_started/quick_start_market_data
- **API Spec**: https://kalshi-public-docs.s3.amazonaws.com/KalshiAPI.html

### Base URLs

**Producción (Recomendado):**
```
https://api.elections.kalshi.com/trade-api/v2
```

**Alternativa:**
```
https://trading-api.kalshi.com/trade-api/v2
```

**Demo:**
```
https://demo-api.kalshi.co/trade-api/v2
```

### Endpoints Utilizados

#### GET /markets
Obtiene todos los mercados activos con paginación.

**Sin autenticación** (para datos públicos)

```bash
curl "https://api.elections.kalshi.com/trade-api/v2/markets?limit=100&status=open"
```

**Parámetros:**
- `limit`: Número de mercados por página (1-1000, default: 100)
- `status`: Filtro por estado (`open`, `closed`, `settled`)
- `cursor`: Token de paginación (opcional)
- `series_ticker`: Filtrar por serie específica (opcional)

**Respuesta:**
```json
{
  "markets": [
    {
      "ticker": "TRUMP2024",
      "title": "Will Donald Trump win the 2024 Presidential Election?",
      "yes_bid": 53,
      "yes_ask": 54,
      "last_price": 53,
      "volume": 6230000.0,
      "open_interest": 980000.0,
      "status": "open",
      "expiration_time": "2024-11-06T00:00:00Z",
      "event_ticker": "PRES2024"
    }
  ],
  "cursor": "eyJwYWdlIjoyfQ=="
}
```

**Paginación:**
- Usa `cursor` del response anterior
- `GET /markets?cursor=eyJwYWdlIjoyfQ==&limit=100&status=open`

**Límites:**
- Sin rate limit estricto para datos públicos
- No requiere API key para consultas de mercado
- Requiere autenticación para trading

### Ejemplo Python
```python
import requests

response = requests.get(
    "https://api.elections.kalshi.com/trade-api/v2/markets",
    params={
        'limit': 100,
        'status': 'open'
    },
    headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    },
    timeout=8
)

data = response.json()
markets = data['markets']
cursor = data.get('cursor', None)
```

### Nota Importante sobre api.elections.kalshi.com

⚠️ **A pesar del subdominio "elections"**, este endpoint da acceso a **TODOS los mercados de Kalshi**, no solo los relacionados con elecciones:
- Mercados de economía (inflación, tasas de interés, etc.)
- Mercados de clima (temperatura, precipitación, etc.)
- Mercados de tecnología (Bitcoin, stocks, etc.)
- Mercados de deportes y entretenimiento
- Y por supuesto, mercados de elecciones

---

## 🔐 Autenticación

### Polymarket
**Para lectura (público):** No requiere autenticación
**Para trading:** Requiere:
- Private key (wallet Ethereum)
- Firma de transacciones con EIP-712
- Ver: https://docs.polymarket.com/developers/CLOB/authentication

### Kalshi
**Para lectura (público):** No requiere autenticación
**Para trading:** Requiere:
- Email + Password (login)
- API Key + Secret (generado después del login)
- Ver: https://docs.kalshi.com/getting_started/quick_start_market_data

---

## 🚦 Rate Limits

### Polymarket
- **Lectura pública**: ~1000 requests/hora
- **Con autenticación**: Más generoso (sin límite público documentado)

### Kalshi
- **Lectura pública**: Sin límite estricto documentado
- **Con autenticación**: Rate limits más altos

---

## ⚠️ Errores Comunes

### 403 Forbidden
**Causa**: Cloudflare bloquea tu IP (geo-restricción o bot detection)

**Solución**:
- Usar VPN para cambiar ubicación
- Ejecutar desde máquina local (no cloud/Docker)
- Agregar headers de navegador real (User-Agent, Accept)

### 429 Too Many Requests
**Causa**: Excediste el rate limit

**Solución**:
- Agregar delays entre requests (0.3-0.5 segundos)
- Implementar exponential backoff
- Usar paginación eficiente

### Timeout
**Causa**: Red lenta o API sobrecargada

**Solución**:
- Aumentar timeout (8-10 segundos)
- Reintentar con backoff
- Verificar conectividad

---

## 📊 Formato de Precios

### Polymarket
- **Formato**: Probabilidad decimal (0.0 - 1.0)
- **Ejemplo**: `0.58` = 58% de probabilidad
- **Campo**: `tokens[0].price`

### Kalshi
- **Formato**: Centavos (0 - 100)
- **Ejemplo**: `58` = 58¢ = 58% de probabilidad
- **Campos**: `yes_bid`, `yes_ask`, `last_price`
- **Conversión**: `price_decimal = price_cents / 100.0`

---

## 🔄 Paginación

### Polymarket
- **Método**: Cursor-based
- **Campo**: `next_cursor` en respuesta
- **Uso**: `?next_cursor=eyJza2lwIjoxMDB9`

### Kalshi
- **Método**: Cursor-based
- **Campo**: `cursor` en respuesta
- **Uso**: `?cursor=eyJwYWdlIjoyfQ==`
- **Límite por página**: Hasta 1000 mercados

---

## ✅ Testing de Endpoints

Ver `test_apis.py` para probar ambos endpoints:

```bash
python3 test_apis.py
```

**Salida esperada** (si funcionan):
```
✅ Respuesta: 200 (0.85s)
✅ Mercados obtenidos: 100
✅ Primer mercado: Will Trump win the 2024 Presidential Election?
✅ Next cursor: Sí
```

---

## 📚 Referencias

### Polymarket
- Docs: https://docs.polymarket.com/
- GitHub: https://github.com/Polymarket
- Discord: https://discord.gg/polymarket

### Kalshi
- Docs: https://docs.kalshi.com/
- Help Center: https://help.kalshi.com/kalshi-api
- Email: support@kalshi.com

---

**Última actualización**: 2025-11-05
**Versión del detector**: 2.0
