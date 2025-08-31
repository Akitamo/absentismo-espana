"""
Componente Card con estilo Tesla Analytics
Contenedor reutilizable para todas las visualizaciones
"""

import streamlit as st
from typing import Optional
from contextlib import contextmanager

class TeslaCard:
    """
    Card contenedor con el estilo exacto del template Tesla.
    Fondo blanco, sombra sutil, bordes redondeados.
    """
    
    def __init__(
        self, 
        title: str = None,
        subtitle: str = None,
        show_divider: bool = False,
        height: Optional[int] = None,
        padding: str = "24px"
    ):
        """
        Inicializa el Tesla Card.
        
        Args:
            title: Título principal del card
            subtitle: Subtítulo opcional
            show_divider: Si mostrar línea divisora bajo el título
            height: Altura fija opcional en píxeles
            padding: Padding interno del card
        """
        self.title = title
        self.subtitle = subtitle
        self.show_divider = show_divider
        self.height = height
        self.padding = padding
        self.card_id = f"tesla_card_{id(self)}"
        
    @contextmanager
    def render(self):
        """
        Context manager para renderizar el contenido dentro del card.
        
        Uso:
            card = TeslaCard("Mi Título")
            with card.render():
                st.plotly_chart(fig)
        """
        # Aplicar estilos del card
        self._apply_styles()
        
        # Marcador invisible para identificar este card
        st.markdown(f'<div class="tesla-card-marker-{self.card_id}" style="display:none"></div>', unsafe_allow_html=True)
        
        # Crear container con estilo de card
        container = st.container()
        with container:
            # Renderizar header si hay título
            if self.title or self.subtitle:
                self._render_header()
            
            # Container para el contenido con padding
            content_container = st.container()
            with content_container:
                yield
    
    def _apply_styles(self):
        """Aplica los estilos CSS del card estilo Tesla"""
        height_style = f"min-height: {self.height}px;" if self.height else ""
        
        css = f"""
        <style>
            /* Aplicar estilo de card a los containers de esta sección */
            [data-testid="column"] > div:has(.tesla-card-marker-{self.card_id}) {{
                background: #FFFFFF;
                border-radius: 20px;
                padding: {self.padding};
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.05);
                margin-bottom: 24px;
                {height_style}
            }}
            
            /* Contenedor principal del card */
            .element-container:has(.tesla-card-marker-{self.card_id}) + .element-container {{
                background: #FFFFFF;
                border-radius: 20px;
                padding: {self.padding};
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.05);
            }}
            
            /* Header del card */
            .tesla-card-header {{
                margin-bottom: 20px;
            }}
            
            .tesla-card-title {{
                color: #000000;
                font-size: 18px;
                font-weight: 600;
                margin: 0;
                line-height: 1.4;
            }}
            
            .tesla-card-subtitle {{
                color: #696974;
                font-size: 14px;
                font-weight: 400;
                margin-top: 4px;
            }}
            
            /* Divider */
            .tesla-card-divider {{
                border: none;
                border-top: 1px solid #EFF0F6;
                margin: 16px 0;
            }}
            
            /* Contenido del card */
            .tesla-card-content {{
                width: 100%;
            }}
            
            /* Ajustar gráficos dentro del card */
            .tesla-card-{self.card_id} .js-plotly-plot {{
                border-radius: 8px;
                overflow: hidden;
            }}
            
            /* Quitar márgenes de elementos Streamlit dentro del card */
            .tesla-card-{self.card_id} > div > div {{
                margin-bottom: 0 !important;
            }}
            
            .tesla-card-{self.card_id} .stPlotlyChart {{
                margin: 0 !important;
                padding: 0 !important;
            }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def _render_header(self):
        """Renderiza el header del card con título y subtítulo"""
        header_html = '<div class="tesla-card-header">'
        
        if self.title:
            header_html += f'<h3 class="tesla-card-title">{self.title}</h3>'
        
        if self.subtitle:
            header_html += f'<p class="tesla-card-subtitle">{self.subtitle}</p>'
        
        header_html += '</div>'
        
        if self.show_divider:
            header_html += '<hr class="tesla-card-divider">'
        
        st.markdown(header_html, unsafe_allow_html=True)


def render_tesla_card(
    content_func,
    title: str = None,
    subtitle: str = None,
    **kwargs
):
    """
    Función helper para renderizar contenido en un Tesla Card.
    
    Args:
        content_func: Función que genera el contenido
        title: Título del card
        subtitle: Subtítulo opcional
        **kwargs: Argumentos adicionales para TeslaCard
    
    Ejemplo:
        def mi_grafico():
            st.plotly_chart(fig)
        
        render_tesla_card(mi_grafico, title="Mi Gráfico")
    """
    card = TeslaCard(title=title, subtitle=subtitle, **kwargs)
    with card.render():
        content_func()