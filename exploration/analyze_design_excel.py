#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis del Excel de diseño de tabla v3.
"""

import pandas as pd
from pathlib import Path
import json
import sys
import io

# Configurar encoding para salida
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_design_excel():
    """Analiza el Excel con el diseño de la tabla consolidada."""
    
    excel_path = Path(r"C:\Users\aluni\Downloads\ETCL_6042_6063_diseno_tabla_v3.xlsx")
    
    # Leer todas las hojas
    excel_data = pd.ExcelFile(excel_path)
    sheets = excel_data.sheet_names
    
    print(f"Excel con {len(sheets)} hojas: {sheets}")
    print("="*80)
    
    # Analizar cada hoja
    for sheet_name in sheets:
        print(f"\n{'='*80}")
        print(f"HOJA: {sheet_name}")
        print(f"{'='*80}")
        
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        print(f"Dimensiones: {df.shape}")
        print(f"Columnas: {df.columns.tolist()}")
        
        if sheet_name == 'Diccionario':
            print("\nPrimeros 10 campos del diccionario:")
            print(df.head(10).to_string())
            
        elif sheet_name == 'Dominios':
            print("\nDominios disponibles:")
            for col in df.columns:
                valores_unicos = df[col].dropna().unique()
                print(f"\n{col}: ({len(valores_unicos)} valores)")
                if len(valores_unicos) <= 20:
                    for val in valores_unicos:
                        print(f"  - {val}")
                else:
                    print(f"  - {list(valores_unicos[:5])} ... [{len(valores_unicos)} total]")
                    
        elif sheet_name == 'Clave_Indices':
            print("\nDefinición de claves e índices:")
            print(df.to_string())
            
        elif sheet_name == 'Validaciones':
            print("\nReglas de validación:")
            if 'validacion' in df.columns or 'regla' in df.columns:
                for idx, row in df.iterrows():
                    try:
                        print(f"{idx+1}. {row.to_dict()}")
                    except UnicodeEncodeError:
                        # Intentar con representación segura
                        print(f"{idx+1}. [contenido con caracteres especiales]")
            else:
                try:
                    print(df.head().to_string())
                except UnicodeEncodeError:
                    print("Contenido con caracteres especiales - ver Excel directamente")
                
        elif sheet_name == 'Alcance_y_Roles':
            print("\nDefinición de roles y alcance:")
            print(df.to_string())
            
        elif sheet_name == 'Cobertura_6042_6063':
            print("\nCobertura por tabla:")
            print(df.to_string())
            
        elif sheet_name == 'Jerarquia_Sector':
            print("\nJerarquía CNAE (primeros 20):")
            print(df.head(20).to_string())
    
    # Extraer información clave para el procesador
    print(f"\n{'='*80}")
    print("RESUMEN PARA IMPLEMENTACIÓN")
    print(f"{'='*80}")
    
    # Diccionario de campos
    df_dict = pd.read_excel(excel_path, sheet_name='Diccionario')
    campos_clave = df_dict[df_dict['es_clave'] == 'SI'] if 'es_clave' in df_dict.columns else df_dict.head(10)
    print("\nCampos clave de la tabla:")
    print(campos_clave[['campo', 'tipo', 'descripcion']].to_string() if 'campo' in df_dict.columns else "Ver diccionario completo arriba")
    
    # Dominios de métricas y causas
    df_dom = pd.read_excel(excel_path, sheet_name='Dominios')
    if 'metrica' in df_dom.columns:
        print("\nMétricas válidas:")
        for m in df_dom['metrica'].dropna().unique():
            print(f"  - {m}")
    
    if 'causa' in df_dom.columns:
        print("\nCausas de horas no trabajadas:")
        for c in df_dom['causa'].dropna().unique():
            print(f"  - {c}")
    
    # Generar configuración JSON
    config = {
        'campos_clave': [],
        'dominios': {},
        'jerarquia_sector': {}
    }
    
    # Extraer dominios
    for col in df_dom.columns:
        valores = df_dom[col].dropna().unique().tolist()
        if valores:
            # Convertir numpy types a Python natives
            valores_clean = []
            for v in valores:
                if pd.isna(v):
                    continue
                elif isinstance(v, (int, float)):
                    valores_clean.append(str(v) if not v.is_integer() else int(v))
                else:
                    valores_clean.append(str(v))
            config['dominios'][col] = valores_clean
    
    # Guardar configuración
    config_path = Path(__file__).parent.parent / 'config' / 'tabla_procesada_config.json'
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Configuración guardada en: {config_path}")
    
    return config

if __name__ == "__main__":
    analyze_design_excel()