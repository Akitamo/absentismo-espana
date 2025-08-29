"""
Registro central de visualizaciones disponibles
Permite registrar y obtener visualizaciones por nombre
"""

from typing import Dict, Type, Optional, Any
from .base import BaseVisualization

# Registro global de visualizaciones
VISUALIZATIONS: Dict[str, Type[BaseVisualization]] = {}

def register_visualization(name: str, visualization_class: Type[BaseVisualization]):
    """
    Registra una nueva visualización en el sistema.
    
    Args:
        name: Nombre único para identificar la visualización
        visualization_class: Clase que hereda de BaseVisualization
    """
    if not issubclass(visualization_class, BaseVisualization):
        raise ValueError(f"{visualization_class} debe heredar de BaseVisualization")
    
    VISUALIZATIONS[name] = visualization_class
    print(f"Visualización '{name}' registrada exitosamente")

def get_visualization(name: str, data: Any, config: Optional[Dict] = None) -> BaseVisualization:
    """
    Obtiene una instancia de visualización por nombre.
    
    Args:
        name: Nombre de la visualización registrada
        data: Datos para la visualización
        config: Configuración opcional
        
    Returns:
        Instancia de la visualización solicitada
        
    Raises:
        KeyError: Si la visualización no está registrada
    """
    if name not in VISUALIZATIONS:
        available = ', '.join(VISUALIZATIONS.keys())
        raise KeyError(f"Visualización '{name}' no encontrada. Disponibles: {available}")
    
    visualization_class = VISUALIZATIONS[name]
    return visualization_class(data=data, config=config)

def list_visualizations() -> list:
    """
    Lista todas las visualizaciones registradas.
    
    Returns:
        Lista de nombres de visualizaciones disponibles
    """
    return list(VISUALIZATIONS.keys())

# Auto-registro de visualizaciones incluidas
def auto_register():
    """Registra automáticamente las visualizaciones incluidas"""
    try:
        from .charts.line_charts import AbsentismoTemporalPlotly, AbsentismoComparativoPlotly
        
        register_visualization('absentismo_temporal', AbsentismoTemporalPlotly)
        register_visualization('absentismo_comparativo', AbsentismoComparativoPlotly)
        
    except ImportError as e:
        print(f"Error al auto-registrar visualizaciones: {e}")

# Ejecutar auto-registro al importar
auto_register()