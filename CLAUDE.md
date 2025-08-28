# CLAUDE.md

This file provides stable context for Claude AI when working with this repository.

## Project Overview
**AbsentismoEspana** - Modular system for extracting and processing Spain's National Statistics Institute (INE) labor absenteeism data from the ETCL (Encuesta Trimestral de Coste Laboral) dataset.

## Repository Information
- **GitHub:** https://github.com/Akitamo/absentismo-espana
- **Language:** Python 3.8+
- **License:** MIT

## Architecture
```
Modular Agent-Based System:
├── Agent Extractor: Downloads and validates CSV data from INE ✅ COMPLETED
│   ├── INEScraper: Checks for updates from INE website
│   ├── Downloader: Robust CSV download with retries
│   ├── MetadataManager: Version tracking and hash validation
│   ├── UpdateManager: Smart incremental updates
│   └── MetricsExtractor: 51 unique metrics identified and validated (112% coverage)
└── Agent Processor: Transforms raw data into unified analysis table ✅ COMPLETED
```

## Project Structure
```
absentismo-espana/
├── agent_extractor/     # Data extraction from INE
├── agent_processor/     # Data processing into unified table ✅ COMPLETED
│   └── scripts/        # Processor utility scripts
│       ├── load_all_tables.py                   # Load all tables to DuckDB
│       └── generate_consolidated_validation_report.py  # Generate validation reports
├── config/              # Configuration files
│   ├── tables.json      # 35 INE table definitions
│   └── procesador_config_completo.json # Agent Processor configuration
├── data/
│   ├── raw/csv/        # 35 Original CSV files from INE (one per table)
│   ├── INE/            # Excel files downloaded directly from INE for validation
│   ├── analysis.db     # DuckDB database with 149,247 processed records
│   ├── metadata/       # Update tracking and version control
│   ├── backups/        # Automatic backups with timestamps
│   └── exploration_reports/ # Analysis reports and Excel matrices
│       ├── structure/  # Individual table structure analysis (JSON)
│       ├── *.json      # Comprehensive analysis data
│       └── *.xlsx      # Excel reports with column matrices
├── exploration/         # Data exploration scripts and tools
│   ├── 01_initial_analysis/    # Initial CSV structure analysis
│   ├── 02_pattern_detection/   # Pattern consolidation and schema unification
│   ├── 03_validation/          # Final validation and metrics extraction
│   └── archive/                # Historical scripts for reference
├── docs/                # Reference documentation
│   └── metodologia_ETCL_INE_2023.pdf # Official INE methodology document
├── scripts/            # Utility scripts
│   ├── generate_metadata.py      # Retroactive metadata generation
│   └── validate_no_duplicates.py # Anti-duplicate validation and cleanup
├── main.py             # CLI interface
├── requirements.txt    # Python dependencies (pandas, openpyxl, numpy)
├── README.md          # User documentation
├── CLAUDE.md          # This file (stable context)
└── CONTEXT.md         # Dynamic project status
```

## Key Commands
```bash
# Basic commands
python main.py --check              # Check for updates (deprecated - slow)
python main.py --download-all       # Download all tables
python main.py --download [table_id] # Download specific table
python main.py --info [table_id]    # Get table information

# Smart update commands (recommended)
python main.py --check-smart        # Fast update check using local metadata
python main.py --update [table_id]  # Update specific table if new data available
python main.py --update-all         # Update all tables with new data

# Process data (when implemented)
python main.py --process-all
python main.py --process [table_id]

# Auxiliary scripts
python scripts/generate_metadata.py      # Generate retroactive metadata for existing files
python scripts/validate_no_duplicates.py # Validate and clean duplicate CSV files

# Agent Processor scripts  
python agent_processor/scripts/load_all_tables.py                    # Load all 6 tables to DuckDB
python agent_processor/scripts/generate_consolidated_validation_report.py  # Generate validation reports

# Key exploration scripts (in organized folders)
python exploration/01_initial_analysis/csv_explorer.py               # Initial CSV structure analysis
python exploration/01_initial_analysis/columns_analyzer.py           # Mass analysis with Excel output
python exploration/02_pattern_detection/consolidate_patterns.py      # Pattern consolidation across tables
python exploration/02_pattern_detection/unified_schema_35_tables.py  # Unified schema application
python exploration/03_validation/extract_all_metrics_detailed.py     # Extract 51 unique metrics (VALIDATED)
python exploration/03_validation/validate_all_tables.py              # Exhaustive validation - 100% success
python exploration/03_validation/final_matrix_consolidated.py        # Final consolidated matrix
```

## Data Sources
- **35 ETCL tables** from INE covering:
  - Tiempo de trabajo (6 tables)
  - Costes básicos (2 tables)  
  - Series temporales (2 tables)
  - Costes detallados (8 tables)
  - Costes salariales (4 tables)
  - Vacantes (8 tables)
  - Otros costes (5 tables)

## Technical Considerations
- **Multi-encoding support:** UTF-8, Latin-1, ISO-8859-1, CP1252
- **Robust downloads:** 3-retry system with exponential backoff
- **Path handling:** Use `Path(__file__).parent` (no hardcoding)
- **Error handling:** Comprehensive try-except blocks
- **Data formats:** CSV input, JSON/CSV output
- **Metadata system:** JSON files with SHA256 hashes for version tracking
- **Backup system:** Automatic backups before updates with timestamps
- **Update strategy:** Incremental updates only when new data is available
- **INE data behavior:** Downloads complete historical files (2008T1 to latest), not incremental
- **Duplicate prevention:** Pattern-based file matching to prevent duplicates when INE changes names
- **Windows compatibility:** Text markers instead of emojis for console output
- **Anti-duplication system:** Automatic cleanup of old files when updating to prevent duplicates

## Development Guidelines
1. **IMPORTANT: Always propose actions before implementing** - Never proceed with code changes until explicitly approved with "ok"
2. Each agent must be independent and self-contained
3. Follow existing code patterns and conventions
4. Test with subset (2-3 tables) before full runs
5. Maintain backward compatibility with existing data
6. Document all new functionality in docstrings

## Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what

## Metodología INE de Referencia
- **Documento oficial**: `docs/metodologia_ETCL_INE_2023.pdf` (Encuesta Trimestral de Coste Laboral)
- **35 variables publicadas** confirmadas por el INE
- **Definiciones oficiales** de todas las métricas y dimensiones en páginas 18-20 del documento
- **Cobertura**: Secciones B-S CNAE-09, 82 divisiones de actividad, 17 CCAA (Ceuta y Melilla con Andalucía)
- **Periodo**: Datos trimestrales desde 2008T1 (algunas series desde 2000T1)

### Métricas Extraídas y Validadas (19-ago-2025)
**51 métricas únicas identificadas** con 112% de cobertura respecto a metodología INE:

**Cobertura por Categoría:**
- **COSTES LABORALES**: 16/18 métricas directas (88.9% - faltan 2 calculadas)
- **TIEMPO DE TRABAJO**: 18/13 métricas (138.5% - mayor detalle que esperado)  
- **COSTE SALARIAL**: 4/4 métricas (100% - completo)
- **VACANTES**: 3/2 métricas (150% - incluye sub-métricas)
- **SERIES TEMPORALES**: Valores, índices y tasas de variación

**Métricas Faltantes Identificadas:**
- "Coste total" (posiblemente sinónimo de "Coste laboral total" que sí tenemos)

**Métricas Excluidas (No Relevantes para Absentismo):**
- "Subvenciones y bonificaciones" - No aplicable al análisis de absentismo laboral

### Estructura de Datos Confirmada (Validada con Metodología INE)
**7 Categorías de Métricas:**
1. **COSTES LABORALES** (18 tablas): Por trabajador/hora, hasta 15 componentes
2. **TIEMPO DE TRABAJO** (6 tablas): Horas pactadas, efectivas, extras, IT, vacaciones
3. **COSTE SALARIAL** (4 tablas): Ordinario, extraordinario, atrasados
4. **VACANTES** (4 tablas): Número absoluto de puestos vacantes
5. **MOTIVOS NO VACANTES** (4 tablas): Distribución porcentual
6. **SERIES TEMPORALES** (2 tablas): Valores, índices, tasas variación

**Dimensiones Principales:**
- **PERIODO**: 100% tablas, formato YYYYTQ
- **SECTOR**: 77% tablas (Industria, Construcción, Servicios, Total)
- **TIPO JORNADA**: 20% tablas (Completa, Parcial, Ambas)
- **CCAA**: 20% tablas (17 comunidades + Total Nacional)
- **TAMAÑO EMPRESA**: 11% tablas (8 grupos por número trabajadores)

## Development Tools

### MCP DuckDB Server (Development Only)
- **Status:** Configured and available for data exploration
- **Purpose:** Fast SQL queries on CSVs during development phase
- **Database:** `data/analysis.db` (auto-created)
- **Usage:** Query CSVs directly without loading into memory

Example queries:
```sql
-- Read CSV directly
SELECT * FROM read_csv('data/raw/csv/6042_*.csv') LIMIT 10;

-- Analyze periods
SELECT periodo, COUNT(*) 
FROM read_csv('data/raw/csv/*.csv') 
GROUP BY periodo ORDER BY periodo;

-- Detect dimensions (columns with few unique values)
SELECT column_name, COUNT(DISTINCT column_value) as unique_count
FROM (SELECT unnest(columns(*)) FROM read_csv('data/raw/csv/6042_*.csv'))
WHERE unique_count < 100;
```

**IMPORTANT:** MCP is for exploration only. Production logic must be in Python.

### Data Exploration Tools (Python-based)
- **csv_explorer.py:** Automated structure analysis with dimension/metric detection
- **columns_analyzer.py:** Mass analysis of all 35 tables generating Excel matrices
- **analyze_8_tables.py:** Advanced analysis with unique values extraction for pattern identification
- **consolidate_patterns.py:** Pattern consolidation identifying uniform behaviors across tables
- **unified_schema_35_tables.py:** Unified schema application with dimension normalization
- **identify_metrics_per_table.py:** Clear metric categorization into 7 main types
- **final_matrix_consolidated.py:** Final consolidated matrix with complete data structure
- **Pandas integration:** Deep analysis with encoding detection and data profiling
- **Excel output:** Progressive matrices from initial exploration to final consolidated structure
- **JSON reports:** Structured analysis data validated against official INE methodology
- **INE Validation:** 100% alignment with official methodology document

## Important Notes
- Always check CONTEXT.md for current project status
- **INE Data Logic:** Each CSV contains COMPLETE historical data from 2008T1 to latest quarter
- **Update Behavior:** When new data is available, INE provides the entire updated file
- **File Management:** System creates backups and replaces old files to prevent duplicates
- INE updates data quarterly (verify with --check-smart command)
- Preserve original CSV encoding when processing
- Handle missing values and data anomalies gracefully
- Use pattern matching ({codigo}_*.csv) to handle INE filename variations
- **DATABASE PATH:** Always use absolute path: `C:\dev\projects\absentismo-espana\data\analysis.db`

## Data Quality Status (19-ago-2025)
✅ **AGENT EXTRACTOR COMPLETED: 100% validation confirmed**
- **51 unique metrics extracted** from 35 INE tables
- **112% coverage** of direct metrics vs INE methodology (51/45.5 expected)
- 33 of 35 tables validated against web INE endpoints
- All validated tables show perfect match (3+ values per table)
- Total of 150+ numeric values verified
- Tables 6047 and 6049 lack web endpoints but use same extraction process
- **Metrics categorization validated** against official INE methodology document
- **Confidence level: Maximum - Agent Extractor ready for production**

## Agent Processor (Completado 27-nov-2024)

### Estado: COMPLETADO Y VALIDADO ✅
- ✅ Pipeline ETL completamente funcional (Extractor, Transformer, Loader)
- ✅ DuckDB integrado con esquema de 25 campos (incluye metrica_codigo y metrica_ine)
- ✅ Carga completa: 149,247 registros (2008T1-2025T1)
- ✅ Validación 100%: TODAS las tablas validadas contra archivos INE
- ✅ Sin duplicados, con prevención de agregaciones incorrectas
- ✅ Nomenclatura y códigos estándar implementados

### Purpose
Transform raw CSV data from 6 specific INE tables (6042-6046, 6063) into a unified analysis table for absenteeism reporting (Adecco/Randstad format).

### Input Tables (Tiempo de Trabajo only)
- **6042**: Nacional + Sectores B-S + Jornada → incluye TOTAL nacional
- **6043**: Nacional + Secciones CNAE + Jornada → incluye TOTAL nacional
- **6044**: Nacional + Sectores B-S (sin jornada) → incluye TOTAL nacional
- **6045**: Nacional + Secciones CNAE (sin jornada) → incluye TOTAL nacional
- **6046**: Nacional + Divisiones CNAE (sin jornada) → incluye TOTAL nacional
- **6063**: CCAA + Sectores B-S + Jornada → incluye TOTAL nacional y por CCAA

**IMPORTANTE**: Todas las tablas incluyen el TOTAL nacional (cuando cnae_nivel='TOTAL'), calculado para cada métrica y trimestre.

### Output Table Structure: `observaciones_tiempo_trabajo`

**Primary Key**: `periodo + ambito_territorial + ccaa_codigo + cnae_nivel + cnae_codigo + tipo_jornada + metrica + causa`
**IMPORTANTE**: Esta clave primaria NO incluye `fuente_tabla`, lo que significa que el mismo TOTAL nacional aparece múltiples veces (una por cada tabla fuente)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| periodo | VARCHAR(6) | YES | Quarter (YYYYTQ) |
| ambito_territorial | ENUM | YES | NAC or CCAA |
| ccaa_codigo | VARCHAR(2) | NO | INE code or NULL |
| cnae_nivel | ENUM | YES | TOTAL, SECTOR_BS, SECCION, DIVISION |
| cnae_codigo | VARCHAR(5) | NO | CNAE code or NULL |
| jerarquia_sector_cod | VARCHAR(50) | NO | Path: TOTAL>SECCION>C>DIVISION>10 |
| jerarquia_sector_lbl | VARCHAR(100) | NO | Path: Total>Sección C>División 10 |
| tipo_jornada | ENUM | NO | TOTAL, COMPLETA, PARCIAL, NULL (NULL for tables 6044-6046) |
| metrica | VARCHAR(30) | YES | horas_pactadas, horas_pagadas, horas_efectivas, horas_extraordinarias, horas_no_trabajadas |
| causa | VARCHAR(30) | NO | 14 valores: vacaciones, festivos, it_total, maternidad_paternidad, permisos_retribuidos, razones_tecnicas_economicas, compensacion_extras, otras_remuneradas, perdidas_lugar_trabajo, conflictividad, otras_no_remuneradas, representacion_sindical, pagadas_agregado, no_pagadas_agregado, vacaciones_y_fiestas, NULL |
| metrica_codigo | VARCHAR(10) | YES | Códigos estándar: HP, HPAG, HE, HEXT, HNT, HNTRa-i, HNTnR1-2, etc. |
| metrica_ine | VARCHAR(150) | YES | Nombre exacto del INE para cada métrica |
| valor | DECIMAL | YES | Numeric value |
| es_total_ccaa | BOOLEAN | YES | TRUE if NAC |
| es_total_cnae | BOOLEAN | YES | TRUE if TOTAL level |
| es_total_jornada | BOOLEAN | YES | TRUE if NULL or TOTAL |
| rol_grano | ENUM | YES | NAC_TOTAL, NAC_TOTAL_JORNADA, NAC_SECTOR_BS, NAC_SECTOR_BS_JORNADA, NAC_SECCION, NAC_SECCION_JORNADA, NAC_DIVISION, CCAA_TOTAL, CCAA_TOTAL_JORNADA, CCAA_SECTOR_BS, CCAA_SECTOR_BS_JORNADA |
| fuente_tabla | VARCHAR(4) | YES | Código de tabla INE (6042-6046, 6063) - CRÍTICO para filtrar duplicados del TOTAL |
| version_datos | VARCHAR(10) | NO | INE data version (e.g., "2024T3") |
| fecha_carga | TIMESTAMP | YES | Load timestamp for audit |

**Total: 25 campos** (actualizado 28-nov-2024)

### Key Design Decisions

1. **Heterogeneous Granularity Solution**: `rol_grano` field identifies granularity combinations (NOTE: does not prevent duplicate TOTAL across tables)
2. **Double Counting Prevention**: Boolean flags (`es_total_*`) explicitly mark totals
3. **Jornada Handling**: NULL when not available (tables 6044-6046), with `es_total_jornada` flag
4. **Metrics Structure**: Separated into `metrica` (5 types) + `causa` (14 types for HNT)
5. **CCAA Limitation**: Only available in table 6063 at B-S level
6. **Ceuta/Melilla**: Integrated with Andalucía (INE decision maintained)
7. **TOTAL Nacional Duplication**: Each table (6042-6046, 6063) includes the same TOTAL nacional - use `fuente_tabla` filter to avoid duplication

### Validation Rules

1. **Uniqueness**: No duplicates in primary key
2. **Completeness**: causa required if metrica='horas_no_trabajadas'
3. **Mathematical Coherence**: HE ≈ HP + HEXT - HNT_total (±0.5)
4. **Sum of Causes**: Σ(HNT by cause) ≈ HNT_total (±0.5)
5. **No Mixed Levels**: Never sum different cnae_nivel or ambito_territorial

### Processing Configuration
- **Source**: `config/procesador_config_completo.json`
- **Mappings**: INE column names → standardized fields
- **Validations**: 16 business rules from Excel v3
- **Domains**: Closed lists for all categorical fields

### Decisiones Técnicas Validadas
1. **VALORES TAL CUAL DEL INE**: NO dividir por 10 (151 = 15.1 horas)
2. **Mapeos confirmados desde exploración** (NO re-mapear):
   - tipo_jornada: Ya validado en `consolidate_patterns.py`
   - sectores: Mapeo completo validado
   - CCAA: 17 comunidades + Total Nacional
3. **Campo rol_grano**: Previene agregaciones incorrectas (funcionando)

### Estado de Validaciones
- ✅ TODAS las tablas (6042-6046, 6063) validadas al 100%
- ✅ 149,247 registros cargados correctamente
- ✅ Coherencia matemática verificada: HE = HP + HEXT - HNT

### IMPORTANTE - Reglas de Validación
1. **PRIMERO** consultar `docs/EXPLORACION_VALIDADA.md` - Contiene TODOS los valores ya validados
2. SIEMPRE usar valores de exploración validada (agosto 2025)
3. NO re-validar directamente contra CSVs sin revisar exploración previa
4. Solo contrastar con URLs INE si el valor NO está en exploración validada
5. Generar reporte consolidado de todas las validaciones

### Diferencia CRÍTICA: Horas Pagadas vs Horas Efectivas
**IMPORTANTE**: Son métricas DIFERENTES en el INE:
- **Horas pagadas**: Todas las horas por las que se paga (incluye vacaciones, permisos, etc.)
- **Horas efectivas**: Solo las horas realmente trabajadas
- **Relación**: Horas pagadas > Horas efectivas (SIEMPRE)
- **Ejemplo real**: Industria 2025T1: Pagadas=166.0, Efectivas=144.2 (diferencia=21.8)

## Nomenclatura y Códigos de Métricas

### Códigos Estándar (campo metrica_codigo)

**Métricas Base:**
- `HP` - Horas pactadas
- `HPAG` - Horas pagadas
- `HE` - Horas efectivas
- `HEXT` - Horas extraordinarias
- `HNT` - Horas no trabajadas (total)

**Horas No Trabajadas Remuneradas:**
- `HNTR` - Total remuneradas (agregado)
- `HNTRa` - Vacaciones
- `HNTRb` - Festivos
- `HNTRc` - I.T. (Incapacidad Temporal)
- `HNTRd` - Maternidad/Paternidad
- `HNTRe` - Permisos remunerados
- `HNTRf` - Razones técnicas o económicas
- `HNTRg` - Compensación horas extras
- `HNTRh` - Pérdidas en lugar de trabajo
- `HNTRi` - Otras remuneradas

**Horas No Trabajadas No Remuneradas:**
- `HNTnR` - Total no remuneradas (agregado)
- `HNTnR1` - Conflictividad laboral
- `HNTnR2` - Otras causas no remuneradas

**Especial:**
- `HNTRab` - Vacaciones y festivos (agregado para tablas con menos detalle)

### Mapeo de Causas

| causa (interno) | metrica_codigo | metrica_ine (nombre INE) |
|----------------|----------------|--------------------------|
| vacaciones | HNTRa | Horas no trabajadas por vacaciones |
| festivos | HNTRb | Horas no trabajadas por fiestas |
| it_total | HNTRc | Horas no trabajadas por I.T |
| maternidad_paternidad | HNTRd | Horas no trabajadas por maternidad |
| permisos_retribuidos | HNTRe | Horas no trabajadas por permisos remunerados |
| razones_tecnicas_economicas | HNTRf | Horas no trabajadas por razones técnicas o económicas |
| compensacion_extras | HNTRg | Horas no trabajadas por compensación horas extras |
| perdidas_lugar_trabajo | HNTRh | Horas perdidas en el lugar de trabajo |
| otras_remuneradas | HNTRi | Otras horas no trabajadas y remuneradas |
| conflictividad | HNTnR1 | Horas no trabajadas por conflictividad laboral |
| otras_no_remuneradas | HNTnR2 | Horas no trabajadas por otras causas |
| vacaciones_y_fiestas | HNTRab | Horas no trabajadas por vacaciones y fiestas |

## Lógica de Validación de Datos

### Fuentes de Verdad (por orden de prioridad)
1. **Scripts de exploración validados** (agosto 2025)
   - `exploration/validate_specific_values.py`
   - `exploration/validate_all_tables.py`
   - `exploration/consolidate_patterns.py`
2. **Web INE** (https://www.ine.es/jaxiT3/Datos.htm?t={codigo})
3. **Metodología INE** (docs/metodologia_ETCL_INE_2023.pdf)

### NUNCA usar como fuente primaria:
- CSVs directamente (ya validados en exploración)
- Valores hardcodeados sin verificar origen

### Documentación de Exploración Validada
- **CRÍTICO**: `docs/EXPLORACION_VALIDADA.md` - Consultar SIEMPRE antes de cualquier validación
- Contiene todos los valores validados, mapeos confirmados y lecciones aprendidas
- Si un valor está ahí, NO necesita re-validación

## Streamlit Dashboard de Absentismo (Sprint 1 - Completado 28-nov-2024)

### Ubicación y Estructura
```
streamlit_app/
├── app.py              # Aplicación principal Streamlit
└── test_db_connection.py  # Script de prueba de conexión
```

### Ejecución
```bash
# Desde el directorio raíz del proyecto
cd streamlit_app
streamlit run app.py

# URL de acceso
http://localhost:8502
```

### Configuración Crítica de Base de Datos
**IMPORTANTE:** La ruta de la base de datos DEBE ser absoluta en Windows:
```python
db_path_str = r"C:\dev\projects\absentismo-espana\data\analysis.db"
```

### Metodología de Cálculo Adecco (Validada)
```python
# 1. Horas Pactadas Efectivas (HPE)
HPE = HP + HEXT - Vacaciones - Festivos - ERTEs
# Valor Q4 2024: 137.2 horas

# 2. Horas No Trabajadas Motivos Ocasionales (HNTmo)
HNTmo = IT + Maternidad + Permisos + Compensación + Otras_rem + Pérdidas + Conflictividad + Otras_no_rem
# Valor Q4 2024: 10.2 horas

# 3. Tasa de Absentismo General
Tasa_Absentismo = (HNTmo / HPE) × 100
# Valor Q4 2024: 7.43% (Adecco reporta 7.4%)

# 4. Tasa de IT
Tasa_IT = (IT / HPE) × 100  
# Valor Q4 2024: 5.76% (Adecco reporta 5.8%)
```

### IMPORTANTE: Manejo del TOTAL Nacional en Queries
**PROBLEMA IDENTIFICADO (28-nov-2024):** Las 6 tablas INE (6042-6046, 6063) incluyen todas el mismo valor TOTAL nacional por diseño del INE. 

**Definición del TOTAL Nacional en el INE:**
El TOTAL nacional corresponde a los registros donde:
- **Tipo Jornada**: "AMBAS JORNADAS" o "TOTAL" (NULL en tablas sin jornada)
- **Secciones CNAE**: "B_S Industria, construcción y servicios (excepto actividades de los hogares...)"
- **Sectores CNAE**: "B_S Industria, construcción y servicios (excepto actividades de los hogares...)"
- **Ámbito**: "Total nacional"

Cada tabla calcula y almacena su propio TOTAL para cada métrica y trimestre. Esto facilita la validación y referencia, pero causa que el mismo valor aparezca 6 veces en nuestra base de datos.

**SOLUCIÓN CORRECTA:** Usar filtros de dimensiones, NO trucos SQL como AVG, MAX o DISTINCT:
```sql
-- CORRECTO: Filtrar por una tabla específica para evitar duplicados
SELECT SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp
FROM observaciones_tiempo_trabajo
WHERE periodo = '2024T4'
    AND ambito_territorial = 'NAC'
    AND cnae_nivel = 'TOTAL'
    AND fuente_tabla = '6042'  -- Usar solo tabla 6042 para TOTAL nacional
    AND tipo_jornada = 'TOTAL'
```

**NUNCA HACER:**
- NO usar AVG para "promediar" duplicados
- NO usar MAX o MIN para tomar un valor arbitrario
- NO usar DISTINCT ON como parche
- NO modificar los datos originales

**LECCIÓN APRENDIDA:** Los datos del INE son correctos. El problema surge porque cargamos el mismo TOTAL de múltiples fuentes. La solución es filtrar por la fuente apropiada según el nivel de detalle deseado.

### Características Implementadas (Sprint 1)
- ✅ Conexión a DuckDB con datos INE-ETCL
- ✅ Cálculo de KPIs principales (Tasa Absentismo, Tasa IT)
- ✅ 6 pestañas de análisis (estructura base)
- ✅ Filtro por periodo trimestral
- ✅ Metodología Adecco exacta (NO Randstad)
- ✅ Valores coincidentes con informes publicados

### Valores de Referencia Q4 2024
| Métrica | Valor INE | Unidad |
|---------|-----------|--------|
| HP (Horas Pactadas) | 151.4 | horas/trabajador |
| HEXT (Horas Extras) | 0.8 | horas/trabajador |
| Vacaciones + Festivos | 14.9 | horas/trabajador |
| ERTEs | 0.1 | horas/trabajador |
| IT | 7.9 | horas/trabajador |
| HPE (calculado) | 137.2 | horas/trabajador |
| HNTmo (calculado) | 10.2 | horas/trabajador |

### Troubleshooting Común
1. **Error "No se encuentra la base de datos"**: 
   - Verificar ruta absoluta en `app.py` línea 62
   - Debe ser: `r"C:\dev\projects\absentismo-espana\data\analysis.db"`

2. **Valores incorrectos en tasas**:
   - Verificar uso de AVG en lugar de SUM
   - Confirmar nivel de agregación: usar cnae_nivel = 'TOTAL'

3. **Error de caché en Streamlit**:
   - Ejecutar: `streamlit cache clear`
   - Reiniciar servidor

4. **Encoding errors en Windows**:
   - No usar emojis o caracteres Unicode en output
   - Usar ASCII equivalentes