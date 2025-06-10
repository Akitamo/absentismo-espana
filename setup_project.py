#!/usr/bin/env python
"""
Script de configuración inicial para AbsentismoEspana
Ejecutar después de clonar el repositorio en un nuevo equipo
"""
import os
import sys
import subprocess
from pathlib import Path

class SetupAbsentismo:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent
        self.venv_path = self.project_root / 'venv'
        
    def print_header(self, text):
        """Imprime un encabezado formateado"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
        
    def check_python_version(self):
        """Verifica la versión de Python"""
        print("🐍 Verificando versión de Python...")
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python {version.major}.{version.minor} detectado")
            print("⚠️  Se requiere Python 3.8 o superior")
            return False
            
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
        
    def create_virtual_env(self):
        """Crea el entorno virtual si no existe"""
        if self.venv_path.exists():
            print(f"✅ Entorno virtual ya existe en: {self.venv_path}")
            return True
            
        print("📦 Creando entorno virtual...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], 
                         cwd=self.project_root, check=True)
            print("✅ Entorno virtual creado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creando entorno virtual: {e}")
            return False
            
    def get_pip_command(self):
        """Obtiene el comando pip correcto según el SO"""
        if os.name == 'nt':  # Windows
            pip_path = self.venv_path / 'Scripts' / 'pip.exe'
        else:  # Linux/Mac
            pip_path = self.venv_path / 'bin' / 'pip'
            
        if pip_path.exists():
            return str(pip_path)
        else:
            print("⚠️  No se encontró pip en el entorno virtual")
            return None
            
    def install_dependencies(self):
        """Instala las dependencias del proyecto"""
        pip_cmd = self.get_pip_command()
        if not pip_cmd:
            return False
            
        requirements_path = self.project_root / 'requirements.txt'
        if not requirements_path.exists():
            print("❌ No se encontró requirements.txt")
            return False
            
        print("📦 Instalando dependencias...")
        try:
            # Actualizar pip primero
            subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Instalar dependencias
            result = subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], 
                                  cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencias instaladas correctamente")
                return True
            else:
                print(f"❌ Error instalando dependencias: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en instalación: {e}")
            return False
            
    def create_directories(self):
        """Crea la estructura de directorios necesaria"""
        print("📁 Creando estructura de directorios...")
        
        directories = [
            'data/raw/csv',
            'data/raw/json', 
            'data/processed',
            'informes',
            'logs',
            'backups_historicos'
        ]
        
        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {dir_path}")
            
    def setup_config_files(self):
        """Configura archivos de configuración"""
        print("⚙️  Configurando archivos...")
        
        # Crear config/database.env si no existe
        db_env = self.project_root / 'config' / 'database.env'
        db_template = self.project_root / 'config' / 'database.env.template'
        
        if not db_env.exists() and db_template.exists():
            print("   📝 Creando database.env desde template...")
            db_env.write_text(db_template.read_text())
            print("   ⚠️  Recuerda configurar database.env con tus credenciales")
            
    def fix_paths(self):
        """Ejecuta el script de corrección de rutas"""
        fix_script = self.project_root / 'fix_paths.py'
        if fix_script.exists():
            print("🔧 Corrigiendo rutas hardcodeadas...")
            python_cmd = str(self.venv_path / 'Scripts' / 'python.exe') if os.name == 'nt' else str(self.venv_path / 'bin' / 'python')
            
            if Path(python_cmd).exists():
                subprocess.run([python_cmd, str(fix_script)], cwd=self.project_root)
            else:
                # Usar Python del sistema si el del venv no existe aún
                subprocess.run([sys.executable, str(fix_script)], cwd=self.project_root)
                
    def show_activation_instructions(self):
        """Muestra instrucciones para activar el entorno virtual"""
        self.print_header("CONFIGURACIÓN COMPLETADA")
        
        print("✅ El proyecto está listo para usar!")
        print("\n📋 Para empezar a trabajar:")
        
        if os.name == 'nt':  # Windows
            print("\n   1. Activar entorno virtual:")
            print("      venv\\Scripts\\activate")
        else:  # Linux/Mac
            print("\n   1. Activar entorno virtual:")
            print("      source venv/bin/activate")
            
        print("\n   2. Verificar instalación:")
        print("      python -c \"import pandas; print('✅ Pandas instalado')\"")
        
        print("\n   3. Descargar datos del INE:")
        print("      cd scripts/csv_extractors")
        print("      python ejecutar_descarga_masiva.py")
        
        print("\n   4. Ejecutar análisis:")
        print("      python ejecutar_analisis_completo.py")
        
        print("\n📚 Para más información, consulta README.md")
        
    def run_setup(self):
        """Ejecuta el proceso completo de configuración"""
        self.print_header("CONFIGURACIÓN INICIAL - AbsentismoEspana")
        
        # 1. Verificar Python
        if not self.check_python_version():
            return False
            
        # 2. Crear entorno virtual
        if not self.create_virtual_env():
            return False
            
        # 3. Instalar dependencias
        if not self.install_dependencies():
            print("⚠️  Continúa con la configuración a pesar del error...")
            
        # 4. Crear directorios
        self.create_directories()
        
        # 5. Configurar archivos
        self.setup_config_files()
        
        # 6. Corregir rutas
        self.fix_paths()
        
        # 7. Mostrar instrucciones finales
        self.show_activation_instructions()
        
        return True

def main():
    """Función principal"""
    setup = SetupAbsentismo()
    
    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
