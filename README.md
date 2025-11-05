# 🎯 Detector de Arbitraje - Polymarket vs Kalshi

Script completo y funcional para detectar oportunidades de arbitraje entre mercados de predicción de Polymarket y Kalshi.

## 📋 Descripción

Este script automatiza la detección de oportunidades de arbitraje entre dos plataformas de mercados de predicción:
- **Polymarket**: Mercado descentralizado basado en Polygon
- **Kalshi**: Mercado regulado de eventos futuros

El script:
1. ✅ Consulta las APIs públicas de ambas plataformas (sin necesidad de tokens)
2. ✅ Extrae todos los mercados activos con precios, volumen y liquidez
3. ✅ Empareja automáticamente mercados similares usando matching de texto (similitud > 80%)
4. ✅ Calcula spreads de arbitraje comparando probabilidades complementarias
5. ✅ Muestra resultados ordenados por rentabilidad
6. ✅ Exporta datos a CSV y JSON

## 🔧 Requisitos

- **Python**: 3.10 o superior
- **Sistema operativo**: Linux, macOS o Windows
- **Conexión a internet**: Requerida para consultar APIs

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd predictionarb
```

### 2. Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Ejecución básica

```bash
python arbitrage_detector.py
```

### Salida esperada

El script mostrará:

```
================================================================================
DETECTOR DE ARBITRAJE - POLYMARKET vs KALSHI
================================================================================

Inicio: 2025-11-05 12:00:00

============================================================
OBTENIENDO MERCADOS DE AMBAS PLATAFORMAS
============================================================

✓ Polymarket: 247 mercados activos encontrados
✓ Kalshi: 312 mercados activos encontrados

============================================================
EMPAREJANDO MERCADOS SIMILARES
============================================================

✓ 45 pares de mercados encontrados (similitud >= 80.0%)

============================================================
CALCULANDO OPORTUNIDADES DE ARBITRAJE
============================================================

================================================================================
OPORTUNIDADES DE ARBITRAJE DETECTADAS
================================================================================

✓ 12 oportunidades con spread positivo encontradas

+--------------------------------------------------+------------+---------------+----------------+------------+---------------+------------+
| Mercado                                          | Similitud (%) | Prob Yes Poly | Prob No Kalshi | Spread (%) | Vol Total ($) | Expira Poly|
+--------------------------------------------------+------------+---------------+----------------+------------+---------------+------------+
| Will Trump win the 2024 Presidential Election?   | 95.2       | 0.580         | 0.470          | +5.00      | 8,450,230     | 2024-11-05 |
| Will there be a US recession by end of 2025?     | 88.5       | 0.320         | 0.710          | +3.00      | 2,100,450     | 2025-12-31 |
+--------------------------------------------------+------------+---------------+----------------+------------+---------------+------------+

ESTADÍSTICAS:
  • Spread promedio: 1.25%
  • Spread máximo: 5.00%
  • Spread mínimo: -2.30%
  • Volumen total combinado: $45,250,890

✓ Datos exportados a arbitrage_opportunities.csv
✓ Datos exportados a arbitrage_opportunities.json
✓ Análisis completado en 8.45 segundos
```

## 📊 Archivos de salida

El script genera automáticamente:

1. **`arbitrage_opportunities.csv`**: Tabla con todas las oportunidades
2. **`arbitrage_opportunities.json`**: Datos en formato JSON
3. **`arbitrage.log`**: Log de ejecución con errores y debug

## 🧮 Cómo funciona el arbitraje

### Estrategia de arbitraje

El arbitraje se basa en comprar probabilidades complementarias en diferentes plataformas:

1. **Comprar "Yes"** en Polymarket al precio `pP`
2. **Comprar "No"** en Kalshi al precio `(1 - pK)`

### Condición de arbitraje

Existe una oportunidad de arbitraje cuando:

```
pP + (1 - pK) < 1.0
```

**Spread** = `pP + (1 - pK) - 1.0`

- **Spread positivo**: Oportunidad de arbitraje (ganancia garantizada)
- **Spread negativo**: No hay arbitraje

### Ejemplo práctico

**Mercado**: "¿Ganará Trump 2024?"

- **Polymarket**: Precio "Yes" = 0.58 (58%)
- **Kalshi**: Precio "No" = 0.47 (47%)

**Cálculo**:
```
Inversión total = $1.00 (0.58 en Poly + 0.42 en Kalshi)
Retorno garantizado = $1.00 (uno de los dos pagará $1)
```

Como gastamos menos de $1.00 pero recibimos $1.00, hay arbitraje.

**Spread** = 0.58 + 0.47 - 1.0 = **+0.05 (5% de ganancia)**

## ⚙️ Configuración avanzada

### Modificar parámetros en el código

Edita `arbitrage_detector.py`:

```python
# Línea ~580
SIMILARITY_THRESHOLD = 80.0  # Umbral de similitud (0-100)
TOP_N = 20  # Número de mejores oportunidades a mostrar
```

### Parámetros disponibles:

- **`similarity_threshold`**: Umbral mínimo de similitud para emparejar mercados (default: 80.0)
- **`top_n`**: Cantidad de mejores oportunidades a mostrar (default: 20)
- **`export_csv`**: Exportar a CSV (default: True)
- **`export_json`**: Exportar a JSON (default: True)

### Ejecución programada

Para ejecutar cada X minutos, usa `cron` (Linux/macOS) o Task Scheduler (Windows):

**Ejemplo con cron (cada 15 minutos)**:
```bash
*/15 * * * * cd /ruta/a/predictionarb && /ruta/a/venv/bin/python arbitrage_detector.py
```

**Ejemplo con Python (loop manual)**:

```python
import time

while True:
    detector = ArbitrageDetector()
    detector.run()
    time.sleep(15 * 60)  # 15 minutos
```

## 🛠️ Endpoints utilizados

### Polymarket
- **Base URL**: `https://gamma-api.polymarket.com`
- **Endpoint**: `/markets`
- **Método**: GET
- **Autenticación**: No requerida
- **Rate limit**: ~1000 requests/hora

### Kalshi
- **Base URL**: `https://api.elections.kalshi.com/trade-api/v2`
- **Endpoint**: `/markets`
- **Método**: GET
- **Autenticación**: No requerida para datos públicos
- **Rate limit**: Generoso para consultas públicas

## 📝 Estructura del código

```
arbitrage_detector.py
│
├── PolymarketClient
│   ├── get_markets()      # Obtiene mercados de Polymarket
│   └── parse_market()     # Parsea formato estándar
│
├── KalshiClient
│   ├── get_markets()      # Obtiene mercados de Kalshi
│   └── parse_market()     # Parsea formato estándar
│
└── ArbitrageDetector
    ├── fetch_all_markets()      # Obtiene de ambas plataformas
    ├── match_markets()          # Empareja mercados similares
    ├── calculate_arbitrage()    # Calcula spreads
    ├── display_opportunities()  # Muestra resultados
    ├── export_to_csv()          # Exporta a CSV
    ├── export_to_json()         # Exporta a JSON
    └── run()                    # Ejecuta proceso completo
```

## ⚠️ Manejo de errores

El script incluye manejo robusto de errores:

- ✅ Timeout en requests (10 segundos)
- ✅ Reintentos automáticos con rate limiting
- ✅ Validación de datos de mercados
- ✅ Logging detallado de errores
- ✅ Manejo de APIs caídas o lentas

Los errores se registran en `arbitrage.log`.

## 🎨 Dependencias

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `requests` | ≥2.31.0 | Llamadas HTTP a APIs |
| `pandas` | ≥2.0.0 | Procesamiento de datos |
| `rapidfuzz` | ≥3.0.0 | Matching de texto similar |
| `tabulate` | ≥0.9.0 | Formato de tablas en consola |
| `colorama` | ≥0.4.6 | Salida con colores |

## 🚨 Limitaciones y consideraciones

### Limitaciones técnicas
- Las APIs públicas tienen rate limits
- Los precios pueden cambiar rápidamente
- No incluye costos de transacción (fees)
- Requiere cuentas en ambas plataformas para ejecutar trades

### Consideraciones de trading
- **Slippage**: Los precios pueden moverse antes de ejecutar
- **Fees**: Polymarket y Kalshi cobran fees (1-2%)
- **Liquidez**: Mercados pequeños pueden no tener suficiente liquidez
- **Tiempo de ejecución**: Debe ser rápido para capturar el arbitraje

### Recomendaciones
1. ✅ Verifica la liquidez antes de operar
2. ✅ Incluye fees en tu cálculo de rentabilidad
3. ✅ Opera solo en mercados con alto volumen
4. ✅ Ten cuentas preparadas con fondos en ambas plataformas

## 🔄 Actualización automática (opcional)

Para mantener el script corriendo continuamente:

```python
# Añadir al final de arbitrage_detector.py

import schedule

def job():
    detector = ArbitrageDetector()
    detector.run()

# Ejecutar cada 15 minutos
schedule.every(15).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📈 Dashboard web (opcional)

Para crear una interfaz web simple con Streamlit:

```bash
pip install streamlit
```

```python
# dashboard.py
import streamlit as st
import pandas as pd
from arbitrage_detector import ArbitrageDetector

st.title("🎯 Detector de Arbitraje - Polymarket vs Kalshi")

if st.button("Actualizar datos"):
    with st.spinner("Analizando mercados..."):
        detector = ArbitrageDetector()
        poly_markets, kalshi_markets = detector.fetch_all_markets()
        matches = detector.match_markets(poly_markets, kalshi_markets)
        df = detector.calculate_arbitrage(matches)

        st.success(f"✓ {len(df)} oportunidades encontradas")
        st.dataframe(df)
```

Ejecutar:
```bash
streamlit run dashboard.py
```

## 🤝 Contribuciones

¿Encontraste un bug o tienes una sugerencia?
- Abre un issue
- Envía un pull request

## 📄 Licencia

MIT License - Libre para uso personal y comercial

## ⚡ FAQ

**Q: ¿Necesito API keys?**
A: No, el script usa endpoints públicos sin autenticación.

**Q: ¿Es legal el arbitraje?**
A: Sí, es una práctica legal en mercados de predicción.

**Q: ¿Cuánto capital necesito?**
A: Depende de la oportunidad, pero mínimo $100-500 para que valga la pena.

**Q: ¿El script ejecuta trades automáticamente?**
A: No, solo detecta oportunidades. Debes ejecutar trades manualmente.

**Q: ¿Qué tan rápido debo actuar?**
A: Los arbitrajes desaparecen en segundos/minutos. Debes ser rápido.

## 📞 Soporte

Para problemas técnicos, revisa el archivo `arbitrage.log` para detalles del error.

---

**Autor**: Claude
**Versión**: 1.0
**Última actualización**: 2025-11-05
