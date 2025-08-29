"""
Clase base para todas las visualizaciones
Define la interfaz común y funcionalidad compartida
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
from pathlib import Path

class BaseVisualization(ABC):
    """
    Clase base abstracta para todas las visualizaciones.
    Toda visualización debe heredar de esta clase.
    """
    
    def __init__(self, data: Any, config: Optional[Dict] = None):
        """
        Inicializa la visualización.
        
        Args:
            data: Datos para la visualización (DataFrame, dict, list, etc.)
            config: Configuración opcional específica de la visualización
        """
        self.data = data
        self.config = config or {}
        self.tokens = self._load_tokens()
        self.theme = self._get_theme()
    
    def _load_tokens(self) -> Dict:
        """Carga los design tokens desde el archivo JSON"""
        tokens_path = Path(__file__).parent.parent / "design" / "tokens.json"
        try:
            with open(tokens_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: tokens.json not found at {tokens_path}")
            return {}
    
    def _get_theme(self) -> Dict:
        """Obtiene el tema basado en los tokens para la librería específica"""
        return {
            'colors': self.tokens.get('colors', {}),
            'typography': self.tokens.get('typography', {}),
            'spacing': self.tokens.get('spacing', {}),
            'borders': self.tokens.get('borders', {})
        }
    
    @abstractmethod
    def render(self) -> Any:
        """
        Genera y retorna la visualización.
        Debe ser implementado por cada visualización específica.
        
        Returns:
            El objeto de visualización (plotly.Figure, altair.Chart, matplotlib.Figure, etc.)
        """
        pass
    
    @abstractmethod
    def get_library(self) -> str:
        """
        Retorna el nombre de la librería utilizada.
        
        Returns:
            String con el nombre: 'plotly', 'altair', 'matplotlib', 'echarts', etc.
        """
        pass
    
    def get_height(self) -> int:
        """
        Retorna la altura recomendada para la visualización.
        Puede ser sobrescrito por visualizaciones específicas.
        
        Returns:
            Altura en píxeles
        """
        return self.config.get('height', 400)
    
    def get_title(self) -> str:
        """
        Retorna el título de la visualización.
        
        Returns:
            String con el título o None
        """
        return self.config.get('title', '')
    
    def to_container(self) -> Dict:
        """
        Empaqueta la visualización para el contenedor estándar.
        
        Returns:
            Diccionario con toda la información necesaria para renderizar
        """
        return {
            'chart': self.render(),
            'library': self.get_library(),
            'height': self.get_height(),
            'title': self.get_title(),
            'config': self.config
        }
    
    def validate_data(self) -> bool:
        """
        Valida que los datos sean apropiados para la visualización.
        Puede ser sobrescrito por visualizaciones específicas.
        
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        return self.data is not None