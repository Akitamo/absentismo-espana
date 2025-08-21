"""
Extractor de datos desde archivos CSV del INE
Maneja diferentes encodings y estructuras de tabla
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import chardet

logger = logging.getLogger(__name__)

class Extractor:
    """
    Extrae datos de los CSVs del INE con manejo robusto de encodings
    """
    
    # Encodings a probar en orden
    ENCODINGS = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'iso-8859-15']
    
    # Separadores posibles
    SEPARATORS = [';', ',', '\t']
    
    def __init__(self, raw_dir: Path, config: Dict):
        """
        Inicializa el extractor
        
        Args:
            raw_dir: Directorio con los CSVs crudos
            config: Configuración con mappings
        """
        self.raw_dir = raw_dir
        self.config = config
        self.mappings = config.get('mappings', {})
        self.tables_config = self.mappings.get('tables_config', {})
        
    def extract_table(self, table_id: str, test_mode: bool = False) -> pd.DataFrame:
        """
        Extrae datos de una tabla específica
        
        Args:
            table_id: ID de la tabla (ej: '6042')
            test_mode: Si True, extrae solo datos recientes para testing
            
        Returns:
            DataFrame con los datos extraídos
        """
        # Buscar archivo CSV
        csv_file = self._find_csv_file(table_id)
        if not csv_file:
            raise FileNotFoundError(f"No se encontró archivo CSV para tabla {table_id}")
        
        logger.info(f"Extrayendo datos de: {csv_file.name}")
        
        # Detectar encoding y separador
        encoding, separator = self._detect_file_format(csv_file)
        logger.info(f"Formato detectado - Encoding: {encoding}, Separador: '{separator}'")
        
        # Leer CSV
        try:
            df = pd.read_csv(
                csv_file,
                encoding=encoding,
                sep=separator,
                decimal=',',
                thousands='.',
                na_values=['..', '...', 'n.d.', 'N.D.', '']
            )
            
            logger.info(f"Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
            
            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()
            
            # Identificar columnas
            columns_info = self._identify_columns(df, table_id)
            logger.info(f"Columnas identificadas: {columns_info}")
            
            # Validar estructura básica
            self._validate_structure(df, table_id)
            
            # En modo test, filtrar solo datos recientes
            if test_mode and 'Periodo' in df.columns:
                df = self._filter_test_data(df)
                logger.info(f"Modo test: filtrados a {len(df)} registros")
            
            # Limpiar valores numéricos
            df = self._clean_numeric_values(df, columns_info)
            
            # Añadir metadatos
            df['fuente_tabla'] = table_id
            df['tabla_nombre'] = self.tables_config.get(table_id, {}).get('name', f'Tabla {table_id}')
            
            return df
            
        except Exception as e:
            logger.error(f"Error leyendo CSV {csv_file}: {str(e)}")
            raise
    
    def _find_csv_file(self, table_id: str) -> Optional[Path]:
        """
        Busca el archivo CSV para una tabla
        
        Args:
            table_id: ID de la tabla
            
        Returns:
            Path al archivo CSV o None si no existe
        """
        # Buscar con patrón
        pattern = f"{table_id}_*.csv"
        csv_files = list(self.raw_dir.glob(pattern))
        
        if not csv_files:
            # Intentar con nombre exacto
            exact_file = self.raw_dir / f"{table_id}.csv"
            if exact_file.exists():
                return exact_file
            return None
        
        # Si hay múltiples, tomar el más reciente
        if len(csv_files) > 1:
            csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            logger.warning(f"Múltiples archivos para tabla {table_id}, usando: {csv_files[0].name}")
        
        return csv_files[0]
    
    def _detect_file_format(self, file_path: Path) -> Tuple[str, str]:
        """
        Detecta el encoding y separador del archivo
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Tupla (encoding, separator)
        """
        # Detectar encoding con chardet
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Leer primeros 10KB
            result = chardet.detect(raw_data)
            detected_encoding = result['encoding']
            confidence = result['confidence']
            
        logger.info(f"Encoding detectado por chardet: {detected_encoding} (confianza: {confidence:.2f})")
        
        # Si la confianza es baja, probar encodings conocidos
        if confidence < 0.7:
            for encoding in self.ENCODINGS:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(1000)  # Probar leyendo
                    logger.info(f"Encoding validado: {encoding}")
                    detected_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
        
        # Detectar separador
        separator = ';'  # Por defecto, INE usa punto y coma
        try:
            with open(file_path, 'r', encoding=detected_encoding) as f:
                first_line = f.readline()
                # Contar ocurrencias de posibles separadores
                sep_counts = {sep: first_line.count(sep) for sep in self.SEPARATORS}
                separator = max(sep_counts, key=sep_counts.get)
        except:
            pass
        
        return detected_encoding or 'latin-1', separator
    
    def _identify_columns(self, df: pd.DataFrame, table_id: str) -> Dict:
        """
        Identifica el tipo de cada columna (dimensión vs métrica)
        
        Args:
            df: DataFrame con los datos
            table_id: ID de la tabla
            
        Returns:
            Diccionario con información de columnas
        """
        columns_info = {
            'dimensiones': [],
            'metricas': [],
            'tiempo_trabajo': None
        }
        
        # Patrones para identificar dimensiones
        dimension_patterns = [
            'periodo', 'sector', 'seccion', 'division', 'actividad',
            'comunidad', 'ccaa', 'jornada', 'tipo de jornada',
            'establecimiento', 'tamaño'
        ]
        
        # Patrones para columna de métricas
        metric_column_patterns = [
            'tiempo de trabajo', 'componentes del coste',
            'componente del coste', 'motivos', 'variable'
        ]
        
        for col in df.columns:
            col_lower = col.lower().strip()
            
            # Verificar si es dimensión
            is_dimension = any(pattern in col_lower for pattern in dimension_patterns)
            
            # Verificar si es la columna que contiene las métricas
            is_metric_column = any(pattern in col_lower for pattern in metric_column_patterns)
            
            if is_dimension:
                columns_info['dimensiones'].append(col)
            elif is_metric_column:
                columns_info['tiempo_trabajo'] = col
            else:
                # Si no es dimensión ni columna de métricas, es una columna de valores
                if df[col].dtype in ['float64', 'int64', 'object']:
                    # Verificar si contiene valores numéricos
                    try:
                        pd.to_numeric(df[col].dropna().iloc[:10], errors='coerce')
                        columns_info['metricas'].append(col)
                    except:
                        pass
        
        return columns_info
    
    def _validate_structure(self, df: pd.DataFrame, table_id: str):
        """
        Valida la estructura básica del DataFrame
        
        Args:
            df: DataFrame a validar
            table_id: ID de la tabla
            
        Raises:
            ValueError si la estructura no es válida
        """
        # Validaciones básicas
        if df.empty:
            raise ValueError(f"Tabla {table_id} está vacía")
        
        # Verificar columna Periodo
        if 'Periodo' not in df.columns:
            raise ValueError(f"Tabla {table_id} no tiene columna 'Periodo'")
        
        # Verificar que hay datos numéricos
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_columns) == 0:
            # Intentar encontrar columnas con valores numéricos como strings
            potential_numeric = []
            for col in df.columns:
                if col != 'Periodo':
                    try:
                        pd.to_numeric(df[col].dropna().iloc[:10], errors='coerce')
                        potential_numeric.append(col)
                    except:
                        pass
            
            if not potential_numeric:
                logger.warning(f"Tabla {table_id} no tiene columnas numéricas evidentes")
    
    def _filter_test_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra datos para modo test (solo períodos recientes)
        
        Args:
            df: DataFrame completo
            
        Returns:
            DataFrame filtrado
        """
        # Ordenar por periodo descendente y tomar los últimos 4 trimestres
        df_sorted = df.sort_values('Periodo', ascending=False)
        unique_periods = df_sorted['Periodo'].unique()[:4]  # Últimos 4 trimestres
        
        return df[df['Periodo'].isin(unique_periods)]
    
    def _clean_numeric_values(self, df: pd.DataFrame, columns_info: Dict) -> pd.DataFrame:
        """
        Limpia y convierte valores numéricos
        
        Args:
            df: DataFrame con datos
            columns_info: Información sobre las columnas
            
        Returns:
            DataFrame con valores numéricos limpios
        """
        # Identificar columnas numéricas
        numeric_cols = columns_info.get('metricas', [])
        
        for col in numeric_cols:
            if col in df.columns:
                # Limpiar valores
                df[col] = df[col].astype(str).str.replace('.', '', regex=False)  # Quitar separador de miles
                df[col] = df[col].str.replace(',', '.', regex=False)  # Cambiar decimal
                df[col] = df[col].str.strip()
                
                # Convertir a numérico
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Para columnas de tipo objeto que deberían ser numéricas
        for col in df.columns:
            if df[col].dtype == 'object' and col not in columns_info.get('dimensiones', []):
                # Intentar conversión
                try:
                    # Primero intentar conversión directa
                    test_values = pd.to_numeric(df[col].dropna().iloc[:10], errors='coerce')
                    if not test_values.isna().all():
                        # Limpiar y convertir
                        df[col] = df[col].astype(str).str.replace('.', '', regex=False)
                        df[col] = df[col].str.replace(',', '.', regex=False)
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    pass
        
        return df
    
    def extract_all(self, table_ids: List[str], test_mode: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Extrae datos de múltiples tablas
        
        Args:
            table_ids: Lista de IDs de tablas
            test_mode: Si True, modo test
            
        Returns:
            Diccionario con DataFrames por tabla
        """
        extracted_data = {}
        
        for table_id in table_ids:
            try:
                df = self.extract_table(table_id, test_mode)
                extracted_data[table_id] = df
                logger.info(f"Tabla {table_id} extraída exitosamente")
            except Exception as e:
                logger.error(f"Error extrayendo tabla {table_id}: {str(e)}")
                raise
        
        return extracted_data