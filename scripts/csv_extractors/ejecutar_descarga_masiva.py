#!/usr/bin/env python
"""
Script temporal para ejecutar la descarga masiva de todas las tablas CSV del INE
"""

import os
import sys
from pathlib import Path

# Configurar el directorio de trabajo
script_dir = Path(__file__).parent
os.chdir(script_dir)

print(f"📁 Directorio de trabajo: {os.getcwd()}")

# Importar el extractor
try:
    from extractor_csv_ine import ExtractorCSV_INE
    print("✅ ExtractorCSV_INE importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ExtractorCSV_INE: {e}")
    sys.exit(1)

def main():
    """Función principal"""
    print("🚀 INICIANDO DESCARGA MASIVA DE TODAS LAS TABLAS CSV")
    print("=" * 60)
    
    # Inicializar extractor
    try:
        extractor = ExtractorCSV_INE("config_csv.json")
        print("✅ Extractor inicializado")
    except Exception as e:
        print(f"❌ Error inicializando extractor: {e}")
        return False
    
    # Cargar URLs
    urls_file = "../../urls_etcl_completo.json"
    if not extractor.cargar_urls_etcl(urls_file):
        print(f"❌ Error cargando URLs desde {urls_file}")
        return False
    
    print("✅ URLs cargadas correctamente")
    
    # Verificar sistema
    print("\n🔍 VERIFICANDO SISTEMA...")
    verificacion = extractor.verificar_sistema()
    
    print(f"💾 Espacio disponible: {verificacion['espacio_disponible_gb']} GB")
    print(f"🌐 Conexión INE: {'✅' if verificacion['conexion_ine'] else '❌'}")
    print(f"📁 Directorios: {'✅' if verificacion['directorios_ok'] else '❌'}")
    print(f"⚙️  Configuración: {'✅' if verificacion['config_valida'] else '❌'}")
    print(f"🔗 URLs cargadas: {'✅' if verificacion['urls_cargadas'] else '❌'}")
    
    # Mostrar estado actual de tablas
    disponibles = extractor.listar_tablas_disponibles()
    total_tablas = sum(len(cat) for cat in disponibles.values())
    total_activas_antes = sum(1 for cat in disponibles.values() for t in cat if t['activa'])
    
    print(f"\n📊 ESTADO ACTUAL: {total_activas_antes}/{total_tablas} tablas activas")
    
    est = verificacion['estimacion_descarga']
    print(f"📦 Estimación descarga completa:")
    print(f"   - Archivos: {est['archivos_total']}")
    print(f"   - Tamaño estimado: ~{est['tamaño_estimado_mb']} MB")
    print(f"   - Tiempo estimado: ~{est['tiempo_estimado_min']} minutos")
    
    # Preguntar confirmación (en este caso, automático)
    print(f"\n🔄 ACTIVANDO TODAS LAS CATEGORÍAS...")
    
    # Activar todas las categorías
    if extractor.activar_todas_categorias():
        print(f"✅ Todas las categorías activadas: {total_tablas}/{total_tablas} tablas")
        
        # Proceder con descarga
        print("\n🚀 INICIANDO DESCARGA MASIVA...")
        print("=" * 60)
        
        informe = extractor.descargar_todas_activas()
        
        if 'error' in informe:
            print(f"❌ Error durante la descarga: {informe['error']}")
            return False
        else:
            # Mostrar resultados
            resumen = informe['resumen']
            print("\n" + "=" * 60)
            print("🏁 DESCARGA MASIVA COMPLETADA")
            print("=" * 60)
            print(f"✅ Archivos exitosos: {resumen['exitosos']}/{resumen['total_intentos']}")
            print(f"📊 Tasa de éxito: {resumen['tasa_exito']:.1%}")
            print(f"📦 Tamaño total descargado: {resumen['tamaño_total_mb']:.1f} MB")
            print(f"⏱️  Tiempo total: {resumen['tiempo_total_min']:.1f} minutos")
            print(f"💾 Velocidad promedio: {resumen['velocidad_promedio_mbps']:.2f} MB/s")
            
            if resumen['errores'] > 0:
                print(f"⚠️  Archivos con errores: {resumen['errores']}")
                print("   (Ver logs para detalles)")
            
            # Mostrar archivos descargados
            print(f"\n📁 Archivos guardados en: data/raw/csv/")
            
            # Mostrar estadísticas por categoría
            print("\n📈 ESTADÍSTICAS POR CATEGORÍA:")
            for categoria, stats in informe.get('estadisticas_por_categoria', {}).items():
                print(f"   {categoria}: {stats['exitosos']}/{stats['total']} archivos")
            
            return True
    else:
        print("❌ Error activando todas las categorías")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        if exito:
            print("\n🎉 ¡DESCARGA MASIVA COMPLETADA EXITOSAMENTE!")
        else:
            print("\n💥 Error durante la descarga masiva")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Descarga interrumpida por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
