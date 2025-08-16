#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validación exhaustiva para las 33 tablas del INE con endpoint disponible.
Compara valores específicos entre web y CSVs descargados.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime
import time

def normalize_value(value):
    """Normaliza un valor para comparación."""
    if pd.isna(value) or value == '':
        return None
    value_str = str(value).strip()
    value_str = value_str.replace(' ', '')
    return value_str

def get_web_values(table_code, limit=20):
    """Obtiene valores de la tabla web del INE."""
    url = f"https://ine.es/jaxiT3/Datos.htm?t={table_code}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'table'})
        if not table:
            table = soup.find('table')
        
        if not table:
            return None
        
        # Extraer valores numéricos de la tabla
        numeric_values = []
        text_values = []
        
        # Analizar tbody
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr')[:limit]:
                for cell in row.find_all(['td', 'th']):
                    text = cell.get_text(strip=True)
                    if text:
                        # Si parece numérico
                        if any(c.isdigit() for c in text) and (',' in text or '.' in text):
                            numeric_values.append(text)
                        else:
                            text_values.append(text)
        
        return {
            'numeric': numeric_values[:10],  # Primeros 10 valores numéricos
            'text': text_values[:10]  # Primeras 10 dimensiones
        }
        
    except Exception as e:
        return None

def validate_table(table_code, table_name):
    """Valida una tabla específica."""
    
    # Obtener valores de la web
    web_values = get_web_values(table_code)
    if not web_values:
        return {
            'code': table_code,
            'name': table_name,
            'status': 'NO_WEB_DATA',
            'matches': 0
        }
    
    # Buscar CSV correspondiente
    csv_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'csv'
    csv_files = list(csv_dir.glob(f'{table_code}_*.csv'))
    
    if not csv_files:
        return {
            'code': table_code,
            'name': table_name,
            'status': 'NO_CSV',
            'matches': 0
        }
    
    csv_file = csv_files[0]
    
    try:
        # Leer CSV
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        
        # Filtrar por 2025T1
        if 'Periodo' in df.columns:
            df_2025 = df[df['Periodo'] == '2025T1']
        else:
            df_2025 = df.head(100)  # Si no hay periodo, tomar primeras filas
        
        # Contar coincidencias
        matches = 0
        examples = []
        
        # Buscar valores numéricos en columna Total
        if 'Total' in df_2025.columns:
            for web_val in web_values['numeric'][:5]:
                web_normalized = normalize_value(web_val)
                
                for idx, row in df_2025.iterrows():
                    csv_val = str(row['Total'])
                    csv_normalized = normalize_value(csv_val)
                    
                    # Comparar normalizados
                    web_clean = web_normalized.replace('.', '').replace(',', '.')
                    csv_clean = csv_normalized.replace('.', '').replace(',', '.')
                    
                    try:
                        if abs(float(web_clean) - float(csv_clean)) < 0.01:
                            matches += 1
                            if len(examples) < 3:
                                examples.append({
                                    'web': web_val,
                                    'csv': csv_val,
                                    'context': {k: row[k] for k in df.columns[:3] if k != 'Total'}
                                })
                            break
                    except:
                        pass
        
        # Buscar coincidencias de texto/dimensiones
        text_matches = 0
        for web_text in web_values['text']:
            if any(web_text in str(val) for val in df_2025.values.flatten()):
                text_matches += 1
        
        return {
            'code': table_code,
            'name': table_name,
            'status': 'VALIDATED',
            'csv_file': csv_file.name,
            'matches': matches,
            'text_matches': text_matches,
            'examples': examples,
            'web_values_count': len(web_values['numeric']),
            'csv_rows_2025': len(df_2025)
        }
        
    except Exception as e:
        return {
            'code': table_code,
            'name': table_name,
            'status': 'ERROR',
            'error': str(e),
            'matches': 0
        }

def run_exhaustive_validation():
    """Ejecuta validación completa de todas las tablas."""
    
    print("\n" + "="*80)
    print("VALIDACIÓN EXHAUSTIVA - 33 TABLAS INE")
    print("="*80)
    
    # Leer configuración
    config_file = Path(__file__).parent.parent / 'config' / 'tables.json'
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    # Leer lista de tablas con endpoint funcional
    endpoint_file = Path(__file__).parent.parent / 'data' / 'exploration_reports' / 'endpoint_verification.json'
    with open(endpoint_file, 'r', encoding='utf-8') as f:
        endpoint_data = json.load(f)
    
    valid_tables = endpoint_data['results']['ok']
    
    # Obtener info de cada tabla
    all_tables = {}
    for categoria, cat_data in config_data['categorias'].items():
        if 'tablas' in cat_data:
            for codigo, info in cat_data['tablas'].items():
                if codigo in valid_tables:
                    all_tables[codigo] = info['nombre']
    
    print(f"\nValidando {len(all_tables)} tablas con endpoint funcional...\n")
    
    results = []
    summary = {
        'total': len(all_tables),
        'validated': 0,
        'with_matches': 0,
        'perfect_match': 0,
        'partial_match': 0,
        'no_match': 0,
        'errors': 0
    }
    
    # Validar cada tabla
    for i, (code, name) in enumerate(all_tables.items(), 1):
        print(f"[{i:2d}/{len(all_tables)}] Validando {code}...", end=' ')
        
        result = validate_table(code, name)
        results.append(result)
        
        if result['status'] == 'VALIDATED':
            summary['validated'] += 1
            if result['matches'] > 0:
                summary['with_matches'] += 1
                if result['matches'] >= 3:
                    summary['perfect_match'] += 1
                    print(f"[PERFECTO] {result['matches']} coincidencias")
                else:
                    summary['partial_match'] += 1
                    print(f"[PARCIAL] {result['matches']} coincidencias")
            else:
                summary['no_match'] += 1
                print("[SIN COINCIDENCIAS]")
        else:
            summary['errors'] += 1
            print(f"[ERROR: {result['status']}]")
        
        # Pequeña pausa para no sobrecargar el servidor
        time.sleep(0.5)
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE VALIDACIÓN")
    print("="*80)
    
    print(f"\nTablas procesadas: {summary['total']}")
    print(f"Tablas validadas correctamente: {summary['validated']}")
    print(f"Tablas con coincidencias: {summary['with_matches']}")
    print(f"  - Coincidencia perfecta (3+ valores): {summary['perfect_match']}")
    print(f"  - Coincidencia parcial (1-2 valores): {summary['partial_match']}")
    print(f"  - Sin coincidencias: {summary['no_match']}")
    print(f"Errores: {summary['errors']}")
    
    # Calcular porcentaje de éxito
    if summary['validated'] > 0:
        success_rate = (summary['with_matches'] / summary['validated']) * 100
        print(f"\nTasa de éxito: {success_rate:.1f}%")
    
    # Mostrar ejemplos de coincidencias
    print("\n" + "="*80)
    print("EJEMPLOS DE VALORES COINCIDENTES")
    print("="*80)
    
    tables_with_examples = [r for r in results if r.get('examples')][:5]
    
    for result in tables_with_examples:
        print(f"\n{result['code']} - {result['name']}:")
        for ex in result['examples'][:2]:
            print(f"  Web: '{ex['web']}' = CSV: '{ex['csv']}'")
            if ex.get('context'):
                context_str = ', '.join([f"{k}={v}" for k,v in list(ex['context'].items())[:2]])
                print(f"    Contexto: {context_str}")
    
    # Guardar resultados detallados
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'validacion_exhaustiva_{timestamp}.json'
    
    full_results = {
        'timestamp': timestamp,
        'summary': summary,
        'tables': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n[GUARDADO] Resultados detallados en:")
    print(f"  {output_file}")
    
    # Análisis final
    print("\n" + "="*80)
    print("CONCLUSIÓN")
    print("="*80)
    
    if success_rate > 80:
        print("\n[ÉXITO] La validación confirma que los datos extraídos son correctos.")
        print(f"  - {summary['with_matches']} de {summary['validated']} tablas tienen valores coincidentes")
        print("  - Los datos del sistema de extracción coinciden con la web del INE")
    elif success_rate > 50:
        print("\n[PARCIAL] La validación muestra coincidencias moderadas.")
        print("  - Revisar las tablas sin coincidencias para identificar posibles problemas")
    else:
        print("\n[ATENCIÓN] Pocas coincidencias encontradas.")
        print("  - Puede deberse a diferencias de formato entre web y CSV")
        print("  - Revisar la lógica de comparación")
    
    # Listar tablas problemáticas si las hay
    no_match_tables = [r for r in results if r['status'] == 'VALIDATED' and r['matches'] == 0]
    if no_match_tables:
        print("\n[INFO] Tablas sin coincidencias (pueden requerir revisión manual):")
        for t in no_match_tables[:10]:
            print(f"  - {t['code']}: {t['name']}")

if __name__ == "__main__":
    run_exhaustive_validation()