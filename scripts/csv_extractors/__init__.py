"""
Módulo de extracción CSV para el Sistema de Absentismo España

Este módulo proporciona funcionalidades para descargar y procesar
archivos CSV de la Encuesta Trimestral de Coste Laboral (ETCL) del INE.

Componentes principales:
- ExtractorCSV_INE: Clase principal para descarga de archivos CSV
- utils_csv: Utilidades para manejo y validación de archivos CSV
- config_csv.json: Configuración del sistema

Uso básico:
    from extractor_csv_ine import ExtractorCSV_INE
    
    extractor = ExtractorCSV_INE()
    extractor.cargar_urls_etcl("../../urls_etcl_completo.json")
    resultados = extractor.descargar_todas_activas()
"""

from .extractor_csv_ine import ExtractorCSV_INE
from . import utils_csv

__version__ = "1.0.0"
__author__ = "Sistema Absentismo España"

__all__ = [
    'ExtractorCSV_INE',
    'utils_csv'
]