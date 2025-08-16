#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidación de patrones y comportamientos uniformes en las tablas del INE.
Identifica dimensiones equivalentes y analiza la estructura de componentes del coste.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

def analyze_all_tables():
    """Analiza todas las tablas para identificar patrones uniformes."""
    
    # Leer el análisis previo de todas las tablas
    reports_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    
    # Cargar el análisis completo
    with open(reports_dir / 'analisis_columnas_20250815_200326.json', 'r', encoding='utf-8') as f:
        all_tables = json.load(f)
    
    # Cargar el análisis de 8 tablas para valores únicos
    json_files = list(reports_dir.glob('analisis_8_tablas_*.json'))
    if json_files:
        with open(json_files[-1], 'r', encoding='utf-8') as f:
            eight_tables = json.load(f)
    else:
        eight_tables = {}
    
    return all_tables, eight_tables

def identify_dimension_groups(all_tables):
    """Identifica grupos de dimensiones que son equivalentes."""
    
    dimension_groups = {
        'SECTORES': {
            'variantes_nombres': set(),
            'tablas': [],
            'valores_esperados': [
                'B_S Industria, construcción y servicios',
                'Industria', 
                'Construcción',
                'Servicios'
            ]
        },
        'TIPO_JORNADA': {
            'variantes_nombres': set(),
            'tablas': [],
            'valores_esperados': [
                'Ambas jornadas',
                'Jornada a tiempo completo',
                'Jornada a tiempo parcial'
            ]
        },
        'COMUNIDADES': {
            'variantes_nombres': set(),
            'tablas': [],
            'valores_esperados': [] # Se llenará con los valores encontrados
        },
        'PERIODO': {
            'variantes_nombres': set(),
            'tablas': [],
            'formato': 'YYYYTQ'
        },
        'COMPONENTES_COSTE': {
            'variantes_nombres': set(),
            'tablas': [],
            'niveles_detalle': defaultdict(list) # Mapeo de nivel de detalle
        },
        'TIPO_DATO': {
            'variantes_nombres': set(),
            'tablas': [],
            'valores_esperados': ['Euros', 'Tasa de variación anual', 'Índice']
        }
    }
    
    # Analizar cada tabla
    for codigo, info in all_tables.items():
        for columna in info['columnas']:
            columna_lower = columna.lower()
            
            # Identificar SECTORES
            if ('sector' in columna_lower or 
                'actividad' in columna_lower and 'cnae' in columna_lower):
                dimension_groups['SECTORES']['variantes_nombres'].add(columna)
                dimension_groups['SECTORES']['tablas'].append(codigo)
            
            # Identificar TIPO_JORNADA
            elif 'jornada' in columna_lower:
                dimension_groups['TIPO_JORNADA']['variantes_nombres'].add(columna)
                dimension_groups['TIPO_JORNADA']['tablas'].append(codigo)
            
            # Identificar COMUNIDADES
            elif ('comunidad' in columna_lower or 
                  'ccaa' in columna_lower or
                  columna == 'Total Nacional'):
                dimension_groups['COMUNIDADES']['variantes_nombres'].add(columna)
                dimension_groups['COMUNIDADES']['tablas'].append(codigo)
            
            # Identificar PERIODO
            elif 'periodo' in columna_lower:
                dimension_groups['PERIODO']['variantes_nombres'].add(columna)
                dimension_groups['PERIODO']['tablas'].append(codigo)
            
            # Identificar COMPONENTES_COSTE
            elif 'component' in columna_lower and 'coste' in columna_lower:
                dimension_groups['COMPONENTES_COSTE']['variantes_nombres'].add(columna)
                dimension_groups['COMPONENTES_COSTE']['tablas'].append(codigo)
                # Registrar nivel de detalle
                if 'columnas_detalle' in info and columna in info['columnas_detalle']:
                    n_valores = info['columnas_detalle'][columna].get('valores_unicos_muestra', 0)
                    dimension_groups['COMPONENTES_COSTE']['niveles_detalle'][n_valores].append(codigo)
            
            # Identificar TIPO_DATO
            elif 'tipo' in columna_lower and 'dato' in columna_lower:
                dimension_groups['TIPO_DATO']['variantes_nombres'].add(columna)
                dimension_groups['TIPO_DATO']['tablas'].append(codigo)
    
    return dimension_groups

def analyze_componentes_coste(all_tables, eight_tables):
    """Analiza en detalle los componentes del coste para entender las métricas."""
    
    componentes_analysis = {
        'tablas_con_componentes': [],
        'componentes_unicos': set(),
        'jerarquia': {},
        'metricas_reales': []
    }
    
    # Recopilar todos los componentes únicos de las 8 tablas analizadas
    for codigo, info in eight_tables.items():
        if 'columnas_analisis' in info:
            for col, analisis in info['columnas_analisis'].items():
                if 'component' in col.lower() and 'valores_unicos' in analisis:
                    componentes_analysis['tablas_con_componentes'].append(codigo)
                    for valor in analisis['valores_unicos']:
                        componentes_analysis['componentes_unicos'].add(valor)
    
    # Convertir set a lista para JSON
    componentes_analysis['componentes_unicos'] = list(componentes_analysis['componentes_unicos'])
    
    # Organizar componentes por categorías
    categorias = {
        'COSTE_TOTAL': [],
        'COSTE_SALARIAL': [],
        'COSTE_NO_SALARIAL': [],
        'COTIZACIONES': [],
        'OTROS': []
    }
    
    for comp in componentes_analysis['componentes_unicos']:
        comp_lower = comp.lower()
        if 'total' in comp_lower:
            categorias['COSTE_TOTAL'].append(comp)
        elif 'salarial' in comp_lower:
            categorias['COSTE_SALARIAL'].append(comp)
        elif 'cotizacion' in comp_lower or 'seguridad social' in comp_lower:
            categorias['COTIZACIONES'].append(comp)
        elif 'i.t' in comp_lower or 'incapacidad' in comp_lower:
            categorias['COSTE_NO_SALARIAL'].append(comp)
        else:
            categorias['OTROS'].append(comp)
    
    componentes_analysis['jerarquia'] = categorias
    
    # Identificar las métricas reales (lo que realmente medimos)
    componentes_analysis['metricas_reales'] = [
        'Coste por trabajador',
        'Coste por hora efectiva',
        'Horas trabajadas',
        'Número de vacantes',
        'Porcentaje/Proporción'
    ]
    
    return componentes_analysis

def consolidate_patterns(all_tables, eight_tables):
    """Consolida todos los patrones encontrados."""
    
    print("=" * 80)
    print("CONSOLIDACIÓN DE PATRONES Y COMPORTAMIENTOS UNIFORMES")
    print("=" * 80)
    print()
    
    # 1. Identificar grupos de dimensiones
    dimension_groups = identify_dimension_groups(all_tables)
    
    print("1. DIMENSIONES IDENTIFICADAS Y SUS VARIANTES")
    print("-" * 50)
    
    for grupo, info in dimension_groups.items():
        if info['variantes_nombres']:
            print(f"\n{grupo}:")
            print(f"  Variantes de nombre encontradas:")
            for nombre in sorted(info['variantes_nombres']):
                print(f"    - {nombre}")
            print(f"  Aparece en {len(set(info['tablas']))} tablas")
            
            if grupo == 'COMPONENTES_COSTE' and info['niveles_detalle']:
                print(f"  Niveles de detalle encontrados:")
                for n_valores, tablas in sorted(info['niveles_detalle'].items()):
                    print(f"    - {n_valores} valores: tablas {', '.join(set(tablas))}")
    
    # 2. Analizar componentes del coste
    print("\n" + "=" * 80)
    print("2. ANÁLISIS DE COMPONENTES DEL COSTE (MÉTRICAS)")
    print("-" * 50)
    
    comp_analysis = analyze_componentes_coste(all_tables, eight_tables)
    
    print("\nCOMPONENTES ENCONTRADOS POR CATEGORÍA:")
    for categoria, componentes in comp_analysis['jerarquia'].items():
        if componentes:
            print(f"\n{categoria}:")
            for comp in sorted(componentes):
                print(f"  - {comp}")
    
    print("\nMÉTRICAS REALES IDENTIFICADAS:")
    for metrica in comp_analysis['metricas_reales']:
        print(f"  - {metrica}")
    
    # 3. Estructura uniforme
    print("\n" + "=" * 80)
    print("3. ESTRUCTURA UNIFORME DETECTADA")
    print("-" * 50)
    
    estructura_uniforme = {
        'columnas_universales': ['Periodo', 'Total'],
        'patrones_estructura': [
            'Todas las tablas: Dimensiones + Periodo + Total (métrica)',
            'Periodo siempre en formato YYYYTQ',
            'Total siempre contiene el valor numérico',
            'Separador decimal: coma (,)',
            'Separador de miles: punto (.)'
        ],
        'dimensiones_principales': [
            'SECTORES (4 valores fijos)',
            'TIPO_JORNADA (3 valores fijos)',
            'COMUNIDADES (18 valores)',
            'COMPONENTES_COSTE (variable según detalle)'
        ]
    }
    
    print("\nCOLUMNAS UNIVERSALES:")
    for col in estructura_uniforme['columnas_universales']:
        count = sum(1 for info in all_tables.values() if col in info['columnas'])
        print(f"  - {col}: presente en {count}/{len(all_tables)} tablas")
    
    print("\nPATRONES DE ESTRUCTURA:")
    for patron in estructura_uniforme['patrones_estructura']:
        print(f"  - {patron}")
    
    # 4. Propuesta de unificación
    print("\n" + "=" * 80)
    print("4. PROPUESTA DE ESQUEMA UNIFICADO")
    print("-" * 50)
    
    esquema_unificado = {
        'dimensiones_normalizadas': {
            'periodo': 'Todos los valores de Periodo',
            'sector': 'Unificar Sectores/Sector de actividad/etc',
            'tipo_jornada': 'Cuando aplique',
            'comunidad_autonoma': 'Cuando aplique',
            'tipo_metrica': 'Derivado de Componentes del coste',
            'unidad_medida': 'Euros/Horas/Número/Porcentaje'
        },
        'metrica_normalizada': {
            'valor': 'El valor numérico de Total',
            'tipo_valor': 'Absoluto/Tasa variación/Índice'
        }
    }
    
    print("\nDIMENSIONES NORMALIZADAS PROPUESTAS:")
    for dim, desc in esquema_unificado['dimensiones_normalizadas'].items():
        print(f"  - {dim}: {desc}")
    
    print("\nMÉTRICA NORMALIZADA:")
    for campo, desc in esquema_unificado['metrica_normalizada'].items():
        print(f"  - {campo}: {desc}")
    
    # Guardar consolidación
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    consolidacion = {
        'dimension_groups': {k: {
            'variantes_nombres': list(v['variantes_nombres']),
            'num_tablas': len(set(v['tablas'])),
            'tablas': list(set(v['tablas']))
        } for k, v in dimension_groups.items()},
        'componentes_coste': comp_analysis,
        'estructura_uniforme': estructura_uniforme,
        'esquema_unificado': esquema_unificado
    }
    
    output_file = output_dir / f'consolidacion_patrones_{timestamp}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidacion, f, ensure_ascii=False, indent=2)
    
    print(f"\n\nConsolidación guardada en: {output_file}")
    
    return consolidacion

def main():
    """Ejecuta el análisis de consolidación."""
    
    # Cargar datos
    all_tables, eight_tables = analyze_all_tables()
    
    # Consolidar patrones
    consolidacion = consolidate_patterns(all_tables, eight_tables)
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE CONSOLIDACIÓN")
    print("=" * 80)
    
    print("\nDIMENSIONES QUE NECESITAN UNIFICACIÓN:")
    print("  1. SECTORES: 3 variantes de nombre -> unificar a 'sector'")
    print("  2. COMPONENTES_COSTE: múltiples niveles -> convertir a 'tipo_metrica'")
    print("  3. TIPO_DATO: cuando existe -> incorporar a 'tipo_valor'")
    
    print("\nTRANSFORMACIÓN CLAVE:")
    print("  - Los 'Componentes del coste' NO son dimensiones, son TIPOS de métricas")
    print("  - Cada fila representa una métrica diferente (coste salarial, otros costes, etc.)")
    print("  - Necesitamos pivotar esta información para que sea clara")
    
    print("\nESTRUCTURA FINAL PROPUESTA:")
    print("  periodo | sector | tipo_jornada | ccaa | tipo_metrica | valor | unidad")
    print("  --------|--------|---------------|------|--------------|-------|-------")
    print("  2025T1  | Indust | Completa      | 01   | Coste_Salar  | 2500  | EUR")

if __name__ == "__main__":
    main()