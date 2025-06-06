"""
Instalador de Dependencias - Sistema de Análisis de Absentismo
Instala todas las dependencias necesarias para el análisis de factibilidad
"""

import subprocess
import sys
import os
from pathlib import Path

def verificar_python():
    """Verifica la versión de Python"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Se requiere Python 3.8 o superior")
        return False
    
    print("✅ Versión de Python compatible")
    return True

def instalar_dependencias():
    """Instala las dependencias necesarias"""
    dependencias = [
        "pandas>=1.5.0",
        "numpy>=1.21.0", 
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        "jinja2>=3.0.0",
        "openpyxl>=3.0.0",
        "requests>=2.25.0",
        "psycopg2-binary>=2.9.0"  # Para PostgreSQL
    ]
    
    print("📦 INSTALANDO DEPENDENCIAS...")
    print("="*50)
    
    for i, dep in enumerate(dependencias, 1):
        print(f"[{i}/{len(dependencias)}] Instalando {dep}...")
        try:
            resultado = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print(f"  ✅ {dep} instalado correctamente")
            else:
                print(f"  ⚠️  Advertencia instalando {dep}: {resultado.stderr}")
        except Exception as e:
            print(f"  ❌ Error instalando {dep}: {e}")
    
    print("\n✅ INSTALACIÓN DE DEPENDENCIAS COMPLETADA")

def verificar_instalacion():
    """Verifica que las dependencias se instalaron correctamente"""
    print("\n🔍 VERIFICANDO INSTALACIÓN...")
    
    modulos_criticos = [
        ("pandas", "pd"),
        ("numpy", "np"), 
        ("matplotlib.pyplot", "plt"),
        ("json", None),
        ("pathlib", None)
    ]
    
    errores = 0
    for modulo, alias in modulos_criticos:
        try:
            if alias:
                exec(f"import {modulo} as {alias}")
            else:
                exec(f"import {modulo}")
            print(f"  ✅ {modulo}")
        except ImportError as e:
            print(f"  ❌ {modulo}: {e}")
            errores += 1
    
    if errores == 0:
        print("\n🎉 TODAS LAS DEPENDENCIAS VERIFICADAS CORRECTAMENTE")
        return True
    else:
        print(f"\n⚠️  {errores} dependencias con problemas")
        return False

def main():
    """Función principal"""
    print("🚀 INSTALADOR DE DEPENDENCIAS")
    print("Sistema de Análisis de Absentismo España")
    print("="*60)
    
    # Verificar Python
    if not verificar_python():
        sys.exit(1)
    
    # Instalar dependencias
    instalar_dependencias()
    
    # Verificar instalación
    if verificar_instalacion():
        print("\n✅ SISTEMA LISTO PARA EJECUTAR ANÁLISIS")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Ejecutar: python ejecutar_analisis_completo.py")
        print("   2. Revisar informes generados en: ../../informes/")
        print("   3. Abrir informe HTML en navegador")
    else:
        print("\n❌ PROBLEMAS DE INSTALACIÓN DETECTADOS")
        print("💡 Intente ejecutar manualmente:")
        print("   pip install pandas numpy matplotlib seaborn plotly jinja2")

if __name__ == "__main__":
    main()
