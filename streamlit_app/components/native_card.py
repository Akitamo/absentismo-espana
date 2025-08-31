"""
Card component usando contenedores nativos de Streamlit
Solución limpia sin hacks HTML, 100% compatible con Streamlit
"""

import streamlit as st
from contextlib import contextmanager
from typing import Optional

@contextmanager
def card(title: str | None = None, subtitle: str | None = None):
    """
    Crea un card usando st.container(border=True) nativo de Streamlit.
    
    Args:
        title: Título principal del card
        subtitle: Subtítulo o descripción
    
    Yields:
        Contexto del container para añadir contenido
    """
    c = st.container(border=True)  # nativo
    with c:
        if title: 
            st.markdown(f"### {title}")
        if subtitle: 
            st.caption(subtitle)
        yield