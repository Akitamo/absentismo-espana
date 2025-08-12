"""
Scraper para páginas del INE
Detecta actualizaciones y cambios en las tablas de absentismo
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import logging

class INEScraper:
    """Extrae información de las páginas del INE"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / 'config' / 'tables.json'
        self.metadata_path = Path(__file__).parent.parent / 'data' / 'metadata'
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self.session = self._create_session()
        self.logger = self._setup_logger()
    
    def _load_config(self):
        """Carga la configuración de tablas"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_session(self):
        """Crea una sesión HTTP reutilizable"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def _setup_logger(self):
        """Configura el logger"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return logger
    
    def check_updates(self):
        """Verifica actualizaciones en todas las tablas"""
        updates = {
            'fecha_verificacion': datetime.now().isoformat(),
            'tablas_verificadas': 0,
            'actualizaciones_detectadas': [],
            'errores': []
        }
        
        for categoria, info in self.config['categorias'].items():
            self.logger.info(f"Verificando categoría: {categoria}")
            
            for codigo, tabla_info in info['tablas'].items():
                try:
                    # Verificar disponibilidad vía JSON API
                    response = self.session.get(
                        tabla_info['url_json'],
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extraer información temporal
                        periodo_info = self._extract_periodo_info(data)
                        
                        updates['tablas_verificadas'] += 1
                        
                        # Guardar metadata de la tabla
                        tabla_metadata = {
                            'codigo': codigo,
                            'nombre': tabla_info['nombre'],
                            'categoria': categoria,
                            'ultimo_periodo': periodo_info.get('ultimo_periodo'),
                            'total_periodos': periodo_info.get('total_periodos'),
                            'fecha_verificacion': datetime.now().isoformat()
                        }
                        
                        # Comparar con metadata anterior si existe
                        if self._check_if_updated(codigo, tabla_metadata):
                            updates['actualizaciones_detectadas'].append(tabla_metadata)
                        
                        # Guardar metadata actual
                        self._save_table_metadata(codigo, tabla_metadata)
                        
                except Exception as e:
                    error_info = {
                        'codigo': codigo,
                        'error': str(e)
                    }
                    updates['errores'].append(error_info)
                    self.logger.error(f"Error verificando tabla {codigo}: {e}")
        
        # Guardar resumen de verificación
        self._save_verification_summary(updates)
        
        return updates
    
    def _extract_periodo_info(self, json_data):
        """Extrae información de periodos del JSON"""
        periodo_info = {
            'ultimo_periodo': None,
            'total_periodos': 0,
            'periodos_disponibles': []
        }
        
        try:
            # El formato del JSON del INE varía, intentar diferentes estructuras
            if isinstance(json_data, list) and len(json_data) > 0:
                # Buscar campos de periodo
                for item in json_data:
                    if 'Periodo' in item:
                        periodo_info['periodos_disponibles'].append(item['Periodo'])
                
                if periodo_info['periodos_disponibles']:
                    periodo_info['ultimo_periodo'] = max(periodo_info['periodos_disponibles'])
                    periodo_info['total_periodos'] = len(set(periodo_info['periodos_disponibles']))
        except:
            pass
        
        return periodo_info
    
    def _check_if_updated(self, codigo, nueva_metadata):
        """Verifica si hay actualizaciones comparando con metadata anterior"""
        metadata_file = self.metadata_path / f"tabla_{codigo}_metadata.json"
        
        if not metadata_file.exists():
            return True  # Primera vez, considerar como actualización
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_anterior = json.load(f)
            
            # Comparar último periodo
            if metadata_anterior.get('ultimo_periodo') != nueva_metadata.get('ultimo_periodo'):
                return True
            
            # Comparar total de periodos
            if metadata_anterior.get('total_periodos') != nueva_metadata.get('total_periodos'):
                return True
                
        except:
            return True
        
        return False
    
    def _save_table_metadata(self, codigo, metadata):
        """Guarda la metadata de una tabla"""
        metadata_file = self.metadata_path / f"tabla_{codigo}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _save_verification_summary(self, updates):
        """Guarda el resumen de verificación"""
        summary_file = self.metadata_path / f"verificacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(updates, f, indent=2, ensure_ascii=False)
    
    def get_table_info(self, codigo_tabla):
        """Obtiene información detallada de una tabla específica"""
        for categoria, info in self.config['categorias'].items():
            if codigo_tabla in info['tablas']:
                tabla_info = info['tablas'][codigo_tabla]
                
                try:
                    response = self.session.get(tabla_info['url_json'], timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'codigo': codigo_tabla,
                            'nombre': tabla_info['nombre'],
                            'categoria': categoria,
                            'url_csv': tabla_info['url_csv'],
                            'url_json': tabla_info['url_json'],
                            'datos_disponibles': len(data) if isinstance(data, list) else 0,
                            'periodo_info': self._extract_periodo_info(data)
                        }
                except Exception as e:
                    self.logger.error(f"Error obteniendo info de tabla {codigo_tabla}: {e}")
        
        return None