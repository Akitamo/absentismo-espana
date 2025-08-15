"""
Agent Extractor - Módulo para extraer información del INE
Fase 1: Solo descarga y detección de actualizaciones
"""

from .ine_scraper import INEScraper
from .downloader import Downloader
from .updater import UpdateManager
from .metadata_manager import MetadataManager

class INEExtractor:
    """Agente principal para extracción de datos del INE"""
    
    def __init__(self):
        self.scraper = INEScraper()
        self.downloader = Downloader()
        self.updater = UpdateManager()
        self.metadata_manager = MetadataManager()
    
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
    
    def check_updates_smart(self):
        """Verifica actualizaciones usando metadata local"""
        return self.updater.check_all_updates()
    
    def update_table(self, codigo_tabla):
        """Actualiza una tabla específica si hay nuevos datos"""
        return self.updater.update_table(codigo_tabla)
    
    def update_all(self):
        """Actualiza todas las tablas con nuevos datos disponibles"""
        return self.updater.update_all()

__all__ = ['INEExtractor', 'INEScraper', 'Downloader', 'UpdateManager', 'MetadataManager']