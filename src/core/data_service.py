"""
Data service agnóstico de frontend para consultas a DuckDB.
"""

from __future__ import annotations

import os
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import duckdb
import pandas as pd


log = logging.getLogger(__name__)


def _db_path() -> Path:
    p = os.getenv("APP_DB_PATH", str(Path("data") / "analysis.db"))
    return Path(p)


def _connect() -> duckdb.DuckDBPyConnection:
    path = _db_path()
    try:
        return duckdb.connect(str(path), read_only=True)
    except Exception as e:
        log.error("No se pudo abrir DuckDB en %s: %s", path, e)
        # Conexión in-memory para evitar romper la app; devolverá vacíos
        return duckdb.connect(database=":memory:")


class DataService:
    def __init__(self) -> None:
        self._conn = None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self._conn = _connect()
        return self._conn

    @lru_cache(maxsize=1)
    def get_available_periods(self) -> List[str]:
        q = """
            SELECT DISTINCT periodo
            FROM observaciones_tiempo_trabajo
            ORDER BY periodo DESC
        """
        try:
            df = self.conn.execute(q).df()
            return df["periodo"].tolist()
        except Exception as e:
            log.warning("Fallo get_available_periods: %s", e)
            return ["2024T4", "2024T3", "2024T2", "2024T1"]

    @lru_cache(maxsize=1)
    def get_ccaa_list(self) -> List[str]:
        q = """
            SELECT DISTINCT ccaa_nombre
            FROM observaciones_tiempo_trabajo
            WHERE ccaa_nombre IS NOT NULL
            ORDER BY ccaa_nombre
        """
        try:
            df = self.conn.execute(q).df()
            return df["ccaa_nombre"].tolist()
        except Exception as e:
            log.warning("Fallo get_ccaa_list: %s", e)
            return []

    @lru_cache(maxsize=1)
    def get_sectors_list(self) -> List[str]:
        q = """
            SELECT DISTINCT cnae_nombre
            FROM observaciones_tiempo_trabajo
            WHERE cnae_nombre IS NOT NULL
              AND cnae_nivel = 'SECTOR_BS'
            ORDER BY cnae_nombre
        """
        try:
            df = self.conn.execute(q).df()
            return df["cnae_nombre"].tolist()
        except Exception as e:
            log.warning("Fallo get_sectors_list: %s", e)
            return []

    def _kpis_query(self, where_clause: str) -> str:
        return f"""
        WITH metricas AS (
            SELECT 
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp,
                SUM(CASE WHEN metrica = 'horas_extraordinarias' THEN valor ELSE 0 END) as hext,
                COALESCE(
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones_y_fiestas' THEN valor END),
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones' THEN valor END) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'festivos' THEN valor END), 0)
                ) as vac_fest,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'razones_tecnicas_economicas' THEN valor ELSE 0 END) as ertes,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) as it,
                (
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'maternidad_paternidad' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'permisos_retribuidos' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'compensacion_extras' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'otras_remuneradas' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'perdidas_lugar_trabajo' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'conflictividad' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'otras_no_remuneradas' THEN valor END), 0)
                ) as hntmo_total
            FROM observaciones_tiempo_trabajo
            WHERE {where_clause}
        )
        SELECT 
            hp, hext, vac_fest, ertes, it, hntmo_total,
            (hp + hext - vac_fest - ertes) as hpe,
            CASE WHEN (hp + hext - vac_fest - ertes) > 0
                 THEN (hntmo_total / (hp + hext - vac_fest - ertes)) * 100 ELSE 0 END as tasa_absentismo,
            CASE WHEN (hp + hext - vac_fest - ertes) > 0
                 THEN (it / (hp + hext - vac_fest - ertes)) * 100 ELSE 0 END as tasa_it
        FROM metricas
        """

    def get_kpis(self, periodo: str, ccaa: str = "Total Nacional", sector: str = "Todos") -> Dict:
        filters = [f"periodo = '{periodo}'"]
        if ccaa == "Total Nacional":
            filters += [
                "ambito_territorial = 'NAC'",
                "cnae_nivel = 'TOTAL'",
                "(tipo_jornada IS NULL)",
                "fuente_tabla = '6044'",
            ]
        else:
            filters.append(f"ccaa_nombre = '{ccaa}'")
        if sector != "Todos":
            filters.append(f"cnae_nombre = '{sector}'")
        where_clause = " AND ".join(filters)
        try:
            df = self.conn.execute(self._kpis_query(where_clause)).df()
            if df.empty and ccaa == "Total Nacional":
                where_fb = where_clause.replace("fuente_tabla = '6044'", "fuente_tabla = '6042'")
                where_fb = where_fb.replace("(tipo_jornada IS NULL)", "(tipo_jornada = 'TOTAL')")
                df = self.conn.execute(self._kpis_query(where_fb)).df()
            if df.empty:
                return self._defaults()
            r = df.iloc[0]
            return {
                "tasa_absentismo": float(r["tasa_absentismo"]),
                "tasa_it": float(r["tasa_it"]),
                "hpe": float(r["hpe"]),
                "hntmo": float(r["hntmo_total"]),
            }
        except Exception as e:
            log.warning("Fallo get_kpis: %s", e)
            return self._defaults()

    def _defaults(self) -> Dict:
        return {"tasa_absentismo": 7.4, "tasa_it": 5.8, "hpe": 137.2, "hntmo": 10.2}

    def get_evolution_data(self, ccaa: str = "Total Nacional", sector: str = "Todos") -> pd.DataFrame:
        filters = []
        if ccaa == "Total Nacional":
            filters += [
                "ambito_territorial = 'NAC'",
                "cnae_nivel = 'TOTAL'",
                "fuente_tabla = '6044'",
                "(tipo_jornada IS NULL)",
            ]
        else:
            filters.append(f"ccaa_nombre = '{ccaa}'")
        if sector != "Todos":
            filters.append(f"cnae_nombre = '{sector}'")
        where_clause = " AND ".join(filters) if filters else "1=1"

        q = f"""
        WITH metricas_periodo AS (
            SELECT periodo,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp,
                SUM(CASE WHEN metrica = 'horas_extraordinarias' THEN valor ELSE 0 END) as hext,
                COALESCE(
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones_y_fiestas' THEN valor END),
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones' THEN valor END) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'festivos' THEN valor END), 0)
                ) as vac_fest,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'razones_tecnicas_economicas' THEN valor ELSE 0 END) as ertes,
                (
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'maternidad_paternidad' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'permisos_retribuidos' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'compensacion_extras' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'otras_remuneradas' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'perdidas_lugar_trabajo' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'conflictividad' THEN valor END), 0) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'otras_no_remuneradas' THEN valor END), 0)
                ) as hntmo
            FROM observaciones_tiempo_trabajo
            WHERE {where_clause}
            GROUP BY periodo
        )
        SELECT periodo,
               (hp + hext - vac_fest - ertes) as hpe,
               hntmo,
               CASE WHEN (hp + hext - vac_fest - ertes) > 0
                    THEN (hntmo / (hp + hext - vac_fest - ertes)) * 100 ELSE 0 END as tasa_absentismo
        FROM metricas_periodo
        ORDER BY periodo ASC
        """
        try:
            df = self.conn.execute(q).df()
            if df.empty and ccaa == "Total Nacional":
                q_fb = q.replace("fuente_tabla = '6044'", "fuente_tabla = '6042'")
                q_fb = q_fb.replace("(tipo_jornada IS NULL)", "(tipo_jornada = 'TOTAL')")
                df = self.conn.execute(q_fb).df()
            return df
        except Exception as e:
            log.warning("Fallo get_evolution_data: %s", e)
            return pd.DataFrame()

    def get_ranking_ccaa(self, periodo: str) -> pd.DataFrame:
        q = f"""
        WITH metricas_ccaa AS (
            SELECT ccaa_nombre,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp,
                SUM(CASE WHEN metrica = 'horas_extraordinarias' THEN valor ELSE 0 END) as hext,
                COALESCE(
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones_y_fiestas' THEN valor END),
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones' THEN valor END) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'festivos' THEN valor END), 0)
                ) as vac_fest,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'razones_tecnicas_economicas' THEN valor ELSE 0 END) as ertes,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' 
                         AND causa NOT IN ('vacaciones', 'festivos', 'razones_tecnicas_economicas')
                         AND causa IS NOT NULL THEN valor ELSE 0 END) as hntmo
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '{periodo}'
              AND ambito_territorial = 'CCAA'
              AND (tipo_jornada = 'TOTAL' OR tipo_jornada = 'AMBAS' OR tipo_jornada IS NULL)
              AND fuente_tabla = '6063'
              AND ccaa_nombre IS NOT NULL
            GROUP BY ccaa_nombre
        )
        SELECT ccaa_nombre as CCAA,
               ROUND(CASE WHEN (hp + hext - vac_fest - ertes) > 0
                          THEN (hntmo / (hp + hext - vac_fest - ertes)) * 100 ELSE 0 END, 1) as Tasa_Absentismo
        FROM metricas_ccaa
        WHERE ccaa_nombre IS NOT NULL
        ORDER BY Tasa_Absentismo DESC
        """
        try:
            return self.conn.execute(q).df()
        except Exception as e:
            log.warning("Fallo get_ranking_ccaa: %s", e)
            return pd.DataFrame()

    def get_evolution_it_data(self, ccaa: str = "Total Nacional", sector: str = "Todos") -> pd.DataFrame:
        filters = []
        if ccaa == "Total Nacional":
            filters += [
                "ambito_territorial = 'NAC'",
                "cnae_nivel = 'TOTAL'",
                "fuente_tabla = '6044'",
                "(tipo_jornada IS NULL)",
            ]
        else:
            filters.append(f"ccaa_nombre = '{ccaa}'")
        if sector != "Todos":
            filters.append(f"cnae_nombre = '{sector}'")
        where_clause = " AND ".join(filters) if filters else "1=1"

        q = f"""
        WITH metricas_periodo AS (
            SELECT periodo,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp,
                SUM(CASE WHEN metrica = 'horas_extraordinarias' THEN valor ELSE 0 END) as hext,
                COALESCE(
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones_y_fiestas' THEN valor END),
                    SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'vacaciones' THEN valor END) +
                    COALESCE(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'festivos' THEN valor END), 0)
                ) as vac_fest,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'razones_tecnicas_economicas' THEN valor ELSE 0 END) as ertes,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) as it
            FROM observaciones_tiempo_trabajo
            WHERE {where_clause}
            GROUP BY periodo
        )
        SELECT periodo,
               (hp + hext - vac_fest - ertes) as hpe,
               CASE WHEN (hp + hext - vac_fest - ertes) > 0
                    THEN (it / (hp + hext - vac_fest - ertes)) * 100 ELSE 0 END as tasa_it
        FROM metricas_periodo
        ORDER BY periodo ASC
        """
        try:
            df = self.conn.execute(q).df()
            if df.empty and ccaa == "Total Nacional":
                q_fb = q.replace("fuente_tabla = '6044'", "fuente_tabla = '6042'")
                q_fb = q_fb.replace("(tipo_jornada IS NULL)", "(tipo_jornada = 'TOTAL')")
                df = self.conn.execute(q_fb).df()
            return df
        except Exception as e:
            log.warning("Fallo get_evolution_it_data: %s", e)
            return pd.DataFrame()
