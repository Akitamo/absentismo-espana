#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis detallado de 8 tablas representativas del INE.
Extrae columnas y valores únicos de dimensiones (no métricas).
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_table(csv_path, codigo):
    """Analiza una tabla y extrae columnas y valores únicos de dimensiones."""
    
    try:
        # Intentar diferentes encodings
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(csv_path, sep=';', encoding=encoding)
                break
            except:
                continue
        
        # Información básica
        info = {
            'codigo': codigo,
            'archivo': csv_path.name,
            'num_filas': len(df),
            'num_columnas': len(df.columns),
            'columnas': list(df.columns),
            'columnas_analisis': {}
        }
        
        # Analizar cada columna
        for col in df.columns:
            valores_unicos = df[col].nunique()
            
            # Determinar si es dimensión o métrica
            # Consideramos dimensión si tiene menos de 100 valores únicos
            # o si es "Periodo" o contiene palabras clave
            es_dimension = (
                valores_unicos < 100 or 
                'periodo' in col.lower() or
                'tipo' in col.lower() or
                'sector' in col.lower() or
                'comunidad' in col.lower() or
                'actividad' in col.lower() or
                'componente' in col.lower() or
                'correcci' in col.lower() or
                'motivo' in col.lower() or
                'tamaño' in col.lower() or
                'jornada' in col.lower() or
                'clase' in col.lower() or
                'cnae' in col.lower()
            )
            
            # Si es "Total" o contiene números, es métrica
            if col.lower() == 'total' or col.lower() == 'total nacional':
                es_dimension = False
            
            info['columnas_analisis'][col] = {
                'tipo_detectado': 'DIMENSION' if es_dimension else 'METRICA',
                'valores_unicos_count': valores_unicos
            }
            
            # Solo extraer valores únicos si es dimensión
            if es_dimension:
                # Obtener todos los valores únicos
                valores = df[col].dropna().unique()
                
                # Ordenar valores
                try:
                    valores_ordenados = sorted(valores)
                except:
                    valores_ordenados = list(valores)
                
                info['columnas_analisis'][col]['valores_unicos'] = valores_ordenados
                
                # Para periodo, mostrar rango
                if 'periodo' in col.lower():
                    info['columnas_analisis'][col]['rango'] = {
                        'primer_periodo': valores_ordenados[0] if valores_ordenados else None,
                        'ultimo_periodo': valores_ordenados[-1] if valores_ordenados else None,
                        'total_periodos': len(valores_ordenados)
                    }
            else:
                # Para métricas, solo mostrar algunos ejemplos
                ejemplos = df[col].dropna().head(5).tolist()
                info['columnas_analisis'][col]['ejemplos'] = [str(x) for x in ejemplos]
        
        return info
        
    except Exception as e:
        return {
            'codigo': codigo,
            'error': str(e)
        }

def main():
    """Analiza 8 tablas representativas."""
    
    # Directorio de CSVs
    csv_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'csv'
    
    # Seleccionar 8 tablas representativas de diferentes categorías
    tablas_seleccionadas = [
        '6042',  # Tiempo de trabajo por tipo de jornada y sectores
        '6030',  # Coste laboral por trabajador por sectores
        '11221', # Costes laborales por trabajador (series)
        '6047',  # Número de vacantes por sectores
        '6061',  # Coste laboral por CCAA y sectores
        '6038',  # Coste salarial por tipo jornada y sectores
        '59391', # Series por sectores de actividad
        '6053'   # Motivos no vacantes por sectores
    ]
    
    # Analizar cada tabla
    resultados = {}
    
    print("=" * 80)
    print("ANÁLISIS DETALLADO DE 8 TABLAS REPRESENTATIVAS DEL INE")
    print("=" * 80)
    print()
    
    for codigo in tablas_seleccionadas:
        # Buscar archivo CSV
        pattern = f"{codigo}_*.csv"
        archivos = list(csv_dir.glob(pattern))
        
        if archivos:
            csv_file = archivos[0]
            print(f"Analizando tabla {codigo}: {csv_file.name}...")
            resultado = analyze_table(csv_file, codigo)
            resultados[codigo] = resultado
        else:
            print(f"No se encontró archivo para tabla {codigo}")
    
    # Guardar resultados en JSON
    output_dir = Path(__file__).parent.parent / 'data' / 'exploration_reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'analisis_8_tablas_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultados guardados en: {output_file}")
    
    # Mostrar resumen en pantalla
    print("\n" + "=" * 80)
    print("RESUMEN DEL ANÁLISIS")
    print("=" * 80)
    
    for codigo, info in resultados.items():
        if 'error' in info:
            print(f"\nTabla {codigo}: ERROR - {info['error']}")
            continue
            
        print(f"\n{'='*60}")
        print(f"TABLA {codigo}: {info['archivo']}")
        print(f"{'='*60}")
        print(f"Filas: {info['num_filas']:,} | Columnas: {info['num_columnas']}")
        print(f"\nCOLUMNAS:")
        
        for col, analisis in info['columnas_analisis'].items():
            tipo = analisis['tipo_detectado']
            n_valores = analisis['valores_unicos_count']
            
            print(f"\n  [{tipo}] {col} ({n_valores} valores únicos)")
            
            if tipo == 'DIMENSION':
                if 'valores_unicos' in analisis:
                    valores = analisis['valores_unicos']
                    if 'periodo' in col.lower() and 'rango' in analisis:
                        rango = analisis['rango']
                        print(f"    Rango: {rango['primer_periodo']} a {rango['ultimo_periodo']} ({rango['total_periodos']} periodos)")
                    elif len(valores) <= 10:
                        print("    Valores:")
                        for v in valores:
                            print(f"      - {v}")
                    else:
                        print(f"    Primeros 5 valores:")
                        for v in valores[:5]:
                            print(f"      - {v}")
                        print(f"    ... (y {len(valores)-5} más)")
            else:
                if 'ejemplos' in analisis:
                    print(f"    Ejemplos: {', '.join(analisis['ejemplos'][:3])}")
    
    print("\n" + "=" * 80)
    print("ANÁLISIS COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()