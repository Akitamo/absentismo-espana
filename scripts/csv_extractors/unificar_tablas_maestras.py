#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unificador de Tablas Maestras - Fase 1
Extrae y unifica: Periodo, CCAA y Tipo de Jornada de todos los CSV
"""

import pandas as pd
import os
from datetime import datetime
import re

# Configuración
CSV_DIR = r"C:\Users\slunagda\AbsentismoEspana\data\raw\csv"
OUTPUT_DIR = r"C:\Users\slunagda\AbsentismoEspana\data\processed"
TABLAS_MAESTRAS_FILE = r"C:\Users\slunagda\AbsentismoEspana\informes\tablas_maestras_unificadas.xlsx"

def crear_directorio_processed():
    """Crea el directorio processed si no existe"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✅ Creado directorio: {OUTPUT_DIR}")

def extraer_valores_unicos(csv_files, nombre_columna_variantes):
    """Extrae valores únicos de una columna que puede tener nombres diferentes"""
    valores_unicos = set()
    archivos_encontrados = []
    
    for csv_file in csv_files:
        try:
            file_path = os.path.join(CSV_DIR, csv_file)
            df = pd.read_csv(file_path, sep=';', encoding='utf-8', nrows=1000)  # Muestra
            
            # Buscar la columna por nombres variantes
            columna_encontrada = None
            for variante in nombre_columna_variantes:
                if variante in df.columns:
                    columna_encontrada = variante
                    break
            
            if columna_encontrada:
                valores = df[columna_encontrada].dropna().unique()
                valores_limpios = [str(v).strip() for v in valores if str(v).strip()]
                valores_unicos.update(valores_limpios)
                archivos_encontrados.append(csv_file)
                print(f"  ✓ {csv_file}: {columna_encontrada} ({len(valores)} valores)")
            
        except Exception as e:
            print(f"  ❌ Error en {csv_file}: {e}")
    
    return sorted(list(valores_unicos)), archivos_encontrados

def crear_tabla_periodo():
    """Crea tabla maestra de periodos"""
    print("\n📅 CREANDO TABLA PERIODO...")
    
    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    
    # Variantes del nombre de la columna periodo
    variantes_periodo = ['Periodo', 'Año', 'Trimestre', 'Fecha']
    
    periodos, archivos = extraer_valores_unicos(csv_files, variantes_periodo)
    
    # Filtrar solo valores que parecen periodos (formato YYYYTX)
    patron_periodo = re.compile(r'20\d{2}T[1-4]')
    periodos_validos = [p for p in periodos if patron_periodo.match(p)]
    
    # Crear DataFrame con información adicional
    datos_periodo = []
    for periodo in sorted(periodos_validos):
        try:
            # Extraer año y trimestre
            año = int(periodo[:4])
            trimestre = int(periodo[5])
            
            # Calcular fechas aproximadas
            mes_inicio = (trimestre - 1) * 3 + 1
            fecha_inicio = f"{año}-{mes_inicio:02d}-01"
            
            datos_periodo.append({
                'PeriodoID': periodo,
                'Año': año,
                'Trimestre': trimestre,
                'FechaInicio': fecha_inicio,
                'Descripcion': f"{trimestre}º Trimestre {año}",
                'OrdenCronologico': año * 10 + trimestre
            })
        except:
            # Si hay error en el parsing, incluir valor básico
            datos_periodo.append({
                'PeriodoID': periodo,
                'Año': None,
                'Trimestre': None,
                'FechaInicio': None,
                'Descripcion': periodo,
                'OrdenCronologico': 999999
            })
    
    df_periodo = pd.DataFrame(datos_periodo)
    
    print(f"  📊 {len(df_periodo)} periodos únicos encontrados")
    print(f"  📁 Presente en {len(archivos)} archivos")
    print(f"  📆 Rango: {df_periodo['PeriodoID'].min()} - {df_periodo['PeriodoID'].max()}")
    
    return df_periodo, archivos

def crear_tabla_ccaa():
    """Crea tabla maestra de Comunidades Autónomas"""
    print("\n🗺️ CREANDO TABLA CCAA...")
    
    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    
    # Variantes del nombre de la columna CCAA
    variantes_ccaa = [
        'Comunidades y Ciudades Autónomas',
        'Comunidad Autónoma', 
        'CCAA',
        'Región',
        'Provincia'
    ]
    
    ccaas, archivos = extraer_valores_unicos(csv_files, variantes_ccaa)
    
    # Filtrar y limpiar nombres de CCAA
    ccaas_conocidas = [
        'Nacional', 'Andalucía', 'Aragón', 'Asturias (Principado de)', 'Balears (Illes)',
        'Canarias', 'Cantabria', 'Castilla y León', 'Castilla-La Mancha', 'Cataluña',
        'Comunitat Valenciana', 'Extremadura', 'Galicia', 'Madrid (Comunidad de)',
        'Murcia (Región de)', 'Navarra (Comunidad Foral de)', 'País Vasco', 'Rioja (La)',
        'Ceuta', 'Melilla'
    ]
    
    # Mapeo de variantes a nombres oficiales
    mapeo_ccaa = {
        'Andalucia': 'Andalucía',
        'Asturias': 'Asturias (Principado de)',
        'Baleares': 'Balears (Illes)',
        'Castilla y Leon': 'Castilla y León',
        'Cataluna': 'Cataluña',
        'Valencia': 'Comunitat Valenciana',
        'Madrid': 'Madrid (Comunidad de)',
        'Murcia': 'Murcia (Región de)',
        'Navarra': 'Navarra (Comunidad Foral de)',
        'Pais Vasco': 'País Vasco',
        'La Rioja': 'Rioja (La)',
        'Rioja': 'Rioja (La)'
    }
    
    # Normalizar nombres encontrados
    ccaas_normalizadas = []
    for ccaa in ccaas:
        ccaa_limpia = ccaa.strip()
        ccaa_normalizada = mapeo_ccaa.get(ccaa_limpia, ccaa_limpia)
        if ccaa_normalizada in ccaas_conocidas or ccaa_normalizada == 'Nacional':
            ccaas_normalizadas.append(ccaa_normalizada)
    
    # Crear DataFrame con información adicional
    datos_ccaa = []
    for i, ccaa in enumerate(sorted(set(ccaas_normalizadas))):
        # Asignar códigos INE aproximados
        codigo_ine = i + 1 if ccaa != 'Nacional' else 0
        
        # Clasificar tipo
        if ccaa == 'Nacional':
            tipo = 'Nacional'
        elif ccaa in ['Ceuta', 'Melilla']:
            tipo = 'Ciudad Autónoma'
        else:
            tipo = 'Comunidad Autónoma'
        
        datos_ccaa.append({
            'CCAA_ID': ccaa,
            'CodigoINE': f"{codigo_ine:02d}" if codigo_ine > 0 else "00",
            'NombreOficial': ccaa,
            'NombreCorto': ccaa.replace(' (Comunidad de)', '').replace(' (Principado de)', '').replace(' (Región de)', '').replace(' (Comunidad Foral de)', ''),
            'Tipo': tipo,
            'EsNacional': ccaa == 'Nacional'
        })
    
    df_ccaa = pd.DataFrame(datos_ccaa)
    
    print(f"  📊 {len(df_ccaa)} CCAA encontradas")
    print(f"  📁 Presente en {len(archivos)} archivos")
    print(f"  🏛️ Incluye: Nacional + {len(df_ccaa[df_ccaa['Tipo'] == 'Comunidad Autónoma'])} CCAA + {len(df_ccaa[df_ccaa['Tipo'] == 'Ciudad Autónoma'])} Ciudades Autónomas")
    
    return df_ccaa, archivos

def crear_tabla_tipo_jornada():
    """Crea tabla maestra de Tipos de Jornada"""
    print("\n⏰ CREANDO TABLA TIPO DE JORNADA...")
    
    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    
    # Variantes del nombre de la columna tipo jornada
    variantes_jornada = [
        'Tipo de jornada',
        'Jornada',
        'Tipo jornada'
    ]
    
    jornadas, archivos = extraer_valores_unicos(csv_files, variantes_jornada)
    
    # Tipos de jornada conocidos
    jornadas_conocidas = [
        'Ambas jornadas',
        'Jornada completa', 
        'Jornada parcial'
    ]
    
    # Filtrar solo valores válidos
    jornadas_validas = [j for j in jornadas if j in jornadas_conocidas]
    
    # Crear DataFrame con información adicional
    datos_jornada = []
    orden = {'Ambas jornadas': 1, 'Jornada completa': 2, 'Jornada parcial': 3}
    
    for jornada in jornadas_validas:
        codigo = jornada.replace(' ', '_').upper()
        
        datos_jornada.append({
            'TipoJornada_ID': jornada,
            'Codigo': codigo,
            'Descripcion': jornada,
            'EsAgregado': jornada == 'Ambas jornadas',
            'OrdenVisualizacion': orden.get(jornada, 99)
        })
    
    df_jornada = pd.DataFrame(datos_jornada)
    df_jornada = df_jornada.sort_values('OrdenVisualizacion')
    
    print(f"  📊 {len(df_jornada)} tipos de jornada encontrados")
    print(f"  📁 Presente en {len(archivos)} archivos")
    print(f"  ⏱️ Tipos: {', '.join(df_jornada['TipoJornada_ID'].tolist())}")
    
    return df_jornada, archivos

def main():
    """Función principal"""
    print("🚀 INICIANDO UNIFICACIÓN DE TABLAS MAESTRAS")
    print("=" * 60)
    
    # Crear directorio de salida
    crear_directorio_processed()
    
    # Crear las tres tablas maestras
    df_periodo, archivos_periodo = crear_tabla_periodo()
    df_ccaa, archivos_ccaa = crear_tabla_ccaa()
    df_jornada, archivos_jornada = crear_tabla_tipo_jornada()
    
    # Guardar cada tabla individual
    print(f"\n💾 GUARDANDO TABLAS INDIVIDUALES...")
    
    df_periodo.to_csv(os.path.join(OUTPUT_DIR, 'tabla_periodo.csv'), index=False, encoding='utf-8')
    df_ccaa.to_csv(os.path.join(OUTPUT_DIR, 'tabla_ccaa.csv'), index=False, encoding='utf-8')
    df_jornada.to_csv(os.path.join(OUTPUT_DIR, 'tabla_tipo_jornada.csv'), index=False, encoding='utf-8')
    
    print(f"  ✅ tabla_periodo.csv")
    print(f"  ✅ tabla_ccaa.csv") 
    print(f"  ✅ tabla_tipo_jornada.csv")
    
    # Guardar archivo Excel consolidado
    print(f"\n📊 CREANDO EXCEL CONSOLIDADO...")
    
    with pd.ExcelWriter(TABLAS_MAESTRAS_FILE, engine='openpyxl') as writer:
        df_periodo.to_excel(writer, sheet_name='Periodo', index=False)
        df_ccaa.to_excel(writer, sheet_name='CCAA', index=False)
        df_jornada.to_excel(writer, sheet_name='TipoJornada', index=False)
        
        # Crear hoja de resumen
        resumen_data = [
            ['Tabla', 'Registros', 'Archivos_Origen', 'Descripcion'],
            ['Periodo', len(df_periodo), len(archivos_periodo), f"Periodos trimestrales desde {df_periodo['PeriodoID'].min()} hasta {df_periodo['PeriodoID'].max()}"],
            ['CCAA', len(df_ccaa), len(archivos_ccaa), f"Comunidades Autónomas + Nacional + Ciudades Autónomas"],
            ['TipoJornada', len(df_jornada), len(archivos_jornada), f"Tipos de jornada laboral"]
        ]
        
        df_resumen = pd.DataFrame(resumen_data[1:], columns=resumen_data[0])
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
    
    print(f"  ✅ {TABLAS_MAESTRAS_FILE}")
    
    # Resumen final
    print(f"\n🎉 ¡UNIFICACIÓN COMPLETADA!")
    print("=" * 60)
    print(f"📊 RESULTADOS:")
    print(f"   • {len(df_periodo)} periodos únicos")
    print(f"   • {len(df_ccaa)} comunidades autónomas")
    print(f"   • {len(df_jornada)} tipos de jornada")
    print(f"\n📁 ARCHIVOS GENERADOS:")
    print(f"   • Tablas individuales CSV: {OUTPUT_DIR}")
    print(f"   • Consolidado Excel: {TABLAS_MAESTRAS_FILE}")
    print(f"\n🎯 PRÓXIMO PASO:")
    print(f"   Estas tablas están listas para importar en Power BI como")
    print(f"   tablas de dimensión para crear el modelo de datos.")

if __name__ == "__main__":
    main()
