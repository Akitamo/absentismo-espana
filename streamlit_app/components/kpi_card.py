"""
Componente KPI Card
"""

import streamlit as st
from typing import Optional

def render_kpi_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None
):
    """
    Renderiza una tarjeta KPI estilizada
    
    Args:
        title: Título del KPI
        value: Valor principal a mostrar
        delta: Cambio o delta (opcional)
        delta_color: Color del delta ("normal", "inverse", "off")
        help_text: Texto de ayuda (opcional)
    """
    
    # Usar el componente metric nativo de Streamlit
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )