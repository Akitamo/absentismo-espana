"""
Componentes de gráficos
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from pathlib import Path

def load_chart_theme():
    """Carga el tema de gráficos desde los tokens"""
    tokens_path = Path(__file__).parent.parent / "design" / "tokens.json"
    with open(tokens_path, 'r') as f:
        tokens = json.load(f)
    return tokens

def render_evolution_chart(data: pd.DataFrame):
    """
    Renderiza un gráfico de evolución temporal
    
    Args:
        data: DataFrame con columnas 'periodo' y 'tasa_absentismo'
    """
    
    if data.empty:
        st.info("No hay datos para mostrar")
        return
    
    # Cargar tema
    tokens = load_chart_theme()
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir línea de tasa de absentismo
    fig.add_trace(go.Scatter(
        x=data['periodo'],
        y=data['tasa_absentismo'],
        mode='lines+markers',
        name='Tasa de Absentismo',
        line=dict(
            color=tokens['colors']['primary'],
            width=3
        ),
        marker=dict(
            size=8,
            color=tokens['colors']['primary']
        ),
        hovertemplate='<b>%{x}</b><br>Tasa: %{y:.1f}%<extra></extra>'
    ))
    
    # Configurar layout
    fig.update_layout(
        title=None,
        xaxis=dict(
            title=None,
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        yaxis=dict(
            title='Tasa de Absentismo (%)',
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="'Inter', sans-serif",
            color=tokens['colors']['text']['primary']
        ),
        margin=dict(l=0, r=0, t=20, b=0),
        height=400,
        hovermode='x unified',
        showlegend=False
    )
    
    # Mostrar gráfico
    st.plotly_chart(fig, use_container_width=True)