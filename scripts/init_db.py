"""
Crea una base DuckDB mínima con datos de ejemplo para el dashboard.
Uso: python scripts/init_db.py  (usa APP_DB_PATH o data/analysis.db)
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb


def db_path() -> Path:
    return Path(os.getenv("APP_DB_PATH", str(Path("data") / "analysis.db")))


def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    path = db_path()
    ensure_parent(path)
    con = duckdb.connect(str(path))

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS observaciones_tiempo_trabajo (
            periodo TEXT,
            ambito_territorial TEXT,
            ccaa_nombre TEXT,
            cnae_nivel TEXT,
            cnae_nombre TEXT,
            tipo_jornada TEXT,
            fuente_tabla TEXT,
            metrica TEXT,
            causa TEXT,
            valor DOUBLE
        );
        """
    )

    # Datos de ejemplo (Total Nacional)
    rows = []
    periods = ["2024T2", "2024T3", "2024T4", "2025T1"]
    for i, periodo in enumerate(periods):
        hp = 150.0 + i  # horas pactadas
        hext = 5.0 + i * 0.2  # horas extra
        vacaciones = 10.0
        festivos = 3.0
        ertes = 0.5
        it_total = 8.0 + i * 0.1
        rows += [
            (periodo, "NAC", None, "TOTAL", None, "TOTAL", "6042", "horas_pactadas", None, hp),
            (periodo, "NAC", None, "TOTAL", None, "TOTAL", "6042", "horas_extraordinarias", None, hext),
            (periodo, "NAC", None, "TOTAL", None, "TOTAL", "6042", "horas_no_trabajadas", "vacaciones", vacaciones),
            (periodo, "NAC", None, "TOTAL", None, "TOTAL", "6042", "horas_no_trabajadas", "festivos", festivos),
            (periodo, "NAC", None, "TOTAL", None, "TOTAL", "6042", "horas_no_trabajadas", "razones_tecnicas_economicas", ertes),
            (periodo, "NAC", None, "TOTAL", None, "TOTAL", "6042", "horas_no_trabajadas", "it_total", it_total),
        ]

    # Ranking por CCAA (un par de ejemplos para 2024T4)
    periodo = "2024T4"
    for ccaa, hntmo, hp_base in [("Madrid", 11.0, 140.0), ("Cataluña", 9.5, 142.0)]:
        rows += [
            (periodo, "CCAA", ccaa, "SECCION", None, "TOTAL", "6063", "horas_pactadas", None, hp_base),
            (periodo, "CCAA", ccaa, "SECCION", None, "TOTAL", "6063", "horas_extraordinarias", None, 4.0),
            (periodo, "CCAA", ccaa, "SECCION", None, "TOTAL", "6063", "horas_no_trabajadas", "vacaciones", 8.0),
            (periodo, "CCAA", ccaa, "SECCION", None, "TOTAL", "6063", "horas_no_trabajadas", "festivos", 2.5),
            (periodo, "CCAA", ccaa, "SECCION", None, "TOTAL", "6063", "horas_no_trabajadas", "razones_tecnicas_economicas", 0.3),
            (periodo, "CCAA", ccaa, "SECCION", None, "TOTAL", "6063", "horas_no_trabajadas", "it_total", hntmo),
        ]

    con.executemany(
        """
        INSERT INTO observaciones_tiempo_trabajo
        (periodo, ambito_territorial, ccaa_nombre, cnae_nivel, cnae_nombre, tipo_jornada,
         fuente_tabla, metrica, causa, valor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    con.close()
    print(f"Base creada con {len(rows)} registros en {path}")


if __name__ == "__main__":
    main()

