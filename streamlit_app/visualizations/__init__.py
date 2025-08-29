"""
Sistema modular de visualizaciones para el Dashboard de Absentismo
Permite crear visualizaciones independientes con diferentes librerías
"""

from .base import BaseVisualization
from .registry import get_visualization, register_visualization, VISUALIZATIONS

__all__ = [
    'BaseVisualization',
    'get_visualization',
    'register_visualization',
    'VISUALIZATIONS'
]