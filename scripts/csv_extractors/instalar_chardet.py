"""
Script rápido para instalar dependencia chardet necesaria para el parser robusto
"""

import subprocess
import sys

def instalar_chardet():
    """Instala la dependencia chardet"""
    print("📦 Instalando chardet para detección de encoding...")
    
    try:
        resultado = subprocess.run([
            sys.executable, "-m", "pip", "install", "chardet>=5.0.0"
        ], capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅ chardet instalado correctamente")
            return True
        else:
            print(f"⚠️ Advertencia: {resultado.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    instalar_chardet()
