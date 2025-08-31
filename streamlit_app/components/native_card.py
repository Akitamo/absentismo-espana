"""
Card component usando contenedores nativos de Streamlit
Solución limpia sin hacks HTML, 100% compatible con Streamlit
"""

import streamlit as st
from contextlib import contextmanager
from typing import Optional

@contextmanager
def card(title: Optional[str] = None, subtitle: Optional[str] = None):
    """
    Crea un card usando st.container(border=True) nativo de Streamlit.
    Esta es la forma correcta y estable de crear cards en Streamlit.
    
    Args:
        title: Título principal del card
        subtitle: Subtítulo o descripción
    
    Yields:
        Contexto del container para añadir contenido
    
    Ejemplo:
        with card("Mi Título", "Mi subtítulo"):
            st.plotly_chart(fig)
    """
    
    # Crear container nativo con borde (Streamlit >= 1.30)
    container = st.container(border=True)
    
    with container:
        # Header del card si hay título o subtítulo
        if title or subtitle:
            # Título
            if title:
                st.markdown(f"### {title}")
            
            # Subtítulo
            if subtitle:
                st.caption(subtitle)
            
            # Separador visual opcional
            if title or subtitle:
                st.markdown("")  # Espacio
        
        # Yield para el contenido del card
        yield


def card_header(title: str, subtitle: Optional[str] = None):
    """
    Helper para crear un header consistente en cards.
    
    Args:
        title: Título principal
        subtitle: Subtítulo opcional
    """
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def card_footer(text: Optional[str] = None, meta: Optional[dict] = None):
    """
    Helper para crear un footer consistente en cards.
    
    Args:
        text: Texto simple para el footer
        meta: Diccionario con metadatos para mostrar
    """
    if text or meta:
        st.markdown("---")
        
        if text:
            st.caption(text)
        
        if meta:
            cols = st.columns(len(meta))
            for i, (key, value) in enumerate(meta.items()):
                with cols[i]:
                    st.caption(f"**{key}:** {value}")


def skeleton_loader(lines: int = 3, height: int = 12):
    """
    Muestra un skeleton loader mientras se cargan los datos.
    Útil para mejorar la percepción de velocidad.
    
    Args:
        lines: Número de líneas del skeleton
        height: Altura de cada línea en píxeles
    """
    for i in range(lines):
        # Variar el ancho para parecer texto real
        width = 100 if i == 0 else (80 - i * 10)
        st.markdown(
            f'<div style="'
            f'height:{height}px;'
            f'width:{width}%;'
            f'background:linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);'
            f'background-size:200% 100%;'
            f'animation:loading 1.5s infinite;'
            f'border-radius:4px;'
            f'margin:8px 0;'
            f'"></div>',
            unsafe_allow_html=True
        )
    
    # CSS para la animación (se inyecta una vez)
    st.markdown("""
        <style>
            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
        </style>
    """, unsafe_allow_html=True)