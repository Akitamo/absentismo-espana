"""
Container estándar para visualizaciones con arquitectura tokens-first
Sistema de slots para estructura consistente
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
import json
from pathlib import Path

class ChartContainer:
    """
    Container con slots para visualizaciones.
    100% tokens-first, sin estilos inline.
    """
    
    def __init__(self, viz_id: str, config: Optional[Dict] = None):
        """
        Inicializa el container.
        
        Args:
            viz_id: Identificador único de la visualización
            config: Configuración opcional del container
        """
        self.viz_id = viz_id
        self.config = config or {}
        self._apply_container_styles()
        
    def _apply_container_styles(self):
        """Aplica estilos del container usando solo clases CSS y tokens"""
        # Determinar si aplicar margen inferior
        no_margin = self.config.get('no_margin', False)
        margin_style = "0" if no_margin else "var(--spacing-lg)"
        
        css = """
        <style>
            /* Container principal */
            .chart-container-""" + self.viz_id + """ {
                background: var(--color-surface);
                border-radius: var(--radius-xl);
                padding: 0;
                box-shadow: var(--shadow-md);
                margin-bottom: """ + margin_style + """;
                overflow: hidden;
            }
            
            /* Slots del container */
            .chart-header {
                padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-sm);
                border-bottom: 1px solid var(--color-border-light);
            }
            
            .chart-header-title {
                color: var(--text-primary);
                font-size: var(--font-size-lg);
                font-weight: var(--font-weight-semibold);
                margin: 0;
            }
            
            .chart-header-subtitle {
                color: var(--text-secondary);
                font-size: var(--font-size-sm);
                margin-top: var(--spacing-xs);
            }
            
            .chart-controls {
                padding: var(--spacing-sm) var(--spacing-lg);
                background: var(--color-background);
                border-bottom: 1px solid var(--color-border-light);
                display: flex;
                gap: var(--spacing-md);
                flex-wrap: wrap;
                align-items: center;
            }
            
            .chart-body {
                padding: var(--spacing-lg);
                min-height: 300px;
                position: relative;
            }
            
            .chart-footer {
                padding: var(--spacing-sm) var(--spacing-lg);
                background: var(--color-background);
                border-top: 1px solid var(--color-border-light);
                font-size: var(--font-size-xs);
                color: var(--text-muted);
            }
            
            /* Estados especiales */
            .chart-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 300px;
                color: var(--text-secondary);
            }
            
            .chart-loading-skeleton {
                width: 100%;
                height: 300px;
                background: linear-gradient(
                    90deg,
                    var(--color-background) 25%,
                    var(--color-border-light) 50%,
                    var(--color-background) 75%
                );
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
            }
            
            @keyframes loading {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}
            
            .chart-error {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 300px;
                color: var(--text-secondary);
                padding: var(--spacing-xl);
                text-align: center;
            }
            
            .chart-error-icon {
                font-size: 3rem;
                margin-bottom: var(--spacing-md);
                opacity: 0.3;
            }
            
            .chart-error-message {
                font-size: var(--font-size-sm);
                color: var(--text-muted);
                max-width: 400px;
            }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    @contextmanager
    def header(self, title: str = None, subtitle: str = None):
        """
        Slot para el header del chart.
        
        Args:
            title: Título principal
            subtitle: Subtítulo opcional
        """
        with st.container():
            if title or subtitle:
                header_html = '<div class="chart-header">'
                if title:
                    header_html += f'<h3 class="chart-header-title">{title}</h3>'
                if subtitle:
                    header_html += f'<p class="chart-header-subtitle">{subtitle}</p>'
                header_html += '</div>'
                st.markdown(header_html, unsafe_allow_html=True)
            yield
    
    @contextmanager
    def controls(self):
        """Slot para controles y filtros del chart"""
        with st.container():
            st.markdown('<div class="chart-controls">', unsafe_allow_html=True)
            # Los controles se añaden dentro del contexto
            cols = st.columns([1])  # Container para los controles
            with cols[0]:
                yield
            st.markdown('</div>', unsafe_allow_html=True)
    
    @contextmanager
    def body(self):
        """Slot para el contenido principal del chart"""
        # Sin divs extra para no romper layout de columnas
        yield
    
    @contextmanager
    def footer(self, text: str = None):
        """
        Slot para el footer del chart.
        
        Args:
            text: Texto opcional para el footer
        """
        with st.container():
            if text:
                st.markdown(f'<div class="chart-footer">{text}</div>', unsafe_allow_html=True)
            else:
                yield
    
    def loading(self, message: str = "Cargando visualización..."):
        """Muestra estado de carga con skeleton"""
        st.markdown(f'''
            <div class="chart-loading">
                <div class="chart-loading-skeleton"></div>
            </div>
        ''', unsafe_allow_html=True)
    
    def error(self, message: str = "Error al cargar la visualización"):
        """
        Muestra estado de error.
        
        Args:
            message: Mensaje de error a mostrar
        """
        st.markdown(f'''
            <div class="chart-error">
                <div class="chart-error-icon">⚠️</div>
                <div class="chart-error-message">{message}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    def render_visualization(self, viz_object: Any, library: str = 'plotly'):
        """
        Renderiza la visualización según su librería.
        
        Args:
            viz_object: Objeto de visualización (Figure, Chart, etc.)
            library: Librería utilizada
        """
        if library == 'plotly':
            st.plotly_chart(
                viz_object,
                use_container_width=True,
                config={
                    'displayModeBar': False,
                    'staticPlot': False,
                }
            )
        elif library == 'altair':
            st.altair_chart(viz_object, use_container_width=True)
        elif library == 'matplotlib':
            st.pyplot(viz_object)
        elif library == 'dataframe':
            st.dataframe(viz_object, use_container_width=True)
        else:
            self.error(f"Librería '{library}' no soportada")


def render_chart_container(
    visualization: Any,
    viz_id: str = None,
    container_config: Optional[Dict] = None
) -> ChartContainer:
    """
    Renderiza una visualización en un container con diseño estándar.
    Versión retrocompatible con la API anterior.
    
    Args:
        visualization: Instancia de BaseVisualization o dict desde to_container()
        viz_id: ID único para la visualización (para namespacing)
        container_config: Configuración adicional del container
        
    Returns:
        ChartContainer: Instancia del container para uso avanzado
    """
    
    # Generar ID si no se proporciona
    if not viz_id:
        viz_id = f"viz_{id(visualization)}"
    
    # Crear container
    container = ChartContainer(viz_id, container_config)
    
    # Si es una instancia de BaseVisualization, convertir a dict
    if hasattr(visualization, 'to_container'):
        viz_data = visualization.to_container()
    else:
        viz_data = visualization
    
    # Extraer información
    chart = viz_data.get('chart')
    library = viz_data.get('library', 'unknown')
    title = viz_data.get('title', '')
    
    # Renderizar con slots - sin div wrapper para respetar columnas
    # Header si hay título
    if title:
        with container.header(title):
            pass
    
    # Body con la visualización
    with container.body():
        try:
            container.render_visualization(chart, library)
        except Exception as e:
            container.error(f"Error: {str(e)}")
    
    return container


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
            viz_id = f"grid_viz_{i}"
            render_chart_container(viz, viz_id)