import json
import sys
import os
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
os.chdir(current_dir)
sys.path.insert(0, str(current_dir))

print("🚀 Iniciando descarga masiva...")
print(f"📁 Directorio: {os.getcwd()}")

# Importar y ejecutar
try:
    from extractor_csv_ine import ExtractorCSV_INE
    
    # Crear extractor
    extractor = ExtractorCSV_INE("config_csv.json")
    extractor.cargar_urls_etcl("../../urls_etcl_completo.json")
    
    # Mostrar estado antes
    disponibles = extractor.listar_tablas_disponibles()
    total_antes = sum(1 for cat in disponibles.values() for t in cat if t['activa'])
    total_tablas = sum(len(cat) for cat in disponibles.values())
    
    print(f"📊 Antes: {total_antes}/{total_tablas} tablas activas")
    
    # Activar todas
    print("🔄 Activando todas las categorías...")
    extractor.activar_todas_categorias()
    
    # Descargar
    print("📥 Iniciando descarga...")
    informe = extractor.descargar_todas_activas()
    
    # Mostrar resultados
    if 'error' in informe:
        print(f"❌ Error: {informe['error']}")
    else:
        resumen = informe['resumen']
        print(f"\n✅ COMPLETADO:")
        print(f"   Exitosos: {resumen['exitosos']}/{resumen['total_intentos']}")
        print(f"   Tasa éxito: {resumen['tasa_exito']:.1%}")
        print(f"   Tamaño: {resumen['tamaño_total_mb']:.1f} MB")
        print(f"   Tiempo: {resumen['tiempo_total_min']:.1f} min")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
