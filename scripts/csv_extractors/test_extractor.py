#!/usr/bin/env python3
"""
Script de prueba para el Extractor CSV del INE
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path de Python
sys.path.append(str(Path(__file__).parent))

try:
    from extractor_csv_ine import ExtractorCSV_INE
    print("✅ Módulo extractor_csv_ine importado correctamente")
except ImportError as e:
    print(f"❌ Error importando módulo: {e}")
    sys.exit(1)

def test_listar_tablas():
    """Prueba listar tablas disponibles"""
    print("\n" + "="*50)
    print("🔍 PRUEBA 1: LISTAR TABLAS DISPONIBLES")
    print("="*50)
    
    try:
        # Inicializar extractor
        extractor = ExtractorCSV_INE("config_csv.json")
        print("✅ ExtractorCSV_INE inicializado")
        
        # Cargar URLs
        urls_file = "../../urls_etcl_completo.json"
        if extractor.cargar_urls_etcl(urls_file):
            print("✅ URLs cargadas correctamente")
        else:
            print("❌ Error cargando URLs")
            return False
        
        # Listar tablas disponibles
        disponibles = extractor.listar_tablas_disponibles()
        
        print("\n📋 RESUMEN DE TABLAS:")
        total_tablas = 0
        tablas_activas = 0
        
        for categoria, tablas in disponibles.items():
            activa = any(t['activa'] for t in tablas)
            estado = "✅ ACTIVA" if activa else "❌ inactiva"
            print(f"\n{estado} {categoria.upper()} ({len(tablas)} tablas):")
            
            for tabla in tablas:
                url_ok = "🌐" if tabla['url_disponible'] else "❌"
                estado_tabla = "ACTIVA" if tabla['activa'] else "inactiva"
                print(f"  {url_ok} {tabla['id']}: {tabla['nombre']} ({estado_tabla})")
                
                total_tablas += 1
                if tabla['activa']:
                    tablas_activas += 1
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"  Total tablas: {total_tablas}")
        print(f"  Tablas activas: {tablas_activas}")
        print(f"  Tablas inactivas: {total_tablas - tablas_activas}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_descarga_muestra():
    """Prueba descarga de una muestra pequeña"""
    print("\n" + "="*50)
    print("📥 PRUEBA 2: DESCARGA DE MUESTRA")
    print("="*50)
    
    try:
        # Inicializar extractor
        extractor = ExtractorCSV_INE("config_csv.json")
        extractor.cargar_urls_etcl("../../urls_etcl_completo.json")
        
        # Obtener tablas activas
        tablas_activas = extractor.obtener_tablas_activas()
        print(f"📊 Tablas activas encontradas: {len(tablas_activas)}")
        
        if len(tablas_activas) == 0:
            print("❌ No hay tablas activas configuradas")
            return False
        
        # Mostrar qué se va a descargar
        print("\n📋 TABLAS A DESCARGAR:")
        for tabla_id, url_csv, info_tabla in tablas_activas:
            print(f"  🌐 {tabla_id}: {info_tabla['nombre']}")
        
        print(f"\n🚀 Iniciando descarga de {len(tablas_activas)} archivos...")
        
        # Realizar descarga
        informe = extractor.descargar_todas_activas()
        
        if 'error' in informe:
            print(f"❌ Error en descarga: {informe['error']}")
            return False
        
        # Mostrar resultados
        resumen = informe['resumen']
        print(f"\n🏁 DESCARGA COMPLETADA:")
        print(f"  ✅ Exitosos: {resumen['exitosos']}")
        print(f"  ❌ Errores: {resumen['errores']}")
        print(f"  📊 Tasa éxito: {resumen['tasa_exito']:.1%}")
        
        # Detalles de archivos descargados
        print(f"\n📁 ARCHIVOS DESCARGADOS:")
        for resultado in informe['resultados_detallados']:
            if resultado['exito']:
                tamaño_mb = resultado['tamaño_bytes'] / (1024 * 1024)
                print(f"  ✅ {resultado['tabla_id']}: {tamaño_mb:.2f} MB")
            else:
                print(f"  ❌ {resultado['tabla_id']}: {resultado['error']}")
        
        return resumen['exitosos'] > 0
        
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_verificar_archivos():
    """Verifica archivos descargados"""
    print("\n" + "="*50)
    print("🔍 PRUEBA 3: VERIFICACIÓN DE ARCHIVOS")
    print("="*50)
    
    try:
        data_dir = Path("../../data/raw/csv")
        
        if not data_dir.exists():
            print("❌ Directorio de datos no existe")
            return False
        
        archivos = list(data_dir.glob("*.csv"))
        print(f"📁 Archivos CSV encontrados: {len(archivos)}")
        
        if len(archivos) == 0:
            print("⚠️  No se encontraron archivos CSV")
            return True
        
        from utils_csv import validar_archivo_csv
        
        archivos_validos = 0
        for archivo in archivos:
            validacion = validar_archivo_csv(archivo)
            if validacion['valido']:
                tamaño_mb = archivo.stat().st_size / (1024 * 1024)
                print(f"  ✅ {archivo.name}: {validacion['filas']} filas, {validacion['columnas']} columnas, {tamaño_mb:.2f} MB")
                archivos_validos += 1
            else:
                print(f"  ❌ {archivo.name}: {validacion['error']}")
        
        print(f"\n📊 RESUMEN VALIDACIÓN:")
        print(f"  Archivos válidos: {archivos_validos}/{len(archivos)}")
        
        return archivos_validos > 0
        
    except Exception as e:
        print(f"❌ Error verificando archivos: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA CSV DEL INE")
    print("="*60)
    
    resultados = []
    
    # Prueba 1: Listar tablas
    resultado1 = test_listar_tablas()
    resultados.append(("Listar tablas", resultado1))
    
    # Prueba 2: Descarga
    if resultado1:
        resultado2 = test_descarga_muestra()
        resultados.append(("Descarga archivos", resultado2))
        
        # Prueba 3: Verificación
        if resultado2:
            resultado3 = test_verificar_archivos()
            resultados.append(("Verificar archivos", resultado3))
    
    # Resumen final
    print("\n" + "="*60)
    print("📋 RESUMEN FINAL DE PRUEBAS")
    print("="*60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        estado = "✅ ÉXITO" if resultado else "❌ FALLO"
        print(f"  {estado}: {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🏁 RESULTADO GLOBAL: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡SISTEMA CSV FUNCIONANDO PERFECTAMENTE!")
    else:
        print("⚠️  Hay problemas que necesitan revisión")
    
    return exitosos == len(resultados)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Pruebas interrumpidas por usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
