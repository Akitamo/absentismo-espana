"""
Simple Card Component con enfoque Streamlit puro
"""

import streamlit as st
from typing import Optional

from contextlib import contextmanager

@contextmanager
def card(title: str = None, subtitle: str = None):
    """
    Crea un card simple con estilo Tesla usando markdown y CSS.
    
    Args:
        title: Título del card
        subtitle: Subtítulo opcional
    
    Yields:
        Contexto para añadir contenido al card
    """
    
    # CSS para el card
    st.markdown("""
        <style>
            .tesla-card {
                background: white;
                padding: 24px;
                border-radius: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.05);
                margin-bottom: 20px;
            }
            .tesla-card-title {
                font-size: 18px;
                font-weight: 600;
                color: #000;
                margin-bottom: 4px;
            }
            .tesla-card-subtitle {
                font-size: 14px;
                color: #696974;
                margin-bottom: 20px;
            }
            .tesla-divider {
                border-top: 1px solid #EFF0F6;
                margin: 16px 0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Crear el card
    st.markdown('<div class="tesla-card">', unsafe_allow_html=True)
    
    # Header
    if title:
        st.markdown(f'<div class="tesla-card-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="tesla-card-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    if title or subtitle:
        st.markdown('<div class="tesla-divider"></div>', unsafe_allow_html=True)
    
    # Yield para el contenido
    yield
    
    # Cerrar el card
    st.markdown('</div>', unsafe_allow_html=True)