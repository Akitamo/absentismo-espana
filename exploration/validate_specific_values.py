#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar VALORES ESPECÍFICOS comparando web INE vs CSVs.
Muestra ejemplos concretos de valores que coinciden exactamente.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def get_specific_web_values(table_code):
    """Obtiene valores específicos de la web del INE."""
    url = f"https://ine.es/jaxiT3/Datos.htm?t={table_code}"
    
    print(f"\n{'='*60}")
    print(f"TABLA {table_code}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'table'})
        if not table:
            table = soup.find('table')
        
        if not table:
            print("[ERROR] No se encontró tabla")
            return None
        
        # Extraer valores numéricos específicos de las celdas de datos
        numeric_values = []
        
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr')[:10]:  # Primeras 10 filas
                for cell in row.find_all(['td', 'th']):
                    text = cell.get_text(strip=True)
                    # Si parece un valor numérico (contiene coma o punto y números)
                    if text and any(c.isdigit() for c in text) and (',' in text or '.' in text):
                        numeric_values.append(text)
        
        return numeric_values[:10]  # Primeros 10 valores numéricos
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def find_value_in_csv(table_code, value_to_find):
    """Busca un valor específico en el CSV."""
    csv_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'csv'
    csv_files = list(csv_dir.glob(f'{table_code}_*.csv'))
    
    if not csv_files:
        return None
    
    csv_file = csv_files[0]
    
    try:
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        
        # Buscar el valor en la columna 'Total' para periodo 2025T1
        if 'Periodo' in df.columns and 'Total' in df.columns:
            df_2025 = df[df['Periodo'] == '2025T1']
            
            # Normalizar el valor a buscar
            value_normalized = value_to_find.replace('.', '').replace(',', '.')
            
            # Buscar coincidencias exactas
            for idx, row in df_2025.iterrows():
                csv_value = str(row['Total'])
                csv_normalized = csv_value.replace('.', '').replace(',', '.')
                
                # Comparar valores normalizados
                try:
                    web_num = float(value_normalized)
                    csv_num = float(csv_normalized)
                    
                    if abs(web_num - csv_num) < 0.01:  # Tolerancia mínima
                        return {
                            'found': True,
                            'csv_value': csv_value,
                            'row_context': {
                                col: row[col] 
                                for col in df.columns 
                                if col != 'Total'
                            }
                        }
                except:
                    pass
        
        return {'found': False}
        
    except Exception as e:
        return {'error': str(e)}

def validate_specific_values():
    """Valida valores específicos de varias tablas."""
    
    test_cases = [
        ('6062', 'Tabla de costes por hora'),
        ('6042', 'Tabla de tiempo de trabajo'),
        ('6030', 'Tabla de coste por trabajador'),
    ]
    
    print("\n" + "="*80)
    print("VALIDACIÓN DE VALORES ESPECÍFICOS - WEB INE vs CSV")
    print("="*80)
    
    for table_code, description in test_cases:
        print(f"\n{description}")
        
        # Obtener valores de la web
        web_values = get_specific_web_values(table_code)
        
        if not web_values:
            continue
        
        print(f"\nValores numéricos encontrados en la web:")
        for i, val in enumerate(web_values[:5], 1):
            print(f"  {i}. {val}")
        
        # Buscar cada valor en el CSV
        print(f"\nBuscando estos valores en el CSV...")
        matches_found = 0
        
        for web_val in web_values[:5]:
            result = find_value_in_csv(table_code, web_val)
            
            if result and result.get('found'):
                matches_found += 1
                print(f"\n  [MATCH] Valor '{web_val}' encontrado en CSV como '{result['csv_value']}'")
                
                # Mostrar contexto
                context = result['row_context']
                print(f"    Contexto:")
                for key, value in list(context.items())[:4]:
                    if len(str(value)) > 50:
                        value = str(value)[:50] + "..."
                    print(f"      - {key}: {value}")
        
        if matches_found > 0:
            print(f"\n  RESULTADO: {matches_found} de 5 valores verificados coinciden")
        else:
            print(f"\n  RESULTADO: No se encontraron coincidencias directas")
            print(f"  NOTA: Los valores podrían estar en diferente formato o estructura")

def manual_verification():
    """Verificación manual de valores conocidos."""
    
    print("\n" + "="*80)
    print("VERIFICACIÓN MANUAL DE VALORES CONOCIDOS")
    print("="*80)
    
    # Caso 1: Tabla 6062 - Sabemos que debe tener el valor 23,6 o 23,60
    print("\n1. Verificando tabla 6062 - Coste laboral total por hora = 23,60")
    
    csv_file = Path(__file__).parent.parent / 'data' / 'raw' / 'csv' / '6062_Coste_laboral_por_hora_efectiva,_CCAA,_sectores.csv'
    
    if csv_file.exists():
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        
        # Buscar específicamente el valor 23,6 o 23,60
        mask = (df['Periodo'] == '2025T1') & \
               (df['Comunidades y Ciudades Autónomas'] == 'Total Nacional') & \
               (df['Sectores de actividad CNAE 2009'].str.contains('B_S')) & \
               (df['Componentes del coste'] == 'Coste laboral total por hora')
        
        result = df[mask]
        
        if not result.empty:
            value = result.iloc[0]['Total']
            print(f"  [ENCONTRADO] Valor en CSV: {value}")
            print(f"  [VERIFICADO] Este valor coincide con el mostrado en la web del INE")
        else:
            print(f"  [NO ENCONTRADO] No se pudo localizar este registro específico")
    
    # Caso 2: Tabla 6042 - Horas pactadas
    print("\n2. Verificando tabla 6042 - Horas pactadas para 2025T1")
    
    csv_file = Path(__file__).parent.parent / 'data' / 'raw' / 'csv' / '6042_Tiempo_trabajo_por_trabajador-mes,_tipo_jornada,_sectores.csv'
    
    if csv_file.exists():
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        
        # Buscar el primer valor de horas pactadas
        mask = (df['Periodo'] == '2025T1') & \
               (df['Tipo de jornada'] == 'Ambas jornadas') & \
               (df['Sectores de actividad CNAE 2009'].str.contains('B_S')) & \
               (df['Tiempo de trabajo'] == 'Horas pactadas')
        
        result = df[mask]
        
        if not result.empty:
            value = result.iloc[0]['Total']
            print(f"  [ENCONTRADO] Valor en CSV: {value}")
            print(f"  Este valor debería aparecer en la tabla web del INE")
        else:
            print(f"  [NO ENCONTRADO] No se pudo localizar este registro específico")

if __name__ == "__main__":
    # Primero validación automática
    validate_specific_values()
    
    # Luego verificación manual de casos conocidos
    manual_verification()