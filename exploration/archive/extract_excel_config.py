#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracción completa de configuración del Excel v3 para el Agent Processor.
"""

import pandas as pd
from pathlib import Path
import json

def extract_complete_config():
    """Extrae toda la configuración necesaria del Excel v3."""
    
    excel_path = Path(r"C:\Users\aluni\Downloads\ETCL_6042_6063_diseno_tabla_v3.xlsx")
    
    # Configuración completa
    config = {
        'tabla_estructura': {},
        'dominios': {},
        'validaciones': [],
        'jerarquia_cnae': [],
        'cobertura_tablas': {},
        'mapeo_columnas_ine': {}
    }
    
    # 1. ESTRUCTURA DE LA TABLA (del Diccionario)
    df_dict = pd.read_excel(excel_path, sheet_name='Diccionario')
    campos = []
    for _, row in df_dict.iterrows():
        campo = {
            'nombre': row['columna'],
            'tipo': row['tipo_dato'],
            'requerido': row['requerido'] == 'Sí',
            'descripcion': row['criterios'],
            'ejemplo': str(row['ejemplo']) if pd.notna(row['ejemplo']) else None
        }
        campos.append(campo)
    config['tabla_estructura'] = campos
    
    # 2. DOMINIOS (valores permitidos)
    df_dom = pd.read_excel(excel_path, sheet_name='Dominios')
    
    # Reorganizar dominios por campo
    dominios_dict = {}
    for _, row in df_dom.iterrows():
        campo = row['campo']
        valor = row['valor_permitido']
        
        if pd.notna(campo) and pd.notna(valor):
            if campo not in dominios_dict:
                dominios_dict[campo] = []
            # Convertir a string si es necesario
            if isinstance(valor, (int, float)):
                valor = str(int(valor)) if valor.is_integer() else str(valor)
            dominios_dict[campo].append(valor)
    
    config['dominios'] = dominios_dict
    
    # 3. VALIDACIONES
    df_val = pd.read_excel(excel_path, sheet_name='Validaciones')
    for _, row in df_val.iterrows():
        validacion = {
            'regla': row['regla'],
            'criterio': row['criterios']
        }
        config['validaciones'].append(validacion)
    
    # 4. JERARQUÍA CNAE
    df_jer = pd.read_excel(excel_path, sheet_name='Jerarquia_Sector')
    for _, row in df_jer.iterrows():
        jerarquia = {
            'cnae_nivel': row['cnae_nivel'],
            'cnae_codigo': str(row['cnae_codigo']) if pd.notna(row['cnae_codigo']) else None,
            'jerarquia_cod': row['jerarquia_sector_cod'],
            'jerarquia_lbl': row['jerarquia_sector_lbl'],
            'ejemplo': row['ejemplo']
        }
        config['jerarquia_cnae'].append(jerarquia)
    
    # 5. COBERTURA POR TABLA
    df_cob = pd.read_excel(excel_path, sheet_name='Cobertura_6042_6063')
    for _, row in df_cob.iterrows():
        tabla = str(int(row['tabla'])) if isinstance(row['tabla'], float) else str(row['tabla'])
        config['cobertura_tablas'][tabla] = {
            'periodo': row['periodo'] == 'Sí',
            'sector': row['sector'],
            'ccaa': row['ccaa'] == 'Sí',
            'jornada': row['jornada'] == 'Sí',
            'granularidad': row['granularidad_sector']
        }
    
    # 6. MAPEO DE COLUMNAS INE A CAMPOS PROCESADOS
    # Basado en análisis previo y documento consolidado
    config['mapeo_columnas_ine'] = {
        'dimensiones': {
            'Periodo': 'periodo',
            'Comunidades y Ciudades Autónomas': 'ccaa_nombre',
            'Tipo de jornada': 'tipo_jornada',
            'Sectores de actividad CNAE 2009': 'cnae_nombre',
            'Secciones de actividad': 'cnae_nombre',
            'Divisiones de la CNAE-09': 'cnae_nombre',
            'Tiempo de trabajo': 'metrica_base'  # Requiere procesamiento adicional
        },
        'metricas_base': {
            'Horas pactadas': 'horas_pactadas',
            'Horas efectivas': 'horas_efectivas', 
            'Horas extraordinarias': 'horas_extraordinarias',
            'Horas pagadas': 'horas_pagadas'  # Para validación
        },
        'causas_hnt': {
            'Horas no trabajadas: incapacidad temporal': 'it_total',
            'Horas no trabajadas: maternidad': 'maternidad_paternidad',
            'Horas no trabajadas: permisos remunerados': 'permisos_retribuidos',
            'Horas no trabajadas: conflictividad laboral': 'conflictividad',
            'Horas no trabajadas: representación sindical': 'representacion_sindical',
            'Horas no trabajadas: otros motivos': 'otros',
            'Horas no trabajadas: vacaciones': 'vacaciones',
            'Horas no trabajadas: fiestas': 'festivos',
            'Horas no trabajadas: razones técnicas o económicas': 'erte_suspension'
        },
        'valor': 'Total'  # Columna que contiene el valor numérico
    }
    
    # 7. CONFIGURACIÓN DE PROCESAMIENTO
    config['procesamiento'] = {
        'tablas_incluidas': ['6042', '6043', '6044', '6045', '6046', '6063'],
        'unidad_fija': 'horas/mes por trabajador',
        'decimal_separator': ',',  # En CSVs originales
        'output_decimal': '.',     # En tabla procesada
        'encoding_csv': 'utf-8-sig',
        'separator_csv': ';'
    }
    
    # 8. REGLAS DE NEGOCIO
    config['reglas_negocio'] = {
        'denominador_tasas': 'horas_pactadas',
        'excluir_absentismo': ['vacaciones', 'festivos', 'erte_suspension'],
        'incluir_absentismo': ['it_total', 'maternidad_paternidad', 'permisos_retribuidos', 
                               'conflictividad', 'representacion_sindical', 'otros'],
        'identidad_he': 'HE = HP + HEXT - HNT_TOTAL',
        'ceuta_melilla': 'Integradas con Andalucía en tabla 6063'
    }
    
    # Guardar configuración completa
    config_path = Path(__file__).parent.parent / 'config' / 'procesador_config_completo.json'
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("Configuracion completa extraida y guardada en:")
    print(f"   {config_path}")
    
    # Resumen de lo extraído
    print("\n" + "="*60)
    print("RESUMEN DE CONFIGURACIÓN EXTRAÍDA:")
    print("="*60)
    print(f"- Campos de tabla: {len(config['tabla_estructura'])}")
    print(f"- Dominios definidos: {len(config['dominios'])}")
    print(f"- Reglas de validación: {len(config['validaciones'])}")
    print(f"- Niveles jerarquía CNAE: {len(config['jerarquia_cnae'])}")
    print(f"- Tablas con cobertura: {len(config['cobertura_tablas'])}")
    
    print("\nDOMINIOS CLAVE:")
    for dominio in ['metrica', 'causa', 'cnae_nivel', 'rol_grano']:
        if dominio in config['dominios']:
            valores = config['dominios'][dominio]
            print(f"\n{dominio.upper()}:")
            for v in valores[:10]:  # Primeros 10
                print(f"  - {v}")
            if len(valores) > 10:
                print(f"  ... ({len(valores)} valores totales)")
    
    return config

if __name__ == "__main__":
    config = extract_complete_config()