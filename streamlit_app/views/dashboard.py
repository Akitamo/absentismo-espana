"""
Página principal del Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Añadir parent path
sys.path.append(str(Path(__file__).parent.parent))

from services.data_service import DataService
from components.kpi_card import render_kpi_card
from components.filters import render_filters
from components.charts import render_evolution_chart
from components.chart_container import render_chart_container
from visualizations import get_visualization

def show():
    """Muestra la página principal del dashboard"""
    
    # Header
    st.markdown("# 📊 Dashboard de Absentismo Laboral")
    st.markdown("Análisis de datos INE-ETCL para España")
    
    # Inicializar servicio de datos
    data_service = DataService()
    
    # Filtros superiores
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        periodo = st.selectbox(
            "Periodo",
            options=data_service.get_available_periods(),
            index=0,  # Más reciente
            help="Seleccione el trimestre a analizar"
        )
    
    with col2:
        ccaa = st.selectbox(
            "Comunidad Autónoma",
            options=["Total Nacional"] + data_service.get_ccaa_list(),
            help="Filtrar por CCAA"
        )
    
    with col3:
        sector = st.selectbox(
            "Sector",
            options=["Todos"] + data_service.get_sectors_list(),
            help="Filtrar por sector CNAE"
        )
    
    with col4:
        st.markdown("")  # Espaciador
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    # Separador
    st.markdown("---")
    
    # KPIs principales
    st.markdown("### 📈 Indicadores Principales")
    
    # Obtener métricas
    metrics = data_service.get_kpis(periodo, ccaa, sector)
    
    # Fila de KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_kpi_card(
            title="Tasa de Absentismo",
            value=f"{metrics.get('tasa_absentismo', 0):.1f}%",
            delta=f"{metrics.get('tasa_absentismo_delta', 0):+.1f}pp",
            delta_color="inverse" if metrics.get('tasa_absentismo_delta', 0) > 0 else "normal",
            help_text="Porcentaje de horas no trabajadas sobre HPE"
        )
    
    with col2:
        render_kpi_card(
            title="Tasa IT",
            value=f"{metrics.get('tasa_it', 0):.1f}%",
            delta=f"{metrics.get('tasa_it_delta', 0):+.1f}pp",
            delta_color="inverse" if metrics.get('tasa_it_delta', 0) > 0 else "normal",
            help_text="Incapacidad Temporal sobre HPE"
        )
    
    with col3:
        render_kpi_card(
            title="Horas Pactadas Efectivas",
            value=f"{metrics.get('hpe', 0):.1f}h",
            delta=f"{metrics.get('hpe_delta', 0):+.1f}h",
            help_text="HPE = HP + HEXT - Vacaciones - Festivos"
        )
    
    with col4:
        render_kpi_card(
            title="HNT Motivos Ocasionales",
            value=f"{metrics.get('hntmo', 0):.1f}h",
            delta=f"{metrics.get('hntmo_delta', 0):+.1f}h",
            delta_color="inverse" if metrics.get('hntmo_delta', 0) > 0 else "normal",
            help_text="Horas no trabajadas por motivos ocasionales"
        )
    
    # Separador
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Evolución Temporal")
        
        # PRUEBA DE ARQUITECTURA MODULAR
        # Generar datos de ejemplo para la prueba
        periodos = pd.date_range('2020-01', '2024-01', freq='Q')
        datos_ejemplo = pd.DataFrame({
            'periodo': periodos,
            'tasa_absentismo': np.random.uniform(10, 15, len(periodos)) + np.sin(np.arange(len(periodos)) * 0.5) * 2
        })
        datos_ejemplo.set_index('periodo', inplace=True)
        
        try:
            # Crear visualización con el sistema modular
            viz = get_visualization(
                'absentismo_temporal',
                data=datos_ejemplo,
                config={
                    'title': 'Evolución de la Tasa de Absentismo',
                    'height': 350
                }
            )
            
            # Renderizar en contenedor estándar sin margen (está dentro de columnas)
            render_chart_container(viz, container_config={'no_margin': True})
            
        except Exception as e:
            st.error(f"Error en visualización modular: {e}")
            # Fallback al método anterior
            evolution_data = data_service.get_evolution_data(ccaa, sector)
            if not evolution_data.empty:
                render_evolution_chart(evolution_data)
            else:
                st.info("No hay datos disponibles para mostrar")
    
    with col2:
        st.markdown("### 🏆 Ranking por CCAA")
        # Aquí irá el ranking
        ranking_data = data_service.get_ranking_ccaa(periodo)
        if not ranking_data.empty:
            st.dataframe(
                ranking_data.head(10),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay datos de ranking disponibles")
    
    # Footer con información
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("📅 Última actualización: Q1 2025")
    
    with col2:
        st.caption("📊 Fuente: INE - Encuesta Trimestral de Coste Laboral")
    
    with col3:
        st.caption("🔧 Metodología: Adecco + Randstad")