"""
Configuración de rutas del proyecto - Portable y adaptable a cualquier sistema
"""
import os
from pathlib import Path

# Directorio base del proyecto (donde está este archivo)
PROJECT_ROOT = Path(__file__).resolve().parent

# Directorios principales
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
CONFIG_DIR = PROJECT_ROOT / "config"
INFORMES_DIR = PROJECT_ROOT / "informes"
BACKUPS_DIR = PROJECT_ROOT / "backups_historicos"

# Subdirectorios de scripts
CSV_EXTRACTORS_DIR = SCRIPTS_DIR / "csv_extractors"
JSON_EXTRACTORS_DIR = SCRIPTS_DIR / "json_extractors"
SHARED_DIR = SCRIPTS_DIR / "shared"

# Subdirectorios de datos
CSV_DATA_DIR = DATA_RAW_DIR / "csv"
JSON_DATA_DIR = DATA_RAW_DIR / "json"

# Archivos de configuración
DATABASE_CONFIG = CONFIG_DIR / "database.env"
URLS_CONFIG = PROJECT_ROOT / "urls_etcl_completo.json"

# Crear directorios si no existen
def ensure_directories():
    """Crea todos los directorios necesarios si no existen"""
    directories = [
        DATA_DIR, DATA_RAW_DIR, DATA_PROCESSED_DIR,
        SCRIPTS_DIR, CONFIG_DIR, INFORMES_DIR, BACKUPS_DIR,
        CSV_EXTRACTORS_DIR, JSON_EXTRACTORS_DIR, SHARED_DIR,
        CSV_DATA_DIR, JSON_DATA_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Función para obtener rutas absolutas
def get_absolute_path(relative_path):
    """Convierte una ruta relativa en absoluta basada en el proyecto"""
    return PROJECT_ROOT / relative_path

# Función para verificar si estamos en el entorno correcto
def verify_environment():
    """Verifica que estamos en el directorio correcto del proyecto"""
    expected_files = ['.gitignore', 'requirements.txt']
    for file in expected_files:
        if not (PROJECT_ROOT / file).exists():
            raise EnvironmentError(
                f"No se encontró {file} en {PROJECT_ROOT}. "
                "¿Estás ejecutando desde el directorio correcto?"
            )
    return True

# Inicializar directorios al importar
if __name__ != "__main__":
    ensure_directories()
