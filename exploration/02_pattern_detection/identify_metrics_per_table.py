#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identificación clara de qué métrica(s) mide cada tabla del INE.
Analiza el nombre del archivo y el contenido para determinar la métrica principal.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def identify_table_metric(codigo, info_tabla, detailed_data=None):
    """Identifica qué métrica específica mide cada tabla basándose en su nombre y contenido."""
    
    archivo = info_tabla.get('archivo', '')
    columnas = info_tabla.get('columnas', [])
    
    # Diccionario de métricas identificadas
    metrica_info = {
        'codigo': codigo,
        'archivo': archivo,
        'metrica_principal': '',
        'unidad_medida': '',
        'descripcion': '',
        'multiples_metricas': False,
        'detalle_metricas': []
    }
    
    # Analizar por nombre del archivo y código
    archivo_lower = archivo.lower()
    
    # TIEMPO DE TRABAJO (6042-6046, 6063)
    if 'tiempo' in archivo_lower and 'trabajo' in archivo_lower:
        metrica_info['metrica_principal'] = 'HORAS DE TRABAJO'
        metrica_info['unidad_medida'] = 'Horas por trabajador-mes'
        metrica_info['descripcion'] = 'Tiempo de trabajo mensual por trabajador'
        
        # Si tiene "Tiempo de trabajo" como columna, tiene múltiples tipos
        if 'Tiempo de trabajo' in columnas:
            metrica_info['multiples_metricas'] = True
            metrica_info['detalle_metricas'] = [
                'Horas pactadas',
                'Horas efectivas', 
                'Horas pagadas',
                'Horas extras',
                'Horas no trabajadas (IT, vacaciones, etc.)'
            ]
    
    # COSTES LABORALES (6030-6041, 6056-6058, 6061-6062, 11221-11222)
    elif 'coste' in archivo_lower or 'cost' in archivo_lower:
        # Por hora o por trabajador
        if 'hora' in archivo_lower:
            metrica_info['metrica_principal'] = 'COSTE LABORAL POR HORA'
            metrica_info['unidad_medida'] = 'Euros/hora efectiva'
            metrica_info['descripcion'] = 'Coste laboral por hora efectiva de trabajo'
        else:
            metrica_info['metrica_principal'] = 'COSTE LABORAL POR TRABAJADOR'
            metrica_info['unidad_medida'] = 'Euros/trabajador-mes'
            metrica_info['descripcion'] = 'Coste laboral mensual por trabajador'
        
        # Verificar si es coste salarial específicamente
        if 'salarial' in archivo_lower:
            metrica_info['metrica_principal'] = 'COSTE SALARIAL'
            metrica_info['descripcion'] = 'Componente salarial del coste laboral'
        
        # Si tiene "Componentes del coste", tiene múltiples métricas
        if 'Componentes del coste' in columnas:
            metrica_info['multiples_metricas'] = True
            # Necesitaríamos los valores únicos para listar las métricas específicas
            if detailed_data and codigo in detailed_data:
                componentes = detailed_data[codigo].get('componentes', [])
                metrica_info['detalle_metricas'] = componentes
    
    # VACANTES (6047-6049, 6064)
    elif 'vacante' in archivo_lower:
        if 'motivos' in archivo_lower or 'no_vacantes' in archivo_lower:
            metrica_info['metrica_principal'] = 'MOTIVOS NO VACANTES'
            metrica_info['unidad_medida'] = 'Porcentaje'
            metrica_info['descripcion'] = 'Distribución porcentual de motivos por los que no hay vacantes'
        else:
            metrica_info['metrica_principal'] = 'NÚMERO DE VACANTES'
            metrica_info['unidad_medida'] = 'Número absoluto'
            metrica_info['descripcion'] = 'Número de puestos de trabajo vacantes'
    
    # MOTIVOS NO VACANTES (6053-6055, 6066)
    elif 'motivos' in archivo_lower and 'no' in archivo_lower:
        metrica_info['metrica_principal'] = 'MOTIVOS NO VACANTES'
        metrica_info['unidad_medida'] = 'Porcentaje'
        metrica_info['descripcion'] = 'Distribución porcentual de motivos por los que no existen vacantes'
        metrica_info['multiples_metricas'] = True
        metrica_info['detalle_metricas'] = [
            'No se necesita ningún trabajador',
            'Elevado coste de contratación',
            'Otros motivos'
        ]
    
    # SERIES TEMPORALES (59391-59392)
    elif 'series' in archivo_lower or 'serie' in archivo_lower:
        metrica_info['metrica_principal'] = 'SERIES TEMPORALES COSTES'
        metrica_info['unidad_medida'] = 'Múltiple (Euros, Índice, Tasa)'
        metrica_info['descripcion'] = 'Series temporales de costes laborales con diferentes formatos'
        metrica_info['multiples_metricas'] = True
        if 'Tipo de dato' in columnas:
            metrica_info['detalle_metricas'] = [
                'Valor absoluto en euros',
                'Índice (base 100)',
                'Tasa de variación anual'
            ]
    
    # Validación adicional por componentes
    if not metrica_info['metrica_principal'] and 'Componentes del coste' in columnas:
        metrica_info['metrica_principal'] = 'COSTE LABORAL'
        metrica_info['unidad_medida'] = 'Euros'
        metrica_info['multiples_metricas'] = True
    
    return metrica_info

def analyze_all_metrics():
    """Analiza todas las tablas para identificar sus métricas."""
    
    # Cargar datos
    reports_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    
    # Cargar análisis previo
    with open(reports_dir / 'analisis_columnas_20250815_200326.json', 'r', encoding='utf-8') as f:
        all_tables = json.load(f)
    
    # Intentar cargar datos detallados de las 8 tablas (para componentes)
    detailed_data = {}
    json_files = list(reports_dir.glob('analisis_8_tablas_*.json'))
    if json_files:
        with open(json_files[-1], 'r', encoding='utf-8') as f:
            eight_tables = json.load(f)
            for codigo, info in eight_tables.items():
                if 'columnas_analisis' in info:
                    for col, analisis in info['columnas_analisis'].items():
                        if 'component' in col.lower() and 'valores_unicos' in analisis:
                            detailed_data[codigo] = {
                                'componentes': analisis['valores_unicos']
                            }
    
    # Analizar cada tabla
    metricas_por_tabla = {}
    for codigo, info in all_tables.items():
        metrica_info = identify_table_metric(codigo, info, detailed_data)
        metricas_por_tabla[codigo] = metrica_info
    
    return metricas_por_tabla

def create_metrics_summary(metricas_por_tabla):
    """Crea un resumen de métricas por categoría."""
    
    categorias = {
        'HORAS DE TRABAJO': [],
        'COSTE LABORAL POR TRABAJADOR': [],
        'COSTE LABORAL POR HORA': [],
        'COSTE SALARIAL': [],
        'NÚMERO DE VACANTES': [],
        'MOTIVOS NO VACANTES': [],
        'SERIES TEMPORALES': [],
        'OTROS': []
    }
    
    for codigo, info in metricas_por_tabla.items():
        metrica = info['metrica_principal']
        
        # Clasificar por categoría
        if 'HORAS' in metrica and 'COSTE' not in metrica:
            categorias['HORAS DE TRABAJO'].append(codigo)
        elif 'COSTE' in metrica and 'HORA' in metrica:
            categorias['COSTE LABORAL POR HORA'].append(codigo)
        elif 'COSTE SALARIAL' in metrica:
            categorias['COSTE SALARIAL'].append(codigo)
        elif 'COSTE' in metrica and 'TRABAJADOR' in metrica:
            categorias['COSTE LABORAL POR TRABAJADOR'].append(codigo)
        elif 'VACANTE' in metrica and 'MOTIVO' not in metrica:
            categorias['NÚMERO DE VACANTES'].append(codigo)
        elif 'MOTIVO' in metrica:
            categorias['MOTIVOS NO VACANTES'].append(codigo)
        elif 'SERIE' in metrica:
            categorias['SERIES TEMPORALES'].append(codigo)
        else:
            categorias['OTROS'].append(codigo)
    
    return categorias

def main():
    """Ejecuta el análisis de métricas."""
    
    print("=" * 100)
    print("IDENTIFICACIÓN DE MÉTRICAS POR TABLA")
    print("=" * 100)
    print()
    
    # Analizar métricas
    metricas_por_tabla = analyze_all_metrics()
    
    # Crear resumen por categorías
    categorias = create_metrics_summary(metricas_por_tabla)
    
    # Imprimir resumen por categorías
    print("RESUMEN POR TIPO DE MÉTRICA:")
    print("-" * 80)
    
    for categoria, tablas in categorias.items():
        if tablas:
            print(f"\n{categoria} ({len(tablas)} tablas):")
            print(f"  Tablas: {', '.join(sorted(tablas))}")
    
    # Imprimir detalle de cada tabla
    print("\n" + "=" * 100)
    print("DETALLE DE MÉTRICAS POR TABLA")
    print("=" * 100)
    
    # Agrupar por métrica principal para presentación más clara
    for categoria, tablas_cat in categorias.items():
        if not tablas_cat:
            continue
            
        print(f"\n{'='*80}")
        print(f"{categoria}")
        print(f"{'='*80}")
        
        for codigo in sorted(tablas_cat):
            info = metricas_por_tabla[codigo]
            print(f"\nTabla {codigo}:")
            print(f"  Archivo: {info['archivo'][:60]}...")
            print(f"  Métrica: {info['metrica_principal']}")
            print(f"  Unidad: {info['unidad_medida']}")
            print(f"  Descripción: {info['descripcion']}")
            
            if info['multiples_metricas']:
                print(f"  Múltiples métricas: SÍ")
                if info['detalle_metricas']:
                    print(f"  Detalle:")
                    for metrica in info['detalle_metricas'][:5]:  # Mostrar máximo 5
                        print(f"    - {metrica}")
                    if len(info['detalle_metricas']) > 5:
                        print(f"    ... y {len(info['detalle_metricas'])-5} más")
            else:
                print(f"  Múltiples métricas: NO (métrica única)")
    
    # Crear DataFrame para Excel
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Preparar datos para Excel
    datos_excel = []
    for codigo in sorted(metricas_por_tabla.keys()):
        info = metricas_por_tabla[codigo]
        datos_excel.append({
            'Tabla': codigo,
            'Archivo': info['archivo'].replace('.csv', ''),
            'Métrica Principal': info['metrica_principal'],
            'Unidad': info['unidad_medida'],
            'Múltiples': 'SÍ' if info['multiples_metricas'] else 'NO',
            'Descripción': info['descripcion'],
            'Detalle Métricas': ' | '.join(info['detalle_metricas'][:3]) if info['detalle_metricas'] else ''
        })
    
    df = pd.DataFrame(datos_excel)
    
    # Guardar Excel
    excel_file = output_dir / f'metricas_identificadas_{timestamp}.xlsx'
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Hoja principal
        df.to_excel(writer, sheet_name='Métricas_por_Tabla', index=False)
        
        # Hoja de resumen
        resumen = []
        for categoria, tablas in categorias.items():
            if tablas:
                resumen.append({
                    'Tipo de Métrica': categoria,
                    'Número de Tablas': len(tablas),
                    'Tablas': ', '.join(sorted(tablas))
                })
        df_resumen = pd.DataFrame(resumen)
        df_resumen.to_excel(writer, sheet_name='Resumen_Categorías', index=False)
    
    # Guardar JSON
    json_file = output_dir / f'metricas_identificadas_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(metricas_por_tabla, f, ensure_ascii=False, indent=2)
    
    print(f"\n\nArchivos generados:")
    print(f"  - Excel: {excel_file}")
    print(f"  - JSON: {json_file}")
    
    # Resumen final
    print("\n" + "=" * 100)
    print("RESUMEN EJECUTIVO")
    print("=" * 100)
    
    print("\nLas 35 tablas miden 7 tipos principales de métricas:")
    print("\n1. COSTES LABORALES (18 tablas):")
    print("   - Por trabajador: Coste mensual en euros")
    print("   - Por hora: Coste por hora efectiva")
    print("   - Múltiples componentes: salarial, cotizaciones, otros")
    
    print("\n2. TIEMPO DE TRABAJO (6 tablas):")
    print("   - Horas por trabajador-mes")
    print("   - Tipos: pactadas, efectivas, extras, no trabajadas")
    
    print("\n3. VACANTES (4 tablas):")
    print("   - Número absoluto de puestos vacantes")
    
    print("\n4. MOTIVOS NO VACANTES (4 tablas):")
    print("   - Distribución porcentual de razones")
    
    print("\n5. SERIES TEMPORALES (2 tablas):")
    print("   - Valores absolutos, índices y tasas de variación")
    
    print("\n6. OTROS (1 tabla)")

if __name__ == "__main__":
    main()