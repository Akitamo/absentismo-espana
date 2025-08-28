#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar la estructura exacta de las tablas web del INE
y compararla con nuestros CSVs para entender las diferencias.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json

def analyze_web_structure(table_code):
    """Analiza en detalle la estructura de una tabla web del INE."""
    
    url = f"https://ine.es/jaxiT3/Datos.htm?t={table_code}"
    
    print(f"\n{'='*60}")
    print(f"ANALIZANDO ESTRUCTURA WEB - Tabla {table_code}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar tabla
        table = soup.find('table', {'class': 'table'})
        if not table:
            table = soup.find('table')
        
        if not table:
            print("[ERROR] No se encontró tabla en la página")
            return None
        
        print("\n[1] ESTRUCTURA DE LA TABLA WEB:")
        print("-" * 40)
        
        # Analizar headers
        thead = table.find('thead')
        if thead:
            print("\nHEADERS encontrados:")
            header_rows = []
            for i, row in enumerate(thead.find_all('tr')):
                row_headers = []
                for cell in row.find_all(['th', 'td']):
                    text = cell.get_text(strip=True)
                    colspan = cell.get('colspan', '1')
                    rowspan = cell.get('rowspan', '1')
                    if text:
                        row_headers.append({
                            'text': text,
                            'colspan': colspan,
                            'rowspan': rowspan
                        })
                header_rows.append(row_headers)
                print(f"  Fila {i+1}: {len(row_headers)} celdas")
                for j, h in enumerate(row_headers[:5]):  # Primeras 5 celdas
                    print(f"    [{j+1}] '{h['text']}' (colspan={h['colspan']}, rowspan={h['rowspan']})")
        
        # Analizar primeras filas de datos
        tbody = table.find('tbody')
        if tbody:
            print("\nPRIMERAS FILAS DE DATOS:")
            data_rows = tbody.find_all('tr')[:3]  # Primeras 3 filas
            for i, row in enumerate(data_rows):
                cells = row.find_all(['td', 'th'])
                print(f"\n  Fila {i+1}: {len(cells)} celdas")
                for j, cell in enumerate(cells[:5]):  # Primeras 5 celdas
                    text = cell.get_text(strip=True)
                    print(f"    [{j+1}] '{text}'")
        
        # Contar total de filas y columnas
        all_rows = tbody.find_all('tr') if tbody else []
        if all_rows:
            first_row_cells = len(all_rows[0].find_all(['td', 'th']))
            print(f"\nTOTAL: {len(all_rows)} filas x {first_row_cells} columnas")
        
        return {
            'table_code': table_code,
            'url': url,
            'header_rows': header_rows if 'header_rows' in locals() else [],
            'num_data_rows': len(all_rows)
        }
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

def analyze_csv_structure(table_code):
    """Analiza la estructura del CSV correspondiente."""
    
    print(f"\n[2] ESTRUCTURA DEL CSV:")
    print("-" * 40)
    
    csv_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'csv'
    csv_files = list(csv_dir.glob(f'{table_code}_*.csv'))
    
    if not csv_files:
        print(f"[ERROR] No se encontró CSV para tabla {table_code}")
        return None
    
    csv_file = csv_files[0]
    print(f"Archivo: {csv_file.name}")
    
    try:
        # Leer CSV
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        
        print(f"\nDimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"Columnas: {list(df.columns)}")
        
        # Mostrar primeras filas
        print("\nPRIMERAS 3 FILAS:")
        for i in range(min(3, len(df))):
            print(f"\n  Fila {i+1}:")
            row = df.iloc[i]
            for col in df.columns[:5]:  # Primeras 5 columnas
                value = row[col]
                print(f"    {col}: '{value}'")
        
        # Analizar periodo más reciente
        if 'Periodo' in df.columns:
            latest = df[df['Periodo'] == '2025T1']
            print(f"\nRegistros en 2025T1: {len(latest)}")
            
            if len(latest) > 0:
                print("\nPRIMER REGISTRO DE 2025T1:")
                first = latest.iloc[0]
                for col in df.columns:
                    print(f"  {col}: '{first[col]}'")
        
        return {
            'csv_file': csv_file.name,
            'shape': df.shape,
            'columns': list(df.columns)
        }
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

def compare_structures():
    """Compara estructuras de varias tablas representativas."""
    
    test_tables = [
        '6042',  # Tiempo de trabajo - sabemos que funciona
        '6062',  # Coste por hora - también funciona
    ]
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPARATIVO DE ESTRUCTURAS WEB vs CSV")
    print("="*80)
    
    for table_code in test_tables:
        web_structure = analyze_web_structure(table_code)
        csv_structure = analyze_csv_structure(table_code)
        
        print(f"\n[3] ANÁLISIS DE DIFERENCIAS - Tabla {table_code}:")
        print("-" * 40)
        
        if web_structure and csv_structure:
            print("\nOBSERVACIONES:")
            print("- La tabla web parece estar en formato PIVOTADO (columnas como filas)")
            print("- El CSV está en formato LARGO (una fila por observación)")
            print("- Necesitamos 'despivotear' la tabla web para comparar correctamente")
            
            # Intentar mapear correspondencias
            print("\nMAPEO SUGERIDO:")
            print("- Las filas de la web corresponden a combinaciones de dimensiones del CSV")
            print("- Las columnas de la web corresponden a diferentes métricas o periodos")
            print("- Los valores numéricos están en las intersecciones")

if __name__ == "__main__":
    compare_structures()