"""
Ejemplo de visualización usando la nueva arquitectura
Demuestra el uso completo de tokens, slots y namespacing
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, Any
from ..base import BaseVisualization

class ExampleTimeSeriesChart(BaseVisualization):
    """
    Gráfico de serie temporal de ejemplo con controles interactivos.
    Demuestra el uso completo de la nueva arquitectura.
    """
    
    def __init__(self, data: pd.DataFrame, config: Optional[Dict] = None, viz_id: str = None):
        """
        Inicializa el gráfico de serie temporal.
        
        Args:
            data: DataFrame con columnas de fecha y valores
            config: Configuración del gráfico
            viz_id: ID único para namespacing
        """
        super().__init__(data, config, viz_id)
        
        # Configuración por defecto
        self.default_config = {
            'title': 'Serie Temporal',
            'x_column': 'fecha',
            'y_column': 'valor',
            'color': None,  # Usará token por defecto
            'show_markers': True,
            'show_trend': False
        }
        
        # Merge con config del usuario
        self.config = {**self.default_config, **self.config}
    
    def render(self) -> go.Figure:
        """
        Renderiza el gráfico de serie temporal usando tokens.
        
        Returns:
            Figura de Plotly
        """
        # Obtener configuración del estado o usar defaults
        show_markers = self.get_state('show_markers', self.config['show_markers'])
        show_trend = self.get_state('show_trend', self.config['show_trend'])
        
        # Color desde tokens si no se especifica
        line_color = self.config['color'] or self.tokens['colors']['primary']
        
        # Crear figura
        fig = go.Figure()
        
        # Línea principal
        fig.add_trace(go.Scatter(
            x=self.data[self.config['x_column']],
            y=self.data[self.config['y_column']],
            mode='lines+markers' if show_markers else 'lines',
            name=self.config['y_column'],
            line=dict(
                color=line_color,
                width=2
            ),
            marker=dict(
                size=6,
                color=line_color,
                line=dict(color='white', width=1)
            ) if show_markers else None,
            hovertemplate='<b>%{x}</b><br>Valor: %{y:.2f}<extra></extra>'
        ))
        
        # Añadir línea de tendencia si está activada
        if show_trend and len(self.data) > 1:
            from scipy import stats
            import numpy as np
            
            # Calcular tendencia lineal
            x_numeric = range(len(self.data))
            slope, intercept, _, _, _ = stats.linregress(
                x_numeric, 
                self.data[self.config['y_column']]
            )
            trend_line = [slope * x + intercept for x in x_numeric]
            
            fig.add_trace(go.Scatter(
                x=self.data[self.config['x_column']],
                y=trend_line,
                mode='lines',
                name='Tendencia',
                line=dict(
                    color=self.tokens['colors']['text']['muted'],
                    width=1,
                    dash='dash'
                ),
                hoverinfo='skip'
            ))
        
        # Aplicar layout con tokens
        fig.update_layout(
            title=None,  # El título va en el header del container
            font=dict(
                family=self.tokens['typography']['fontFamily'].replace("'", ""),
                size=int(self.tokens['typography']['fontSize']['sm'].replace('rem', '')) * 16
            ),
            plot_bgcolor='white',
            paper_bgcolor='transparent',
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(
                gridcolor=self.tokens['colors']['border_light'],
                linecolor=self.tokens['colors']['border'],
                tickfont=dict(
                    color=self.tokens['colors']['text']['secondary']
                )
            ),
            yaxis=dict(
                gridcolor=self.tokens['colors']['border_light'],
                linecolor=self.tokens['colors']['border'],
                tickfont=dict(
                    color=self.tokens['colors']['text']['secondary']
                )
            ),
            hovermode='x unified',
            showlegend=show_trend,  # Solo mostrar leyenda si hay tendencia
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(
                    size=int(self.tokens['typography']['fontSize']['xs'].replace('rem', '')) * 16,
                    color=self.tokens['colors']['text']['secondary']
                )
            )
        )
        
        return fig
    
    def get_library(self) -> str:
        """Retorna la librería utilizada"""
        return 'plotly'
    
    def get_default_controls(self) -> Dict[str, Any]:
        """
        Define los controles por defecto para esta visualización.
        
        Returns:
            Diccionario con la configuración de controles
        """
        return {
            'show_markers': {
                'type': 'checkbox',
                'label': 'Mostrar puntos',
                'default': True
            },
            'show_trend': {
                'type': 'checkbox', 
                'label': 'Línea de tendencia',
                'default': False
            },
            'y_column': {
                'type': 'selectbox',
                'label': 'Métrica',
                'options': list(self.data.columns),
                'default': self.config['y_column']
            }
        }


class ExampleBarChart(BaseVisualization):
    """
    Gráfico de barras de ejemplo usando tokens y namespacing.
    """
    
    def __init__(self, data: pd.DataFrame, config: Optional[Dict] = None, viz_id: str = None):
        super().__init__(data, config, viz_id)
        
        self.default_config = {
            'title': 'Gráfico de Barras',
            'x_column': 'categoria',
            'y_column': 'valor',
            'orientation': 'vertical',
            'color_scheme': 'primary'
        }
        
        self.config = {**self.default_config, **self.config}
    
    def render(self) -> go.Figure:
        """Renderiza el gráfico de barras"""
        
        # Determinar orientación
        orientation = self.get_state('orientation', self.config['orientation'])
        
        # Seleccionar colores según esquema
        color_scheme = self.get_state('color_scheme', self.config['color_scheme'])
        colors = self._get_color_palette(color_scheme)
        
        # Crear figura
        fig = go.Figure()
        
        # Añadir barras
        if orientation == 'vertical':
            fig.add_trace(go.Bar(
                x=self.data[self.config['x_column']],
                y=self.data[self.config['y_column']],
                marker_color=colors,
                text=self.data[self.config['y_column']],
                textposition='outside',
                textfont=dict(
                    size=int(self.tokens['typography']['fontSize']['xs'].replace('rem', '')) * 16,
                    color=self.tokens['colors']['text']['secondary']
                ),
                hovertemplate='<b>%{x}</b><br>%{y:.1f}<extra></extra>'
            ))
        else:
            fig.add_trace(go.Bar(
                x=self.data[self.config['y_column']],
                y=self.data[self.config['x_column']],
                orientation='h',
                marker_color=colors,
                text=self.data[self.config['y_column']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>%{x:.1f}<extra></extra>'
            ))
        
        # Aplicar layout con tokens
        fig.update_layout(
            font=dict(
                family=self.tokens['typography']['fontFamily'].replace("'", ""),
            ),
            plot_bgcolor='white',
            paper_bgcolor='transparent',
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(
                gridcolor=self.tokens['colors']['border_light'],
                linecolor=self.tokens['colors']['border'],
            ),
            yaxis=dict(
                gridcolor=self.tokens['colors']['border_light'], 
                linecolor=self.tokens['colors']['border'],
            ),
            showlegend=False,
            hovermode='closest'
        )
        
        return fig
    
    def _get_color_palette(self, scheme: str) -> list:
        """Obtiene paleta de colores desde tokens"""
        if scheme == 'primary':
            return self.tokens['colors']['primary']
        elif scheme == 'success':
            return self.tokens['colors']['status']['success']
        elif scheme == 'danger':
            return self.tokens['colors']['status']['danger']
        elif scheme == 'gradient':
            # Crear gradiente entre primary y success
            n = len(self.data)
            return [self.tokens['colors']['primary']] * n
        else:
            return self.tokens['colors']['chart']['primary']
    
    def get_library(self) -> str:
        return 'plotly'


# Registrar las visualizaciones de ejemplo
from ..registry import register_visualization

register_visualization('example_time_series', ExampleTimeSeriesChart)
register_visualization('example_bar_chart', ExampleBarChart)