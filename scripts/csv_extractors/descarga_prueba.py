#!/usr/bin/env python3
"""
Descarga de prueba - 1 archivo solamente
"""

import sys
import os
from pathlib import Path

# Cambiar al directorio correcto  
os.chdir(r'C:\Users\slunagda\absentismoespana\scripts\csv_extractors')

# Importar el extractor
from extractor_csv_ine import ExtractorCSV_INE

print("🚀 DESCARGA DE PRUEBA - 1 ARCHIVO")
print("="*40)

try:
    # Inicializar
    extractor = ExtractorCSV_INE("config_csv.json")
    extractor.cargar_urls_etcl("../../urls_etcl_completo.json")
    
    # Obtener tablas activas
    tablas_activas = extractor.obtener_tablas_activas()
    
    if not tablas_activas:
        print("❌ No hay tablas activas")
        exit(1)
    
    # Tomar solo la primera tabla para prueba
    tabla_id, url_csv, info_tabla = tablas_activas[0]
    
    print(f"📊 Probando con: {tabla_id} - {info_tabla['nombre']}")
    print(f"🌐 URL: {url_csv}")
    
    # Crear directorio de destino
    data_dir = Path("../../data/raw/csv")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Crear nombre de archivo
    from utils_csv import limpiar_nombre_archivo
    nombre_limpio = limpiar_nombre_archivo(info_tabla['nombre'])
    filename = f"{tabla_id}_{nombre_limpio}.csv"
    filepath = data_dir / filename
    
    print(f"📁 Guardando en: {filepath}")
    print("\n⏳ Descargando...")
    
    # Descargar archivo
    resultado = extractor.descargar_archivo(url_csv, filepath, tabla_id, info_tabla)
    
    if resultado['exito']:
        tamaño_mb = resultado['tamaño_bytes'] / (1024 * 1024)
        print(f"✅ ¡ÉXITO! Archivo descargado:")
        print(f"   📁 Archivo: {filepath.name}")
        print(f"   📏 Tamaño: {tamaño_mb:.2f} MB")
        print(f"   ⏱️  Tiempo: {resultado['tiempo_descarga']:.1f} segundos")
        
        # Validar archivo
        from utils_csv import validar_archivo_csv
        validacion = validar_archivo_csv(filepath)
        
        if validacion['valido']:
            print(f"   ✅ Validación: {validacion['filas']} filas, {validacion['columnas']} columnas")
        else:
            print(f"   ⚠️  Validación: {validacion['error']}")
            
    else:
        print(f"❌ Error en descarga: {resultado['error']}")
        
except Exception as e:
    print(f"❌ Error crítico: {e}")
    import traceback
    traceback.print_exc()
