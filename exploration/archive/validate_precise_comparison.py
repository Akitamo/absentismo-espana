#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validación RIGUROSA que compara valores específicos entre web INE y CSVs.
Busca coincidencias exactas para validar la integridad de los datos.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime

def normalize_value(value):
    """Normaliza un valor para comparación."""
    if pd.isna(value) or value == '':
        return None
    value_str = str(value).strip()
    # Normalizar formato numérico
    value_str = value_str.replace(' ', '')  # Quitar espacios
    return value_str

def get_web_table_values(table_code):
    """Obtiene valores específicos de la tabla web del INE."""
    url = f"https://ine.es/jaxiT3/Datos.htm?t={table_code}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'table'})
        if not table:
            table = soup.find('table')
        
        if not table:
            return None
        
        # Extraer todos los valores de la tabla
        values_found = []
        
        # Headers
        thead = table.find('thead')
        if thead:
            for row in thead.find_all('tr'):
                for cell in row.find_all(['th', 'td']):
                    text = cell.get_text(strip=True)
                    if text:
                        values_found.append({
                            'location': 'header',
                            'value': text
                        })
        
        # Data rows
        tbody = table.find('tbody')
        if tbody:
            for i, row in enumerate(tbody.find_all('tr')):
                for j, cell in enumerate(row.find_all(['td', 'th'])):
                    text = cell.get_text(strip=True)
                    if text:
                        values_found.append({
                            'location': f'row_{i+1}_col_{j+1}',
                            'value': text
                        })
        
        return values_found
        
    except Exception as e:
        print(f"Error obteniendo tabla {table_code}: {e}")
        return None

def validate_table_detailed(table_code):
    """Validación detallada de una tabla específica."""
    
    print(f"\n{'='*80}")
    print(f"VALIDACIÓN DETALLADA - Tabla {table_code}")
    print('='*80)
    
    # Obtener valores de la web
    web_values = get_web_table_values(table_code)
    if not web_values:
        print(f"[ERROR] No se pudieron obtener valores web para tabla {table_code}")
        return None
    
    print(f"[OK] Valores web obtenidos: {len(web_values)} valores totales")
    
    # Leer CSV correspondiente
    csv_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'csv'
    csv_files = list(csv_dir.glob(f'{table_code}_*.csv'))
    
    if not csv_files:
        print(f"[ERROR] No se encontró CSV para tabla {table_code}")
        return None
    
    csv_file = csv_files[0]
    print(f"[OK] CSV encontrado: {csv_file.name}")
    
    try:
        # Leer CSV
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        print(f"[OK] CSV leído: {df.shape[0]} filas x {df.shape[1]} columnas")
        
        # Buscar coincidencias específicas
        matches = []
        
        # Filtrar por periodo 2025T1 para comparación más precisa
        df_2025 = df[df['Periodo'] == '2025T1'] if 'Periodo' in df.columns else df
        
        print(f"\nBuscando coincidencias en {len(df_2025)} registros de 2025T1...")
        
        # Para cada valor web, buscar en el CSV
        for web_item in web_values[:50]:  # Limitar a primeros 50 valores para eficiencia
            web_val = normalize_value(web_item['value'])
            
            # Buscar este valor en todas las columnas del CSV
            for col in df_2025.columns:
                csv_matches = df_2025[df_2025[col].astype(str).apply(normalize_value) == web_val]
                
                if not csv_matches.empty:
                    for idx, row in csv_matches.iterrows():
                        matches.append({
                            'web_value': web_item['value'],
                            'web_location': web_item['location'],
                            'csv_column': col,
                            'csv_row': idx,
                            'csv_context': {
                                col_name: row[col_name] 
                                for col_name in df_2025.columns 
                                if col_name != col
                            }
                        })
        
        print(f"\n[RESULTADO] Se encontraron {len(matches)} coincidencias")
        
        # Mostrar algunas coincidencias como ejemplo
        if matches:
            print("\nEJEMPLOS DE COINCIDENCIAS:")
            print("-" * 40)
            
            # Agrupar por tipo de coincidencia
            numeric_matches = [m for m in matches if any(c.isdigit() for c in m['web_value'])]
            text_matches = [m for m in matches if not any(c.isdigit() for c in m['web_value'])]
            
            # Mostrar valores numéricos coincidentes
            if numeric_matches:
                print("\nVALORES NUMÉRICOS COINCIDENTES:")
                for match in numeric_matches[:5]:
                    print(f"  Web: '{match['web_value']}' (en {match['web_location']})")
                    print(f"  CSV: Columna '{match['csv_column']}', Fila {match['csv_row']}")
                    # Mostrar contexto
                    context_str = ', '.join([f"{k}={v}" for k,v in list(match['csv_context'].items())[:3]])
                    print(f"  Contexto: {context_str}")
                    print()
            
            # Mostrar dimensiones coincidentes
            if text_matches:
                print("\nDIMENSIONES COINCIDENTES:")
                unique_texts = list(set([m['web_value'] for m in text_matches]))[:5]
                for text in unique_texts:
                    match = next(m for m in text_matches if m['web_value'] == text)
                    print(f"  '{text}' encontrado en columna '{match['csv_column']}'")
        
        return {
            'table_code': table_code,
            'total_web_values': len(web_values),
            'total_csv_rows': len(df),
            'csv_2025_rows': len(df_2025),
            'total_matches': len(matches),
            'numeric_matches': len([m for m in matches if any(c.isdigit() for c in m['web_value'])]),
            'text_matches': len([m for m in matches if not any(c.isdigit() for c in m['web_value'])]),
            'sample_matches': matches[:10] if matches else []
        }
        
    except Exception as e:
        print(f"[ERROR] Error procesando: {e}")
        return None

def run_comprehensive_validation():
    """Ejecuta validación completa en múltiples tablas."""
    
    # Tablas a validar
    test_tables = [
        '6042',  # Tiempo de trabajo
        '6062',  # Coste por hora  
        '6030',  # Coste por trabajador
        '11221', # Series temporales
        '6038',  # Coste salarial
    ]
    
    print("\n" + "="*80)
    print("VALIDACIÓN RIGUROSA - COMPARACIÓN WEB INE vs CSV")
    print("="*80)
    
    all_results = []
    summary = {
        'tables_validated': 0,
        'tables_with_matches': 0,
        'total_matches': 0,
        'numeric_matches': 0
    }
    
    for table_code in test_tables:
        result = validate_table_detailed(table_code)
        
        if result:
            all_results.append(result)
            summary['tables_validated'] += 1
            
            if result['total_matches'] > 0:
                summary['tables_with_matches'] += 1
                summary['total_matches'] += result['total_matches']
                summary['numeric_matches'] += result['numeric_matches']
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DE VALIDACIÓN")
    print("="*80)
    print(f"Tablas validadas: {summary['tables_validated']}/{len(test_tables)}")
    print(f"Tablas con coincidencias: {summary['tables_with_matches']}")
    print(f"Total de coincidencias encontradas: {summary['total_matches']}")
    print(f"Coincidencias numéricas (valores): {summary['numeric_matches']}")
    
    # Análisis por tabla
    print("\nDETALLE POR TABLA:")
    print("-" * 40)
    for result in all_results:
        if result:
            print(f"\nTabla {result['table_code']}:")
            print(f"  - Valores web analizados: {result['total_web_values']}")
            print(f"  - Filas CSV (2025T1): {result['csv_2025_rows']}")
            print(f"  - Coincidencias totales: {result['total_matches']}")
            print(f"  - Valores numéricos coincidentes: {result['numeric_matches']}")
            print(f"  - Textos/dimensiones coincidentes: {result['text_matches']}")
            
            if result['numeric_matches'] > 0:
                print(f"  [OK] VALIDACION POSITIVA: Se encontraron valores numéricos coincidentes")
    
    # Guardar resultados
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'validacion_rigurosa_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'summary': summary,
            'details': all_results
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n[ARCHIVO] Resultados detallados guardados en:")
    print(f"  {output_file}")
    
    return all_results

if __name__ == "__main__":
    results = run_comprehensive_validation()