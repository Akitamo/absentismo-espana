#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación del esquema unificado a las 35 tablas del INE.
Genera una matriz completa con dimensiones y métricas normalizadas.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Mapeo de nombres de columnas a dimensiones unificadas
COLUMN_MAPPING = {
    # SECTORES
    'Sectores de actividad CNAE 2009': 'sector',
    'Sectores de actividad': 'sector',
    'Sector de actividad': 'sector',
    'Actividad económica CNAE-09': 'sector',
    'Secciones de la CNAE-09': 'sector_detalle',
    'Secciones de actividad': 'sector_detalle',
    'Divisiones de la CNAE-09': 'sector_division',
    
    # TIPO JORNADA
    'Tipo de jornada': 'tipo_jornada',
    
    # GEOGRAFÍA
    'Comunidades y Ciudades Autónomas': 'ccaa',
    'Comunidad autónoma': 'ccaa',
    'Total Nacional': 'ccaa',
    
    # TEMPORAL
    'Periodo': 'periodo',
    
    # MÉTRICAS (no dimensiones)
    'Componentes del coste': 'tipo_metrica',
    
    # OTROS
    'Tipo de dato': 'tipo_valor',
    'Corrección de efectos': 'correccion_efectos',
    'Clase de indicador': 'clase_indicador',
    'Tiempo de trabajo': 'tipo_tiempo_trabajo',
    'Tamaño del establecimiento': 'tamaño_empresa',
    'Motivos por los que no exiten puestos de trabajo vacantes': 'motivo_no_vacante',
    
    # VALOR
    'Total': 'valor',
    'Total Nacional': 'valor'
}

def analyze_table_unified(info_tabla):
    """Analiza una tabla y aplica el esquema unificado."""
    
    codigo = info_tabla.get('codigo', 'unknown')
    
    # Dimensiones y métricas unificadas
    dimensiones_unificadas = []
    metricas = []
    tipo_metrica_detalle = None
    
    # Analizar cada columna
    for columna in info_tabla.get('columnas', []):
        # Aplicar mapeo
        columna_unificada = COLUMN_MAPPING.get(columna, columna.lower().replace(' ', '_'))
        
        # Clasificar
        if columna_unificada == 'valor':
            metricas.append('valor_numerico')
        elif columna_unificada == 'tipo_metrica':
            # Componentes del coste indica múltiples métricas
            if 'columnas_detalle' in info_tabla and columna in info_tabla['columnas_detalle']:
                n_valores = info_tabla['columnas_detalle'][columna].get('valores_unicos_muestra', 0)
                tipo_metrica_detalle = f"tipo_metrica ({n_valores} tipos)"
                metricas.append(tipo_metrica_detalle)
        elif columna_unificada in ['periodo', 'sector', 'sector_detalle', 'sector_division', 
                                   'tipo_jornada', 'ccaa', 'tipo_valor', 'correccion_efectos',
                                   'clase_indicador', 'tipo_tiempo_trabajo', 'tamaño_empresa',
                                   'motivo_no_vacante']:
            if columna_unificada not in dimensiones_unificadas:
                dimensiones_unificadas.append(columna_unificada)
        else:
            # Columna no mapeada
            if columna != 'Total' and columna != 'Total Nacional':
                dimensiones_unificadas.append(f"[{columna}]")
    
    return {
        'codigo': codigo,
        'archivo': info_tabla.get('archivo', ''),
        'num_filas': info_tabla.get('num_filas', 0),
        'dimensiones_unificadas': dimensiones_unificadas,
        'metricas': metricas,
        'columnas_originales': info_tabla.get('columnas', [])
    }

def generate_unified_matrix():
    """Genera la matriz unificada para las 35 tablas."""
    
    # Cargar análisis previo
    reports_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    
    with open(reports_dir / 'analisis_columnas_20250815_200326.json', 'r', encoding='utf-8') as f:
        all_tables = json.load(f)
    
    # Aplicar esquema unificado a cada tabla
    resultados_unificados = {}
    
    for codigo, info in all_tables.items():
        resultado = analyze_table_unified(info)
        resultados_unificados[codigo] = resultado
    
    return resultados_unificados

def create_dimension_matrix(resultados):
    """Crea una matriz de dimensiones y métricas por tabla."""
    
    # Preparar datos para la matriz
    matriz_data = []
    
    # Todas las dimensiones posibles
    todas_dimensiones = set()
    for r in resultados.values():
        todas_dimensiones.update(r['dimensiones_unificadas'])
    
    dimensiones_ordenadas = sorted(todas_dimensiones)
    
    for codigo, info in sorted(resultados.items()):
        fila = {
            'Tabla': codigo,
            'Archivo': info['archivo'].replace('.csv', ''),
            'Filas': info['num_filas']
        }
        
        # Marcar qué dimensiones tiene
        for dim in dimensiones_ordenadas:
            fila[dim] = 'X' if dim in info['dimensiones_unificadas'] else ''
        
        # Métricas
        fila['Métricas'] = ', '.join(info['metricas']) if info['metricas'] else 'valor_numerico'
        
        matriz_data.append(fila)
    
    return pd.DataFrame(matriz_data), dimensiones_ordenadas

def print_analysis_summary(resultados):
    """Imprime un resumen del análisis."""
    
    print("=" * 100)
    print("ANÁLISIS UNIFICADO DE LAS 35 TABLAS DEL INE")
    print("=" * 100)
    print()
    
    # Estadísticas generales
    print("ESTADÍSTICAS GENERALES:")
    print("-" * 50)
    
    # Contar dimensiones más comunes
    dimension_count = {}
    for info in resultados.values():
        for dim in info['dimensiones_unificadas']:
            dimension_count[dim] = dimension_count.get(dim, 0) + 1
    
    print("\nDIMENSIONES MÁS COMUNES:")
    for dim, count in sorted(dimension_count.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(resultados)) * 100
        print(f"  {dim:30} : {count:2} tablas ({pct:.0f}%)")
    
    # Identificar grupos de tablas por dimensiones
    print("\n" + "=" * 100)
    print("GRUPOS DE TABLAS POR ESTRUCTURA")
    print("=" * 100)
    
    # Agrupar por conjunto de dimensiones
    grupos = {}
    for codigo, info in resultados.items():
        dims_key = tuple(sorted(info['dimensiones_unificadas']))
        if dims_key not in grupos:
            grupos[dims_key] = []
        grupos[dims_key].append(codigo)
    
    for i, (dims, tablas) in enumerate(sorted(grupos.items(), key=lambda x: len(x[1]), reverse=True), 1):
        print(f"\nGRUPO {i} ({len(tablas)} tablas):")
        print(f"  Dimensiones: {', '.join(dims)}")
        print(f"  Tablas: {', '.join(sorted(tablas))}")

def main():
    """Ejecuta el análisis unificado."""
    
    # Generar análisis unificado
    resultados = generate_unified_matrix()
    
    # Crear matriz de dimensiones
    df_matriz, dimensiones = create_dimension_matrix(resultados)
    
    # Guardar resultados
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Guardar JSON
    json_file = output_dir / f'esquema_unificado_35_tablas_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    # Guardar Excel con matriz
    excel_file = output_dir / f'matriz_dimensiones_35_tablas_{timestamp}.xlsx'
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Hoja 1: Matriz completa
        df_matriz.to_excel(writer, sheet_name='Matriz_Dimensiones', index=False)
        
        # Hoja 2: Resumen por dimensión
        resumen_dims = []
        for dim in dimensiones:
            count = sum(1 for _, info in resultados.items() if dim in info['dimensiones_unificadas'])
            resumen_dims.append({
                'Dimensión': dim,
                'Tablas': count,
                'Porcentaje': f"{(count/35)*100:.0f}%"
            })
        df_resumen = pd.DataFrame(resumen_dims)
        df_resumen.to_excel(writer, sheet_name='Resumen_Dimensiones', index=False)
        
        # Hoja 3: Detalle por tabla
        detalle = []
        for codigo, info in sorted(resultados.items()):
            detalle.append({
                'Tabla': codigo,
                'Archivo': info['archivo'],
                'Filas': info['num_filas'],
                'Dimensiones': ', '.join(info['dimensiones_unificadas']),
                'Métricas': ', '.join(info['metricas']) if info['metricas'] else 'valor_numerico',
                'Columnas_Originales': ' | '.join(info['columnas_originales'])
            })
        df_detalle = pd.DataFrame(detalle)
        df_detalle.to_excel(writer, sheet_name='Detalle_Tablas', index=False)
    
    print(f"Archivos generados:")
    print(f"  - JSON: {json_file}")
    print(f"  - Excel: {excel_file}")
    print()
    
    # Imprimir resumen
    print_analysis_summary(resultados)
    
    # Imprimir matriz simplificada
    print("\n" + "=" * 100)
    print("MATRIZ DE DIMENSIONES Y MÉTRICAS (35 TABLAS)")
    print("=" * 100)
    print("\nLeyenda: X = dimensión presente | periodo y valor están en todas")
    print("-" * 100)
    
    # Versión simplificada para consola
    print(f"{'Tabla':<8} {'sector':<8} {'jornada':<8} {'ccaa':<6} {'tiempo':<8} {'tamaño':<8} {'Métricas':<40}")
    print("-" * 100)
    
    for codigo in sorted(resultados.keys()):
        info = resultados[codigo]
        dims = info['dimensiones_unificadas']
        
        # Indicadores de presencia
        sector = 'X' if any('sector' in d for d in dims) else ''
        jornada = 'X' if 'tipo_jornada' in dims else ''
        ccaa = 'X' if 'ccaa' in dims else ''
        tiempo = 'X' if 'tipo_tiempo_trabajo' in dims else ''
        tamaño = 'X' if 'tamaño_empresa' in dims else ''
        
        metricas = ', '.join(info['metricas']) if info['metricas'] else 'valor'
        if len(metricas) > 40:
            metricas = metricas[:37] + '...'
        
        print(f"{codigo:<8} {sector:<8} {jornada:<8} {ccaa:<6} {tiempo:<8} {tamaño:<8} {metricas:<40}")
    
    print("-" * 100)
    print("\nNOTA: Todas las tablas incluyen 'periodo' y 'valor' (métrica numérica)")

if __name__ == "__main__":
    main()