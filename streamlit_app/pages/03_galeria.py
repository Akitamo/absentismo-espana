"""
Página Galería - QA Visual de todas las visualizaciones registradas
Auto-discovery de visualizaciones con datos de muestra
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Añadir el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from design.theme import apply_theme
from visualizations.registry import get_registry, get_visualization
from components.chart_container import ChartContainer

# Configuración de la página
st.set_page_config(
    page_title="Galería de Visualizaciones",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar tema
apply_theme()

def generate_sample_data():
    """Genera datos de muestra para las visualizaciones"""
    
    # Datos temporales (serie de tiempo)
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=365),
        end=datetime.now(),
        freq='M'
    )
    
    time_series_data = pd.DataFrame({
        'fecha': dates,
        'absentismo_total': np.random.uniform(3.5, 7.5, len(dates)),
        'absentismo_it': np.random.uniform(2.0, 4.5, len(dates)),
        'absentismo_cc': np.random.uniform(1.0, 3.0, len(dates)),
        'horas_perdidas': np.random.uniform(100000, 500000, len(dates)),
    })
    
    # Datos categóricos
    categorical_data = pd.DataFrame({
        'sector': ['Industria', 'Servicios', 'Construcción', 'Agricultura', 'Tecnología'],
        'tasa_absentismo': [5.2, 4.8, 6.1, 3.9, 3.2],
        'empleados': [250000, 890000, 180000, 95000, 120000],
        'coste_medio': [1500, 1200, 1800, 900, 2100]
    })
    
    # Datos por comunidad autónoma
    ccaa_data = pd.DataFrame({
        'comunidad': ['Madrid', 'Cataluña', 'Andalucía', 'Valencia', 'País Vasco', 
                     'Galicia', 'Castilla y León', 'Canarias', 'Murcia', 'Aragón'],
        'tasa_2023': [4.8, 5.1, 5.9, 5.3, 4.2, 5.5, 5.0, 6.2, 5.7, 4.9],
        'tasa_2024': [4.9, 5.0, 6.1, 5.2, 4.3, 5.4, 5.1, 6.0, 5.8, 5.0],
        'variacion': [0.1, -0.1, 0.2, -0.1, 0.1, -0.1, 0.1, -0.2, 0.1, 0.1]
    })
    
    # Matriz de correlación
    correlation_data = pd.DataFrame(
        np.random.rand(5, 5),
        columns=['Edad', 'Antigüedad', 'Salario', 'Horas_Trabajadas', 'Absentismo'],
        index=['Edad', 'Antigüedad', 'Salario', 'Horas_Trabajadas', 'Absentismo']
    )
    
    return {
        'time_series': time_series_data,
        'categorical': categorical_data,
        'geographical': ccaa_data,
        'correlation': correlation_data
    }

def render_gallery():
    """Renderiza la galería de visualizaciones"""
    
    st.title("🎨 Galería de Visualizaciones")
    st.markdown("""
    Esta página muestra todas las visualizaciones registradas en el sistema con datos de muestra.
    Útil para QA visual y verificación de consistencia de diseño.
    """)
    
    # Obtener registry
    registry = get_registry()
    
    if not registry:
        st.warning("No hay visualizaciones registradas en el sistema.")
        return
    
    # Generar datos de muestra
    sample_data = generate_sample_data()
    
    # Tabs para organizar por tipo de datos
    tab1, tab2, tab3 = st.tabs(["📊 Series Temporales", "📈 Categóricas", "🗺️ Geográficas"])
    
    with tab1:
        st.header("Visualizaciones de Series Temporales")
        
        # Filtrar visualizaciones apropiadas para series temporales
        time_series_viz = ['line_chart', 'area_chart', 'time_series_plotly']
        
        col1, col2 = st.columns(2)
        
        for i, viz_name in enumerate(time_series_viz):
            if viz_name in registry:
                with col1 if i % 2 == 0 else col2:
                    try:
                        # Crear container con slots
                        container = ChartContainer(f"gallery_{viz_name}_ts")
                        
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        
                        # Header
                        with container.header(
                            title=f"Demo: {viz_name.replace('_', ' ').title()}",
                            subtitle="Datos de muestra - Serie temporal"
                        ):
                            pass
                        
                        # Controls (ejemplo de filtros locales)
                        with container.controls():
                            col_a, col_b = st.columns(2)
                            with col_a:
                                metric = st.selectbox(
                                    "Métrica",
                                    ['absentismo_total', 'absentismo_it', 'absentismo_cc'],
                                    key=f"{viz_name}_metric"
                                )
                            with col_b:
                                show_trend = st.checkbox(
                                    "Mostrar tendencia",
                                    key=f"{viz_name}_trend"
                                )
                        
                        # Body con la visualización
                        with container.body():
                            config = {
                                'title': '',
                                'y_column': metric,
                                'show_trend': show_trend
                            }
                            viz = get_visualization(
                                viz_name, 
                                sample_data['time_series'],
                                config,
                                viz_id=f"gallery_{viz_name}"
                            )
                            if viz:
                                chart = viz.render()
                                container.render_visualization(chart, viz.get_library())
                        
                        # Footer
                        with container.footer(f"Librería: {registry[viz_name].get_library() if hasattr(registry[viz_name], 'get_library') else 'unknown'}"):
                            pass
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        container.error(f"Error renderizando {viz_name}: {str(e)}")
    
    with tab2:
        st.header("Visualizaciones Categóricas")
        
        # Filtrar visualizaciones apropiadas para datos categóricos
        categorical_viz = ['bar_chart', 'pie_chart', 'donut_chart']
        
        col1, col2 = st.columns(2)
        
        for i, viz_name in enumerate(categorical_viz):
            if viz_name in registry:
                with col1 if i % 2 == 0 else col2:
                    try:
                        container = ChartContainer(f"gallery_{viz_name}_cat")
                        
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        
                        with container.header(
                            title=f"Demo: {viz_name.replace('_', ' ').title()}",
                            subtitle="Datos categóricos de muestra"
                        ):
                            pass
                        
                        with container.body():
                            config = {
                                'title': '',
                                'x_column': 'sector',
                                'y_column': 'tasa_absentismo'
                            }
                            viz = get_visualization(
                                viz_name,
                                sample_data['categorical'],
                                config,
                                viz_id=f"gallery_{viz_name}_cat"
                            )
                            if viz:
                                chart = viz.render()
                                container.render_visualization(chart, viz.get_library())
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab3:
        st.header("Visualizaciones Geográficas y Especiales")
        
        # Aquí irían mapas, heatmaps, etc.
        st.info("Próximamente: Mapas de España, Heatmaps de correlación, etc.")
    
    # Sección de información del registry
    with st.expander("📋 Visualizaciones Registradas", expanded=False):
        st.subheader("Registry actual:")
        
        for name, viz_class in registry.items():
            st.write(f"- **{name}**: `{viz_class.__name__ if hasattr(viz_class, '__name__') else str(viz_class)}`")
        
        st.markdown("---")
        st.caption(f"Total de visualizaciones registradas: {len(registry)}")
    
    # Sección de estado de los containers
    with st.expander("🔧 Debug: Estado de Session State", expanded=False):
        viz_states = {k: v for k, v in st.session_state.items() if k.startswith("viz:")}
        if viz_states:
            st.json(viz_states)
        else:
            st.info("No hay estados de visualización almacenados")

def main():
    """Función principal de la página"""
    
    # Sidebar con información
    with st.sidebar:
        st.header("📖 Guía de Uso")
        st.markdown("""
        ### Propósito
        Esta galería permite:
        - ✅ Verificar consistencia visual
        - ✅ Probar todas las visualizaciones
        - ✅ QA de diseño y tokens
        - ✅ Debug de estado namespaced
        
        ### Cómo usar
        1. Las visualizaciones se agrupan por tipo
        2. Cada una muestra datos de ejemplo
        3. Los controles son funcionales
        4. El footer muestra la librería usada
        
        ### Añadir nueva viz
        1. Crear clase heredando de `BaseVisualization`
        2. Registrar en `registry.py`
        3. Aparecerá automáticamente aquí
        """)
        
        st.markdown("---")
        
        if st.button("🔄 Recargar Galería"):
            st.rerun()
    
    # Renderizar galería
    render_gallery()

if __name__ == "__main__":
    main()