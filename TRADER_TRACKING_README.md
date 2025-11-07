# 🔍 Polymarket Trader Tracker

Sistema completo para monitorear la actividad de traders específicos en Polymarket en tiempo real.

## 🎯 ¿Qué hace?

Monitorea **continuamente** la actividad de traders específicos y te alerta cuando:
- ✅ Realizan un nuevo trade (BUY/SELL)
- ✅ Abren o cierran posiciones
- ✅ Ejecutan splits, merges, o redemptions
- ✅ Reciben rewards o conversions

**Cobertura**: 100% de todas las transacciones onchain

---

## 🚀 Inicio Rápido

### 1. Obtener Wallet Addresses

Los APIs de Polymarket requieren **wallet addresses** (no usernames).

**Cómo obtener un wallet address:**

1. Ve al perfil del trader en Polymarket:
   ```
   https://polymarket.com/leaderboard
   ```

2. Busca el trader y haz clic en su perfil

3. La URL será algo como:
   ```
   https://polymarket.com/profile/0x1234567890abcdef1234567890abcdef12345678
   ```

4. Copia el wallet address (la parte `0x...`)

### 2. Configurar traders.json

Edita `traders.json` y agrega los traders que quieres monitorear:

```json
{
  "traders": [
    {
      "name": "John Doe",
      "username": "john_doe",
      "wallet": "0x1234567890abcdef1234567890abcdef12345678",
      "tracked_since": "2025-11-07T00:00:00Z",
      "notes": "Trader destacado en mercados políticos"
    },
    {
      "name": "Jane Smith",
      "username": "jane_smith",
      "wallet": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
      "tracked_since": "2025-11-07T00:00:00Z",
      "notes": "Smart money - copy trading"
    }
  ]
}
```

### 3. Ejecutar el Tracker

```bash
python3 trader_tracker.py
```

**Opciones disponibles:**
1. **Monitoreo continuo** - Verifica cada 5 minutos (configurable)
2. **Verificación única** - Ejecuta una sola vez
3. **Ver resumen** - Muestra posiciones actuales de cada trader

---

## 📊 Ejemplo de Output

### Resumen de Trader
```
══════════════════════════════════════════════════════════════════
👤 TRADER: John Doe
   Wallet: 0x1234567890abcdef1234567890abcdef12345678
══════════════════════════════════════════════════════════════════
💰 Valor Total: $45,890.50 USD

📊 Posiciones Actuales (8):

  • Market: Will Trump win the 2024 Presidential Election?
    Outcome: YES | Size: 15,000.00 tokens
    Valor: $8,700.00 | PnL: 📈 $1,200.00 (16.0%)

  • Market: Will there be a US recession by end of 2025?
    Outcome: NO | Size: 8,500.00 tokens
    Valor: $5,950.00 | PnL: 📉 -$450.00 (-7.0%)
══════════════════════════════════════════════════════════════════
```

### Alerta de Nueva Actividad
```
╔═══════════════════════════════════════════════════════════════
║ 🔔 NUEVA ACTIVIDAD DETECTADA
╠═══════════════════════════════════════════════════════════════
║ Trader:       John Doe
║ Tipo:         TRADE
║ Mercado:      Will Trump win the 2024 Presidential Election?
║ Lado:         BUY
║ Outcome:      YES
║ USDC:         $2,500.00
║ Tokens:       4,310.34
║ Timestamp:    2025-11-07 14:32:15
║ TX Hash:      0xabcd1234...
╚═══════════════════════════════════════════════════════════════
```

---

## ⚙️ Configuración Avanzada

### Cambiar Intervalo de Monitoreo

Por defecto: 5 minutos (300 segundos)

**Opción 1**: En el prompt al ejecutar
```bash
python3 trader_tracker.py
# Selecciona opción 1
# Ingresa intervalo deseado (ej: 180 para 3 minutos)
```

**Opción 2**: Modificar en `traders.json`
```json
{
  "config": {
    "polling_interval_seconds": 180
  }
}
```

### Rate Limits

**Polymarket Data API**:
- Tier gratuito: 1,000 requests/hora
- Tier premium: Rate limits aumentados

**Consumo del tracker**:
- 1 request por trader por ciclo
- Si monitoreas 10 traders cada 5 minutos:
  - 10 requests × 12 ciclos/hora = **120 requests/hora**
  - ✅ Bien dentro del límite

**Recomendación**:
- <50 traders: Usa tier gratuito
- >50 traders: Considera tier premium

---

## 📈 Casos de Uso

### 1. Copy Trading
```
Objetivo: Replicar trades de traders exitosos
Intervalo: 3-5 minutos
Acción: Al detectar nueva posición, ejecutar trade similar
```

### 2. Risk Management
```
Objetivo: Monitorear exposición de tu equipo
Intervalo: 10-15 minutos
Acción: Alertar si alguien excede límites de riesgo
```

### 3. Market Intelligence
```
Objetivo: Detectar movimientos de "smart money"
Intervalo: 5 minutos
Acción: Analizar patrones antes de grandes movimientos
```

### 4. Research
```
Objetivo: Estudiar estrategias de trading
Intervalo: 1 hora
Acción: Guardar datos para análisis posterior
```

---

## 🛠️ Endpoints Utilizados

### 1. GET /activity
**URL**: `https://data-api.polymarket.com/activity`

**Parámetros**:
- `user`: Wallet address (requerido)
- `limit`: Número de actividades (default 100)
- `start`: Timestamp desde (opcional)

**Response**: Lista de todas las actividades onchain

### 2. GET /positions
**URL**: `https://data-api.polymarket.com/positions`

**Parámetros**:
- `user`: Wallet address (requerido)
- `limit`: Número de posiciones (default 100)

**Response**: Posiciones actuales con PnL

### 3. GET /value
**URL**: `https://data-api.polymarket.com/value`

**Parámetros**:
- `user`: Wallet address (requerido)

**Response**: Valor total en USD

---

## 🔧 Solución de Problemas

### Error: "No hay traders configurados"

**Causa**: `traders.json` tiene wallets de ejemplo (0x000...)

**Solución**: Edita `traders.json` y agrega wallet addresses reales

---

### Error: "403 Forbidden"

**Causa**: API bloqueada por geo-restricción

**Soluciones**:
1. Ejecuta desde tu máquina local (no cloud server)
2. Usa VPN para cambiar ubicación
3. Cambia de red WiFi

---

### No detecta actividad nueva

**Esto es normal si**:
- Los traders no han operado recientemente
- Es la primera ejecución (establece baseline)

**Verificación**:
1. Ejecuta opción 3 (Ver resumen)
2. Confirma que obtiene posiciones actuales
3. Si obtiene posiciones → El tracker funciona correctamente

---

### Consumo de rate limits

**Síntomas**: Errores después de muchos requests

**Soluciones**:
1. Aumenta el intervalo (ej: 10 minutos en vez de 5)
2. Reduce el número de traders monitoreados
3. Considera tier premium de Polymarket

---

## 📝 Archivos Generados

### trader_tracker.log
Registro completo de todas las ejecuciones:
```
2025-11-07 14:32:15 - INFO - ✓ Tracker inicializado con 5 traders
2025-11-07 14:32:20 - INFO - 🔍 Monitoreando 5 traders...
2025-11-07 14:32:25 - INFO - ✓ 1 nueva(s) actividad(es)
```

---

## 🚀 Extensiones Futuras

### WebSocket Real-Time (Latencia <1s)

Actualmente el tracker usa polling (REST API) cada X minutos.

**Próxima versión**: WebSocket para notificaciones instantáneas

**Ventajas**:
- Latencia <1 segundo (vs 5 minutos)
- No consume rate limits
- Conexión persistente

**Implementación**: Ver `TRADER_TRACKING_RESEARCH.md` sección WebSocket

### Base de Datos

Guardar histórico de actividad para análisis:
- PostgreSQL o SQLite
- Queries históricos
- Dashboards con métricas

### Notificaciones

Alertas vía:
- 📧 Email
- 💬 Telegram bot
- 🔔 Discord webhooks
- 📱 Push notifications

### Dashboard Web

Interfaz Streamlit para:
- Ver traders en tiempo real
- Gráficos de actividad
- Filtros y búsqueda

---

## 📚 Documentación Adicional

- **Investigación completa**: `TRADER_TRACKING_RESEARCH.md`
- **API Reference**: [Polymarket Data API Docs](https://docs.polymarket.com/developers/misc-endpoints/data-api-activity)
- **WebSocket Guide**: [Polymarket WebSocket Docs](https://docs.polymarket.com/developers/CLOB/websocket/wss-overview)

---

## ⚡ FAQ

**Q: ¿Los datos son reales?**
A: Sí, 100% reales desde la Data API oficial de Polymarket.

**Q: ¿Necesito API keys?**
A: No, la Data API es pública y no requiere autenticación.

**Q: ¿Cómo encuentro traders interesantes?**
A: Ve al [Leaderboard de Polymarket](https://polymarket.com/leaderboard) y busca traders con alto PnL o volumen.

**Q: ¿Puedo trackear mi propia cuenta?**
A: Sí, solo agrega tu wallet address a `traders.json`.

**Q: ¿El tracker ejecuta trades automáticamente?**
A: No, solo monitorea y alerta. No ejecuta trades.

**Q: ¿Funciona con todas las redes?**
A: Polymarket opera en Polygon. El tracker funciona con cualquier wallet de Polygon que opere en Polymarket.

---

## 🎯 Resumen

| Característica | Estado | Notas |
|----------------|--------|-------|
| **Monitoreo 100%** | ✅ | Captura todas las transacciones onchain |
| **Múltiples traders** | ✅ | Sin límite (respetando rate limits) |
| **Tiempo real** | 🟡 | Polling cada 5 min (WebSocket próximamente) |
| **Posiciones actuales** | ✅ | Con PnL en tiempo real |
| **Valor total** | ✅ | Agregado en USD |
| **Historial** | ✅ | Acceso ilimitado hacia atrás |
| **Sin autenticación** | ✅ | API pública |
| **Gratuito** | ✅ | Hasta 1,000 requests/hora |

---

**Autor**: Claude
**Versión**: 1.0
**Fecha**: 2025-11-07
**Licencia**: MIT
