"""
Procesador principal para datos ETCL
Orquesta el pipeline ETL completo
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

from .etl import Extractor, Transformer, Loader
from .validators import BusinessValidator, DataQualityValidator

logger = logging.getLogger(__name__)

class ProcessorETCL:
    """
    Procesador principal para transformar datos ETCL del INE
    en tabla unificada para análisis de absentismo
    """
    
    REQUIRED_TABLES = ['6042', '6043', '6044', '6045', '6046', '6063']
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializa el procesador con configuración
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.raw_dir = self.data_dir / "raw" / "csv"
        self.processed_dir = self.data_dir / "processed"
        self.db_path = self.data_dir / "analysis.db"
        
        # Crear directorio de procesados si no existe
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Cargar configuración
        self.config = self._load_config(config_path)
        
        # Inicializar componentes
        self.extractor = Extractor(self.raw_dir, self.config)
        self.transformer = Transformer(self.config)
        self.loader = Loader(self.db_path)
        self.business_validator = BusinessValidator()
        self.quality_validator = DataQualityValidator()
        
        logger.info(f"ProcessorETCL inicializado. DB: {self.db_path}")
    
    def _load_config(self, config_path: Optional[Path] = None) -> Dict:
        """
        Carga la configuración del procesador
        
        Returns:
            Diccionario con toda la configuración
        """
        configs = {}
        
        # Cargar mappings
        mappings_path = Path(__file__).parent / "config" / "mappings.json"
        if mappings_path.exists():
            with open(mappings_path, 'r', encoding='utf-8') as f:
                configs['mappings'] = json.load(f)
        
        # Cargar configuración completa del procesador
        processor_config_path = self.base_dir / "config" / "procesador_config_completo.json"
        if processor_config_path.exists():
            with open(processor_config_path, 'r', encoding='utf-8') as f:
                configs['processor'] = json.load(f)
        
        # Cargar configuración personalizada si se proporciona
        if config_path and config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
                configs.update(custom_config)
        
        return configs
    
    def process_all(self, test_mode: bool = False) -> Dict[str, Any]:
        """
        Procesa todas las tablas requeridas
        
        Args:
            test_mode: Si True, procesa solo un período para testing
            
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        logger.info("Iniciando procesamiento completo de tablas ETCL")
        stats = {
            'inicio': datetime.now(),
            'tablas_procesadas': [],
            'registros_totales': 0,
            'errores': [],
            'validaciones': {}
        }
        
        try:
            # 1. EXTRACCIÓN
            logger.info("FASE 1: Extracción de datos")
            raw_data = {}
            for table_id in self.REQUIRED_TABLES:
                logger.info(f"Extrayendo tabla {table_id}")
                try:
                    df = self.extractor.extract_table(table_id, test_mode=test_mode)
                    raw_data[table_id] = df
                    logger.info(f"Tabla {table_id}: {len(df)} registros extraídos")
                except Exception as e:
                    error_msg = f"Error extrayendo tabla {table_id}: {str(e)}"
                    logger.error(error_msg)
                    stats['errores'].append(error_msg)
            
            if not raw_data:
                raise ValueError("No se pudo extraer ninguna tabla")
            
            # 2. TRANSFORMACIÓN
            logger.info("FASE 2: Transformación de datos")
            transformed_data = self.transformer.transform_all(raw_data)
            stats['registros_totales'] = len(transformed_data)
            logger.info(f"Datos transformados: {stats['registros_totales']} registros")
            
            # 3. VALIDACIÓN DE CALIDAD
            logger.info("FASE 3: Validación de calidad de datos")
            quality_results = self.quality_validator.validate(transformed_data)
            stats['validaciones']['calidad'] = quality_results
            
            if not quality_results['passed']:
                logger.warning(f"Advertencias de calidad: {quality_results['warnings']}")
            
            # 4. VALIDACIÓN DE REGLAS DE NEGOCIO
            logger.info("FASE 4: Validación de reglas de negocio")
            business_results = self.business_validator.validate(transformed_data)
            stats['validaciones']['negocio'] = business_results
            
            if not business_results['passed']:
                raise ValueError(f"Validación de negocio falló: {business_results['errors']}")
            
            # 5. CARGA A BASE DE DATOS
            logger.info("FASE 5: Carga a base de datos")
            load_results = self.loader.load(transformed_data, replace=True)
            stats['carga'] = load_results
            
            # 6. EXPORTAR A CSV PARA VERIFICACIÓN
            if test_mode:
                output_path = self.processed_dir / f"test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                transformed_data.to_csv(output_path, index=False, encoding='utf-8')
                logger.info(f"Datos de prueba exportados a: {output_path}")
                stats['archivo_test'] = str(output_path)
            
            stats['fin'] = datetime.now()
            stats['duracion'] = str(stats['fin'] - stats['inicio'])
            stats['exitoso'] = True
            stats['tablas_procesadas'] = list(raw_data.keys())
            
            logger.info(f"Procesamiento completado exitosamente en {stats['duracion']}")
            
        except Exception as e:
            logger.error(f"Error en procesamiento: {str(e)}")
            stats['exitoso'] = False
            stats['error_principal'] = str(e)
            raise
        
        return stats
    
    def process_table(self, table_id: str, test_mode: bool = False) -> Dict[str, Any]:
        """
        Procesa una tabla individual
        
        Args:
            table_id: ID de la tabla a procesar (ej: '6042')
            test_mode: Si True, procesa solo un período para testing
            
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        if table_id not in self.REQUIRED_TABLES:
            raise ValueError(f"Tabla {table_id} no está en la lista de tablas requeridas: {self.REQUIRED_TABLES}")
        
        logger.info(f"Procesando tabla individual: {table_id}")
        
        stats = {
            'tabla': table_id,
            'inicio': datetime.now()
        }
        
        try:
            # Extraer
            df = self.extractor.extract_table(table_id, test_mode=test_mode)
            stats['registros_extraidos'] = len(df)
            
            # Transformar
            transformed = self.transformer.transform_table(table_id, df)
            stats['registros_transformados'] = len(transformed)
            
            # Validar
            quality_results = self.quality_validator.validate(transformed)
            business_results = self.business_validator.validate(transformed)
            
            stats['validaciones'] = {
                'calidad': quality_results,
                'negocio': business_results
            }
            
            # Cargar (append mode para tabla individual)
            load_results = self.loader.load(transformed, replace=False)
            stats['carga'] = load_results
            
            stats['fin'] = datetime.now()
            stats['duracion'] = str(stats['fin'] - stats['inicio'])
            stats['exitoso'] = True
            
            logger.info(f"Tabla {table_id} procesada exitosamente")
            
        except Exception as e:
            logger.error(f"Error procesando tabla {table_id}: {str(e)}")
            stats['exitoso'] = False
            stats['error'] = str(e)
            raise
        
        return stats
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del procesador y la base de datos
        
        Returns:
            Diccionario con información de estado
        """
        status = {
            'db_exists': self.db_path.exists(),
            'db_path': str(self.db_path),
            'processed_dir': str(self.processed_dir),
            'raw_dir': str(self.raw_dir)
        }
        
        # Verificar qué tablas están disponibles
        available_tables = []
        for table_id in self.REQUIRED_TABLES:
            csv_pattern = f"{table_id}_*.csv"
            csv_files = list(self.raw_dir.glob(csv_pattern))
            if csv_files:
                available_tables.append({
                    'id': table_id,
                    'file': csv_files[0].name,
                    'size_mb': round(csv_files[0].stat().st_size / 1024 / 1024, 2)
                })
        
        status['available_tables'] = available_tables
        status['missing_tables'] = [t for t in self.REQUIRED_TABLES 
                                   if t not in [at['id'] for at in available_tables]]
        
        # Si existe la DB, obtener estadísticas
        if status['db_exists']:
            try:
                stats = self.loader.get_stats()
                status['db_stats'] = stats
            except Exception as e:
                status['db_stats'] = {'error': str(e)}
        
        return status