#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar nuestros datos contra los valores publicados en la web del INE.
Utiliza el endpoint directo de datos para comparación automática.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime

def get_ine_web_data(table_code):
    """Obtiene datos de la web del INE para una tabla específica."""
    
    url = f"https://ine.es/jaxiT3/Datos.htm?t={table_code}"
    
    try:
        # Hacer petición
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la tabla de datos
        table = soup.find('table', {'class': 'table'})
        if not table:
            # Buscar alternativas
            table = soup.find('table')
        
        if not table:
            return {
                'table_code': table_code,
                'status': 'no_table_found',
                'url': url
            }
        
        # Extraer datos de la tabla
        data = []
        headers = []
        
        # Obtener headers
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        
        # Obtener filas de datos
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows[:10]:  # Limitar a primeras 10 filas para prueba
                cols = row.find_all(['td', 'th'])
                row_data = [col.get_text(strip=True) for col in cols]
                if row_data:
                    data.append(row_data)
        
        # Buscar periodo más reciente
        periodo_element = soup.find(string=lambda t: '2025T1' in str(t))
        periodo = '2025T1' if periodo_element else 'Unknown'
        
        return {
            'table_code': table_code,
            'status': 'success',
            'url': url,
            'headers': headers,
            'data_sample': data,
            'periodo_reciente': periodo,
            'num_filas': len(data)
        }
        
    except Exception as e:
        return {
            'table_code': table_code,
            'status': 'error',
            'error': str(e),
            'url': url
        }

def compare_with_csv(table_code, ine_data):
    """Compara datos del INE web con nuestros CSVs."""
    
    csv_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'csv'
    
    # Buscar archivo CSV
    csv_files = list(csv_dir.glob(f'{table_code}_*.csv'))
    if not csv_files:
        return {'status': 'csv_not_found'}
    
    csv_file = csv_files[0]
    
    try:
        # Leer CSV
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8', nrows=10)
        
        # Buscar valores específicos para comparar
        # Por ejemplo, buscar el valor más reciente (2025T1)
        if 'Periodo' in df.columns:
            recent_data = df[df['Periodo'] == '2025T1'].head(1)
            
            if not recent_data.empty:
                csv_value = recent_data.iloc[0].to_dict()
                
                return {
                    'status': 'compared',
                    'csv_file': csv_file.name,
                    'csv_sample': csv_value,
                    'ine_sample': ine_data.get('data_sample', [])[0] if ine_data.get('data_sample') else None
                }
        
        return {
            'status': 'no_recent_data',
            'csv_file': csv_file.name
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def validate_tables():
    """Valida un conjunto de tablas representativas."""
    
    # Tablas a validar (una de cada tipo)
    test_tables = [
        '6062',  # Coste laboral por hora (ya probada)
        '6030',  # Coste laboral por trabajador
        '6042',  # Tiempo de trabajo
        '6047',  # Vacantes
        '11221', # Series temporales
        '6038',  # Coste salarial
    ]
    
    results = []
    
    print("=" * 80)
    print("VALIDACIÓN DE DATOS INE - WEB vs CSV")
    print("=" * 80)
    print()
    
    for table_code in test_tables:
        print(f"\nProcesando tabla {table_code}...")
        
        # Obtener datos de la web
        ine_data = get_ine_web_data(table_code)
        
        # Comparar con CSV
        comparison = compare_with_csv(table_code, ine_data)
        
        # Combinar resultados
        result = {
            'table_code': table_code,
            'ine_web': ine_data,
            'comparison': comparison
        }
        
        results.append(result)
        
        # Mostrar resumen
        if ine_data['status'] == 'success':
            print(f"  [OK] Datos web obtenidos: {ine_data.get('num_filas', 0)} filas")
            if ine_data.get('headers'):
                print(f"  Columnas: {', '.join(ine_data['headers'][:3])}...")
        else:
            print(f"  [ERROR] Error obteniendo datos web: {ine_data.get('status')}")
        
        if comparison['status'] == 'compared':
            print(f"  [OK] Comparación realizada con {comparison['csv_file']}")
        else:
            print(f"  - Estado comparación: {comparison['status']}")
    
    # Guardar resultados
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'validacion_ine_web_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n\nResultados guardados en: {output_file}")
    
    return results

def normalize_numeric_value(value_str):
    """Normaliza valores numéricos para comparación."""
    if not value_str:
        return None
    
    # Limpiar el valor
    value_str = str(value_str).strip()
    
    # Reemplazar separador de miles y decimal
    value_str = value_str.replace('.', '')  # Quitar separador de miles
    value_str = value_str.replace(',', '.')  # Cambiar coma decimal por punto
    
    try:
        return float(value_str)
    except:
        return value_str  # Retornar string si no es numérico

def test_single_table():
    """Prueba con una sola tabla para verificar el concepto."""
    
    print("\nPRUEBA RÁPIDA - Tabla 6062")
    print("-" * 40)
    
    # Probar con tabla 6062 que sabemos que funciona
    data = get_ine_web_data('6062')
    
    if data['status'] == 'success':
        print("[OK] Conexión exitosa")
        print(f"URL: {data['url']}")
        print(f"Headers encontrados: {len(data.get('headers', []))}")
        print(f"Filas de datos: {data.get('num_filas', 0)}")
        
        if data.get('data_sample'):
            print("\nPrimer valor de muestra:")
            for i, val in enumerate(data['data_sample'][0][:4]):
                print(f"  {i}: {val}")
    else:
        print(f"[ERROR] Error: {data.get('error', data['status'])}")
    
    return data

if __name__ == "__main__":
    # Primero hacer prueba simple
    test_data = test_single_table()
    
    print("\n" + "=" * 80)
    
    # Si funciona, validar múltiples tablas
    if test_data['status'] == 'success':
        print("\nPrueba exitosa. Procediendo con validación múltiple...")
        validate_tables()
    else:
        print("\nNo se pudo conectar con el endpoint del INE.")
        print("Puede requerir análisis adicional del JavaScript de la página.")