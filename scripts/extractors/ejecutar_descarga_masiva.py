#!/usr/bin/env python
"""
Script temporal para ejecutar la descarga masiva de todas las tablas CSV del INE
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Configurar el directorio de trabajo
script_dir = Path(__file__).parent
os.chdir(script_dir)

print(f"📁 Directorio de trabajo: {os.getcwd()}")

# Importar el extractor y analizador
try:
    from extractor_csv_ine import ExtractorCSV_INE
    from analizar_periodos import AnalizadorPeriodos
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

def generar_snapshot_con_periodos(extractor, informe_descarga):
    """
    Genera un snapshot completo que incluye análisis de periodos
    
    Args:
        extractor: Instancia de ExtractorCSV_INE
        informe_descarga: Resultado de la descarga masiva
        
    Returns:
        bool: True si se generó correctamente
    """
    try:
        print("\n📸 Generando snapshot con análisis de periodos...")
        
        # Primero generar el snapshot normal
        if not extractor.generar_snapshot():
            print("❌ Error generando snapshot base")
            return False
        
        # Ahora añadir el análisis de periodos
        print("🔍 Analizando periodos en los archivos descargados...")
        analizador = AnalizadorPeriodos()
        analisis_periodos = analizador.analizar_todos_los_csv()
        
        if not analisis_periodos:
            print("⚠️ No se pudo realizar el análisis de periodos")
            return True  # El snapshot base sí se generó
        
        # Guardar el análisis en el snapshot
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        snapshot_dir = Path(__file__).parent.parent.parent / "snapshots" / fecha_hoy
        
        # Guardar periodos.json
        periodos_path = snapshot_dir / "periodos.json"
        analizador.guardar_analisis(analisis_periodos, periodos_path)
        
        # Mostrar resumen del análisis
        resumen = analizador.generar_resumen(analisis_periodos)
        print(f"\n📊 ANÁLISIS DE PERIODOS:")
        print(f"   - Archivos analizados: {resumen['archivos_procesados']}/{resumen['total_archivos']}")
        
        if resumen['ultimo_periodo_disponible']:
            ultimo = resumen['ultimo_periodo_disponible']
            print(f"   - Último periodo disponible: {ultimo['texto']} ({ultimo['año']})")
            
            # Si es trimestral, mostrar info adicional
            if 'trimestre' in ultimo:
                print(f"   - Año: {ultimo['año']}, Trimestre: T{ultimo['trimestre']}")
        
        if resumen['archivos_con_error'] > 0:
            print(f"   - ⚠️ Archivos con error: {resumen['archivos_con_error']}")
            for archivo, error in resumen['errores'].items():
                print(f"      - {archivo}: {error}")
        
        print(f"\n✅ Snapshot completo generado en: {snapshot_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Error generando snapshot con periodos: {e}")
        import traceback
        traceback.print_exc()
        return False

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
            
            # Solo mostrar velocidad si existe
            if 'velocidad_promedio_mbps' in resumen:
                print(f"💾 Velocidad promedio: {resumen['velocidad_promedio_mbps']:.2f} MB/s")
            elif resumen['tiempo_total_min'] == 0:
                print(f"💾 Velocidad: N/A (archivos ya existían)")
            
            if resumen['errores'] > 0:
                print(f"⚠️  Archivos con errores: {resumen['errores']}")
                print("   (Ver logs para detalles)")
            
            # Mostrar archivos descargados
            print(f"\n📁 Archivos guardados en: data/raw/csv/")
            
            # Mostrar estadísticas por categoría
            print("\n📈 ESTADÍSTICAS POR CATEGORÍA:")
            for categoria, stats in informe.get('estadisticas_por_categoria', {}).items():
                print(f"   {categoria}: {stats['exitosos']}/{stats['total']} archivos")
            
            # NUEVO: Generar snapshot con análisis de periodos
            if generar_snapshot_con_periodos(extractor, informe):
                print("\n✅ Snapshot con análisis de periodos generado correctamente")
            else:
                print("\n⚠️ Hubo problemas generando el snapshot completo")
            
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
