# 🌐 Interfaz Web - Detector de Arbitraje

Interfaz web interactiva para detectar oportunidades de arbitraje entre Polymarket y Kalshi.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
cd predictionarb
pip3 install -r requirements.txt
```

### 2. Iniciar la Interfaz Web

```bash
streamlit run web_app.py
```

### 3. Elegir Puerto (si está ocupado)

Si el puerto 8501 está ocupado, usa otro:

```bash
streamlit run web_app.py --server.port 8080
```

O cualquier otro puerto disponible (3000, 5000, 8888, etc.)

### 4. Abrir en el Navegador

La interfaz se abrirá automáticamente en:
```
http://localhost:8501
```

O el puerto que hayas elegido.

---

## 📱 Características de la Interfaz

### 🎯 Panel Principal
- **Botón de análisis**: Ejecuta detección de arbitraje con un solo clic
- **Barra de progreso**: Muestra el progreso en tiempo real
- **Métricas en vivo**: Cantidad de mercados, pares, arbitrajes positivos

### ⚙️ Panel Lateral (Configuración)
- **Umbral de similitud**: Ajusta qué tan similares deben ser los mercados (50-100%)
- **Top N**: Cuántas oportunidades mostrar (5-100)
- **Información**: Explicación sobre el arbitraje

### 📊 Visualizaciones
1. **Gráfico de distribución**: Histograma de todos los spreads
2. **Top 10**: Barra horizontal con mejores oportunidades
3. **Tabla interactiva**: Todos los resultados con colores
4. **Detalles expandibles**: URLs de los mercados

### 💾 Exportación
- **Descargar CSV**: Resultados en formato Excel/CSV
- **Descargar JSON**: Datos en formato JSON estructurado

### 📈 Estadísticas
- Spread promedio, mediano, mínimo, máximo
- Volumen total combinado
- Porcentaje de arbitrajes positivos

---

## 🎨 Capturas de Pantalla

### Vista Principal
```
┌─────────────────────────────────────────────────────┐
│      💰 DETECTOR DE ARBITRAJE                       │
│    Polymarket vs Kalshi - Datos 100% Reales        │
│                                                      │
│  [🚀 DETECTAR OPORTUNIDADES DE ARBITRAJE]          │
│                                                      │
│  📊 Resumen General                                 │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐    │
│  │ 247  │ │ 1247 │ │  45  │ │  12  │ │ 5.2% │    │
│  │Markets│ │Markets│ │ Pairs│ │ Arb  │ │ Max  │    │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘    │
│                                                      │
│  📈 [Gráfico de Distribución]  [Top 10 Bars]       │
│                                                      │
│  🎯 Oportunidades de Arbitraje                      │
│  ┌────────────────────────────────────────────┐   │
│  │ Mercado          │ Spread │ Volumen        │   │
│  │ Trump 2024       │ +5.2%  │ $14,680,230   │   │
│  │ US Recession     │ +3.1%  │ $3,990,450    │   │
│  └────────────────────────────────────────────┘   │
│                                                      │
│  💾 [📥 Descargar CSV] [📥 Descargar JSON]         │
└─────────────────────────────────────────────────────┘
```

---

## ⌨️ Comandos Útiles

### Cambiar Puerto
```bash
# Puerto 8080
streamlit run web_app.py --server.port 8080

# Puerto 3000
streamlit run web_app.py --server.port 3000

# Puerto 5000
streamlit run web_app.py --server.port 5000
```

### Modo Desarrollo (con auto-reload)
```bash
streamlit run web_app.py --server.runOnSave true
```

### Modo Headless (sin abrir navegador)
```bash
streamlit run web_app.py --server.headless true
```

### Ver en Red Local
```bash
streamlit run web_app.py --server.address 0.0.0.0
```

Luego accede desde otro dispositivo con:
```
http://TU_IP_LOCAL:8501
```

---

## 🔧 Solución de Problemas

### Error: "Address already in use"

**Problema**: El puerto 8501 está ocupado.

**Solución**: Usa otro puerto:
```bash
streamlit run web_app.py --server.port 8080
```

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Problema**: Streamlit no está instalado.

**Solución**:
```bash
pip3 install streamlit plotly
```

### Error: "No se pudieron obtener mercados"

**Problema**: APIs bloqueadas por geo-restricción.

**Solución**:
1. Usa VPN
2. Ejecuta desde tu máquina local (no cloud)
3. Cambia de red WiFi

### La interfaz se ve rara

**Problema**: Caché de Streamlit.

**Solución**:
```bash
# Limpiar caché
streamlit cache clear

# Reiniciar servidor
Ctrl + C (detener)
streamlit run web_app.py
```

---

## 📦 Estructura de Archivos

```
predictionarb/
├── web_app.py              # ← Interfaz web (ejecutar este)
├── arbitrage_detector.py   # ← Lógica backend
├── requirements.txt        # ← Dependencias
├── README.md              # ← Documentación general
└── WEB_INTERFACE.md       # ← Esta guía
```

---

## 🎯 Casos de Uso

### Uso Personal
1. Ejecuta: `streamlit run web_app.py`
2. Analiza mercados con el botón
3. Descarga resultados en CSV
4. Revisa oportunidades en Excel

### Análisis Frecuente
1. Deja la interfaz abierta
2. Refresca el análisis cada 15 minutos
3. Monitorea spreads en tiempo real
4. Exporta cuando encuentres buenos spreads

### Demo/Presentación
1. Ejecuta con: `streamlit run web_app.py --server.address 0.0.0.0`
2. Comparte tu IP local con la audiencia
3. Todos pueden ver la interfaz en sus dispositivos
4. Realiza análisis en vivo

---

## 💡 Tips y Trucos

### Maximizar Oportunidades
- Reduce el umbral de similitud a 70-75%
- Aumenta "Top N" a 50 o más
- Ejecuta análisis cada 10-15 minutos

### Mejorar Rendimiento
- Cierra otras pestañas del navegador
- Usa conexión a internet rápida
- Ejecuta en horarios de bajo tráfico API

### Personalización
- Edita `web_app.py` para cambiar colores
- Modifica umbrales por defecto (línea 75-85)
- Añade más gráficos según necesites

---

## 🆚 CLI vs Web Interface

| Característica | CLI (terminal) | Web Interface |
|---------------|----------------|---------------|
| **Facilidad de uso** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Visualizaciones** | ❌ | ✅ Gráficos interactivos |
| **Exportación** | ✅ Auto CSV/JSON | ✅ Botones descarga |
| **Configuración** | Editar código | Sliders en vivo |
| **Monitoreo** | Logs en terminal | Dashboard visual |
| **Mejor para** | Scripts/Automation | Análisis manual |

---

## 📞 Soporte

Si tienes problemas:

1. **Verifica instalación**:
   ```bash
   python3 --version  # Debe ser 3.10+
   streamlit --version  # Debe estar instalado
   ```

2. **Logs de error**:
   - Revisa la terminal donde ejecutaste `streamlit run`
   - Copia el error completo
   - Verifica `arbitrage.log`

3. **Test de conectividad**:
   ```bash
   curl -I https://clob.polymarket.com
   curl -I https://api.elections.kalshi.com/trade-api/v2/markets
   ```

---

## 🎉 ¡Disfruta!

Ya tienes una interfaz web completa y profesional para detectar arbitrajes.

**Siguiente paso**: Ejecuta y empieza a detectar oportunidades 🚀

```bash
streamlit run web_app.py
```

---

**Versión**: 2.0
**Última actualización**: 2025-11-05
**Autor**: Claude
