#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Matriz final consolidada con dimensiones y métricas claramente identificadas.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def create_final_matrix():
    """Crea la matriz final consolidada."""
    
    # Definir la matriz manualmente con toda la información recopilada
    matriz = [
        # HORAS DE TRABAJO (6 tablas)
        {'codigo': '6042', 'metrica': 'HORAS TRABAJO', 'unidad': 'Horas/mes', 'sector': 'X', 'jornada': 'X', 'ccaa': '', 'tamaño': '', 'detalle': 'Tipos de horas (pactadas, efectivas, extras, IT, vacaciones)'},
        {'codigo': '6043', 'metrica': 'HORAS TRABAJO', 'unidad': 'Horas/mes', 'sector': 'Secc', 'jornada': 'X', 'ccaa': '', 'tamaño': '', 'detalle': 'Tipos de horas por secciones CNAE'},
        {'codigo': '6044', 'metrica': 'HORAS TRABAJO', 'unidad': 'Horas/mes', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Tipos de horas'},
        {'codigo': '6045', 'metrica': 'HORAS TRABAJO', 'unidad': 'Horas/mes', 'sector': 'Secc', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Tipos de horas por secciones'},
        {'codigo': '6046', 'metrica': 'HORAS TRABAJO', 'unidad': 'Horas/mes', 'sector': 'Div', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Tipos de horas por divisiones'},
        {'codigo': '6063', 'metrica': 'HORAS TRABAJO', 'unidad': 'Horas/mes', 'sector': 'X', 'jornada': 'X', 'ccaa': 'X', 'tamaño': '', 'detalle': 'Tipos de horas por CCAA'},
        
        # COSTE POR TRABAJADOR (9 tablas)
        {'codigo': '6030', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'EUR/mes', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': '15 componentes coste (salarial, cotizaciones, IT, etc)'},
        {'codigo': '6031', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'EUR/mes', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': 'X', 'detalle': '7 componentes por tamaño empresa'},
        {'codigo': '6032', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'EUR/mes', 'sector': 'Secc', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': '12 componentes por secciones'},
        {'codigo': '6033', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'EUR/mes', 'sector': 'Div', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': '7 componentes por divisiones'},
        {'codigo': '6056', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'EUR/mes', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'IT e indemnizaciones'},
        {'codigo': '6061', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'EUR/mes', 'sector': 'X', 'jornada': '', 'ccaa': 'X', 'tamaño': '', 'detalle': '7 componentes por CCAA'},
        {'codigo': '11221', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'EUR/mes', 'sector': '', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Serie temporal (total, salarial, otros)'},
        {'codigo': '59391', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'Múltiple', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Series: euros, índice, tasa variación'},
        {'codigo': '59392', 'metrica': 'COSTE/TRABAJADOR', 'unidad': 'Múltiple', 'sector': '', 'jornada': '', 'ccaa': 'X', 'tamaño': '', 'detalle': 'Series por CCAA'},
        
        # COSTE POR HORA (8 tablas)
        {'codigo': '6034', 'metrica': 'COSTE/HORA', 'unidad': 'EUR/hora', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': '4 componentes'},
        {'codigo': '6035', 'metrica': 'COSTE/HORA', 'unidad': 'EUR/hora', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': 'X', 'detalle': '4 componentes por tamaño'},
        {'codigo': '6036', 'metrica': 'COSTE/HORA', 'unidad': 'EUR/hora', 'sector': 'Secc', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': '4 componentes por secciones'},
        {'codigo': '6037', 'metrica': 'COSTE/HORA', 'unidad': 'EUR/hora', 'sector': 'Div', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': '4 componentes por divisiones'},
        {'codigo': '6057', 'metrica': 'COSTE/HORA', 'unidad': 'EUR/hora', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Hora extraordinaria'},
        {'codigo': '6058', 'metrica': 'COSTE/HORA', 'unidad': 'EUR/hora', 'sector': '', 'jornada': '', 'ccaa': 'X', 'tamaño': '', 'detalle': 'Hora extraordinaria por CCAA'},
        {'codigo': '6062', 'metrica': 'COSTE/HORA', 'unidad': 'EUR/hora', 'sector': 'X', 'jornada': '', 'ccaa': 'X', 'tamaño': '', 'detalle': '4 componentes por CCAA'},
        {'codigo': '11222', 'metrica': 'COSTE/HORA', 'unidad': 'EUR/hora', 'sector': '', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Serie temporal'},
        
        # COSTE SALARIAL (4 tablas)
        {'codigo': '6038', 'metrica': 'COSTE SALARIAL', 'unidad': 'EUR/mes', 'sector': 'X', 'jornada': 'X', 'ccaa': '', 'tamaño': '', 'detalle': 'Ordinario, extraordinario, atrasados'},
        {'codigo': '6039', 'metrica': 'COSTE SALARIAL', 'unidad': 'EUR/mes', 'sector': 'Secc', 'jornada': 'X', 'ccaa': '', 'tamaño': '', 'detalle': 'Por secciones CNAE'},
        {'codigo': '6040', 'metrica': 'COSTE SALARIAL/HORA', 'unidad': 'EUR/hora', 'sector': 'X', 'jornada': 'X', 'ccaa': '', 'tamaño': '', 'detalle': 'Salarial por hora'},
        {'codigo': '6041', 'metrica': 'COSTE SALARIAL/HORA', 'unidad': 'EUR/hora', 'sector': 'Secc', 'jornada': 'X', 'ccaa': '', 'tamaño': '', 'detalle': 'Salarial/hora por secciones'},
        
        # VACANTES (4 tablas)
        {'codigo': '6047', 'metrica': 'Nº VACANTES', 'unidad': 'Número', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Puestos vacantes'},
        {'codigo': '6048', 'metrica': 'Nº VACANTES', 'unidad': 'Número', 'sector': 'Secc', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Por secciones'},
        {'codigo': '6049', 'metrica': 'Nº VACANTES', 'unidad': 'Número', 'sector': '', 'jornada': '', 'ccaa': '', 'tamaño': 'X', 'detalle': 'Por tamaño empresa'},
        {'codigo': '6064', 'metrica': 'Nº VACANTES', 'unidad': 'Número', 'sector': '', 'jornada': '', 'ccaa': 'X', 'tamaño': '', 'detalle': 'Por CCAA'},
        
        # MOTIVOS NO VACANTES (4 tablas)
        {'codigo': '6053', 'metrica': '% MOTIVOS NO VAC', 'unidad': '%', 'sector': 'X', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Distribución motivos'},
        {'codigo': '6054', 'metrica': '% MOTIVOS NO VAC', 'unidad': '%', 'sector': 'Secc', 'jornada': '', 'ccaa': '', 'tamaño': '', 'detalle': 'Por secciones'},
        {'codigo': '6055', 'metrica': '% MOTIVOS NO VAC', 'unidad': '%', 'sector': '', 'jornada': '', 'ccaa': '', 'tamaño': 'X', 'detalle': 'Por tamaño'},
        {'codigo': '6066', 'metrica': '% MOTIVOS NO VAC', 'unidad': '%', 'sector': '', 'jornada': '', 'ccaa': 'X', 'tamaño': '', 'detalle': 'Por CCAA'},
    ]
    
    # Crear DataFrame
    df = pd.DataFrame(matriz)
    
    # Reordenar columnas
    df = df[['codigo', 'metrica', 'unidad', 'sector', 'jornada', 'ccaa', 'tamaño', 'detalle']]
    
    return df

def main():
    """Genera la matriz final consolidada."""
    
    print("=" * 120)
    print("MATRIZ FINAL CONSOLIDADA - 35 TABLAS INE")
    print("=" * 120)
    print()
    
    # Crear matriz
    df = create_final_matrix()
    
    # Guardar Excel
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = output_dir / f'matriz_final_consolidada_{timestamp}.xlsx'
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Hoja principal
        df.to_excel(writer, sheet_name='Matriz_Completa', index=False)
        
        # Hoja de resumen por métrica
        resumen = df.groupby('metrica').agg({
            'codigo': 'count',
            'sector': lambda x: sum(x != ''),
            'jornada': lambda x: sum(x != ''),
            'ccaa': lambda x: sum(x != ''),
            'tamaño': lambda x: sum(x != '')
        }).rename(columns={'codigo': 'num_tablas'})
        resumen.to_excel(writer, sheet_name='Resumen_Metricas')
        
        # Hoja de leyenda
        leyenda = pd.DataFrame([
            {'Símbolo': 'X', 'Significado': 'Dimensión por sectores (Industria, Construcción, Servicios, Total)'},
            {'Símbolo': 'Secc', 'Significado': 'Dimensión por secciones CNAE (más detallado que sectores)'},
            {'Símbolo': 'Div', 'Significado': 'Dimensión por divisiones CNAE (máximo detalle)'},
            {'Símbolo': '', 'Significado': 'Dimensión no presente en esta tabla'},
        ])
        leyenda.to_excel(writer, sheet_name='Leyenda', index=False)
    
    # Imprimir matriz en consola
    print("LEYENDA:")
    print("  X    = Tiene la dimensión (sectores básicos)")
    print("  Secc = Por secciones CNAE (más detalle)")
    print("  Div  = Por divisiones CNAE (máximo detalle)")
    print("  -    = No tiene esa dimensión")
    print()
    print("-" * 120)
    print(f"{'Tabla':<6} {'Métrica':<18} {'Unidad':<10} {'Sect':<5} {'Jorn':<5} {'CCAA':<5} {'Tam':<5} {'Detalle':<50}")
    print("-" * 120)
    
    for _, row in df.iterrows():
        sect = row['sector'] if row['sector'] else '-'
        jorn = row['jornada'] if row['jornada'] else '-'
        ccaa = row['ccaa'] if row['ccaa'] else '-'
        tam = row['tamaño'] if row['tamaño'] else '-'
        detalle = row['detalle'][:47] + '...' if len(row['detalle']) > 50 else row['detalle']
        
        print(f"{row['codigo']:<6} {row['metrica']:<18} {row['unidad']:<10} {sect:<5} {jorn:<5} {ccaa:<5} {tam:<5} {detalle:<50}")
    
    print("-" * 120)
    
    # Resumen
    print("\nRESUMEN POR MÉTRICAS:")
    print("-" * 50)
    for metrica in df['metrica'].unique():
        tablas = df[df['metrica'] == metrica]
        print(f"{metrica:20} : {len(tablas)} tablas")
    
    print(f"\nExcel guardado en: {excel_file}")
    
    # Análisis de cobertura
    print("\n" + "=" * 120)
    print("ANÁLISIS DE COBERTURA DE DIMENSIONES")
    print("=" * 120)
    
    total_tablas = len(df)
    print(f"\nDe las {total_tablas} tablas:")
    print(f"  - {sum(df['sector'] != '')} tienen dimensión SECTOR ({sum(df['sector'] != '')*100/total_tablas:.0f}%)")
    print(f"  - {sum(df['jornada'] != '')} tienen dimensión TIPO JORNADA ({sum(df['jornada'] != '')*100/total_tablas:.0f}%)")
    print(f"  - {sum(df['ccaa'] != '')} tienen dimensión CCAA ({sum(df['ccaa'] != '')*100/total_tablas:.0f}%)")
    print(f"  - {sum(df['tamaño'] != '')} tienen dimensión TAMAÑO EMPRESA ({sum(df['tamaño'] != '')*100/total_tablas:.0f}%)")
    print(f"  - {total_tablas} tienen PERIODO (100%) - todas")
    print(f"  - {total_tablas} tienen VALOR numérico (100%) - todas")

if __name__ == "__main__":
    main()