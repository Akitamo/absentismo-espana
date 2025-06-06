#!/usr/bin/env python3
"""
Prueba rápida del extractor CSV
"""

import sys
import os
import json
from pathlib import Path

# Cambiar al directorio correcto
os.chdir(r'C:\Users\slunagda\absentismoespana\scripts\csv_extractors')

# Importar el extractor
try:
    from extractor_csv_ine import ExtractorCSV_INE
    print("✅ Módulo importado correctamente")
except Exception as e:
    print(f"❌ Error importando: {e}")
    exit(1)

# Prueba básica
try:
    print("\n🔍 PRUEBA BÁSICA DEL EXTRACTOR")
    print("="*40)
    
    # Inicializar
    extractor = ExtractorCSV_INE("config_csv.json")
    print("✅ Extractor inicializado")
    
    # Cargar URLs
    if extractor.cargar_urls_etcl("../../urls_etcl_completo.json"):
        print("✅ URLs cargadas")
    else:
        print("❌ Error cargando URLs")
        exit(1)
    
    # Verificar que se pueden obtener tablas activas
    tablas_activas = extractor.obtener_tablas_activas()
    print(f"✅ Tablas activas encontradas: {len(tablas_activas)}")
    
    # Mostrar primeras 3 tablas como ejemplo
    print("\n📋 MUESTRA DE TABLAS ACTIVAS:")
    for i, (tabla_id, url_csv, info_tabla) in enumerate(tablas_activas[:3]):
        print(f"  {i+1}. {tabla_id}: {info_tabla['nombre']}")
        print(f"     URL: {url_csv[:80]}...")
    
    if len(tablas_activas) > 3:
        print(f"  ... y {len(tablas_activas) - 3} más")
    
    print(f"\n🎉 SISTEMA LISTO PARA DESCARGAR {len(tablas_activas)} ARCHIVOS")
    
except Exception as e:
    print(f"❌ Error en prueba: {e}")
    import traceback
    traceback.print_exc()
