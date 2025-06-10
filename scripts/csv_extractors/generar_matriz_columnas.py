from pathlib import Path
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Matriz de Columnas para Power BI
Crea una matriz cruzada: filas=columnas, columnas=archivos CSV, celdas=X si existe
"""

import pandas as pd
import os
import logging

# Configuración
CSV_DIR = r"Path(__file__).resolve().parent\data\raw\csv"
OUTPUT_FILE = r"Path(__file__).resolve().parent\informes\matriz_columnas_powerbi.xlsx"

def main():
    """Función principal para generar matriz de columnas"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("🔍 Iniciando análisis de archivos CSV...")
    
    # 1. Obtener lista de archivos CSV
    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    csv_files.sort()
    
    print(f"📁 Encontrados {len(csv_files)} archivos CSV")
    
    # 2. Extraer headers de cada CSV
    all_columns = set()
    file_columns = {}
    
    for csv_file in csv_files:
        try:
            file_path = os.path.join(CSV_DIR, csv_file)
            # Usar separador punto y coma detectado
            df = pd.read_csv(file_path, nrows=0, sep=';', encoding='utf-8')
            columns = list(df.columns)
            file_columns[csv_file] = columns
            all_columns.update(columns)
            print(f"  ✅ {csv_file}: {len(columns)} columnas")
        except Exception as e:
            print(f"  ❌ Error en {csv_file}: {e}")
            file_columns[csv_file] = []
    
    # 3. Crear matriz
    all_columns = sorted(list(all_columns))
    print(f"\n📊 Generando matriz con {len(all_columns)} columnas únicas...")
    
    # Crear DataFrame matriz
    matriz_data = []
    for column in all_columns:
        row = {'Columna': column}
        for csv_file in csv_files:
            row[csv_file] = 'X' if column in file_columns.get(csv_file, []) else ''
        matriz_data.append(row)
    
    matriz_df = pd.DataFrame(matriz_data)
    
    # 4. Guardar en Excel
    try:
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            matriz_df.to_excel(writer, sheet_name='Matriz_Columnas', index=False)
        
        print(f"\n🎉 ¡Matriz generada exitosamente!")
        print(f"📍 Archivo: {OUTPUT_FILE}")
        print(f"📈 Dimensiones: {len(all_columns)} columnas × {len(csv_files)} archivos")
        print(f"💾 Tamaño matriz: {matriz_df.shape}")
        
    except Exception as e:
        print(f"❌ Error al guardar Excel: {e}")

if __name__ == "__main__":
    main()
