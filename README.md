# AbsentismoEspana - Sistema de Análisis de Datos ETCL del INE

Sistema automatizado para descargar y analizar los datos de absentismo laboral de España desde las tablas ETCL del Instituto Nacional de Estadística.

## 🎯 Objetivo
Mantener actualizados los datos de absentismo laboral en España descargando automáticamente las 35 tablas ETCL del INE y preparándolos para análisis.

## 📋 Funcionalidades
- ✅ Descarga automática de 35 tablas ETCL en formato CSV
- ✅ Sistema de reintentos y validación de descargas
- ✅ Backup automático de versiones anteriores
- ✅ Logs detallados de cada operación
- ✅ Sistema de snapshots para histórico de descargas
- ✅ Análisis de periodos para detectar nuevos trimestres
- ✅ Comparación automática para identificar actualizaciones del INE
- ✅ Análisis exploratorio de datos

## 📋 Requisitos previos
- Python 3.8 o superior
- Git
- Conexión a internet

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/Akitamo/absentismo-espana.git
cd absentismoespana
```

### 2. Configuración inicial (Windows)
```bash
# Ejecutar el script de setup
setup_proyecto.bat
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 📖 Uso

### 1. Descargar todos los CSVs

```bash
cd scripts\descarga
python ejecutar_descarga_completa.py
```

O directamente con opciones:
```bash
# Ver estado del sistema
python descargar_ine.py --verificar-sistema

# Ver tablas disponibles
python descargar_ine.py --listar
```

### 2. Análisis exploratorio de datos

Después de descargar los CSVs:

```bash
# Opción A: Usando el script Python
cd scripts\procesamiento
python TEST_reconocimiento_inicial.py

# Opción B: Usando el batch desde la raíz
reconocimiento_inicial.bat
```

### 3. Comparar snapshots

Para detectar nuevos periodos del INE:

```bash
cd scripts\procesamiento

# Comparar dos fechas
python comparar_snapshots.py --fecha1 2025-06-10 --fecha2 2025-06-11

# Ver snapshots disponibles
python comparar_snapshots.py --listar
```

## 📁 Estructura del proyecto
```
absentismoespana/
├── data/                               # Todos los datos
│   ├── raw/
│   │   └── csv/                        # 35 CSVs del INE (~37MB)
│   └── processed/                      # Datos procesados
│       ├── analisis/                   # Resultados de análisis
│       └── comparaciones/              # Comparaciones entre snapshots
│
├── scripts/                            # Todos los scripts
│   ├── descarga/                       # Scripts de descarga
│   │   ├── descargar_ine.py
│   │   └── ejecutar_descarga_completa.py
│   │
│   ├── procesamiento/                  # Scripts de análisis
│   │   ├── TEST_reconocimiento_inicial.py
│   │   ├── analizar_periodos.py
│   │   └── comparar_snapshots.py
│   │
│   └── utilidades/                     # Código compartido
│       ├── config.py                   # Configuración
│       └── helpers.py                  # Funciones auxiliares
│
├── snapshots/                          # Histórico de descargas
│   └── YYYY-MM-DD/                     # Un snapshot por fecha
│       ├── metadata.json
│       ├── checksums.json
│       └── periodos.json
│
├── backups/                            # Respaldos automáticos
├── logs/                               # Registros
├── requirements.txt                    # Dependencias Python
└── README.md                           # Este archivo
```

## 📊 Datos descargados

### Categorías de datos (35 tablas en total):
1. **Tiempo de trabajo** (6 tablas) - Horas trabajadas/no trabajadas
2. **Costes básicos** (2 tablas) - Costes por trabajador y hora
3. **Series temporales** (2 tablas) - Evolución histórica
4. **Costes detallados** (8 tablas) - Por sectores y CNAE
5. **Costes salariales** (4 tablas) - Salarios por tipo jornada
6. **Vacantes** (8 tablas) - Puestos vacantes y motivos
7. **Otros costes** (5 tablas) - IT, horas extra, por CCAA

## 🔧 Configuración

La configuración está en `scripts/utilidades/config.py`:
- Activar/desactivar categorías de descarga
- Parámetros de reintentos y timeouts
- Rutas de almacenamiento

## 📝 Resultados

- **CSVs descargados**: `data/raw/csv/`
- **Análisis**: `data/processed/analisis/`
- **Comparaciones**: `data/processed/comparaciones/`
- **Logs**: `logs/`

## 🔄 Actualizaciones del INE

El INE actualiza los datos trimestralmente. El sistema detecta automáticamente:
- Nuevos trimestres disponibles
- Revisiones de datos históricos
- Cambios en la estructura de archivos

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🗓️ Próximos pasos

- [x] Sistema de descarga automática
- [x] Detección de nuevos periodos
- [x] Análisis exploratorio inicial
- [ ] Base de datos PostgreSQL
- [ ] API REST
- [ ] Dashboard PowerBI
- [ ] Análisis con IA
