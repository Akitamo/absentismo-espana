"""
Transformador de datos ETCL
Mapea dimensiones y pivota métricas según diseño validado
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class Transformer:
    """
    Transforma datos crudos del INE en formato unificado
    """
    
    def __init__(self, config: Dict):
        """
        Inicializa el transformador con configuración
        
        Args:
            config: Configuración con mappings y reglas
        """
        self.config = config
        self.mappings = config.get('mappings', {})
        self.dimension_mappings = self.mappings.get('dimension_mappings', {})
        self.metric_mappings = self.mappings.get('metric_mappings', {})
        self.tables_config = self.mappings.get('tables_config', {})
        
    def transform_all(self, raw_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Transforma datos de todas las tablas en formato unificado
        
        Args:
            raw_data: Diccionario con DataFrames por tabla
            
        Returns:
            DataFrame unificado con estructura final
        """
        transformed_dfs = []
        
        for table_id, df in raw_data.items():
            logger.info(f"Transformando tabla {table_id}")
            try:
                transformed = self.transform_table(table_id, df)
                transformed_dfs.append(transformed)
                logger.info(f"Tabla {table_id} transformada: {len(transformed)} registros")
            except Exception as e:
                logger.error(f"Error transformando tabla {table_id}: {str(e)}")
                raise
        
        # Combinar todas las tablas
        result = pd.concat(transformed_dfs, ignore_index=True)
        
        # Ordenar columnas según diseño
        result = self._order_columns(result)
        
        logger.info(f"Transformación completa: {len(result)} registros totales")
        return result
    
    def transform_table(self, table_id: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforma una tabla individual
        
        Args:
            table_id: ID de la tabla
            df: DataFrame con datos crudos
            
        Returns:
            DataFrame transformado
        """
        # Obtener configuración de la tabla
        table_config = self.tables_config.get(table_id, {})
        
        # 1. Identificar estructura de la tabla
        structure = self._identify_table_structure(df, table_id)
        logger.info(f"Estructura identificada para {table_id}: {structure['type']}")
        
        # 2. Pivotar datos si es necesario
        if structure['type'] == 'wide':
            df_long = self._pivot_to_long(df, structure)
        else:
            df_long = df.copy()
        
        # 3. Mapear periodo
        df_long = self._map_periodo(df_long)
        
        # 4. Mapear dimensiones territoriales
        df_long = self._map_territorial(df_long, table_id)
        
        # 5. Mapear dimensiones sectoriales
        df_long = self._map_sectorial(df_long, table_id)
        
        # 6. Mapear tipo de jornada
        df_long = self._map_jornada(df_long, table_id)
        
        # 7. Mapear métricas y causas
        df_long = self._map_metrics(df_long)
        
        # 8. Calcular campos derivados
        df_long = self._calculate_derived_fields(df_long, table_id)
        
        # 9. Añadir metadatos
        df_long = self._add_metadata(df_long, table_id)
        
        # 10. Limpiar y validar
        df_long = self._clean_and_validate(df_long)
        
        return df_long
    
    def _identify_table_structure(self, df: pd.DataFrame, table_id: str) -> Dict:
        """
        Identifica si la tabla es wide (columnas = métricas) o long
        
        Args:
            df: DataFrame a analizar
            table_id: ID de la tabla
            
        Returns:
            Diccionario con información de estructura
        """
        structure = {
            'type': 'unknown',
            'metric_column': None,
            'value_columns': [],
            'dimension_columns': []
        }
        
        # Buscar columna "Tiempo de trabajo" o similar
        metric_columns = [col for col in df.columns 
                         if 'tiempo de trabajo' in col.lower() 
                         or 'componente' in col.lower()
                         or 'motivos' in col.lower()]
        
        if metric_columns:
            # Formato long: métricas en una columna
            structure['type'] = 'long'
            structure['metric_column'] = metric_columns[0]
            
            # Identificar columnas de valores (numéricas)
            for col in df.columns:
                if col != structure['metric_column']:
                    if df[col].dtype in ['float64', 'int64']:
                        structure['value_columns'].append(col)
                    elif col not in ['fuente_tabla', 'tabla_nombre']:
                        structure['dimension_columns'].append(col)
        else:
            # Formato wide: cada métrica es una columna
            structure['type'] = 'wide'
            
            # Todas las columnas numéricas son métricas
            for col in df.columns:
                if df[col].dtype in ['float64', 'int64']:
                    structure['value_columns'].append(col)
                elif col not in ['fuente_tabla', 'tabla_nombre']:
                    structure['dimension_columns'].append(col)
        
        return structure
    
    def _pivot_to_long(self, df: pd.DataFrame, structure: Dict) -> pd.DataFrame:
        """
        Pivota datos de formato wide a long
        
        Args:
            df: DataFrame en formato wide
            structure: Información de estructura
            
        Returns:
            DataFrame en formato long
        """
        # Si ya está en formato long, renombrar columna de valor si existe
        if structure['type'] == 'long':
            # Buscar columna de valores (generalmente llamada 'Total' en INE)
            value_columns = structure.get('value_columns', [])
            if value_columns and len(value_columns) == 1:
                # Renombrar la columna de valor a 'valor'
                df = df.rename(columns={value_columns[0]: 'valor'})
            elif 'Total' in df.columns:
                df = df.rename(columns={'Total': 'valor'})
            return df
        
        # Pivotar columnas de valores a filas
        id_vars = structure['dimension_columns'] + ['fuente_tabla', 'tabla_nombre']
        value_vars = structure['value_columns']
        
        df_long = pd.melt(
            df,
            id_vars=id_vars,
            value_vars=value_vars,
            var_name='Tiempo de trabajo',
            value_name='valor'
        )
        
        return df_long
    
    def _map_periodo(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mapea y valida el periodo, añadiendo fechas de inicio y fin
        
        Args:
            df: DataFrame con columna Periodo
            
        Returns:
            DataFrame con periodo mapeado
        """
        if 'Periodo' not in df.columns:
            raise ValueError("No se encuentra la columna Periodo")
        
        # Renombrar a minúsculas
        df['periodo'] = df['Periodo']
        
        # Calcular fechas de inicio y fin del trimestre
        def get_quarter_dates(periodo):
            try:
                year = int(periodo[:4])
                quarter = int(periodo[5])
                
                # Mapeo de trimestre a mes inicial
                quarter_to_month = {1: 1, 2: 4, 3: 7, 4: 10}
                month = quarter_to_month[quarter]
                
                # Fecha inicio
                inicio = pd.Timestamp(year, month, 1)
                
                # Fecha fin (último día del trimestre)
                if quarter == 4:
                    fin = pd.Timestamp(year, 12, 31)
                else:
                    next_month = month + 3
                    fin = pd.Timestamp(year, next_month, 1) - pd.Timedelta(days=1)
                
                return inicio, fin
            except:
                return pd.NaT, pd.NaT
        
        # Aplicar cálculo
        dates = df['periodo'].apply(get_quarter_dates)
        df['periodo_inicio'] = dates.apply(lambda x: x[0])
        df['periodo_fin'] = dates.apply(lambda x: x[1])
        
        return df
    
    def _map_territorial(self, df: pd.DataFrame, table_id: str) -> pd.DataFrame:
        """
        Mapea dimensiones territoriales (nacional vs CCAA)
        
        Args:
            df: DataFrame
            table_id: ID de la tabla
            
        Returns:
            DataFrame con dimensiones territoriales mapeadas
        """
        # Por defecto, ámbito nacional
        df['ambito_territorial'] = 'NAC'
        df['ccaa_codigo'] = None
        df['ccaa_nombre'] = None
        
        # Solo tabla 6063 tiene CCAA
        if table_id == '6063' and 'Comunidades y Ciudades Autónomas' in df.columns:
            ccaa_mapping = self.dimension_mappings.get('comunidades', {}).get('6063', {})
            
            for ccaa_name, mapping in ccaa_mapping.items():
                mask = df['Comunidades y Ciudades Autónomas'] == ccaa_name
                df.loc[mask, 'ambito_territorial'] = mapping['ambito_territorial']
                if mapping['ccaa_codigo']:
                    df.loc[mask, 'ccaa_codigo'] = mapping['ccaa_codigo']
                    df.loc[mask, 'ccaa_nombre'] = ccaa_name
        
        return df
    
    def _map_sectorial(self, df: pd.DataFrame, table_id: str) -> pd.DataFrame:
        """
        Mapea dimensiones sectoriales (CNAE)
        
        Args:
            df: DataFrame
            table_id: ID de la tabla
            
        Returns:
            DataFrame con dimensiones sectoriales mapeadas
        """
        # Inicializar columnas
        df['cnae_nivel'] = None
        df['cnae_codigo'] = None
        df['cnae_nombre'] = None
        df['jerarquia_sector_lbl'] = None
        
        # Obtener nivel CNAE de la tabla
        table_config = self.tables_config.get(table_id, {})
        cnae_nivel = table_config.get('cnae_nivel', 'TOTAL')
        
        # Buscar columna de sectores
        sector_columns = [col for col in df.columns 
                         if any(s in col.lower() for s in ['sector', 'seccion', 'division', 'actividad'])]
        
        if not sector_columns:
            # No hay dimensión sectorial, todo es TOTAL
            df['cnae_nivel'] = 'TOTAL'
            df['cnae_codigo'] = None
            df['cnae_nombre'] = None
            df['jerarquia_sector_lbl'] = 'Total'
            return df
        
        sector_col = sector_columns[0]
        
        # Obtener mapping específico de la tabla
        if table_id in ['6042', '6044', '6063']:
            # Sectores B-S
            sector_mapping = self.dimension_mappings.get('sectores', {}).get('6042', {})
        elif table_id in ['6043', '6045']:
            # Secciones
            sector_mapping = self.dimension_mappings.get('sectores', {}).get('6043', {})
            # Añadir mapeo para B_S si no existe
            for val in df[sector_col].unique():
                if val and val.startswith('B_S') and val not in sector_mapping:
                    sector_mapping[val] = {'cnae_nivel': 'TOTAL', 'cnae_codigo': None}
        elif table_id == '6046':
            # Divisiones - requiere mapeo especial
            sector_mapping = self._build_division_mapping(df[sector_col].unique())
        else:
            sector_mapping = {}
        
        # Aplicar mapping
        for sector_name, mapping in sector_mapping.items():
            mask = df[sector_col] == sector_name
            if mask.any():
                df.loc[mask, 'cnae_nivel'] = mapping['cnae_nivel']
                df.loc[mask, 'cnae_codigo'] = mapping['cnae_codigo']
                df.loc[mask, 'cnae_nombre'] = sector_name if mapping['cnae_codigo'] else None
                
                # Construir jerarquía
                if mapping['cnae_nivel'] == 'TOTAL':
                    df.loc[mask, 'jerarquia_sector_lbl'] = 'Total'
                elif mapping['cnae_nivel'] == 'SECTOR_BS':
                    df.loc[mask, 'jerarquia_sector_lbl'] = f"Total>Sector {mapping['cnae_codigo']}"
                elif mapping['cnae_nivel'] == 'SECCION':
                    df.loc[mask, 'jerarquia_sector_lbl'] = f"Total>Sección {mapping['cnae_codigo']}"
                elif mapping['cnae_nivel'] == 'DIVISION':
                    # Para divisiones necesitamos saber la sección padre
                    seccion = self._get_seccion_from_division(mapping['cnae_codigo'])
                    df.loc[mask, 'jerarquia_sector_lbl'] = f"Total>Sección {seccion}>División {mapping['cnae_codigo']}"
        
        # Asegurar que todos los registros tienen cnae_nivel
        # Si algún registro no fue mapeado, asignar el nivel por defecto de la tabla
        if df['cnae_nivel'].isna().any() or (df['cnae_nivel'] == '').any():
            # Usar el cnae_nivel configurado para la tabla
            default_nivel = cnae_nivel
            df.loc[df['cnae_nivel'].isna() | (df['cnae_nivel'] == ''), 'cnae_nivel'] = default_nivel
            
            # Si es TOTAL y no tiene jerarquía, asignarla
            mask_total = (df['cnae_nivel'] == 'TOTAL') & df['jerarquia_sector_lbl'].isna()
            df.loc[mask_total, 'jerarquia_sector_lbl'] = 'Total'
        
        return df
    
    def _map_jornada(self, df: pd.DataFrame, table_id: str) -> pd.DataFrame:
        """
        Mapea tipo de jornada
        
        Args:
            df: DataFrame
            table_id: ID de la tabla
            
        Returns:
            DataFrame con jornada mapeada
        """
        # Verificar si la tabla tiene jornada
        table_config = self.tables_config.get(table_id, {})
        has_jornada = table_config.get('has_jornada', False)
        
        if not has_jornada:
            df['tipo_jornada'] = None
        else:
            # Buscar columna de jornada
            jornada_columns = [col for col in df.columns 
                              if 'jornada' in col.lower() or 'tiempo' in col.lower()]
            
            if jornada_columns:
                jornada_col = jornada_columns[0]
                jornada_mapping = self.dimension_mappings.get('tipo_jornada', {}).get('mapping', {})
                
                # Mapear valores
                df['tipo_jornada'] = df[jornada_col].map(jornada_mapping)
                
                # Si no se encuentra mapping, usar valor original
                df['tipo_jornada'] = df['tipo_jornada'].fillna(df[jornada_col])
            else:
                df['tipo_jornada'] = 'TOTAL'
        
        return df
    
    def _map_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mapea métricas y causas desde la columna "Tiempo de trabajo"
        
        Args:
            df: DataFrame con columna de métricas
            
        Returns:
            DataFrame con métricas y causas mapeadas
        """
        # Buscar columna de métricas
        metric_column = None
        for col in df.columns:
            if 'tiempo de trabajo' in col.lower() or 'componente' in col.lower():
                metric_column = col
                break
        
        if not metric_column:
            # Si no hay columna de métricas, asumir que ya están mapeadas
            if 'metrica' not in df.columns:
                df['metrica'] = 'horas_efectivas'  # Default
                df['causa'] = None
            return df
        
        # Inicializar columnas
        df['metrica'] = None
        df['causa'] = None
        
        # Aplicar mapping
        for metric_text, mapping in self.metric_mappings.items():
            mask = df[metric_column] == metric_text
            if mask.any():
                df.loc[mask, 'metrica'] = mapping['metrica']
                df.loc[mask, 'causa'] = mapping['causa']
        
        # Validar que todas las métricas fueron mapeadas
        unmapped = df[df['metrica'].isna()][metric_column].unique()
        if len(unmapped) > 0:
            logger.warning(f"Métricas sin mapear: {unmapped}")
            # Intentar mapeo aproximado
            for value in unmapped:
                if pd.notna(value):
                    value_lower = str(value).lower()
                    if 'pactada' in value_lower:
                        df.loc[df[metric_column] == value, 'metrica'] = 'horas_pactadas'
                    elif 'efectiva' in value_lower:
                        df.loc[df[metric_column] == value, 'metrica'] = 'horas_efectivas'
                    elif 'extraordinaria' in value_lower or 'extra' in value_lower:
                        df.loc[df[metric_column] == value, 'metrica'] = 'horas_extraordinarias'
                    elif 'no trabajada' in value_lower:
                        df.loc[df[metric_column] == value, 'metrica'] = 'horas_no_trabajadas'
        
        return df
    
    def _calculate_derived_fields(self, df: pd.DataFrame, table_id: str) -> pd.DataFrame:
        """
        Calcula campos derivados y flags
        
        Args:
            df: DataFrame
            table_id: ID de la tabla
            
        Returns:
            DataFrame con campos derivados
        """
        # Flags de totalización
        df['es_total_ccaa'] = df['ambito_territorial'] == 'NAC'
        df['es_total_cnae'] = df['cnae_nivel'] == 'TOTAL'
        df['es_total_jornada'] = df['tipo_jornada'].isin([None, 'TOTAL'])
        
        # Calcular rol_grano
        table_config = self.tables_config.get(table_id, {})
        rol_grano_base = table_config.get('rol_grano_base', 'UNKNOWN')
        
        def calculate_rol_grano(row):
            parts = []
            
            # Territorial
            if row['ambito_territorial'] == 'NAC':
                parts.append('NAC')
            else:
                parts.append('CCAA')
            
            # Sectorial
            if row['cnae_nivel'] == 'TOTAL':
                parts.append('TOTAL')
            elif row['cnae_nivel'] == 'SECTOR_BS':
                parts.append('SECTOR_BS')
            elif row['cnae_nivel'] == 'SECCION':
                parts.append('SECCION')
            elif row['cnae_nivel'] == 'DIVISION':
                parts.append('DIVISION')
            
            # Jornada
            if pd.notna(row['tipo_jornada']) and row['tipo_jornada'] != 'TOTAL':
                parts.append('JORNADA')
            
            return '_'.join(parts)
        
        df['rol_grano'] = df.apply(calculate_rol_grano, axis=1)
        
        # Unidad de medida
        df['unidad'] = 'horas/mes por trabajador'
        
        return df
    
    def _add_metadata(self, df: pd.DataFrame, table_id: str) -> pd.DataFrame:
        """
        Añade metadatos al DataFrame
        
        Args:
            df: DataFrame
            table_id: ID de la tabla
            
        Returns:
            DataFrame con metadatos
        """
        # Fuente de la tabla
        if 'fuente_tabla' not in df.columns:
            df['fuente_tabla'] = table_id
        
        # Versión de datos (último periodo disponible)
        if 'periodo' in df.columns:
            version = df['periodo'].max()
            df['version_datos'] = version
        else:
            df['version_datos'] = None
        
        # Fecha de carga
        df['fecha_carga'] = datetime.now()
        
        return df
    
    def _clean_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y valida el DataFrame final
        
        Args:
            df: DataFrame a limpiar
            
        Returns:
            DataFrame limpio
        """
        # Eliminar columnas temporales y originales
        columns_to_drop = [
            'Periodo', 'Tiempo de trabajo', 'tabla_nombre',
            'Tipo de jornada', 'Sectores de actividad CNAE 2009',
            'Comunidades y Ciudades Autónomas', 'Secciones', 'Divisiones'
        ]
        for col in columns_to_drop:
            if col in df.columns:
                df = df.drop(columns=[col])
        
        # Asegurar que valor es numérico
        if 'valor' in df.columns:
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            
            # Los valores del INE vienen multiplicados por 10 (151 = 15.1 horas)
            df['valor'] = df['valor'] / 10.0
            
            # Redondear a 3 decimales según diseño
            df['valor'] = df['valor'].round(3)
            
            # Eliminar filas sin valor
            df = df[df['valor'].notna()]
        else:
            # Si no existe columna valor, puede que esté en 'Total' u otra
            if 'Total' in df.columns:
                df['valor'] = pd.to_numeric(df['Total'], errors='coerce') / 10.0
                df['valor'] = df['valor'].round(3)
                df = df.drop(columns=['Total'])
            else:
                logger.warning(f"No se encontró columna 'valor'. Columnas disponibles: {list(df.columns)}")
        
        # Validar que no hay duplicados en la clave primaria
        key_columns = ['periodo', 'ambito_territorial', 'ccaa_codigo', 'cnae_nivel', 
                      'cnae_codigo', 'tipo_jornada', 'metrica', 'causa']
        
        # Reemplazar None con string vacío para la clave
        for col in key_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        # Verificar duplicados
        duplicates = df.duplicated(subset=key_columns, keep=False)
        if duplicates.any():
            logger.warning(f"Se encontraron {duplicates.sum()} registros duplicados")
            # Mantener el primer registro de cada grupo duplicado
            df = df.drop_duplicates(subset=key_columns, keep='first')
        
        # Restaurar None donde corresponda
        for col in ['ccaa_codigo', 'ccaa_nombre', 'cnae_codigo', 'cnae_nombre', 
                   'tipo_jornada', 'causa', 'jerarquia_sector_lbl']:
            if col in df.columns:
                df[col] = df[col].replace('', None)
        
        return df
    
    def _order_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ordena las columnas según el diseño especificado
        
        Args:
            df: DataFrame a ordenar
            
        Returns:
            DataFrame con columnas ordenadas
        """
        column_order = [
            'periodo', 'periodo_inicio', 'periodo_fin',
            'ambito_territorial', 'ccaa_codigo', 'ccaa_nombre',
            'cnae_nivel', 'cnae_codigo', 'cnae_nombre',
            'jerarquia_sector_lbl',
            'tipo_jornada',
            'metrica', 'causa',
            'valor', 'unidad',
            'fuente_tabla',
            'es_total_ccaa', 'es_total_cnae', 'es_total_jornada',
            'rol_grano',
            'version_datos', 'fecha_carga'
        ]
        
        # Seleccionar solo columnas que existen
        columns_present = [col for col in column_order if col in df.columns]
        
        return df[columns_present]
    
    def _build_division_mapping(self, divisions: List[str]) -> Dict:
        """
        Construye mapping para divisiones CNAE (tabla 6046)
        
        Args:
            divisions: Lista de divisiones encontradas
            
        Returns:
            Diccionario de mapping
        """
        mapping = {}
        
        for division in divisions:
            if pd.isna(division):
                continue
                
            division_str = str(division).strip()
            
            # Buscar patrón de división (número de 2 dígitos)
            import re
            match = re.search(r'\b(\d{2})\b', division_str)
            
            if match:
                codigo = match.group(1)
                mapping[division] = {
                    'cnae_nivel': 'DIVISION',
                    'cnae_codigo': codigo
                }
            elif 'total' in division_str.lower() or division_str.startswith('B_S'):
                mapping[division] = {
                    'cnae_nivel': 'TOTAL',
                    'cnae_codigo': None
                }
        
        return mapping
    
    def _get_seccion_from_division(self, division_code: str) -> str:
        """
        Obtiene la sección CNAE correspondiente a una división
        
        Args:
            division_code: Código de división (2 dígitos)
            
        Returns:
            Código de sección (letra)
        """
        # Mapping simplificado división -> sección
        division_to_seccion = {
            '05': 'B', '06': 'B', '07': 'B', '08': 'B', '09': 'B',  # B: Extractivas
            '10': 'C', '11': 'C', '12': 'C', '13': 'C', '14': 'C',  # C: Manufacturera
            '15': 'C', '16': 'C', '17': 'C', '18': 'C', '19': 'C',
            '20': 'C', '21': 'C', '22': 'C', '23': 'C', '24': 'C',
            '25': 'C', '26': 'C', '27': 'C', '28': 'C', '29': 'C',
            '30': 'C', '31': 'C', '32': 'C', '33': 'C',
            '35': 'D',  # D: Energía
            '36': 'E', '37': 'E', '38': 'E', '39': 'E',  # E: Agua
            '41': 'F', '42': 'F', '43': 'F',  # F: Construcción
            '45': 'G', '46': 'G', '47': 'G',  # G: Comercio
            '49': 'H', '50': 'H', '51': 'H', '52': 'H', '53': 'H',  # H: Transporte
            '55': 'I', '56': 'I',  # I: Hostelería
            '58': 'J', '59': 'J', '60': 'J', '61': 'J', '62': 'J', '63': 'J',  # J: Información
            '64': 'K', '65': 'K', '66': 'K',  # K: Financieras
            '68': 'L',  # L: Inmobiliarias
            '69': 'M', '70': 'M', '71': 'M', '72': 'M', '73': 'M', '74': 'M', '75': 'M',  # M: Profesionales
            '77': 'N', '78': 'N', '79': 'N', '80': 'N', '81': 'N', '82': 'N',  # N: Administrativas
            '84': 'O',  # O: Administración pública
            '85': 'P',  # P: Educación
            '86': 'Q', '87': 'Q', '88': 'Q',  # Q: Sanidad
            '90': 'R', '91': 'R', '92': 'R', '93': 'R',  # R: Artísticas
            '94': 'S', '95': 'S', '96': 'S',  # S: Otros servicios
        }
        
        try:
            division_num = str(division_code).zfill(2)
            return division_to_seccion.get(division_num, 'UNKNOWN')
        except:
            return 'UNKNOWN'