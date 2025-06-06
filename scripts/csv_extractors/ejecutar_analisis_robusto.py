"""
Ejecutor Simplificado - Análisis Robusto de Factibilidad
Ejecuta el análisis paso a paso con manejo robusto de errores
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def ejecutar_paso(script_name, descripcion):
    """Ejecuta un paso individual del análisis"""
    print(f"\n{'='*60}")
    print(f"🚀 EJECUTANDO: {descripcion}")
    print(f"{'='*60}")
    
    try:
        # Ejecutar script
        resultado = subprocess.run([
            sys.executable, script_name
        ], cwd=Path(__file__).parent)
        
        if resultado.returncode == 0:
            print(f"✅ {descripcion} - COMPLETADO")
            return True
        else:
            print(f"❌ {descripcion} - ERROR (código: {resultado.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {descripcion} - EXCEPCIÓN: {e}")
        return False

def verificar_archivos_csv():
    """Verifica que existan archivos CSV"""
    data_dir = Path("../../data/raw/csv")
    archivos_csv = list(data_dir.glob("*.csv"))
    
    if len(archivos_csv) < 10:
        print(f"❌ Insuficientes archivos CSV: {len(archivos_csv)} encontrados")
        return False
    
    print(f"✅ {len(archivos_csv)} archivos CSV encontrados")
    return True

def verificar_dependencias():
    """Verifica que estén las dependencias necesarias"""
    try:
        import pandas
        import chardet
        print("✅ Dependencias verificadas")
        return True
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        print("💡 Ejecute: python instalar_chardet.py")
        return False

def main():
    """Función principal simplificada"""
    print("🎯 ANÁLISIS ROBUSTO DE FACTIBILIDAD - EJECUTOR SIMPLIFICADO")
    print("="*80)
    print("Procesará archivos CSV problemáticos del INE para análisis de absentismo")
    print("="*80)
    
    # Verificaciones previas
    if not verificar_dependencias():
        print("\n💡 Instalando dependencias...")
        if ejecutar_paso("instalar_chardet.py", "Instalación de Dependencias"):
            print("✅ Dependencias instaladas, reinicie el script")
        return False
    
    if not verificar_archivos_csv():
        print("❌ Prerequisitos no cumplidos")
        return False
    
    # Pipeline de análisis
    pasos = [
        ("analisis_estructura_robusto.py", "Análisis Robusto de Estructura CSV"),
        ("detector_absentismo.py", "Detección de Datos de Absentismo"),
        ("generar_informe_factibilidad_corregido.py", "Generación de Informe HTML")
    ]
    
    # Ejecutar cada paso
    exitos = 0
    inicio_total = datetime.now()
    
    for script, descripcion in pasos:
        if ejecutar_paso(script, descripcion):
            exitos += 1
        else:
            print(f"\n❌ PROCESO INTERRUMPIDO en: {descripcion}")
            break
    
    # Verificar archivos generados
    archivos_esperados = [
        "../../informes/analisis_estructura_robusto.json",
        "../../informes/deteccion_absentismo_detallada.json", 
        "../../informes/factibilidad_absentismo.html"
    ]
    
    archivos_generados = 0
    for archivo in archivos_esperados:
        if Path(archivo).exists():
            tamaño_kb = Path(archivo).stat().st_size / 1024
            print(f"✅ Generado: {Path(archivo).name} ({tamaño_kb:.1f} KB)")
            archivos_generados += 1
        else:
            print(f"❌ No encontrado: {Path(archivo).name}")
    
    # Resumen final
    tiempo_total = (datetime.now() - inicio_total).total_seconds() / 60
    
    print("\n" + "="*80)
    print("🏁 ANÁLISIS ROBUSTO COMPLETADO")
    print("="*80)
    
    if exitos == len(pasos):
        print("✅ ESTADO: COMPLETADO EXITOSAMENTE")
        print(f"📊 Pasos completados: {exitos}/{len(pasos)}")
        print(f"📁 Archivos generados: {archivos_generados}/{len(archivos_esperados)}")
        print(f"⏱️  Tiempo total: {tiempo_total:.1f} minutos")
        
        if archivos_generados == len(archivos_esperados):
            print(f"\n🎉 ¡ANÁLISIS COMPLETADO EXITOSAMENTE!")
            print(f"📋 PRÓXIMOS PASOS:")
            print(f"   1. Abrir: informes/factibilidad_absentismo.html")
            print(f"   2. Revisar: informes/analisis_estructura_robusto.json")
            print(f"   3. Validar: informes/deteccion_absentismo_detallada.json")
            return True
        else:
            print(f"⚠️ Algunos archivos no se generaron correctamente")
    else:
        print("❌ ESTADO: COMPLETADO CON ERRORES")
        print(f"📊 Pasos completados: {exitos}/{len(pasos)}")
        print(f"💡 Revise los errores mostrados arriba")
    
    return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
