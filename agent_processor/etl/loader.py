"""
Loader para cargar datos transformados a DuckDB
"""

import duckdb
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Loader:
    """
    Cargador de datos a DuckDB para análisis ETCL
    """
    
    def __init__(self, db_path: Path):
        """
        Inicializa el loader con la ruta a la base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos DuckDB
        """
        self.db_path = db_path
        self.conn = None
        self.table_name = 'observaciones_tiempo_trabajo'
        
    def connect(self):
        """
        Establece conexión con DuckDB
        """
        try:
            self.conn = duckdb.connect(str(self.db_path))
            logger.info(f"Conectado a DuckDB: {self.db_path}")
        except Exception as e:
            logger.error(f"Error conectando a DuckDB: {str(e)}")
            raise
            
    def disconnect(self):
        """
        Cierra la conexión con DuckDB
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Desconectado de DuckDB")
            
    def create_schema(self):
        """
        Crea el schema de la tabla si no existe
        """
        if not self.conn:
            self.connect()
            
        try:
            # Crear tabla principal
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                -- Campos temporales
                periodo VARCHAR(6) NOT NULL,
                periodo_inicio DATE NOT NULL,
                periodo_fin DATE NOT NULL,
                
                -- Dimensiones territoriales
                ambito_territorial VARCHAR(4) NOT NULL,
                ccaa_codigo VARCHAR(2),
                ccaa_nombre VARCHAR(50),
                
                -- Dimensiones sectoriales
                cnae_nivel VARCHAR(10) NOT NULL,
                cnae_codigo VARCHAR(5),
                cnae_nombre VARCHAR(200),
                jerarquia_sector_cod VARCHAR(50),
                jerarquia_sector_lbl VARCHAR(100),
                
                -- Dimensiones laborales
                tipo_jornada VARCHAR(8),
                
                -- Métricas
                metrica VARCHAR(25) NOT NULL,
                causa VARCHAR(25),
                valor DECIMAL(12,3) NOT NULL,
                unidad VARCHAR(30) NOT NULL,
                
                -- Metadatos
                fuente_tabla VARCHAR(4) NOT NULL,
                es_total_ccaa BOOLEAN NOT NULL,
                es_total_cnae BOOLEAN NOT NULL,
                es_total_jornada BOOLEAN NOT NULL,
                rol_grano VARCHAR(30) NOT NULL,
                version_datos VARCHAR(10),
                fecha_carga TIMESTAMP,
                
                -- Constraints
                CHECK (ambito_territorial IN ('NAC', 'CCAA')),
                CHECK (cnae_nivel IN ('TOTAL', 'SECTOR_BS', 'SECCION', 'DIVISION')),
                CHECK (tipo_jornada IN ('TOTAL', 'COMPLETA', 'PARCIAL') OR tipo_jornada IS NULL),
                CHECK (metrica IN ('horas_pactadas', 'horas_pagadas', 'horas_efectivas', 'horas_extraordinarias', 'horas_no_trabajadas')),
                CHECK (valor >= 0)
            );
            """
            
            self.conn.execute(create_table_sql)
            logger.info(f"Schema de tabla '{self.table_name}' creado/verificado")
            
            # Crear índices para mejorar rendimiento
            indices = [
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_periodo ON {self.table_name}(periodo)",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_metrica_causa ON {self.table_name}(metrica, causa)",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_rol_grano ON {self.table_name}(rol_grano)",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_ambito ON {self.table_name}(ambito_territorial, ccaa_codigo)",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_cnae ON {self.table_name}(cnae_nivel, cnae_codigo)"
            ]
            
            for idx_sql in indices:
                self.conn.execute(idx_sql)
            
            logger.info("Índices creados/verificados")
            
        except Exception as e:
            logger.error(f"Error creando schema: {str(e)}")
            raise
            
    def load(self, df: pd.DataFrame, replace: bool = False) -> Dict[str, Any]:
        """
        Carga datos en DuckDB
        
        Args:
            df: DataFrame con datos transformados
            replace: Si True, reemplaza todos los datos existentes
            
        Returns:
            Diccionario con estadísticas de carga
        """
        stats = {
            'inicio': datetime.now(),
            'registros_entrada': len(df),
            'registros_cargados': 0,
            'tabla': self.table_name,
            'modo': 'replace' if replace else 'append'
        }
        
        try:
            if not self.conn:
                self.connect()
            
            # Crear schema si no existe
            self.create_schema()
            
            # Si replace, limpiar tabla primero
            if replace:
                self.conn.execute(f"DELETE FROM {self.table_name}")
                logger.info(f"Tabla {self.table_name} limpiada para carga completa")
            
            # Asegurar que las columnas están en el orden correcto
            column_order = [
                'periodo', 'periodo_inicio', 'periodo_fin',
                'ambito_territorial', 'ccaa_codigo', 'ccaa_nombre',
                'cnae_nivel', 'cnae_codigo', 'cnae_nombre',
                'jerarquia_sector_cod', 'jerarquia_sector_lbl',
                'tipo_jornada',
                'metrica', 'causa', 'valor', 'unidad',
                'fuente_tabla',
                'es_total_ccaa', 'es_total_cnae', 'es_total_jornada',
                'rol_grano', 'version_datos', 'fecha_carga'
            ]
            
            # Reordenar columnas del DataFrame
            df_ordered = df[column_order]
            
            # Insertar datos
            # DuckDB puede insertar directamente desde un DataFrame de pandas
            self.conn.register('df_temp', df_ordered)
            
            insert_sql = f"""
            INSERT INTO {self.table_name} 
            SELECT * FROM df_temp
            """
            
            self.conn.execute(insert_sql)
            
            # Obtener conteo de registros insertados
            result = self.conn.execute(f"SELECT COUNT(*) FROM {self.table_name}").fetchone()
            total_records = result[0] if result else 0
            
            stats['registros_cargados'] = len(df)
            stats['total_en_tabla'] = total_records
            stats['fin'] = datetime.now()
            stats['duracion'] = str(stats['fin'] - stats['inicio'])
            stats['exitoso'] = True
            
            logger.info(f"Carga completada: {stats['registros_cargados']} registros en {stats['duracion']}")
            
        except Exception as e:
            logger.error(f"Error durante la carga: {str(e)}")
            stats['exitoso'] = False
            stats['error'] = str(e)
            raise
        finally:
            # Desregistrar el DataFrame temporal
            if self.conn:
                try:
                    self.conn.unregister('df_temp')
                except:
                    pass
        
        return stats
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la base de datos
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.conn:
            self.connect()
        
        stats = {}
        
        try:
            # Total de registros
            result = self.conn.execute(f"SELECT COUNT(*) FROM {self.table_name}").fetchone()
            stats['total_registros'] = result[0] if result else 0
            
            # Registros por tabla fuente
            result = self.conn.execute(f"""
                SELECT fuente_tabla, COUNT(*) as count 
                FROM {self.table_name} 
                GROUP BY fuente_tabla
            """).fetchall()
            stats['por_tabla'] = {row[0]: row[1] for row in result}
            
            # Registros por periodo
            result = self.conn.execute(f"""
                SELECT periodo, COUNT(*) as count 
                FROM {self.table_name} 
                GROUP BY periodo 
                ORDER BY periodo DESC 
                LIMIT 5
            """).fetchall()
            stats['ultimos_periodos'] = {row[0]: row[1] for row in result}
            
            # Registros por métrica
            result = self.conn.execute(f"""
                SELECT metrica, COUNT(*) as count 
                FROM {self.table_name} 
                GROUP BY metrica
            """).fetchall()
            stats['por_metrica'] = {row[0]: row[1] for row in result}
            
            # Verificar integridad (valores nulos en campos requeridos)
            result = self.conn.execute(f"""
                SELECT COUNT(*) 
                FROM {self.table_name} 
                WHERE periodo IS NULL 
                   OR metrica IS NULL 
                   OR valor IS NULL
            """).fetchone()
            stats['registros_invalidos'] = result[0] if result else 0
            
            # Tamaño de la base de datos
            db_file = Path(self.db_path)
            if db_file.exists():
                stats['tamano_db_mb'] = round(db_file.stat().st_size / 1024 / 1024, 2)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            stats['error'] = str(e)
        
        return stats
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y retorna el resultado como DataFrame
        
        Args:
            query: Consulta SQL a ejecutar
            
        Returns:
            DataFrame con los resultados
        """
        if not self.conn:
            self.connect()
        
        try:
            result = self.conn.execute(query).fetchdf()
            return result
        except Exception as e:
            logger.error(f"Error ejecutando query: {str(e)}")
            raise
    
    def create_analysis_views(self):
        """
        Crea vistas materializadas para análisis común
        """
        if not self.conn:
            self.connect()
        
        views = {
            # Vista de tasas de absentismo
            'v_tasa_absentismo': """
                CREATE OR REPLACE VIEW v_tasa_absentismo AS
                SELECT 
                    periodo,
                    ambito_territorial,
                    ccaa_codigo,
                    ccaa_nombre,
                    cnae_nivel,
                    cnae_codigo,
                    cnae_nombre,
                    tipo_jornada,
                    SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as horas_pactadas,
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                             AND causa IN ('it_total', 'maternidad_paternidad', 'permisos_retribuidos', 
                                          'conflictividad', 'representacion_sindical', 'otros')
                        THEN valor ELSE 0 END) as horas_absentismo,
                    ROUND(
                        SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                                 AND causa IN ('it_total', 'maternidad_paternidad', 'permisos_retribuidos', 
                                              'conflictividad', 'representacion_sindical', 'otros')
                            THEN valor ELSE 0 END) * 100.0 / 
                        NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0),
                        2
                    ) as tasa_absentismo
                FROM observaciones_tiempo_trabajo
                GROUP BY periodo, ambito_territorial, ccaa_codigo, ccaa_nombre,
                         cnae_nivel, cnae_codigo, cnae_nombre, tipo_jornada
            """,
            
            # Vista de series temporales nacionales
            'v_serie_nacional': """
                CREATE OR REPLACE VIEW v_serie_nacional AS
                SELECT 
                    periodo,
                    metrica,
                    causa,
                    AVG(valor) as valor_promedio,
                    SUM(valor) as valor_total,
                    COUNT(*) as num_observaciones
                FROM observaciones_tiempo_trabajo
                WHERE ambito_territorial = 'NAC'
                  AND es_total_cnae = TRUE
                  AND es_total_jornada = TRUE
                GROUP BY periodo, metrica, causa
                ORDER BY periodo, metrica, causa
            """,
            
            # Vista de comparativa por CCAA
            'v_comparativa_ccaa': """
                CREATE OR REPLACE VIEW v_comparativa_ccaa AS
                SELECT 
                    periodo,
                    ccaa_nombre,
                    metrica,
                    AVG(valor) as valor_promedio
                FROM observaciones_tiempo_trabajo
                WHERE ambito_territorial = 'CCAA'
                  AND es_total_cnae = TRUE
                  AND es_total_jornada = TRUE
                GROUP BY periodo, ccaa_nombre, metrica
                ORDER BY periodo, ccaa_nombre, metrica
            """
        }
        
        try:
            for view_name, view_sql in views.items():
                self.conn.execute(view_sql)
                logger.info(f"Vista '{view_name}' creada")
            
            logger.info("Todas las vistas de análisis creadas exitosamente")
            
        except Exception as e:
            logger.error(f"Error creando vistas: {str(e)}")
            raise
    
    def __enter__(self):
        """Context manager entrada"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager salida"""
        self.disconnect()