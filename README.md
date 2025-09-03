# AbsentismoEspana

Sistema modular para la extracción y procesamiento de datos de absentismo laboral del Instituto Nacional de Estadística (INE) de España.

## 📊 Descripción

Este proyecto automatiza la descarga y procesamiento de los datos de la Encuesta Trimestral de Coste Laboral (ETCL) del INE, específicamente las 35 tablas relacionadas con costes laborales, tiempo de trabajo y absentismo en España.

### Estado del Proyecto
- **Agent Extractor**: ✅ COMPLETADO - 51 métricas extraídas y validadas
- **Agent Processor**: ✅ VALIDADO - Pipeline ETL 100% funcional, 1,918 validaciones exitosas
- **Dashboard (Dash)**: 📅 EN DESARROLLO - Base con filtros, KPIs y graficos

## 🚀 Características

- **Extracción automática** de 35 tablas del INE
- **Sistema de actualización inteligente** con verificación incremental
- **Metadata y versionado** con tracking completo de cambios
- **Backups automáticos** antes de actualizar datos
- **Detección de actualizaciones** en los datos fuente
- **Procesamiento robusto** con soporte multi-encoding
- **Arquitectura modular** con agentes independientes
- **CLI intuitiva** para todas las operaciones

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/Akitamo/absentismo-espana.git
cd absentismo-espana
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Verificar actualizaciones

Método rápido (recomendado - usa metadata local):
```bash
python main.py --check-smart
```

Método tradicional (más lento - consulta INE directamente):
```bash
python main.py --check
```

### Descargar datos

Todas las tablas:
```bash
python main.py --download-all
```

Tabla específica:
```bash
python main.py --download 6042
```

### Obtener información de una tabla
```bash
python main.py --info 6042
```

### Actualizar datos

Actualizar tabla específica (solo si hay nuevos datos):
```bash
python main.py --update 6042
```

Actualizar todas las tablas con nuevos datos:
```bash
python main.py --update-all
```

### Procesar datos
```bash
# Cargar datos en modo test (últimos 4 trimestres)
python agent_processor/processor.py --test

# Cargar todos los datos históricos (2008T1-presente)
python agent_processor/processor.py --full

# Validar datos contra INE
python validate_against_ine.py
```

## 📁 Estructura del Proyecto

```
absentismo-espana/
├── agent_extractor/    # Módulo de extracción de datos ✅ COMPLETADO
│   ├── downloader.py  # Descarga robusta con reintentos
│   ├── metadata_manager.py # Gestión de versiones y tracking
│   └── updater.py     # Sistema de actualización inteligente
├── agent_processor/    # Módulo de procesamiento 🔧 EN DESARROLLO (85%)
│   ├── processor.py   # Orquestador principal ETL
│   ├── etl/          # Pipeline de transformación
│   │   ├── extractor.py    # Lectura de CSVs
│   │   ├── transformer.py  # Mapeo y pivoteo
│   │   └── loader.py       # Carga a DuckDB
│   └── config/       # Configuración y mapeos
├── config/            # Configuración de tablas
├── data/
│   ├── raw/          # CSVs originales del INE
│   ├── analysis.db   # Base de datos DuckDB
│   ├── metadata/     # Tracking de versiones (JSON)
│   └── backups/      # Backups automáticos
├── scripts/           # Scripts auxiliares
│   └── generate_metadata.py # Generar metadata retroactivo
├── main.py           # Interfaz CLI principal
└── requirements.txt  # Dependencias Python
```

## 📊 Datos Disponibles

El sistema procesa 35 tablas del INE organizadas en 7 categorías:

- **Tiempo de trabajo** (6 tablas): Horas trabajadas y no trabajadas
- **Costes básicos** (2 tablas): Costes por trabajador y hora
- **Series temporales** (2 tablas): Evolución histórica
- **Costes detallados** (8 tablas): Desglose por sector y actividad
- **Costes salariales** (4 tablas): Costes por tipo de jornada
- **Vacantes** (8 tablas): Puestos vacantes y motivos
- **Otros costes** (5 tablas): IT, horas extra, regional

## 🔄 Estado del Proyecto

- ✅ **Fase 1:** Extractor de datos COMPLETADO
  - 51 métricas únicas extraídas y validadas
  - 112% cobertura vs metodología INE
  - Sistema de descarga robusto con reintentos
  - Metadata y versionado implementado
  - Actualización incremental inteligente
  - Backups automáticos funcionando
- 🔧 **Fase 2:** Procesador de datos EN DESARROLLO (85%)
  - Pipeline ETL implementado (Extractor, Transformer, Loader)
  - Base de datos DuckDB integrada
  - Esquema de 23 campos validado
  - Validación contra INE: 1/6 tablas
  - Pendiente: Validación completa y carga histórica
- 📅 **Fase 3:** Dashboard Dash EN DESARROLLO
  - Visualizaciones interactivas
  - Capacidad NL2SQL para consultas en lenguaje natural

Para ver el estado detallado del proyecto, consultar [CONTEXT.md](CONTEXT.md).

## 🔍 Agent Processor - Validación de Datos

### Validación contra INE
```bash
# Validar datos cargados contra valores oficiales del INE
python validate_against_ine.py

# Generar reporte de validación (próximamente)
python validation_report_generator.py
```

### URLs de Referencia INE
Las validaciones se realizan contra los datos oficiales en:
- Tabla 6042: https://www.ine.es/jaxiT3/Datos.htm?t=6042
- Tabla 6043: https://www.ine.es/jaxiT3/Datos.htm?t=6043
- Tabla 6044: https://www.ine.es/jaxiT3/Datos.htm?t=6044
- Tabla 6045: https://www.ine.es/jaxiT3/Datos.htm?t=6045
- Tabla 6046: https://www.ine.es/jaxiT3/Datos.htm?t=6046
- Tabla 6063: https://www.ine.es/jaxiT3/Datos.htm?t=6063

### Estado de Validación (21-ago-2025)
| Tabla | Estado | Observaciones |
|-------|--------|---------------|
| 6042 | Parcial | Discrepancia en sector Industria B-E |
| 6043-6063 | Pendiente | Por validar contra web INE |

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🔗 Enlaces

- [Instituto Nacional de Estadística (INE)](https://www.ine.es)
- [Encuesta Trimestral de Coste Laboral](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736045053&menu=ultiDatos&idp=1254735976596)

## 📧 Contacto

Para preguntas o sugerencias sobre este proyecto, por favor abrir un [issue](https://github.com/Akitamo/absentismo-espana/issues) en GitHub.

---

**Nota:** Este proyecto no está afiliado con el Instituto Nacional de Estadística. Es una herramienta independiente para facilitar el acceso y procesamiento de datos públicos.
## Iniciar Dashboard (Dash)

1) Configura .env (usa .env.example):
`
APP_DB_PATH=data/analysis.db
`

2) Instala dependencias de Dash:
`
pip install -r requirements/base.txt -r requirements/dash.txt
`

3) Arranca la app:
`
python apps/dash/app.py
`

Abre http://127.0.0.1:8050 en el navegador.

Más detalles y tips operativos en `apps/dash/README.md`.
