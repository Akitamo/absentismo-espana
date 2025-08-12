"""
Agent Extractor - Módulo para extraer información del INE
Fase 1: Solo descarga y detección de actualizaciones
"""

from .ine_scraper import INEScraper
from .downloader import Downloader

class INEExtractor:
    """Agente principal para extracción de datos del INE"""
    
    def __init__(self):
        self.scraper = INEScraper()
        self.downloader = Downloader()
    
    def check_for_updates(self):
        """Verifica si hay actualizaciones en las páginas del INE"""
        return self.scraper.check_updates()
    
    def download_all(self, verbose=True):
        """Descarga todas las tablas configuradas"""
        return self.downloader.download_all_tables(verbose=verbose)
    
    def download_table(self, codigo_tabla):
        """Descarga una tabla específica"""
        return self.downloader.download_single_table(codigo_tabla)
    
    def get_table_info(self, codigo_tabla):
        """Obtiene información básica de una tabla desde el INE"""
        return self.scraper.get_table_info(codigo_tabla)

__all__ = ['INEExtractor', 'INEScraper', 'Downloader']