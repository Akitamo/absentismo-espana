#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador de Valores Compartidos para Unificación de Columnas
Genera informe completo con muestras de valores para validación manual
"""

import pandas as pd
import os
from collections import Counter, defaultdict
import re
from difflib import SequenceMatcher

# Configuración
CSV_DIR = r"C:\Users\slunagda\AbsentismoEspana\data\raw\csv"
OUTPUT_FILE = r"C:\Users\slunagda\AbsentismoEspana\informes\analisis_valores_compartidos.xlsx"

def detectar_tipo_columna(valores_unicos):
    """Detecta el tipo de una columna basado en sus valores"""
    if not valores_unicos:
        return "VACIO"
    
    valores_str = [str(v).strip() for v in valores_unicos if pd.notna(v)][:50]  # Muestra
    
    # Detectar patrones temporales
    patron_temporal = re.compile(r'20\d{2}T[1-4]|20\d{2}Q[1-4]|20\d{2}-\d{2}')
    if any(patron_temporal.search(v) for v in valores_str):
        return "TEMPORAL"
    
    # Detectar códigos CNAE/sectores
    patron_cnae = re.compile(r'^[A-Z]_?[A-Z]?\s|^[A-Z]\d+|Industria|Construcción|Servicios')
    if any(patron_cnae.search(v) for v in valores_str):
        return "SECTOR_CNAE"
    
    # Detectar comunidades autónomas
    ccaa_keywords = ['Madrid', 'Cataluña', 'Valencia', 'Andalucía', 'País Vasco', 'Galicia', 'Castilla', 'Aragón', 'Murcia', 'Extremadura', 'Asturias', 'Navarra', 'Cantabria', 'Rioja', 'Baleares', 'Canarias']
    if any(any(keyword in v for keyword in ccaa_keywords) for v in valores_str):
        return "GEOGRAFICO_CCAA"
    
    # Detectar tipos de jornada/trabajo
    if any('jornada' in v.lower() or 'tiempo' in v.lower() or 'completa' in v.lower() for v in valores_str):
        return "TIPO_JORNADA"
    
    # Detectar métricas de tiempo/horas
    if any('horas' in v.lower() or 'tiempo' in v.lower() for v in valores_str):
        return "METRICA_TIEMPO"
    
    # Detectar valores numéricos
    try:
        numericos = [float(v.replace(',', '.')) for v in valores_str if v.replace(',', '.').replace('.', '').replace('-', '').isdigit()]
        if len(numericos) > len(valores_str) * 0.8:  # 80% numéricos
            return "NUMERICO"
    except:
        pass
    
    return "CATEGORICO"

def calcular_similitud(valores1, valores2):
    """Calcula similitud entre dos conjuntos de valores"""
    set1 = set(str(v).strip().lower() for v in valores1 if pd.notna(v))
    set2 = set(str(v).strip().lower() for v in valores2 if pd.notna(v))
    
    if not set1 or not set2:
        return 0.0
    
    interseccion = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return (interseccion / union) * 100 if union > 0 else 0.0

def obtener_muestra_valores(valores, max_valores=15):
    """Obtiene una muestra representativa de valores"""
    valores_limpios = [str(v).strip() for v in valores if pd.notna(v) and str(v).strip()]
    
    if not valores_limpios:
        return "SIN_VALORES"
    
    # Contar frecuencias
    contador = Counter(valores_limpios)
    
    # Tomar los más frecuentes
    mas_frecuentes = contador.most_common(max_valores)
    
    # Formatear como string
    muestra = []
    for valor, freq in mas_frecuentes:
        if freq > 1:
            muestra.append(f"{valor} ({freq})")
        else:
            muestra.append(valor)
    
    return " | ".join(muestra)

def main():
    print("🔍 Iniciando análisis de valores compartidos...")
    
    # 1. Cargar datos de todos los CSV
    print("📂 Cargando datos de archivos CSV...")
    
    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    csv_files.sort()
    
    columnas_info = []
    datos_columnas = {}
    
    for csv_file in csv_files:
        try:
            file_path = os.path.join(CSV_DIR, csv_file)
            print(f"  📄 Procesando {csv_file}...")
            
            # Cargar datos (muestra para análisis)
            df = pd.read_csv(file_path, sep=';', encoding='utf-8', nrows=1000)  # Muestra de 1000 filas
            
            for columna in df.columns:
                valores_unicos = df[columna].dropna().unique()
                tipo_detectado = detectar_tipo_columna(valores_unicos)
                muestra_valores = obtener_muestra_valores(valores_unicos)
                
                key = f"{csv_file}::{columna}"
                datos_columnas[key] = valores_unicos
                
                columnas_info.append({
                    'Columna': columna,
                    'Archivo': csv_file,
                    'Tipo_Detectado': tipo_detectado,
                    'Valores_Unicos_Count': len(valores_unicos),
                    'Muestra_Valores': muestra_valores
                })
                
        except Exception as e:
            print(f"  ❌ Error en {csv_file}: {e}")
    
    print(f"✅ Procesadas {len(columnas_info)} columnas de {len(csv_files)} archivos")
    
    # 2. Análisis de similitudes
    print("🔄 Calculando similitudes entre columnas...")
    
    similitudes = []
    procesadas = set()
    
    for i, info1 in enumerate(columnas_info):
        for j, info2 in enumerate(columnas_info[i+1:], i+1):
            
            key1 = f"{info1['Archivo']}::{info1['Columna']}"
            key2 = f"{info2['Archivo']}::{info2['Columna']}"
            
            # Evitar duplicados
            pair_key = tuple(sorted([key1, key2]))
            if pair_key in procesadas:
                continue
            procesadas.add(pair_key)
            
            # Calcular similitud solo si tienen el mismo tipo
            if info1['Tipo_Detectado'] == info2['Tipo_Detectado'] and info1['Tipo_Detectado'] != "NUMERICO":
                
                valores1 = datos_columnas.get(key1, [])
                valores2 = datos_columnas.get(key2, [])
                
                similitud = calcular_similitud(valores1, valores2)
                
                if similitud > 20:  # Solo similitudes significativas
                    similitudes.append({
                        'Columna_A': info1['Columna'],
                        'Archivo_A': info1['Archivo'],
                        'Columna_B': info2['Columna'],
                        'Archivo_B': info2['Archivo'],
                        'Similitud_Porcentaje': round(similitud, 1),
                        'Tipo_Detectado': info1['Tipo_Detectado'],
                        'Valores_A_Count': info1['Valores_Unicos_Count'],
                        'Valores_B_Count': info2['Valores_Unicos_Count'],
                        'Recomendacion': 'UNIFICAR' if similitud > 70 else 'REVISAR'
                    })
    
    # 3. Generar propuestas de unificación
    print("🎯 Generando propuestas de unificación...")
    
    # Agrupar similitudes por tipo
    grupos_por_tipo = defaultdict(list)
    for sim in similitudes:
        if sim['Similitud_Porcentaje'] > 50:
            grupos_por_tipo[sim['Tipo_Detectado']].append(sim)
    
    propuestas = []
    for tipo, similitudes_tipo in grupos_por_tipo.items():
        if len(similitudes_tipo) >= 2:  # Solo si hay múltiples similitudes
            columnas_relacionadas = set()
            for sim in similitudes_tipo:
                columnas_relacionadas.add(f"{sim['Columna_A']} ({sim['Archivo_A']})")
                columnas_relacionadas.add(f"{sim['Columna_B']} ({sim['Archivo_B']})")
            
            confianza = sum(s['Similitud_Porcentaje'] for s in similitudes_tipo) / len(similitudes_tipo)
            
            propuestas.append({
                'Grupo_Propuesto': f"GRUPO_{tipo}",
                'Tipo': tipo,
                'Columnas_a_Unificar': " | ".join(sorted(columnas_relacionadas)),
                'Num_Columnas': len(columnas_relacionadas),
                'Confianza_Promedio': round(confianza, 1),
                'Accion_Sugerida': 'UNIFICAR' if confianza > 70 else 'REVISAR_MANUAL'
            })
    
    # 4. Guardar resultados
    print("💾 Guardando resultados en Excel...")
    
    df_diccionario = pd.DataFrame(columnas_info)
    df_similitudes = pd.DataFrame(similitudes)
    df_propuestas = pd.DataFrame(propuestas)
    
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        df_diccionario.to_excel(writer, sheet_name='Diccionario_Valores', index=False)
        df_similitudes.to_excel(writer, sheet_name='Matriz_Similitudes', index=False)
        df_propuestas.to_excel(writer, sheet_name='Propuestas_Unificacion', index=False)
    
    print(f"\n🎉 ¡Análisis completado!")
    print(f"📍 Archivo generado: {OUTPUT_FILE}")
    print(f"📊 Resumen:")
    print(f"   • {len(columnas_info)} columnas analizadas")
    print(f"   • {len(similitudes)} similitudes encontradas")
    print(f"   • {len(propuestas)} propuestas de unificación")
    print(f"\n📋 Hojas del Excel:")
    print(f"   • Diccionario_Valores: Todas las columnas con muestras")
    print(f"   • Matriz_Similitudes: Comparaciones detalladas")
    print(f"   • Propuestas_Unificacion: Agrupaciones sugeridas")

if __name__ == "__main__":
    main()
