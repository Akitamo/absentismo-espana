# Descargador de datos ETCL del INE

Sistema automatizado para descargar los CSVs de la Encuesta Trimestral de Coste Laboral (ETCL) del Instituto Nacional de Estadística.

## 🎯 Objetivo
Mantener actualizados los datos de absentismo laboral en España descargando automáticamente las 35 tablas ETCL del INE.

## 📋 Funcionalidades
- ✅ Extrae URLs desde archivos DOCX del INE
- ✅ Descarga automática de 35 tablas ETCL en formato CSV
- ✅ Sistema de reintentos y validación de descargas
- ✅ Backup automático de versiones anteriores
- ✅ Logs detallados de cada operación

## 🚀 Instalación
```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/absentismoespana.git

# Instalar dependencias
pip install -r requirements.txt
```

## 📖 Uso

### 1. Generar/Actualizar URLs (solo si cambian los DOCX)
```bash
python convert_docx_to_json_enhanced.py
```

### 2. Descargar todos los CSVs
```bash
cd scripts/extractors
python ejecutar_descarga_masiva.py
```

O usar el batch:
```bash
descarga_masiva.bat
```

## 📁 Estructura del proyecto
```
absentismoespana/
├── convert_docx_to_json_enhanced.py    # Genera JSON de URLs desde DOCX
├── urls_etcl_completo.json             # JSON con todas las URLs (35 tablas)
├── scripts/
│   └── extractors/
│       ├── extractor_csv_ine.py        # Motor principal de descarga
│       ├── ejecutar_descarga_masiva.py # Script de ejecución
│       ├── config_csv.json             # Configuración de tablas
│       ├── utils_csv.py                # Utilidades auxiliares
│       └── data/raw/csv/               # CSVs descargados organizados por fecha
├── backups_historicos/                 # Backups automáticos
├── requirements.txt
└── README.md
```

## 📊 Datos descargados
- **35 tablas ETCL** organizadas en 8 categorías
- Datos desde 2008 hasta la actualidad
- Actualización trimestral

## 🔧 Configuración
El archivo `scripts/extractors/config_csv.json` contiene:
- Lista de todas las tablas y sus códigos
- Categorías de clasificación
- URLs de descarga
- Parámetros de configuración

## 📝 Logs
Los logs se guardan en:
- `scripts/extractors/logs/descarga_YYYY-MM-DD_HH-MM-SS.log`

## 🗓️ Próximos pasos
- Integración con base de datos PostgreSQL
- API para consulta de datos
- Dashboard PowerBI
- Análisis con IA
