#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mejorado para validar nuestros datos contra los valores publicados en la web del INE.
Realiza comparación numérica precisa y genera reporte detallado.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime
import numpy as np

def normalize_numeric_value(value_str):
    """Normaliza valores numéricos para comparación precisa."""
    if pd.isna(value_str) or value_str == '':
        return None
    
    # Convertir a string y limpiar
    value_str = str(value_str).strip()
    
    # Manejar valores especiales
    if value_str in ['-', '..', 'n.d.', 'NA']:
        return None
    
    # Reemplazar separadores
    value_str = value_str.replace('.', '')  # Quitar separador de miles
    value_str = value_str.replace(',', '.')  # Cambiar coma decimal por punto
    
    try:
        return float(value_str)
    except:
        return None

def extract_ine_table_data(table_code):
    """Extrae datos completos de la tabla del INE usando BeautifulSoup."""
    
    url = f"https://ine.es/jaxiT3/Datos.htm?t={table_code}"
    
    try:
        # Hacer petición con headers para simular navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la tabla de datos principal
        table = soup.find('table', {'class': 'table'})
        if not table:
            table = soup.find('table')
        
        if not table:
            return {
                'status': 'no_table_found',
                'table_code': table_code,
                'url': url
            }
        
        # Extraer todos los datos
        all_data = []
        headers = []
        
        # Procesar headers
        thead = table.find('thead')
        if thead:
            for row in thead.find_all('tr'):
                row_headers = []
                for th in row.find_all(['th', 'td']):
                    text = th.get_text(strip=True)
                    if text:
                        row_headers.append(text)
                if row_headers:
                    headers.append(row_headers)
        
        # Procesar datos
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    text = cell.get_text(strip=True)
                    row_data.append(text)
                if row_data:
                    all_data.append(row_data)
        
        # Detectar estructura de la tabla
        # Las tablas del INE típicamente tienen estructura pivotada
        
        return {
            'status': 'success',
            'table_code': table_code,
            'url': url,
            'headers': headers,
            'data': all_data,
            'num_rows': len(all_data),
            'num_cols': len(all_data[0]) if all_data else 0
        }
        
    except requests.RequestException as e:
        return {
            'status': 'request_error',
            'table_code': table_code,
            'url': url,
            'error': str(e)
        }
    except Exception as e:
        return {
            'status': 'parse_error',
            'table_code': table_code,
            'url': url,
            'error': str(e)
        }

def compare_values(web_value, csv_value, tolerance=0.01):
    """Compara dos valores numéricos con tolerancia."""
    web_num = normalize_numeric_value(web_value)
    csv_num = normalize_numeric_value(csv_value)
    
    if web_num is None or csv_num is None:
        return {
            'match': web_value == csv_value,  # Comparación de strings
            'type': 'text',
            'web': web_value,
            'csv': csv_value
        }
    
    # Comparación numérica con tolerancia
    diff = abs(web_num - csv_num)
    match = diff <= tolerance
    
    return {
        'match': match,
        'type': 'numeric',
        'web': web_num,
        'csv': csv_num,
        'difference': diff,
        'percentage_diff': (diff / web_num * 100) if web_num != 0 else 0
    }

def validate_table_comprehensive(table_code):
    """Validación completa de una tabla comparando web vs CSV."""
    
    print(f"\n{'='*60}")
    print(f"Validando tabla {table_code}")
    print('='*60)
    
    # Obtener datos de la web
    web_data = extract_ine_table_data(table_code)
    
    if web_data['status'] != 'success':
        print(f"[ERROR] No se pudieron obtener datos web: {web_data.get('error', web_data['status'])}")
        return web_data
    
    print(f"[OK] Datos web obtenidos: {web_data['num_rows']} filas x {web_data['num_cols']} columnas")
    
    # Buscar archivo CSV correspondiente
    csv_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'csv'
    csv_files = list(csv_dir.glob(f'{table_code}_*.csv'))
    
    if not csv_files:
        print(f"[ERROR] No se encontró archivo CSV para tabla {table_code}")
        return {
            'status': 'csv_not_found',
            'table_code': table_code,
            'web_data': web_data
        }
    
    csv_file = csv_files[0]
    print(f"[OK] Archivo CSV encontrado: {csv_file.name}")
    
    # Leer CSV
    try:
        # Probar diferentes encodings
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                df_csv = pd.read_csv(csv_file, sep=';', encoding=encoding)
                print(f"[OK] CSV leído con encoding {encoding}")
                break
            except:
                continue
        
        # Mostrar información del CSV
        print(f"    Dimensiones CSV: {df_csv.shape[0]} filas x {df_csv.shape[1]} columnas")
        print(f"    Columnas: {', '.join(df_csv.columns[:5])}...")
        
        # Filtrar por periodo más reciente para comparación
        if 'Periodo' in df_csv.columns:
            latest_period = '2025T1'
            df_latest = df_csv[df_csv['Periodo'] == latest_period].copy()
            print(f"    Registros en {latest_period}: {len(df_latest)}")
            
            # Realizar comparaciones de muestra
            comparisons = []
            
            # Comparar primeros valores numéricos
            numeric_cols = df_latest.select_dtypes(include=[np.number]).columns.tolist()
            value_col = 'Total' if 'Total' in df_latest.columns else df_latest.columns[-1]
            
            if len(df_latest) > 0 and len(web_data['data']) > 0:
                # Comparar primeros valores
                sample_size = min(5, len(df_latest), len(web_data['data']))
                
                print(f"\n    Comparación de muestra ({sample_size} registros):")
                matches = 0
                
                for i in range(sample_size):
                    if i < len(df_latest):
                        csv_row = df_latest.iloc[i]
                        
                        # Buscar valor correspondiente en datos web
                        if i < len(web_data['data']) and len(web_data['data'][i]) > 2:
                            # Típicamente el valor está en las últimas columnas
                            web_value = web_data['data'][i][-1]  # Último valor
                            csv_value = csv_row[value_col] if value_col in csv_row else None
                            
                            if csv_value is not None:
                                comp = compare_values(web_value, csv_value)
                                comparisons.append(comp)
                                
                                if comp['match']:
                                    matches += 1
                                    print(f"      [{i+1}] MATCH: {comp['web']} == {comp['csv']}")
                                else:
                                    print(f"      [{i+1}] DIFF: Web={comp['web']} CSV={comp['csv']} (diff={comp.get('difference', 'N/A')})")
                
                match_rate = (matches / sample_size) * 100 if sample_size > 0 else 0
                print(f"\n    Tasa de coincidencia: {match_rate:.1f}% ({matches}/{sample_size})")
            
            return {
                'status': 'validated',
                'table_code': table_code,
                'csv_file': csv_file.name,
                'web_data_summary': {
                    'rows': web_data['num_rows'],
                    'cols': web_data['num_cols']
                },
                'csv_data_summary': {
                    'total_rows': df_csv.shape[0],
                    'total_cols': df_csv.shape[1],
                    'latest_period_rows': len(df_latest)
                },
                'sample_comparisons': comparisons,
                'match_rate': match_rate
            }
        
        else:
            print("[WARNING] No se encontró columna 'Periodo' en el CSV")
            return {
                'status': 'no_period_column',
                'table_code': table_code,
                'csv_file': csv_file.name
            }
            
    except Exception as e:
        print(f"[ERROR] Error procesando CSV: {str(e)}")
        return {
            'status': 'csv_error',
            'table_code': table_code,
            'error': str(e)
        }

def validate_all_tables():
    """Valida todas las tablas configuradas."""
    
    # Leer configuración de tablas
    config_file = Path(__file__).parent.parent / 'config' / 'tables.json'
    
    with open(config_file, 'r', encoding='utf-8') as f:
        tables_config = json.load(f)
    
    # Seleccionar subset representativo para prueba inicial
    test_tables = [
        '6042',  # Tiempo de trabajo
        '6030',  # Coste laboral por trabajador
        '6062',  # Coste laboral por hora
        '6047',  # Vacantes
        '11221', # Series temporales
        '6038',  # Coste salarial
        '6050',  # Otros costes
        '6045'   # Tiempo trabajo divisiones
    ]
    
    results = []
    summary = {
        'total': len(test_tables),
        'success': 0,
        'failed': 0,
        'match_rates': []
    }
    
    print("\n" + "="*80)
    print("VALIDACIÓN COMPLETA DE DATOS INE - WEB vs CSV")
    print("="*80)
    
    for table_code in test_tables:
        result = validate_table_comprehensive(table_code)
        results.append(result)
        
        if result['status'] == 'validated':
            summary['success'] += 1
            if 'match_rate' in result:
                summary['match_rates'].append(result['match_rate'])
        else:
            summary['failed'] += 1
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DE VALIDACIÓN")
    print("="*80)
    print(f"Tablas procesadas: {summary['total']}")
    print(f"Validaciones exitosas: {summary['success']}")
    print(f"Validaciones fallidas: {summary['failed']}")
    
    if summary['match_rates']:
        avg_match_rate = sum(summary['match_rates']) / len(summary['match_rates'])
        print(f"Tasa de coincidencia promedio: {avg_match_rate:.1f}%")
    
    # Guardar resultados detallados
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'validacion_ine_enhanced_{timestamp}.json'
    
    full_results = {
        'timestamp': timestamp,
        'summary': summary,
        'validations': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultados detallados guardados en: {output_file}")
    
    return full_results

if __name__ == "__main__":
    # Ejecutar validación completa
    results = validate_all_tables()
    
    # Mostrar tablas con problemas si las hay
    failed_tables = [r for r in results['validations'] if r['status'] != 'validated']
    if failed_tables:
        print("\n" + "="*80)
        print("TABLAS CON PROBLEMAS:")
        for table in failed_tables:
            print(f"  - {table['table_code']}: {table['status']}")