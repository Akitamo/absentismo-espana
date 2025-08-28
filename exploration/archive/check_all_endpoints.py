#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar qué tablas tienen endpoint web disponible en el INE.
Identifica cuáles necesitarían validación manual.
"""

import requests
from pathlib import Path
import json
from datetime import datetime

def check_endpoint(table_code):
    """Verifica si un endpoint existe y es accesible."""
    url = f"https://ine.es/jaxiT3/Datos.htm?t={table_code}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Verificar que realmente tiene una tabla
            if '<table' in response.text.lower():
                return {'status': 'OK', 'url': url}
            else:
                return {'status': 'NO_TABLE', 'url': url}
        elif response.status_code == 404:
            return {'status': 'NOT_FOUND', 'url': url}
        else:
            return {'status': f'ERROR_{response.status_code}', 'url': url}
            
    except Exception as e:
        return {'status': 'EXCEPTION', 'error': str(e), 'url': url}

def check_all_tables():
    """Verifica todas las tablas configuradas."""
    
    # Leer configuración de tablas
    config_file = Path(__file__).parent.parent / 'config' / 'tables.json'
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        
    # Extraer todas las tablas de todas las categorías
    tables_config = {}
    categorias = config_data.get('categorias', {})
    
    for categoria, cat_data in categorias.items():
        if 'tablas' in cat_data:
            for codigo, tabla_info in cat_data['tablas'].items():
                tables_config[codigo] = tabla_info
    
    print("\n" + "="*80)
    print("VERIFICACIÓN DE ENDPOINTS WEB DEL INE")
    print("="*80)
    print(f"\nVerificando {len(tables_config)} tablas...\n")
    
    results = {
        'ok': [],
        'no_table': [],
        'not_found': [],
        'error': []
    }
    
    # Verificar cada tabla
    for i, (code, info) in enumerate(tables_config.items(), 1):
        print(f"[{i:2d}/{len(tables_config)}] Verificando tabla {code}...", end=' ')
        
        result = check_endpoint(code)
        
        if result['status'] == 'OK':
            results['ok'].append(code)
            print("[OK]")
        elif result['status'] == 'NO_TABLE':
            results['no_table'].append(code)
            print("[SIN TABLA]")
        elif result['status'] == 'NOT_FOUND':
            results['not_found'].append(code)
            print("[404 NO ENCONTRADO]")
        else:
            results['error'].append((code, result['status']))
            print(f"[ERROR: {result['status']}]")
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE RESULTADOS")
    print("="*80)
    
    print(f"\n[OK] TABLAS CON ENDPOINT FUNCIONAL: {len(results['ok'])}/{len(tables_config)}")
    if results['ok']:
        print("   Códigos:", ', '.join(results['ok'][:10]))
        if len(results['ok']) > 10:
            print(f"   ... y {len(results['ok'])-10} más")
    
    print(f"\n[X] TABLAS SIN ENDPOINT (404): {len(results['not_found'])}")
    if results['not_found']:
        print("   Códigos:", ', '.join(results['not_found']))
        print("\n   ESTAS TABLAS NECESITARÍAN VALIDACIÓN MANUAL:")
        for code in results['not_found']:
            csv_files = list(Path(__file__).parent.parent.glob(f'data/raw/csv/{code}_*.csv'))
            if csv_files:
                print(f"   - {code}: {csv_files[0].name}")
    
    print(f"\n[!] TABLAS SIN CONTENIDO DE TABLA: {len(results['no_table'])}")
    if results['no_table']:
        print("   Códigos:", ', '.join(results['no_table']))
    
    print(f"\n[ERROR] TABLAS CON OTROS ERRORES: {len(results['error'])}")
    if results['error']:
        for code, error in results['error']:
            print(f"   - {code}: {error}")
    
    # Guardar resultados
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_tables': len(tables_config),
        'results': {
            'ok': results['ok'],
            'no_table': results['no_table'],
            'not_found': results['not_found'],
            'error': [{'code': c, 'error': e} for c, e in results['error']]
        },
        'summary': {
            'with_endpoint': len(results['ok']),
            'without_endpoint': len(results['not_found']),
            'problematic': len(results['no_table']) + len(results['error'])
        }
    }
    
    output_file = Path(__file__).parent.parent / 'data' / 'exploration_reports' / 'endpoint_verification.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n[GUARDADO] Resultados en: {output_file}")
    
    # Recomendación final
    print("\n" + "="*80)
    print("RECOMENDACIÓN")
    print("="*80)
    
    if results['not_found']:
        print(f"\n[!] Hay {len(results['not_found'])} tablas sin endpoint web disponible.")
        print("   Estas tablas requerirían validación manual o un método alternativo.")
        print("   Puedes validarlas manualmente comparando algunos valores del CSV")
        print("   con los datos publicados en los boletines del INE.")
    else:
        print("\n[OK] Todas las tablas tienen endpoint disponible para validación automática.")
    
    return output

if __name__ == "__main__":
    check_all_tables()