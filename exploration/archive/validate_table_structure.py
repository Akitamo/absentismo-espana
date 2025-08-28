#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validación de estructura de tablas y problema de dimensiones heterogéneas.
"""

import pandas as pd
from pathlib import Path

def analyze_table_dimensions():
    """Analiza las dimensiones de cada tabla de tiempo trabajo."""
    
    base_path = Path(__file__).parent.parent / 'data' / 'raw' / 'csv'
    
    # Tablas de tiempo trabajo
    tables = {
        '6042': 'Tiempo_trabajo_por_trabajador-mes,_tipo_jornada,_sectores.csv',
        '6043': 'Tiempo_trabajo_por_trabajador-mes,_tipo_jornada,_secciones_CNAE.csv',
        '6044': 'Tiempo_trabajo_por_trabajador-mes,_sectores.csv',
        '6045': 'Tiempo_trabajo_por_trabajador-mes,_secciones_CNAE.csv',
        '6046': 'Tiempo_trabajo_por_trabajador-mes,_divisiones_CNAE.csv',
        '6063': 'Tiempo_trabajo_por_trabajador-mes,_CCAA,_tipo_jornada,_sectores.csv'
    }
    
    results = {}
    
    for codigo, filename in tables.items():
        filepath = base_path / f"{codigo}_{filename}"
        
        print(f"\n{'='*60}")
        print(f"Analizando tabla {codigo}")
        print(f"{'='*60}")
        
        # Leer CSV
        df = pd.read_csv(filepath, sep=';', encoding='utf-8-sig', decimal=',')
        
        # Identificar columnas
        cols = df.columns.tolist()
        print(f"Columnas: {cols}")
        
        # Analizar valores únicos para 2025T1 y Horas pactadas
        df_hp_2025 = df[(df['Periodo'] == '2025T1') & 
                        (df.iloc[:, -2] == 'Horas pactadas')]
        
        # Dimensiones únicas
        dimensions = {}
        
        # CCAA
        if 'Comunidades y Ciudades Autónomas' in cols:
            ccaa_values = df_hp_2025['Comunidades y Ciudades Autónomas'].unique()
            dimensions['CCAA'] = len(ccaa_values)
            print(f"  CCAA: {len(ccaa_values)} valores")
            if len(ccaa_values) <= 5:
                print(f"    -> {list(ccaa_values)}")
        else:
            dimensions['CCAA'] = 0
            print(f"  CCAA: No disponible")
        
        # Tipo Jornada
        if 'Tipo de jornada' in cols:
            jornada_values = df_hp_2025['Tipo de jornada'].unique()
            dimensions['Jornada'] = len(jornada_values)
            print(f"  Jornada: {jornada_values.tolist()}")
        else:
            dimensions['Jornada'] = 0
            print(f"  Jornada: No disponible")
        
        # Sectores
        sector_col = None
        for col in cols:
            if 'Sector' in col or 'actividad' in col or 'CNAE' in col:
                sector_col = col
                break
        
        if sector_col:
            sector_values = df_hp_2025[sector_col].unique()
            dimensions['Sectores'] = len(sector_values)
            print(f"  Sectores ({sector_col}): {len(sector_values)} valores")
            
            # Mostrar ejemplos
            print(f"    Ejemplos: {list(sector_values[:5])}")
            
            # Verificar si hay totales
            totals = [s for s in sector_values if 'B_S' in s or 'Total' in s]
            if totals:
                print(f"    TOTALES encontrados: {totals}")
        
        # Valores para comparación
        print(f"\nValores 2025T1 - Horas pactadas:")
        
        # Total B_S
        total_bs = df_hp_2025[df_hp_2025[sector_col].str.contains('B_S', na=False)]
        if not total_bs.empty:
            valor = total_bs.iloc[0]['Total']
            print(f"  Total B_S (ambas jornadas): {valor}")
        
        # Por sector específico
        for sector in ['Industria', 'Construcción', 'Servicios']:
            sector_data = df_hp_2025[df_hp_2025[sector_col] == sector]
            if not sector_data.empty:
                # Buscar ambas jornadas
                if 'Tipo de jornada' in cols:
                    ambas = sector_data[sector_data['Tipo de jornada'] == 'Ambas jornadas']
                    if not ambas.empty:
                        valor = ambas.iloc[0]['Total']
                        print(f"  {sector} (ambas jornadas): {valor}")
                else:
                    valor = sector_data.iloc[0]['Total']
                    print(f"  {sector}: {valor}")
        
        results[codigo] = dimensions
    
    # Resumen comparativo
    print(f"\n{'='*60}")
    print("RESUMEN COMPARATIVO DE DIMENSIONES")
    print(f"{'='*60}")
    
    print("\n| Tabla | CCAA | Jornada | Sectores | Notas |")
    print("|-------|------|---------|----------|-------|")
    
    for codigo, dims in results.items():
        ccaa = "✓" if dims['CCAA'] > 0 else "✗"
        jornada = "✓" if dims['Jornada'] > 0 else "✗"
        
        if codigo == '6042' or codigo == '6044':
            nivel = "Agregado (3)"
        elif codigo == '6043' or codigo == '6045':
            nivel = "Secciones (21)"
        elif codigo == '6046':
            nivel = "Divisiones (82)"
        elif codigo == '6063':
            nivel = "Agregado + CCAA"
        else:
            nivel = f"({dims['Sectores']})"
        
        print(f"| {codigo} | {ccaa} | {jornada} | {nivel} | |")
    
    # Validar duplicación
    print(f"\n{'='*60}")
    print("VALIDACIÓN DE DUPLICACIÓN")
    print(f"{'='*60}")
    
    # Comparar valores entre 6042 y 6063 para Total Nacional
    df_6042 = pd.read_csv(base_path / f"6042_{tables['6042']}", sep=';', encoding='utf-8-sig', decimal=',')
    df_6063 = pd.read_csv(base_path / f"6063_{tables['6063']}", sep=';', encoding='utf-8-sig', decimal=',')
    
    # Filtrar 2025T1, Horas pactadas, Ambas jornadas, B_S
    df_6042_test = df_6042[(df_6042['Periodo'] == '2025T1') & 
                           (df_6042['Tiempo de trabajo'] == 'Horas pactadas') &
                           (df_6042['Tipo de jornada'] == 'Ambas jornadas') &
                           (df_6042['Sectores de actividad CNAE 2009'].str.contains('B_S'))]
    
    df_6063_test = df_6063[(df_6063['Periodo'] == '2025T1') & 
                           (df_6063['Tiempo de trabajo'] == 'Horas pactadas') &
                           (df_6063['Tipo de jornada'] == 'Ambas jornadas') &
                           (df_6063['Comunidades y Ciudades Autónomas'] == 'Total Nacional') &
                           (df_6063['Sectores de actividad CNAE 2009'].str.contains('B_S'))]
    
    if not df_6042_test.empty and not df_6063_test.empty:
        val_6042 = df_6042_test.iloc[0]['Total']
        val_6063 = df_6063_test.iloc[0]['Total']
        
        print(f"\nComparación Total Nacional B_S (2025T1, HP, Ambas jornadas):")
        print(f"  Tabla 6042: {val_6042}")
        print(f"  Tabla 6063: {val_6063}")
        
        if val_6042 == val_6063:
            print("  ✓ VALORES IDÉNTICOS - Los totales nacionales coinciden")
            print("  ⚠️ RIESGO: Si sumamos ambas tablas, duplicaríamos el valor")
        else:
            print("  ✗ VALORES DIFERENTES - Revisar")

if __name__ == "__main__":
    analyze_table_dimensions()