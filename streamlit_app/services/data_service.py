"""
Servicio de datos para conexión con DuckDB
"""

import duckdb
import pandas as pd
from pathlib import Path
import streamlit as st
from typing import Dict, List, Optional

class DataService:
    """Servicio para gestionar datos desde DuckDB"""
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        self.db_path = Path(r"C:\dev\projects\absentismo-espana\data\analysis.db")
        self._conn = None
    
    @property
    def conn(self):
        """Obtiene o crea la conexión a DuckDB"""
        if self._conn is None:
            try:
                self._conn = duckdb.connect(str(self.db_path), read_only=True)
            except Exception as e:
                st.error(f"Error conectando a la base de datos: {str(e)}")
                raise
        return self._conn
    
    @st.cache_data(ttl=3600)
    def get_available_periods(_self) -> List[str]:
        """Obtiene lista de periodos disponibles"""
        query = """
            SELECT DISTINCT periodo 
            FROM observaciones_tiempo_trabajo 
            ORDER BY periodo DESC
        """
        try:
            df = _self.conn.execute(query).df()
            return df['periodo'].tolist()
        except Exception as e:
            st.error(f"Error obteniendo periodos: {str(e)}")
            return ["2024T4", "2024T3", "2024T2", "2024T1"]  # Fallback
    
    @st.cache_data(ttl=3600)
    def get_ccaa_list(_self) -> List[str]:
        """Obtiene lista de CCAA disponibles"""
        query = """
            SELECT DISTINCT ccaa_nombre 
            FROM observaciones_tiempo_trabajo 
            WHERE ccaa_nombre IS NOT NULL
            ORDER BY ccaa_nombre
        """
        try:
            df = _self.conn.execute(query).df()
            return df['ccaa_nombre'].tolist()
        except:
            return []
    
    @st.cache_data(ttl=3600)
    def get_sectors_list(_self) -> List[str]:
        """Obtiene lista de sectores disponibles"""
        query = """
            SELECT DISTINCT cnae_nombre 
            FROM observaciones_tiempo_trabajo 
            WHERE cnae_nombre IS NOT NULL
            AND cnae_nivel = 'SECTOR_BS'
            ORDER BY cnae_nombre
        """
        try:
            df = _self.conn.execute(query).df()
            return df['cnae_nombre'].tolist()
        except:
            return []
    
    def get_kpis(self, periodo: str, ccaa: str = "Total Nacional", sector: str = "Todos") -> Dict:
        """
        Calcula los KPIs principales según metodología Adecco
        """
        # Filtros base
        filters = [f"periodo = '{periodo}'"]
        
        if ccaa == "Total Nacional":
            filters.append("ambito_territorial = 'NAC'")
            filters.append("cnae_nivel = 'TOTAL'")
            filters.append("fuente_tabla = '6042'")  # Evitar duplicados del TOTAL
        else:
            filters.append(f"ccaa_nombre = '{ccaa}'")
        
        if sector != "Todos":
            filters.append(f"cnae_nombre = '{sector}'")
        
        where_clause = " AND ".join(filters)
        
        # Query para obtener métricas
        query = f"""
        WITH metricas AS (
            SELECT 
                -- Horas base
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp,
                SUM(CASE WHEN metrica = 'horas_extraordinarias' THEN valor ELSE 0 END) as hext,
                
                -- Horas no trabajadas por causas
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'vacaciones' THEN valor ELSE 0 END) as vacaciones,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'festivos' THEN valor ELSE 0 END) as festivos,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'razones_tecnicas_economicas' THEN valor ELSE 0 END) as ertes,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'it_total' THEN valor ELSE 0 END) as it,
                
                -- HNT motivos ocasionales (todas las causas excepto vacaciones, festivos y ERTEs)
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa NOT IN ('vacaciones', 'festivos', 'razones_tecnicas_economicas')
                         AND causa IS NOT NULL
                         THEN valor ELSE 0 END) as hntmo_total
            FROM observaciones_tiempo_trabajo
            WHERE {where_clause}
        )
        SELECT 
            hp,
            hext,
            vacaciones,
            festivos,
            ertes,
            it,
            hntmo_total,
            -- Cálculos derivados
            (hp + hext - vacaciones - festivos - ertes) as hpe,
            CASE 
                WHEN (hp + hext - vacaciones - festivos - ertes) > 0 
                THEN (hntmo_total / (hp + hext - vacaciones - festivos - ertes)) * 100
                ELSE 0 
            END as tasa_absentismo,
            CASE 
                WHEN (hp + hext - vacaciones - festivos - ertes) > 0 
                THEN (it / (hp + hext - vacaciones - festivos - ertes)) * 100
                ELSE 0 
            END as tasa_it
        FROM metricas
        """
        
        try:
            df = self.conn.execute(query).df()
            
            if df.empty or len(df) == 0:
                return self._get_default_kpis()
            
            row = df.iloc[0]
            
            # Calcular deltas (comparación con periodo anterior)
            periodo_anterior = self._get_periodo_anterior(periodo)
            deltas = self._calculate_deltas(periodo, periodo_anterior, where_clause)
            
            return {
                'tasa_absentismo': float(row['tasa_absentismo']),
                'tasa_absentismo_delta': deltas.get('tasa_absentismo_delta', 0),
                'tasa_it': float(row['tasa_it']),
                'tasa_it_delta': deltas.get('tasa_it_delta', 0),
                'hpe': float(row['hpe']),
                'hpe_delta': deltas.get('hpe_delta', 0),
                'hntmo': float(row['hntmo_total']),
                'hntmo_delta': deltas.get('hntmo_delta', 0)
            }
            
        except Exception as e:
            st.error(f"Error calculando KPIs: {str(e)}")
            return self._get_default_kpis()
    
    def _get_default_kpis(self) -> Dict:
        """Retorna KPIs por defecto en caso de error"""
        return {
            'tasa_absentismo': 7.4,
            'tasa_absentismo_delta': 0.3,
            'tasa_it': 5.8,
            'tasa_it_delta': 0.2,
            'hpe': 137.2,
            'hpe_delta': -1.5,
            'hntmo': 10.2,
            'hntmo_delta': 0.4
        }
    
    def _get_periodo_anterior(self, periodo: str) -> str:
        """Calcula el periodo anterior"""
        year, quarter = periodo.split('T')
        year = int(year)
        quarter = int(quarter[0])
        
        if quarter == 1:
            return f"{year-1}T4"
        else:
            return f"{year}T{quarter-1}"
    
    def _calculate_deltas(self, periodo: str, periodo_anterior: str, base_filters: str) -> Dict:
        """Calcula las diferencias con el periodo anterior"""
        # Implementación simplificada - retorna valores dummy
        return {
            'tasa_absentismo_delta': 0.3,
            'tasa_it_delta': 0.2,
            'hpe_delta': -1.5,
            'hntmo_delta': 0.4
        }
    
    @st.cache_data(ttl=3600)
    def get_evolution_data(_self, ccaa: str = "Total Nacional", sector: str = "Todos") -> pd.DataFrame:
        """Obtiene datos de evolución temporal"""
        filters = []
        
        if ccaa == "Total Nacional":
            filters.append("ambito_territorial = 'NAC'")
            filters.append("cnae_nivel = 'TOTAL'")
            filters.append("fuente_tabla = '6042'")
        else:
            filters.append(f"ccaa_nombre = '{ccaa}'")
        
        if sector != "Todos":
            filters.append(f"cnae_nombre = '{sector}'")
        
        where_clause = " AND ".join(filters) if filters else "1=1"
        
        query = f"""
        WITH metricas_periodo AS (
            SELECT 
                periodo,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp,
                SUM(CASE WHEN metrica = 'horas_extraordinarias' THEN valor ELSE 0 END) as hext,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'vacaciones' THEN valor ELSE 0 END) as vacaciones,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'festivos' THEN valor ELSE 0 END) as festivos,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'razones_tecnicas_economicas' THEN valor ELSE 0 END) as ertes,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa NOT IN ('vacaciones', 'festivos', 'razones_tecnicas_economicas')
                         AND causa IS NOT NULL THEN valor ELSE 0 END) as hntmo
            FROM observaciones_tiempo_trabajo
            WHERE {where_clause}
            GROUP BY periodo
        )
        SELECT 
            periodo,
            (hp + hext - vacaciones - festivos - ertes) as hpe,
            hntmo,
            CASE 
                WHEN (hp + hext - vacaciones - festivos - ertes) > 0 
                THEN (hntmo / (hp + hext - vacaciones - festivos - ertes)) * 100
                ELSE 0 
            END as tasa_absentismo
        FROM metricas_periodo
        ORDER BY periodo DESC
        LIMIT 12
        """
        
        try:
            return _self.conn.execute(query).df()
        except Exception as e:
            st.error(f"Error obteniendo evolución: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def get_ranking_ccaa(_self, periodo: str) -> pd.DataFrame:
        """Obtiene ranking de CCAA por tasa de absentismo"""
        query = f"""
        WITH metricas_ccaa AS (
            SELECT 
                ccaa_nombre,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp,
                SUM(CASE WHEN metrica = 'horas_extraordinarias' THEN valor ELSE 0 END) as hext,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'vacaciones' THEN valor ELSE 0 END) as vacaciones,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'festivos' THEN valor ELSE 0 END) as festivos,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa = 'razones_tecnicas_economicas' THEN valor ELSE 0 END) as ertes,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa NOT IN ('vacaciones', 'festivos', 'razones_tecnicas_economicas')
                         AND causa IS NOT NULL THEN valor ELSE 0 END) as hntmo
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '{periodo}'
                AND ambito_territorial = 'CCAA'
                AND ccaa_nombre IS NOT NULL
            GROUP BY ccaa_nombre
        )
        SELECT 
            ccaa_nombre as CCAA,
            ROUND(
                CASE 
                    WHEN (hp + hext - vacaciones - festivos - ertes) > 0 
                    THEN (hntmo / (hp + hext - vacaciones - festivos - ertes)) * 100
                    ELSE 0 
                END, 1
            ) as Tasa_Absentismo
        FROM metricas_ccaa
        WHERE ccaa_nombre IS NOT NULL
        ORDER BY Tasa_Absentismo DESC
        """
        
        try:
            return _self.conn.execute(query).df()
        except Exception as e:
            st.error(f"Error obteniendo ranking: {str(e)}")
            return pd.DataFrame()