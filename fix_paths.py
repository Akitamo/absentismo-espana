"""
Script para corregir rutas hardcodeadas y hacer el proyecto portable
"""
import os
import re
from pathlib import Path

def fix_hardcoded_paths(file_path):
    """Corrige las rutas hardcodeadas en un archivo Python"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de rutas hardcodeadas a corregir
        replacements = [
            # Rutas absolutas de Windows con usuario específico
            (r'C:\\Users\\slunagda\\AbsentismoEspana', 'Path(__file__).resolve().parent'),
            (r'C:\\Users\\aluni\\absentismoespana', 'Path(__file__).resolve().parent'),
            (r'r"C:\\Users\\[^"]+\\[Aa]bsentismo[Ee]spana"', 'str(Path(__file__).resolve().parent)'),
            
            # Rutas relativas para directorios comunes
            (r'os\.path\.join\(base_dir,\s*"([^"]+)"\)', r'PROJECT_ROOT / "\1"'),
            
            # Imports absolutos a relativos
            (r'from scripts\.', 'from .'),
            (r'import scripts\.', 'from . import '),
        ]
        
        # Aplicar reemplazos
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Si el archivo usa Path pero no la importa, agregar el import
        if 'Path(' in content and 'from pathlib import Path' not in content:
            if 'import' in content:
                # Agregar después de los otros imports
                lines = content.split('\n')
                import_added = False
                for i, line in enumerate(lines):
                    if line.strip().startswith('import') or line.strip().startswith('from'):
                        continue
                    elif not line.strip() or not import_added:
                        lines.insert(i, 'from pathlib import Path')
                        import_added = True
                        break
                content = '\n'.join(lines)
            else:
                # Agregar al principio después del docstring
                content = 'from pathlib import Path\n\n' + content
        
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def fix_all_python_files(root_dir):
    """Corrige todos los archivos Python en el directorio"""
    root_path = Path(root_dir)
    fixed_count = 0
    
    print("🔧 Corrigiendo rutas hardcodeadas en archivos Python...")
    
    for py_file in root_path.rglob('*.py'):
        # Omitir archivos en venv, .git, __pycache__
        if any(part in str(py_file) for part in ['venv', '.git', '__pycache__', 'fix_paths.py']):
            continue
            
        if fix_hardcoded_paths(py_file):
            print(f"   ✅ Corregido: {py_file.relative_to(root_path)}")
            fixed_count += 1
    
    return fixed_count

def create_env_template():
    """Crea un template para el archivo .env"""
    env_template = """# Configuración de base de datos para AbsentismoEspana
# Copiar este archivo como 'database.env' y rellenar con valores reales

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=absentismo_db
DB_USER=tu_usuario
DB_PASSWORD=tu_password

# Opciones adicionales
DB_SCHEMA=public
DB_SSL_MODE=prefer
"""
    
    config_dir = Path(__file__).parent / 'config'
    template_path = config_dir / 'database.env.template'
    
    if not template_path.exists():
        with open(template_path, 'w') as f:
            f.write(env_template)
        print(f"✅ Creado template de configuración: {template_path}")

def main():
    """Función principal"""
    project_root = Path(__file__).resolve().parent
    
    print("🚀 Preparando proyecto para ser portable...")
    print(f"📁 Directorio del proyecto: {project_root}")
    
    # 1. Corregir rutas hardcodeadas
    fixed = fix_all_python_files(project_root)
    print(f"\n📝 Archivos corregidos: {fixed}")
    
    # 2. Crear template de configuración
    create_env_template()
    
    # 3. Verificar requirements.txt
    requirements_path = project_root / 'requirements.txt'
    if requirements_path.exists():
        print(f"✅ requirements.txt encontrado")
    else:
        print(f"❌ requirements.txt no encontrado - debes crearlo")
    
    print("\n✨ Proyecto preparado para ser portable!")
    print("\n📋 Próximos pasos para usar en otro equipo:")
    print("   1. git clone <tu-repositorio>")
    print("   2. cd absentismoespana")
    print("   3. python -m venv venv")
    print("   4. venv\\Scripts\\activate (Windows) o source venv/bin/activate (Linux/Mac)")
    print("   5. pip install -r requirements.txt")
    print("   6. Copiar config/database.env.template a config/database.env y configurar")

if __name__ == "__main__":
    main()
