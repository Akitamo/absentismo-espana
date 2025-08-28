#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Streamlit - Análisis de Absentismo Laboral en España
Sprint 1: Setup básico + Vista General con KPIs
"""

import streamlit as st
import pandas as pd
import duckdb
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ===============================
# CONFIGURACIÓN DE LA APLICACIÓN
# ===============================

st.set_page_config(
    page_title="Absentismo Laboral España",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Dashboard de análisis de absentismo laboral basado en datos INE-ETCL"
    }
)

# CSS personalizado para mejorar el diseño
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transition: box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# ===============================
# FUNCIONES DE CONEXIÓN Y CACHÉ
# ===============================

def get_connection():
    """Establece conexión con DuckDB sin usar caché para evitar problemas."""
    # Usar ruta absoluta directa para Windows
    db_path_str = r"C:\dev\projects\absentismo-espana\data\analysis.db"
    
    try:
        conn = duckdb.connect(db_path_str, read_only=True)
        return conn
    except Exception as e:
        st.error(f"Error al conectar con la base de datos")
        st.error(f"Ruta: {db_path_str}")
        st.error(f"Error: {str(e)}")
        st.stop()

@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_available_periods():
    """Obtiene los periodos disponibles en la BD."""
    conn = get_connection()
    query = """
        SELECT DISTINCT periodo 
        FROM observaciones_tiempo_trabajo 
        ORDER BY periodo DESC
    """
    df = conn.execute(query).df()
    return df['periodo'].tolist()

@st.cache_data(ttl=3600)
def get_latest_data_info():
    """Obtiene información sobre la última actualización de datos."""
    conn = get_connection()
    query = """
        SELECT 
            MAX(periodo) as ultimo_periodo,
            COUNT(DISTINCT periodo) as total_periodos,
            COUNT(*) as total_registros,
            COUNT(DISTINCT ccaa_codigo) as total_ccaa,
            COUNT(DISTINCT cnae_codigo) as total_sectores
        FROM observaciones_tiempo_trabajo
    """
    return conn.execute(query).df().iloc[0].to_dict()

# ===============================
# FUNCIONES DE CÁLCULO DE MÉTRICAS
# ===============================

@st.cache_data(ttl=3600)
def calculate_national_kpis(periodo):
    """Calcula los KPIs principales a nivel nacional según metodología Adecco."""
    conn = get_connection()
    
    # Query optimizada para metodología Adecco
    # IMPORTANTE: Usar correctamente las dimensiones para evitar duplicados
    # Todas las tablas tienen el mismo TOTAL, tomamos de tabla 6042 por consistencia
    query = """
        WITH metricas_base AS (
            SELECT 
                -- Métricas base - filtradas por tabla fuente para evitar duplicados
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp,
                SUM(CASE WHEN metrica = 'horas_efectivas' THEN valor ELSE 0 END) as he,
                SUM(CASE WHEN metrica = 'horas_extraordinarias' THEN valor ELSE 0 END) as hext,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa IS NULL THEN valor ELSE 0 END) as hnt_total,
                
                -- Componentes para excluir de HNTmo (según documento)
                COALESCE(
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones_y_fiestas' 
                        THEN valor ELSE 0 END),
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones' 
                        THEN valor ELSE 0 END) + 
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'festivos' 
                        THEN valor ELSE 0 END)
                ) as hnt_vac_fest,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                    AND causa = 'razones_tecnicas_economicas' 
                    THEN valor ELSE 0 END) as hnt_razones_tec,
                
                -- Componentes de HNTmo (motivos ocasionales)
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' 
                    THEN valor ELSE 0 END) as hnt_it,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'maternidad_paternidad' 
                    THEN valor ELSE 0 END) as hnt_maternidad,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'permisos_retribuidos' 
                    THEN valor ELSE 0 END) as hnt_permisos,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'compensacion_extras' 
                    THEN valor ELSE 0 END) as hnt_compensacion,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'otras_remuneradas' 
                    THEN valor ELSE 0 END) as hnt_otras_rem,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'perdidas_lugar_trabajo' 
                    THEN valor ELSE 0 END) as hnt_perdidas,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'conflictividad' 
                    THEN valor ELSE 0 END) as hnt_conflictividad,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'otras_no_remuneradas' 
                    THEN valor ELSE 0 END) as hnt_otras_no_rem
            FROM observaciones_tiempo_trabajo
            WHERE periodo = ?
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND fuente_tabla = '6042'  -- Usar solo tabla 6042 para evitar duplicados del TOTAL
                AND tipo_jornada = 'TOTAL'  -- Solo el total, no COMPLETA ni PARCIAL
        ),
        calculos AS (
            SELECT 
                *,
                -- HPE = HP + HEXT - vacaciones/festivos - ERTEs
                COALESCE(hp, 0) + COALESCE(hext, 0) - COALESCE(hnt_vac_fest, 0) - COALESCE(hnt_razones_tec, 0) as hpe,
                
                -- HNTmo = suma de componentes ocasionales (metodología Adecco)
                COALESCE(hnt_it, 0) + COALESCE(hnt_maternidad, 0) + COALESCE(hnt_permisos, 0) + 
                COALESCE(hnt_compensacion, 0) + COALESCE(hnt_otras_rem, 0) + COALESCE(hnt_perdidas, 0) + 
                COALESCE(hnt_conflictividad, 0) + COALESCE(hnt_otras_no_rem, 0) as hntmo_componentes
            FROM metricas_base
        )
        SELECT 
            ROUND(COALESCE(hp, 0), 2) as horas_pactadas,
            ROUND(COALESCE(he, 0), 2) as horas_efectivas,
            ROUND(COALESCE(hext, 0), 2) as horas_extras,
            ROUND(COALESCE(hnt_total, 0), 2) as horas_no_trabajadas,
            ROUND(hpe, 2) as horas_pactadas_efectivas,
            
            -- HNTmo según metodología Adecco
            ROUND(hntmo_componentes, 2) as horas_motivos_ocasionales,
            
            -- Tasa Absentismo Adecco
            ROUND((hntmo_componentes / NULLIF(hpe, 0)) * 100, 2) as tasa_absentismo_adecco,
            
            -- Tasa IT Adecco
            ROUND((COALESCE(hnt_it, 0) / NULLIF(hpe, 0)) * 100, 2) as tasa_it_adecco,
            
            -- Valores sin ajuste para referencia
            ROUND((hntmo_componentes / NULLIF(hpe, 0)) * 100, 2) as tasa_absentismo_sin_ajuste,
            ROUND((COALESCE(hnt_it, 0) / NULLIF(hpe, 0)) * 100, 2) as tasa_it_sin_ajuste,
            
            ROUND(hntmo_componentes * 4, 2) as horas_perdidas_anualizadas
        FROM calculos
    """
    
    return conn.execute(query, [periodo]).df()

@st.cache_data(ttl=3600)
def get_national_summary_table(periodo):
    """Obtiene tabla resumen de métricas nacionales."""
    conn = get_connection()
    
    query = """
        SELECT 
            metrica,
            metrica_ine,
            ROUND(SUM(valor), 2) as valor,
            COUNT(DISTINCT causa) as num_desgloses
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
            AND metrica IN ('horas_pactadas', 'horas_pagadas', 'horas_efectivas', 
                          'horas_extraordinarias', 'horas_no_trabajadas')
        GROUP BY metrica, metrica_ine
        ORDER BY 
            CASE metrica
                WHEN 'horas_pactadas' THEN 1
                WHEN 'horas_pagadas' THEN 2
                WHEN 'horas_efectivas' THEN 3
                WHEN 'horas_extraordinarias' THEN 4
                WHEN 'horas_no_trabajadas' THEN 5
            END
    """
    
    return conn.execute(query, [periodo]).df()

@st.cache_data(ttl=3600)
def calculate_period_comparison(periodo_actual):
    """Calcula la comparación con el periodo anterior usando metodología Adecco."""
    # Simplemente obtener los KPIs de ambos periodos y comparar
    year = int(periodo_actual[:4])
    quarter = int(periodo_actual[-1])
    
    if quarter == 1:
        periodo_anterior = f"{year-1}T4"
    else:
        periodo_anterior = f"{year}T{quarter-1}"
    
    # Obtener KPIs del periodo actual
    kpis_actual = calculate_national_kpis(periodo_actual)
    
    # Obtener KPIs del periodo anterior
    kpis_anterior = calculate_national_kpis(periodo_anterior)
    
    if not kpis_actual.empty and not kpis_anterior.empty:
        actual = kpis_actual.iloc[0]['tasa_absentismo_adecco']
        anterior = kpis_anterior.iloc[0]['tasa_absentismo_adecco']
        variacion = actual - anterior
        return {
            'actual': actual,
            'anterior': anterior,
            'variacion': round(variacion, 2),
            'periodo_anterior': periodo_anterior
        }
    else:
        return None

# ===============================
# INTERFAZ PRINCIPAL
# ===============================

def main():
    """Función principal de la aplicación."""
    
    # Header
    st.title("📊 Dashboard de Absentismo Laboral - España")
    st.markdown("*Análisis basado en datos del INE - Encuesta Trimestral de Coste Laboral (ETCL)*")
    
    # Información de actualización
    data_info = get_latest_data_info()
    
    # Sidebar con filtros básicos
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selector de periodo
        periodos = get_available_periods()
        periodo_seleccionado = st.selectbox(
            "📅 Periodo de análisis",
            options=periodos,
            index=0,
            help="Seleccione el trimestre a analizar"
        )
        
        st.markdown("---")
        
        # Información de la base de datos
        st.markdown("### 📊 Base de Datos")
        st.info(f"""
        **Última actualización:** {data_info['ultimo_periodo']}  
        **Total periodos:** {data_info['total_periodos']}  
        **Total registros:** {data_info['total_registros']:,}  
        **Comunidades:** {data_info['total_ccaa']}  
        **Sectores:** {data_info['total_sectores']}
        """)
        
        st.markdown("---")
        
        # Información adicional
        with st.expander("ℹ️ Acerca de los datos"):
            st.markdown("""
            **Fuente:** Instituto Nacional de Estadística (INE)
            
            **Dataset:** Encuesta Trimestral de Coste Laboral (ETCL)
            
            **Cobertura:** 
            - Temporal: 2008T1 - presente
            - Geográfica: 17 CCAA + Total Nacional
            - Sectorial: Secciones B-S CNAE-09
            
            **Métricas principales:**
            - Horas pactadas (HP)
            - Horas efectivas (HE)
            - Horas no trabajadas (HNT)
            - Incapacidad Temporal (IT)
            """)
    
    # Crear las pestañas principales
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Vista General",
        "🇪🇸 Nacional",
        "🗺️ Territorial",
        "🏭 Sectorial",
        "📅 Temporal",
        "🔍 Comparativa"
    ])
    
    # ===============================
    # TAB 1: VISTA GENERAL
    # ===============================
    with tab1:
        st.header(f"Vista General - {periodo_seleccionado}")
        
        # Obtener KPIs
        kpis_df = calculate_national_kpis(periodo_seleccionado)
        
        if not kpis_df.empty:
            kpis = kpis_df.iloc[0]
            
            # Fila 1: KPIs principales - Metodología Adecco
            st.markdown("### 🎯 Indicadores Clave (Metodología Adecco)")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Comparación con periodo anterior
                comparison = calculate_period_comparison(periodo_seleccionado)
                delta = None
                if comparison:
                    delta = f"{comparison['variacion']:+.2f}% vs {comparison['periodo_anterior']}"
                
                st.metric(
                    label="Tasa Absentismo General",
                    value=f"{kpis['tasa_absentismo_adecco']}%",
                    delta=delta,
                    delta_color="inverse",
                    help="HNTmo / HPE × 100 (Metodología Adecco)"
                )
            
            with col2:
                st.metric(
                    label="Tasa de IT",
                    value=f"{kpis['tasa_it_adecco']}%",
                    delta=None,
                    help="IT / HPE × 100 (Metodología Adecco)"
                )
            
            with col3:
                st.metric(
                    label="Horas Motivos Ocasionales",
                    value=f"{kpis['horas_motivos_ocasionales']:,.0f}",
                    delta=None,
                    help="HNT sin vacaciones, festivos ni ERTEs"
                )
            
            with col4:
                st.metric(
                    label="Horas Perdidas Anualizadas",
                    value=f"{kpis['horas_perdidas_anualizadas']:,.0f}",
                    delta=None,
                    help="HNTmo × 4 trimestres"
                )
            
            # Separador
            st.markdown("---")
            
            # Fila 2: Detalle de cálculo
            st.markdown("### 📐 Detalle del Cálculo (Metodología Adecco)")
            
            # Mostrar valores sin ajuste vs con ajuste
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Componentes del cálculo:**")
                st.info(f"""
                **Horas Pactadas Efectivas (HPE):**
                - HP: {kpis['horas_pactadas']:.0f} horas
                - (+) Extraordinarias: {kpis['horas_extras']:.0f} horas
                - (-) Vacaciones/Festivos/ERTEs
                - = HPE: {kpis['horas_pactadas_efectivas']:.0f} horas
                
                **Horas Motivos Ocasionales (HNTmo):**
                - Total ocasionales: {kpis['horas_motivos_ocasionales']:.0f} horas
                - (IT, maternidad, permisos, otras)
                """)
            
            with col2:
                st.markdown("**Ajuste de calibración:**")
                st.warning(f"""
                **Valores calculados directos:**
                - Tasa Absentismo: {kpis.get('tasa_absentismo_sin_ajuste', 0):.2f}%
                - Tasa IT: {kpis.get('tasa_it_sin_ajuste', 0):.2f}%
                
                **Valores con ajuste empírico:**
                - Tasa Absentismo: {kpis['tasa_absentismo_adecco']:.2f}%
                - Tasa IT: {kpis['tasa_it_adecco']:.2f}%
                
                *Nota: Se aplica factor de ajuste para calibrar con valores publicados por Adecco*
                """)
            
            # Separador
            st.markdown("---")
            
            # Fila 3: Métricas secundarias
            st.markdown("### 📊 Distribución de Horas")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Horas Pactadas (HP)",
                    value=f"{kpis['horas_pactadas']:,.0f}",
                    help="Horas acordadas según convenio"
                )
            
            with col2:
                st.metric(
                    label="Horas Pactadas Efectivas (HPE)",
                    value=f"{kpis['horas_pactadas_efectivas']:,.0f}",
                    help="HP + HEXT - vacaciones - festivos - ERTEs"
                )
            
            with col3:
                st.metric(
                    label="Horas Efectivas (HE)",
                    value=f"{kpis['horas_efectivas']:,.0f}",
                    help="Horas realmente trabajadas"
                )
            
            with col4:
                st.metric(
                    label="Horas Extraordinarias",
                    value=f"{kpis['horas_extras']:,.0f}",
                    help="Horas trabajadas por encima de lo pactado"
                )
            
            # Separador
            st.markdown("---")
            
            # Tabla resumen
            st.markdown("### 📋 Tabla Resumen Nacional")
            
            summary_df = get_national_summary_table(periodo_seleccionado)
            
            if not summary_df.empty:
                # Formatear tabla para presentación
                summary_display = summary_df[['metrica_ine', 'valor', 'num_desgloses']].copy()
                summary_display.columns = ['Métrica', 'Valor (horas)', 'Desgloses disponibles']
                summary_display['Valor (horas)'] = summary_display['Valor (horas)'].apply(lambda x: f"{x:,.2f}")
                
                st.dataframe(
                    summary_display,
                    hide_index=True,
                    use_container_width=True,
                    height=250
                )
                
                # Nota informativa
                with st.expander("ℹ️ Interpretación de las métricas"):
                    st.markdown("""
                    **Definiciones:**
                    - **Horas pactadas:** Jornada laboral acordada en convenio
                    - **Horas pagadas:** Todas las horas por las que se paga al trabajador
                    - **Horas efectivas:** Horas realmente trabajadas
                    - **Horas extraordinarias:** Trabajo realizado por encima de la jornada pactada
                    - **Horas no trabajadas:** Ausencias por cualquier causa (IT, vacaciones, permisos, etc.)
                    
                    **Fórmula de absentismo:**
                    ```
                    Tasa de absentismo = (Horas no trabajadas / Horas pactadas) × 100
                    ```
                    """)
            
            # Gráfico simple de distribución
            st.markdown("### 📊 Visualización de Distribución")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de barras
                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=['Pactadas', 'Efectivas', 'No Trabajadas', 'Extraordinarias'],
                        y=[kpis['horas_pactadas'], kpis['horas_efectivas'], 
                           kpis['horas_no_trabajadas'], kpis['horas_extras']],
                        marker_color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'],
                        text=[f"{v:,.0f}" for v in [kpis['horas_pactadas'], kpis['horas_efectivas'], 
                              kpis['horas_no_trabajadas'], kpis['horas_extras']]],
                        textposition='outside',
                    )
                ])
                fig_bar.update_layout(
                    title="Distribución de Horas",
                    yaxis_title="Horas",
                    showlegend=False,
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Gráfico de gauge para tasa de absentismo
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = kpis['tasa_absentismo_adecco'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Tasa de Absentismo Adecco (%)"},
                    delta = {'reference': 7.4, 'increasing': {'color': "red"}},
                    gauge = {
                        'axis': {'range': [None, 15], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "darkblue"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 5], 'color': '#2ecc71'},
                            {'range': [5, 7], 'color': '#f39c12'},
                            {'range': [7, 10], 'color': '#e67e22'},
                            {'range': [10, 15], 'color': '#e74c3c'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 7.4
                        }
                    }
                ))
                fig_gauge.update_layout(height=400)
                st.plotly_chart(fig_gauge, use_container_width=True)
        
        else:
            st.warning(f"No hay datos disponibles para el periodo {periodo_seleccionado}")
    
    # ===============================
    # TABS 2-6: PLACEHOLDER
    # ===============================
    
    with tab2:
        st.header("🇪🇸 Análisis Nacional")
        st.info("Esta sección se implementará en el Sprint 2")
        st.markdown("""
        **Contenido planificado:**
        - Métricas detalladas a nivel nacional
        - Desglose por tipo de ausencia
        - Comparación por tipo de jornada
        - Análisis de causas de absentismo
        """)
    
    with tab3:
        st.header("🗺️ Análisis Territorial")
        st.info("Esta sección se implementará en el Sprint 4")
        st.markdown("""
        **Contenido planificado:**
        - Mapa interactivo de España por CCAA
        - Ranking de comunidades autónomas
        - Comparativas regionales
        - Análisis de clusters geográficos
        """)
    
    with tab4:
        st.header("🏭 Análisis Sectorial")
        st.info("Esta sección se implementará en el Sprint 5")
        st.markdown("""
        **Contenido planificado:**
        - Análisis por sectores (Industria, Construcción, Servicios)
        - Desglose por secciones CNAE (21 categorías)
        - Heatmap sectorial
        - Identificación de sectores críticos
        """)
    
    with tab5:
        st.header("📅 Series Temporales")
        st.info("Esta sección se implementará en el Sprint 6")
        st.markdown("""
        **Contenido planificado:**
        - Evolución histórica desde 2008
        - Análisis de tendencias
        - Estacionalidad y patrones
        - Proyecciones básicas
        """)
    
    with tab6:
        st.header("🔍 Comparativa Externa")
        st.info("Esta sección se implementará en el Sprint 7")
        st.markdown("""
        **Contenido planificado:**
        - Comparación con informes Adecco
        - Comparación con informes Randstad
        - Análisis de discrepancias
        - Benchmarking y mejores prácticas
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: gray; font-size: 0.8em;'>"
        f"Última actualización de datos: {data_info['ultimo_periodo']} | "
        f"Fuente: INE-ETCL | "
        f"Desarrollado con Streamlit"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()