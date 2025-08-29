"""
Contenedor estándar para visualizaciones
Aplica el diseño consistente definido en el sistema de diseño
"""

import streamlit as st
from typing import Dict, Any, Optional

def render_chart_container(
    visualization: Any,
    container_config: Optional[Dict] = None
) -> None:
    """
    Renderiza una visualización en un contenedor con diseño estándar.
    
    Args:
        visualization: Instancia de BaseVisualization o dict desde to_container()
        container_config: Configuración adicional del contenedor
    """
    
    config = container_config or {}
    
    # Si es una instancia de BaseVisualization, convertir a dict
    if hasattr(visualization, 'to_container'):
        viz_data = visualization.to_container()
    else:
        viz_data = visualization
    
    # Extraer información
    chart = viz_data.get('chart')
    library = viz_data.get('library', 'unknown')
    title = viz_data.get('title', '')
    height = viz_data.get('height', 400)
    
    # Crear contenedor con estilo
    with st.container():
        # Aplicar CSS del contenedor
        st.markdown("""
            <style>
                .chart-container {
                    background: var(--color-surface);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-lg);
                    box-shadow: var(--shadow-md);
                    margin-bottom: var(--spacing-lg);
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Título si existe
        if title:
            st.markdown(f"""
                <h3 style='
                    color: var(--text-primary);
                    font-size: var(--font-size-lg);
                    font-weight: var(--font-weight-semibold);
                    margin-bottom: var(--spacing-md);
                '>
                    {title}
                </h3>
            """, unsafe_allow_html=True)
        
        # Renderizar según la librería
        if library == 'plotly':
            st.plotly_chart(
                chart,
                use_container_width=True,
                config={
                    'displayModeBar': False,  # Ocultar toolbar para diseño limpio
                    'staticPlot': False,       # Mantener interactividad
                }
            )
        
        elif library == 'altair':
            st.altair_chart(chart, use_container_width=True)
        
        elif library == 'matplotlib':
            st.pyplot(chart)
        
        elif library == 'dataframe':
            st.dataframe(chart, use_container_width=True, height=height)
        
        else:
            st.error(f"Librería '{library}' no soportada en el contenedor")


def render_chart_grid(visualizations: list, columns: int = 2) -> None:
    """
    Renderiza múltiples visualizaciones en una grilla.
    
    Args:
        visualizations: Lista de visualizaciones
        columns: Número de columnas en la grilla
    """
    
    cols = st.columns(columns)
    
    for i, viz in enumerate(visualizations):
        with cols[i % columns]:
            render_chart_container(viz)