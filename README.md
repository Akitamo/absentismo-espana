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
- ✅ Compatible con múltiples equipos/usuarios

## 📋 Requisitos previos
- Python 3.8 o superior
- Git
- Conexión a internet

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/absentismoespana.git
cd absentismoespana
```

### 2. Configuración inicial (Windows)
```bash
# Ejecutar el script de setup
setup_proyecto.bat
```

Este script automáticamente:
- Verifica la instalación de Python
- Crea un entorno virtual
- Instala todas las dependencias
- Crea la estructura de directorios necesaria
- Verifica que todos los archivos estén presentes

### 3. Configuración manual (Linux/Mac o si prefieres)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p logs data/raw/csv data/processed/csv backups/csv
```

## 📖 Uso

### 1. Generar/Actualizar URLs (solo si cambian los DOCX)
```bash
python convert_docx_to_json_enhanced.py
```
Este paso solo es necesario si el INE cambia la estructura de las URLs.

### 2. Descargar todos los CSVs

#### Opción A: Usando el script Python
```bash
cd scripts/extractors
python ejecutar_descarga_masiva.py
```

#### Opción B: Usando el batch (Windows)
```bash
scripts\extractors\descarga_masiva.bat
```

#### Opción C: Con opciones avanzadas
```bash
cd scripts/extractors

# Ver tablas disponibles
python extractor_csv_ine.py --listar

# Verificar sistema antes de descargar
python extractor_csv_ine.py --verificar-sistema

# Activar categoría específica
python extractor_csv_ine.py --activar tiempo_trabajo

# Descargar solo tablas activas
python extractor_csv_ine.py
```

## 📁 Estructura del proyecto
```
absentismoespana/
├── convert_docx_to_json_enhanced.py    # Genera JSON de URLs desde DOCX
├── urls_etcl_completo.json             # JSON con todas las URLs (35 tablas)
├── setup_proyecto.bat                  # Script de configuración inicial
├── scripts/
│   └── extractors/
│       ├── extractor_csv_ine.py        # Motor principal de descarga
│       ├── ejecutar_descarga_masiva.py # Script de ejecución simple
│       ├── config_csv.json             # Configuración de tablas
│       ├── utils_csv.py                # Utilidades auxiliares
│       ├── descarga_masiva.bat         # Batch para Windows
│       └── data/raw/csv/               # CSVs descargados organizados por fecha
├── logs/                               # Logs de descargas
├── backups/                            # Backups automáticos
├── config/                             # Configuración adicional
├── requirements.txt                    # Dependencias Python
└── README.md                           # Este archivo
```

## 📊 Datos descargados

### Categorías de datos (35 tablas en total):
1. **Tiempo de trabajo** (6 tablas)
   - Por trabajador y mes
   - Por tipo de jornada
   - Por sectores, CCAA, divisiones CNAE

2. **Costes básicos** (2 tablas)
   - Costes laborales por trabajador
   - Costes laborales por hora efectiva

3. **Series temporales** (2 tablas)
   - Por sectores de actividad
   - Por comunidad autónoma

4. **Costes detallados** (8 tablas)
   - Por sectores y tamaños
   - Por secciones y divisiones CNAE

5. **Costes salariales** (4 tablas)
   - Por tipo de jornada
   - Por sectores y secciones CNAE

6. **Vacantes** (8 tablas)
   - Número de vacantes
   - Motivos de no vacantes

7. **Otros costes** (5 tablas)
   - Percepciones IT
   - Horas extraordinarias
   - Por CCAA y sectores

### Formato de archivos descargados
Los archivos se guardan con el formato:
```
{CODIGO_TABLA}_{NOMBRE_DESCRIPTIVO}.csv
```
Ejemplo: `6042_Tiempo_trabajo_por_trabajador_mes_tipo_jornada_sectores.csv`

## 🔧 Configuración

### config_csv.json
Contiene la configuración de todas las tablas organizadas por categorías. Cada categoría puede activarse/desactivarse para la descarga.

### Parámetros configurables:
- `reintentos_maximos`: Número de reintentos por archivo (default: 3)
- `timeout_segundos`: Tiempo máximo de espera (default: 30)
- `verificar_existencia`: Si verificar archivos existentes (default: true)
- `crear_backup`: Si crear backup de versiones anteriores (default: true)
- `validar_csv`: Si validar que el CSV sea válido (default: true)

## 📝 Logs

Los logs se guardan automáticamente en:
- `logs/extractor_csv.log` - Log general
- `logs/informe_descarga_YYYY-MM-DD_HH-MM-SS.json` - Informe detallado de cada descarga

## 🔄 Actualización de datos

El INE actualiza los datos trimestralmente. Se recomienda:
1. Ejecutar la descarga al inicio de cada trimestre
2. Verificar en la web del INE si hay nuevas tablas disponibles
3. Si hay cambios en las URLs, actualizar los archivos DOCX y regenerar el JSON

## 🛠️ Solución de problemas

### Error: "Python no está instalado"
- Instalar Python 3.8+ desde https://www.python.org
- Asegurarse de marcar "Add Python to PATH" durante la instalación

### Error: "Archivo de URLs no encontrado"
- Ejecutar: `python convert_docx_to_json_enhanced.py`

### Error de conexión al descargar
- Verificar conexión a internet
- El sistema reintentará automáticamente 3 veces
- Revisar los logs para más detalles

### Archivos corruptos o incompletos
- El sistema valida automáticamente cada CSV
- Los archivos inválidos se eliminan y se reintentan
- Se crean backups automáticos de versiones anteriores

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 🗓️ Próximos pasos

- [ ] Integración con base de datos PostgreSQL
- [ ] API REST para consulta de datos
- [ ] Dashboard en PowerBI
- [ ] Análisis automático con IA
- [ ] Notificaciones automáticas de actualizaciones

## 📞 Contacto

Para preguntas o sugerencias sobre el proyecto, abrir un issue en GitHub.
