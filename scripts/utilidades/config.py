"""
Configuración del proyecto AbsentismoEspana
Convertido automáticamente desde config_csv.json
"""
from pathlib import Path

# Ruta base del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Configuración principal
CONFIG = {
  "categorias": {
    "tiempo_trabajo": {
      "activa": True,
      "descripcion": "Tablas de tiempo de trabajo por trabajador y mes",
      "tablas": [
        "6042",
        "6043",
        "6044",
        "6045",
        "6046",
        "6063"
      ],
      "nombres": {
        "6042": "Tiempo trabajo por trabajador-mes, tipo jornada, sectores",
        "6043": "Tiempo trabajo por trabajador-mes, tipo jornada, secciones CNAE",
        "6044": "Tiempo trabajo por trabajador-mes, sectores",
        "6045": "Tiempo trabajo por trabajador-mes, secciones CNAE",
        "6046": "Tiempo trabajo por trabajador-mes, divisiones CNAE",
        "6063": "Tiempo trabajo por trabajador-mes, CCAA, tipo jornada, sectores"
      }
    },
    "costes_basicos": {
      "activa": True,
      "descripcion": "Costes laborales fundamentales",
      "tablas": [
        "11221",
        "11222"
      ],
      "nombres": {
        "11221": "Costes laborales por trabajador",
        "11222": "Costes laborales por hora efectiva de trabajo"
      }
    },
    "series_temporales": {
      "activa": True,
      "descripcion": "Series temporales por sectores y CCAA",
      "tablas": [
        "59391",
        "59392"
      ],
      "nombres": {
        "59391": "Series por sectores de actividad y componentes del coste",
        "59392": "Series por comunidad autónoma y componentes del coste"
      }
    },
    "costes_detallados": {
      "activa": True,
      "descripcion": "Costes laborales detallados por sectores y tamaños",
      "tablas": [
        "6030",
        "6031",
        "6032",
        "6033",
        "6034",
        "6035",
        "6036",
        "6037"
      ],
      "nombres": {
        "6030": "Coste laboral por trabajador por sectores",
        "6031": "Coste laboral por trabajador por tamaño, sectores",
        "6032": "Coste laboral por trabajador por secciones CNAE",
        "6033": "Coste laboral por trabajador por divisiones CNAE",
        "6034": "Coste laboral por hora efectiva por sectores",
        "6035": "Coste laboral por hora efectiva por tamaño, sectores",
        "6036": "Coste laboral por hora efectiva por secciones CNAE",
        "6037": "Coste laboral por hora efectiva por divisiones CNAE"
      }
    },
    "costes_salariales": {
      "activa": True,
      "descripcion": "Costes salariales específicos",
      "tablas": [
        "6038",
        "6039",
        "6040",
        "6041"
      ],
      "nombres": {
        "6038": "Coste salarial por trabajador, tipo jornada, sectores",
        "6039": "Coste salarial por trabajador, tipo jornada, secciones CNAE",
        "6040": "Coste salarial por hora efectiva, tipo jornada, sectores",
        "6041": "Coste salarial por hora efectiva, tipo jornada, secciones CNAE"
      }
    },
    "vacantes": {
      "activa": True,
      "descripcion": "Datos de vacantes y motivos",
      "tablas": [
        "6047",
        "6048",
        "6049",
        "6053",
        "6054",
        "6055",
        "6064",
        "6066"
      ],
      "nombres": {
        "6047": "Número de vacantes por sectores",
        "6048": "Número de vacantes por secciones",
        "6049": "Número de vacantes por tamaño establecimiento",
        "6053": "Motivos no vacantes por sectores",
        "6054": "Motivos no vacantes por secciones",
        "6055": "Motivos no vacantes por tamaño establecimiento",
        "6064": "Número de vacantes por comunidad autónoma",
        "6066": "Motivos no vacantes por comunidad autónoma"
      }
    },
    "otros_costes": {
      "activa": True,
      "descripcion": "Otros costes laborales específicos",
      "tablas": [
        "6056",
        "6057",
        "6058",
        "6061",
        "6062"
      ],
      "nombres": {
        "6056": "Percepciones IT, coste indemnización por actividad",
        "6057": "Coste por hora extraordinaria, actividad económica",
        "6058": "Coste por hora extraordinaria por CCAA",
        "6061": "Coste laboral por trabajador, CCAA, sectores",
        "6062": "Coste laboral por hora efectiva, CCAA, sectores"
      }
    }
  },
  "configuracion_descarga": {
    "reintentos_maximos": 3,
    "timeout_segundos": 30,
    "delay_entre_reintentos": 2,
    "verificar_existencia": True,
    "sobrescribir_existentes": False,
    "crear_backup": True,
    "validar_csv": True,
    "encoding": "utf-8"
  },
  "rutas": {
    "datos_raw": "data/raw/csv/",
    "datos_procesados": "data/processed/csv/",
    "logs": "logs/",
    "backups": "backups/csv/"
  },
  "logging": {
    "nivel": "INFO",
    "formato": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "archivo": "logs/extractor_csv.log"
  }
}

# Rutas de datos usando pathlib
DATA_RAW_PATH = PROJECT_ROOT / 'data' / 'raw' / 'csv'
DATA_PROCESSED_PATH = PROJECT_ROOT / 'data' / 'processed'
SNAPSHOTS_PATH = PROJECT_ROOT / 'snapshots'
LOGS_PATH = PROJECT_ROOT / 'logs'
BACKUPS_PATH = PROJECT_ROOT / 'backups'

# Funciones helper
def get_categoria_config(categoria):
    """Obtener configuración de una categoría específica"""
    return CONFIG.get('categorias', {}).get(categoria, {})

def get_ruta_raw():
    """Obtener ruta completa a datos raw"""
    return DATA_RAW_PATH

def get_ruta_procesados():
    """Obtener ruta completa a datos procesados"""
    return DATA_PROCESSED_PATH

def get_todas_las_tablas():
    """Obtener lista de todas las tablas disponibles"""
    todas_tablas = []
    for categoria in CONFIG['categorias'].values():
        if categoria.get('activa', True):
            todas_tablas.extend(categoria.get('tablas', []))
    return todas_tablas

def get_nombre_tabla(codigo_tabla):
    """Obtener el nombre descriptivo de una tabla por su código"""
    for categoria in CONFIG['categorias'].values():
        if codigo_tabla in categoria.get('nombres', {}):
            return categoria['nombres'][codigo_tabla]
    return f"Tabla {codigo_tabla}"
