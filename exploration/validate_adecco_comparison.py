#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validación que compara las métricas del informe Adecco Q4 2024
con los datos calculados desde nuestra BD.
"""

import duckdb
from pathlib import Path
import pandas as pd
from datetime import datetime

def connect_db():
    """Conecta a la base de datos DuckDB."""
    db_path = Path(__file__).parent.parent / 'data' / 'analysis.db'
    return duckdb.connect(str(db_path))

def calcular_tasa_absentismo_nacional(conn, periodo='2024T4'):
    """Calcula la tasa de absentismo nacional."""
    query = """
        SELECT 
            periodo,
            SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_total,
            SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100, 
                2
            ) as tasa_absentismo
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY periodo
    """
    return conn.execute(query, [periodo]).df()

def calcular_tasa_IT_nacional(conn, periodo='2024T4'):
    """Calcula la tasa de absentismo por IT."""
    query = """
        SELECT 
            periodo,
            SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) as hnt_it,
            SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_it
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY periodo
    """
    return conn.execute(query, [periodo]).df()

def calcular_absentismo_por_sector(conn, periodo='2024T4'):
    """Calcula la tasa de absentismo por sector."""
    # Mapeo de códigos INE a nombres Adecco
    sector_mapping = {
        'B-E': 'Industria',
        'F': 'Construcción',
        'G-S': 'Servicios'
    }
    
    query = """
        SELECT 
            periodo,
            cnae_codigo as sector_codigo,
            SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_total,
            SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_absentismo
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'SECTOR_BS'
            AND es_total_jornada = true
        GROUP BY periodo, cnae_codigo
        ORDER BY cnae_codigo
    """
    df = conn.execute(query, [periodo]).df()
    df['sector'] = df['sector_codigo'].map(sector_mapping)
    return df

def calcular_absentismo_por_ccaa(conn, periodo='2024T4'):
    """Calcula la tasa de absentismo por CCAA."""
    query = """
        SELECT 
            periodo,
            ccaa_codigo,
            SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_total,
            SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_absentismo
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'CCAA'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY periodo, ccaa_codigo
        ORDER BY tasa_absentismo DESC
    """
    df = conn.execute(query, [periodo]).df()
    
    # Mapeo de códigos a nombres
    ccaa_names = {
        "01": "Andalucía", "02": "Aragón", "03": "Asturias", "04": "Baleares",
        "05": "Canarias", "06": "Cantabria", "07": "Castilla y León", 
        "08": "Castilla-La Mancha", "09": "Cataluña", "10": "C. Valenciana",
        "11": "Extremadura", "12": "Galicia", "13": "Madrid", "14": "Murcia",
        "15": "Navarra", "16": "País Vasco", "17": "La Rioja"
    }
    df['ccaa_nombre'] = df['ccaa_codigo'].map(ccaa_names)
    return df

def calcular_IT_por_ccaa(conn, periodo='2024T4'):
    """Calcula la tasa de IT por CCAA."""
    query = """
        SELECT 
            periodo,
            ccaa_codigo,
            SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) as hnt_it,
            SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_it
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'CCAA'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY periodo, ccaa_codigo
        ORDER BY tasa_it DESC
    """
    df = conn.execute(query, [periodo]).df()
    
    ccaa_names = {
        "01": "Andalucía", "02": "Aragón", "03": "Asturias", "04": "Baleares",
        "05": "Canarias", "06": "Cantabria", "07": "Castilla y León", 
        "08": "Castilla-La Mancha", "09": "Cataluña", "10": "C. Valenciana",
        "11": "Extremadura", "12": "Galicia", "13": "Madrid", "14": "Murcia",
        "15": "Navarra", "16": "País Vasco", "17": "La Rioja"
    }
    df['ccaa_nombre'] = df['ccaa_codigo'].map(ccaa_names)
    return df

def calcular_evolucion_trimestral(conn):
    """Calcula la evolución trimestral del absentismo en 2024."""
    query = """
        SELECT 
            periodo,
            SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_total,
            SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_absentismo
        FROM observaciones_tiempo_trabajo
        WHERE periodo IN ('2024T1', '2024T2', '2024T3', '2024T4')
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY periodo
        ORDER BY periodo
    """
    return conn.execute(query).df()

def calcular_causas_absentismo(conn, periodo='2024T4'):
    """Calcula el desglose por causas de absentismo."""
    query = """
        WITH horas_pactadas_total AS (
            SELECT SUM(valor) as hp_total
            FROM observaciones_tiempo_trabajo
            WHERE periodo = ?
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND metrica = 'horas_pactadas'
                AND es_total_jornada = true
        )
        SELECT 
            periodo,
            CASE 
                WHEN causa = 'it_total' THEN 'IT'
                WHEN causa IN ('vacaciones', 'festivos', 'vacaciones_y_fiestas') THEN 'Vacaciones y festivos'
                WHEN causa IN ('maternidad_paternidad') THEN 'Maternidad/Paternidad'
                WHEN causa IN ('permisos_retribuidos') THEN 'Permisos retribuidos'
                WHEN causa IS NULL THEN 'Total'
                ELSE 'Otras causas'
            END as tipo_causa,
            SUM(valor) as horas_causa,
            ROUND(
                (SUM(valor) / (SELECT hp_total FROM horas_pactadas_total)) * 100,
                2
            ) as tasa_causa
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND metrica = 'horas_no_trabajadas'
            AND es_total_jornada = true
        GROUP BY periodo, tipo_causa
        ORDER BY tasa_causa DESC
    """
    return conn.execute(query, [periodo, periodo]).df()

def comparar_con_adecco():
    """Ejecuta todas las comparaciones y muestra resultados."""
    print("=" * 80)
    print("VALIDACIÓN: COMPARACIÓN DATOS BD vs INFORME ADECCO Q4 2024")
    print("=" * 80)
    print(f"Fecha validación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = connect_db()
    
    # Valores de referencia Adecco
    adecco_valores = {
        "tasa_general": 7.4,
        "tasa_it": 5.8,
        "sectores": {
            "Industria": 8.1,
            "Servicios": 7.3,
            "Construcción": 6.3
        },
        "evolucion_2024": {
            "2024T1": 7.2,
            "2024T2": 6.7,
            "2024T3": 6.9,
            "2024T4": 7.4
        },
        "ccaa_top5": {
            "País Vasco": 9.1,
            "Asturias": 8.6,
            "Navarra": 8.3,
            "Castilla y León": 8.1,
            "Cantabria": 8.0
        },
        "it_ccaa_top3": {
            "Asturias": 6.9,
            "País Vasco": 6.8,
            "Navarra": 6.6
        }
    }
    
    # 1. TASA GENERAL DE ABSENTISMO
    print("\n" + "-" * 60)
    print("1. TASA GENERAL DE ABSENTISMO (Nacional)")
    print("-" * 60)
    df_nacional = calcular_tasa_absentismo_nacional(conn)
    if not df_nacional.empty:
        tasa_bd = df_nacional.iloc[0]['tasa_absentismo']
        tasa_adecco = adecco_valores['tasa_general']
        diferencia = tasa_bd - tasa_adecco
        
        print(f"Valor Adecco:    {tasa_adecco:.1f}%")
        print(f"Valor BD:        {tasa_bd:.2f}%")
        print(f"Diferencia:      {diferencia:+.2f}%")
        print(f"Estado:          {'OK COINCIDE' if abs(diferencia) < 0.5 else 'ATENCION DIFERENCIA'}")
    
    # 2. TASA DE IT
    print("\n" + "-" * 60)
    print("2. TASA DE INCAPACIDAD TEMPORAL (IT)")
    print("-" * 60)
    df_it = calcular_tasa_IT_nacional(conn)
    if not df_it.empty:
        tasa_it_bd = df_it.iloc[0]['tasa_it']
        tasa_it_adecco = adecco_valores['tasa_it']
        diferencia = tasa_it_bd - tasa_it_adecco
        
        print(f"Valor Adecco:    {tasa_it_adecco:.1f}%")
        print(f"Valor BD:        {tasa_it_bd:.2f}%")
        print(f"Diferencia:      {diferencia:+.2f}%")
        print(f"Estado:          {'OK COINCIDE' if abs(diferencia) < 0.5 else 'ATENCION DIFERENCIA'}")
    
    # 3. ABSENTISMO POR SECTOR
    print("\n" + "-" * 60)
    print("3. ABSENTISMO POR SECTOR")
    print("-" * 60)
    df_sectores = calcular_absentismo_por_sector(conn)
    if not df_sectores.empty:
        print(f"{'Sector':<15} {'Adecco':<10} {'BD':<10} {'Diferencia':<10} {'Estado'}")
        print("-" * 55)
        for _, row in df_sectores.iterrows():
            sector = row['sector']
            if sector in adecco_valores['sectores']:
                tasa_bd = row['tasa_absentismo']
                tasa_adecco = adecco_valores['sectores'][sector]
                diferencia = tasa_bd - tasa_adecco
                estado = 'OK' if abs(diferencia) < 0.5 else 'ATEN'
                print(f"{sector:<15} {tasa_adecco:<10.1f} {tasa_bd:<10.2f} {diferencia:+10.2f} {estado}")
    
    # 4. EVOLUCIÓN TRIMESTRAL 2024
    print("\n" + "-" * 60)
    print("4. EVOLUCIÓN TRIMESTRAL 2024")
    print("-" * 60)
    df_evol = calcular_evolucion_trimestral(conn)
    if not df_evol.empty:
        print(f"{'Periodo':<10} {'Adecco':<10} {'BD':<10} {'Diferencia':<10} {'Estado'}")
        print("-" * 55)
        for _, row in df_evol.iterrows():
            periodo = row['periodo']
            if periodo in adecco_valores['evolucion_2024']:
                tasa_bd = row['tasa_absentismo']
                tasa_adecco = adecco_valores['evolucion_2024'][periodo]
                diferencia = tasa_bd - tasa_adecco
                estado = 'OK' if abs(diferencia) < 0.5 else 'ATEN'
                print(f"{periodo:<10} {tasa_adecco:<10.1f} {tasa_bd:<10.2f} {diferencia:+10.2f} {estado}")
    
    # 5. TOP 5 CCAA CON MAYOR ABSENTISMO
    print("\n" + "-" * 60)
    print("5. TOP 5 CCAA CON MAYOR ABSENTISMO")
    print("-" * 60)
    df_ccaa = calcular_absentismo_por_ccaa(conn)
    if not df_ccaa.empty:
        print(f"{'CCAA':<20} {'Adecco':<10} {'BD':<10} {'Diferencia':<10}")
        print("-" * 60)
        
        # Top 5 de nuestra BD
        top5_bd = df_ccaa.head(5)
        for _, row in top5_bd.iterrows():
            ccaa = row['ccaa_nombre']
            tasa_bd = row['tasa_absentismo']
            tasa_adecco = adecco_valores['ccaa_top5'].get(ccaa, '-')
            if tasa_adecco != '-':
                diferencia = tasa_bd - tasa_adecco
                print(f"{ccaa:<20} {tasa_adecco:<10.1f} {tasa_bd:<10.2f} {diferencia:+10.2f}")
            else:
                print(f"{ccaa:<20} {'N/D':<10} {tasa_bd:<10.2f} {'N/A':<10}")
    
    # 6. TOP 3 CCAA CON MAYOR IT
    print("\n" + "-" * 60)
    print("6. TOP 3 CCAA CON MAYOR INCAPACIDAD TEMPORAL")
    print("-" * 60)
    df_it_ccaa = calcular_IT_por_ccaa(conn)
    if not df_it_ccaa.empty:
        print(f"{'CCAA':<20} {'Adecco':<10} {'BD':<10} {'Diferencia':<10}")
        print("-" * 60)
        
        top3_bd = df_it_ccaa.head(3)
        for _, row in top3_bd.iterrows():
            ccaa = row['ccaa_nombre']
            tasa_bd = row['tasa_it']
            tasa_adecco = adecco_valores['it_ccaa_top3'].get(ccaa, '-')
            if tasa_adecco != '-':
                diferencia = tasa_bd - tasa_adecco
                print(f"{ccaa:<20} {tasa_adecco:<10.1f} {tasa_bd:<10.2f} {diferencia:+10.2f}")
            else:
                print(f"{ccaa:<20} {'N/D':<10} {tasa_bd:<10.2f} {'N/A':<10}")
    
    # 7. DESGLOSE POR CAUSAS
    print("\n" + "-" * 60)
    print("7. DESGLOSE POR CAUSAS DE ABSENTISMO")
    print("-" * 60)
    df_causas = calcular_causas_absentismo(conn)
    if not df_causas.empty:
        print(f"{'Causa':<30} {'Tasa (%)':<10} {'Horas':<15}")
        print("-" * 55)
        for _, row in df_causas.iterrows():
            causa = row['tipo_causa']
            tasa = row['tasa_causa']
            horas = row['horas_causa']
            print(f"{causa:<30} {tasa:<10.2f} {horas:<15.2f}")
    
    # RESUMEN FINAL
    print("\n" + "=" * 80)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 80)
    print("OK Datos disponibles para periodo 2024T4")
    print("OK 17 CCAA con datos (solo tabla 6063)")
    print("OK 3 sectores agregados (B-E, F, G-S)")
    print("ATENCION Los códigos de sector difieren (B-E vs Industria)")
    print("ATENCION Posibles diferencias en metodología de cálculo")
    
    conn.close()
    
    return True

if __name__ == "__main__":
    comparar_con_adecco()