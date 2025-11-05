#!/usr/bin/env python3
"""
Interfaz Web para Detector de Arbitraje - Polymarket vs Kalshi

Aplicación web interactiva usando Streamlit para detectar oportunidades
de arbitraje entre mercados de predicción.

Autor: Claude
Versión: 2.0
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from arbitrage_detector import ArbitrageDetector, PolymarketClient, KalshiClient
import logging

# Configurar página
st.set_page_config(
    page_title="Detector de Arbitraje - Polymarket vs Kalshi",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .positive-spread {
        color: #00cc00;
        font-weight: bold;
    }
    .negative-spread {
        color: #cc0000;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">💰 Detector de Arbitraje</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Polymarket vs Kalshi - Datos 100% Reales</div>', unsafe_allow_html=True)

# Sidebar - Configuración
with st.sidebar:
    st.header("⚙️ Configuración")

    similarity_threshold = st.slider(
        "Umbral de Similitud (%)",
        min_value=50,
        max_value=100,
        value=80,
        step=5,
        help="Porcentaje mínimo de similitud para emparejar mercados"
    )

    top_n = st.number_input(
        "Oportunidades a Mostrar",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
        help="Número de mejores oportunidades a visualizar"
    )

    st.markdown("---")

    st.markdown("""
    ### 📊 Sobre el Arbitraje

    **¿Qué es arbitraje?**

    Comprar probabilidades complementarias:
    - **"Yes"** en Polymarket
    - **"No"** en Kalshi

    **Hay arbitraje si:**
    ```
    P(Yes_Poly) + P(No_Kalshi) < 1.0
    ```

    **Spread** = Ganancia potencial
    """)

    st.markdown("---")
    st.markdown("### ⚠️ Aviso")
    st.info("Este detector usa **datos 100% reales** de las APIs oficiales.")

# Estado de la aplicación
if 'results' not in st.session_state:
    st.session_state.results = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Botón principal
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 DETECTAR OPORTUNIDADES DE ARBITRAJE", use_container_width=True, type="primary"):

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Paso 1: Inicializar
            status_text.text("🔧 Inicializando detector...")
            progress_bar.progress(10)
            time.sleep(0.5)

            detector = ArbitrageDetector(similarity_threshold=float(similarity_threshold))

            # Paso 2: Obtener mercados
            status_text.text("📡 Obteniendo mercados de Polymarket...")
            progress_bar.progress(20)

            status_text.text("📡 Obteniendo mercados de Kalshi...")
            progress_bar.progress(40)

            poly_markets, kalshi_markets = detector.fetch_all_markets()

            # Paso 3: Emparejar
            status_text.text("🔗 Emparejando mercados similares...")
            progress_bar.progress(60)

            matches = detector.match_markets(poly_markets, kalshi_markets)

            # Paso 4: Calcular arbitraje
            status_text.text("💹 Calculando oportunidades de arbitraje...")
            progress_bar.progress(80)

            df = detector.calculate_arbitrage(matches)

            # Paso 5: Completado
            progress_bar.progress(100)
            status_text.text("✅ Análisis completado!")
            time.sleep(1)

            # Guardar resultados
            st.session_state.results = df
            st.session_state.last_update = datetime.now()
            st.session_state.poly_count = len(poly_markets)
            st.session_state.kalshi_count = len(kalshi_markets)
            st.session_state.matches_count = len(matches)

            progress_bar.empty()
            status_text.empty()

            st.success(f"🎉 ¡Análisis completado! Encontrados {len(matches)} pares de mercados.")
            st.rerun()

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error: {str(e)}")
            st.warning("""
            **Posibles causas:**
            - Restricciones geográficas (usa VPN)
            - APIs temporalmente no disponibles
            - Problema de conectividad

            **Solución:** Ejecuta desde tu máquina local o cambia de red.
            """)

# Mostrar resultados si existen
if st.session_state.results is not None and not st.session_state.results.empty:

    df = st.session_state.results

    # Métricas principales
    st.markdown("---")
    st.subheader("📊 Resumen General")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Mercados Polymarket",
            st.session_state.poly_count,
            delta=None
        )

    with col2:
        st.metric(
            "Mercados Kalshi",
            st.session_state.kalshi_count,
            delta=None
        )

    with col3:
        st.metric(
            "Pares Emparejados",
            st.session_state.matches_count,
            delta=None
        )

    positive_arb = df[df['_spread_numeric'] > 0]

    with col4:
        st.metric(
            "Arbitrajes Positivos",
            len(positive_arb),
            delta=f"{len(positive_arb)/len(df)*100:.1f}%" if len(df) > 0 else "0%"
        )

    with col5:
        st.metric(
            "Spread Máximo",
            f"{df['_spread_numeric'].max():.2f}%",
            delta=None
        )

    # Timestamp
    if st.session_state.last_update:
        st.caption(f"🕐 Última actualización: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

    # Gráfico de spreads
    st.markdown("---")
    st.subheader("📈 Distribución de Spreads")

    col1, col2 = st.columns(2)

    with col1:
        # Histograma
        fig_hist = px.histogram(
            df,
            x='_spread_numeric',
            nbins=30,
            title="Distribución de Spreads de Arbitraje",
            labels={'_spread_numeric': 'Spread (%)'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Break-even")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # Top 10 spreads
        top_10 = df.nlargest(10, '_spread_numeric')
        fig_bar = px.bar(
            top_10,
            x='_spread_numeric',
            y=top_10['Mercado'].str[:40],  # Truncar títulos
            orientation='h',
            title="Top 10 Mejores Oportunidades",
            labels={'_spread_numeric': 'Spread (%)', 'y': 'Mercado'},
            color='_spread_numeric',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabla de oportunidades
    st.markdown("---")
    st.subheader("🎯 Oportunidades de Arbitraje Detectadas")

    # Filtro: Solo positivos o todos
    show_only_positive = st.checkbox("Mostrar solo spreads positivos", value=True)

    if show_only_positive:
        display_df = positive_arb.head(top_n)
        st.info(f"📊 Mostrando {len(display_df)} oportunidades con spread positivo")
    else:
        display_df = df.head(top_n)
        st.info(f"📊 Mostrando top {len(display_df)} oportunidades")

    if not display_df.empty:
        # Preparar datos para display
        display_columns = {
            'Mercado': display_df['Mercado'],
            'Similitud': display_df['Similitud (%)'],
            'Prob Yes Poly': display_df['Prob Yes Poly'],
            'Prob No Kalshi': display_df['Prob No Kalshi'],
            'Spread (%)': display_df['Spread (%)'],
            'Volumen Total': display_df['Vol Total ($)'],
            'Expira Poly': display_df['Expira Poly'],
        }

        # Mostrar tabla con formato
        styled_df = pd.DataFrame(display_columns)

        # Aplicar colores a spreads
        def highlight_spread(row):
            spread_val = float(row['Spread (%)'])
            if spread_val > 0:
                return [''] * (len(row) - 2) + ['background-color: #d4edda'] + ['']
            else:
                return [''] * (len(row) - 2) + ['background-color: #f8d7da'] + ['']

        st.dataframe(
            styled_df,
            use_container_width=True,
            height=600
        )

        # Expandir para ver detalles
        with st.expander("🔍 Ver URLs de los mercados"):
            for idx, row in display_df.head(10).iterrows():
                st.markdown(f"""
                **{row['Mercado']}**
                - 🔗 Polymarket: {row['URL Poly']}
                - 🔗 Kalshi: {row['URL Kalshi']}
                - 💹 Spread: **{row['Spread (%)']}**
                """)
                st.markdown("---")

        # Estadísticas detalladas
        st.markdown("---")
        st.subheader("📈 Estadísticas Detalladas")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Spread Promedio", f"{df['_spread_numeric'].mean():.2f}%")

        with col2:
            st.metric("Spread Mediano", f"{df['_spread_numeric'].median():.2f}%")

        with col3:
            st.metric("Spread Mínimo", f"{df['_spread_numeric'].min():.2f}%")

        with col4:
            vol_total = df['_volume_numeric'].sum()
            st.metric("Volumen Total", f"${vol_total:,.0f}")

        # Botones de descarga
        st.markdown("---")
        st.subheader("💾 Descargar Resultados")

        col1, col2 = st.columns(2)

        with col1:
            # CSV
            csv = df.drop(columns=['_spread_numeric', '_volume_numeric']).to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"arbitrage_opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # JSON
            json_data = df.drop(columns=['_spread_numeric', '_volume_numeric']).to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Descargar JSON",
                data=json_data,
                file_name=f"arbitrage_opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    else:
        st.warning("⚠️ No se encontraron oportunidades de arbitraje positivas en este momento.")
        st.info("""
        Esto es **normal**. Los mercados son eficientes y los arbitrajes desaparecen rápidamente.

        **Recomendaciones:**
        - Ejecuta el análisis más frecuentemente
        - Reduce el umbral de similitud
        - Los mercados están bien alineados (buena señal de eficiencia)
        """)

else:
    # Vista inicial
    st.markdown("---")
    st.info("""
    ### 👆 Haz clic en el botón de arriba para comenzar

    El detector analizará **cientos de mercados reales** de Polymarket y Kalshi
    para encontrar oportunidades de arbitraje en tiempo real.

    **¿Qué hace el detector?**
    1. 📡 Obtiene todos los mercados activos de ambas plataformas
    2. 🔗 Empareja mercados similares usando IA
    3. 💹 Calcula spreads de arbitraje
    4. 📊 Muestra las mejores oportunidades
    5. 💾 Permite descargar resultados

    **Datos 100% reales** - Sin simulaciones ni placeholders
    """)

    # Columnas de ejemplo
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### ✅ Ventajas
        - Datos en tiempo real
        - Análisis automático
        - Fácil de usar
        - Exportación de datos
        - Visualizaciones interactivas
        """)

    with col2:
        st.markdown("""
        ### 📋 Requisitos
        - Conexión a internet
        - Acceso a APIs sin restricciones
        - (Opcional) VPN si hay geo-bloqueo
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>💰 <strong>Detector de Arbitraje</strong> v2.0 | Polymarket vs Kalshi</p>
    <p>Datos 100% reales desde APIs oficiales | Desarrollado por Claude</p>
    <p style='font-size: 0.8rem;'>⚠️ Este software es solo para fines educativos e informativos.
    No constituye asesoramiento financiero.</p>
</div>
""", unsafe_allow_html=True)
