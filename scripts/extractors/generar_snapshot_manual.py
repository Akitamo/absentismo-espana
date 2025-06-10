#!/usr/bin/env python
"""
Script para generar manualmente un snapshot de los CSVs descargados
"""

import sys
from pathlib import Path
from extractor_csv_ine import ExtractorCSV_INE

def main():
    """Genera snapshot de los CSVs actuales"""
    print("📸 GENERANDO SNAPSHOT DE CSVs DESCARGADOS")
    print("=" * 50)
    
    # Inicializar extractor
    try:
        extractor = ExtractorCSV_INE("config_csv.json")
        print("✅ Extractor inicializado")
    except Exception as e:
        print(f"❌ Error inicializando extractor: {e}")
        return False
    
    # Verificar que hay CSVs
    data_dir = Path("data/raw/csv")
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"❌ No se encontraron archivos CSV en {data_dir}")
        return False
    
    print(f"📊 Archivos CSV encontrados: {len(csv_files)}")
    
    # Generar snapshot
    print("\n🔄 Procesando archivos...")
    resultado = extractor.generar_snapshot()
    
    if resultado.get('exito'):
        print("\n✅ SNAPSHOT GENERADO EXITOSAMENTE")
        print(f"📁 Ubicación: {resultado['directorio']}")
        print(f"📊 Archivos procesados: {resultado['archivos_procesados']}/{resultado['archivos_totales']}")
        print(f"💾 Tamaño total: {resultado['tamaño_mb']} MB")
        print("\n📝 Archivos generados:")
        print("   - metadata.json")
        print("   - checksums.json")
        print("   - summary.json")
        return True
    else:
        print(f"\n❌ Error generando snapshot: {resultado.get('error')}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        if not exito:
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
