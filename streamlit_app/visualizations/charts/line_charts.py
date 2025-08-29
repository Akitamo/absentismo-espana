"""
Visualizaciones de líneas con diferentes librerías
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, Dict
from ..base import BaseVisualization

class AbsentismoTemporalPlotly(BaseVisualization):
    """
    Gráfico de línea temporal para mostrar evolución del absentismo.
    Usa Plotly para interactividad.
    """
    
    def get_library(self) -> str:
        return 'plotly'
    
    def render(self):
        """Genera el gráfico de línea con Plotly"""
        
        # Asegurar que tenemos un DataFrame
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Los datos deben ser un DataFrame de pandas")
        
        # Configuración desde tokens
        colors = self.tokens.get('colors', {})
        
        # Crear figura
        fig = go.Figure()
        
        # Agregar línea principal
        fig.add_trace(go.Scatter(
            x=self.data.index if self.data.index.name else self.data.iloc[:, 0],
            y=self.data.iloc[:, -1],  # Última columna como valores
            mode='lines+markers',
            name='Tasa de Absentismo',
            line=dict(
                color=colors.get('primary', '#1B59F8'),
                width=3
            ),
            marker=dict(
                size=6,
                color=colors.get('primary', '#1B59F8'),
                line=dict(
                    color='white',
                    width=2
                )
            ),
            hovertemplate='<b>%{x}</b><br>Tasa: %{y:.1f}%<extra></extra>'
        ))
        
        # Actualizar layout con diseño desde tokens
        fig.update_layout(
            title=self.config.get('title', 'Evolución Temporal del Absentismo'),
            xaxis=dict(
                title='Periodo',
                showgrid=True,
                gridcolor=colors.get('border', '#EFF0F6'),
                zeroline=False
            ),
            yaxis=dict(
                title='Tasa de Absentismo (%)',
                showgrid=True,
                gridcolor=colors.get('border', '#EFF0F6'),
                zeroline=False
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(
                family=self.tokens.get('typography', {}).get('fontFamily', 'Inter'),
                color=colors.get('text', {}).get('primary', '#000000')
            ),
            hovermode='x unified',
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0),
            height=self.get_height()
        )
        
        return fig
    
    def validate_data(self) -> bool:
        """Valida que los datos sean apropiados para un gráfico temporal"""
        if not isinstance(self.data, pd.DataFrame):
            return False
        if self.data.empty:
            return False
        return True


class AbsentismoComparativoPlotly(BaseVisualization):
    """
    Gráfico de líneas múltiples para comparar diferentes series.
    Por ejemplo: comparar absentismo entre diferentes CCAA.
    """
    
    def get_library(self) -> str:
        return 'plotly'
    
    def render(self):
        """Genera gráfico de líneas múltiples"""
        
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Los datos deben ser un DataFrame de pandas")
        
        colors = self.tokens.get('colors', {})
        
        # Paleta de colores para múltiples líneas
        color_palette = [
            colors.get('primary', '#1B59F8'),
            colors.get('status', {}).get('success', '#1FE08F'),
            colors.get('status', {}).get('warning', '#FFA500'),
            colors.get('status', {}).get('danger', '#FF3E13'),
            colors.get('chart', {}).get('gray', '#808080')
        ]
        
        fig = go.Figure()
        
        # Agregar una línea por cada columna (excepto la primera si es el índice)
        for i, col in enumerate(self.data.columns):
            if i < len(color_palette):
                color = color_palette[i]
            else:
                color = f'hsl({i * 30}, 70%, 50%)'  # Generar colores adicionales
            
            fig.add_trace(go.Scatter(
                x=self.data.index,
                y=self.data[col],
                mode='lines',
                name=col,
                line=dict(color=color, width=2),
                hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>'
            ))
        
        # Layout
        fig.update_layout(
            title=self.config.get('title', 'Comparativa de Absentismo'),
            xaxis=dict(
                title='Periodo',
                showgrid=True,
                gridcolor=colors.get('border', '#EFF0F6')
            ),
            yaxis=dict(
                title='Tasa de Absentismo (%)',
                showgrid=True,
                gridcolor=colors.get('border', '#EFF0F6')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(
                family=self.tokens.get('typography', {}).get('fontFamily', 'Inter'),
                color=colors.get('text', {}).get('primary', '#000000')
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=0, r=0, t=40, b=60),
            height=self.get_height()
        )
        
        return fig