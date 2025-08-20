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
└── Agent Processor: Transforms raw data into unified analysis table [IN DESIGN]
```

## Project Structure
```
absentismo-espana/
├── agent_extractor/     # Data extraction from INE
├── agent_processor/     # Data processing into unified table [IN DESIGN]
├── config/              # Configuration files
│   ├── tables.json      # 35 INE table definitions
│   └── procesador_config_completo.json # Agent Processor configuration
├── data/
│   ├── raw/csv/        # 35 Original CSV files from INE (one per table)
│   ├── metadata/       # Update tracking and version control
│   ├── backups/        # Automatic backups with timestamps
│   └── exploration_reports/ # Analysis reports and Excel matrices
│       ├── structure/  # Individual table structure analysis (JSON)
│       ├── *.json      # Comprehensive analysis data
│       └── *.xlsx      # Excel reports with column matrices
├── exploration/         # Data exploration scripts and tools
│   ├── csv_explorer.py              # Basic CSV structure analysis
│   ├── columns_analyzer.py          # Mass analysis and Excel generation
│   ├── analyze_8_tables.py          # Advanced analysis with unique values extraction
│   ├── consolidate_patterns.py      # Pattern consolidation across tables
│   ├── unified_schema_35_tables.py  # Unified schema application
│   ├── identify_metrics_per_table.py # Clear metric identification by category
│   ├── final_matrix_consolidated.py # Final consolidated matrix generation
│   └── report_viewer.py             # HTML report generation [WIP]
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

# Data exploration scripts
python exploration/csv_explorer.py              # Analyze CSV structure and identify dimensions/metrics
python exploration/columns_analyzer.py          # Mass analysis of all 35 tables with Excel output
python exploration/analyze_8_tables.py          # Advanced analysis of representative tables with unique values
python exploration/consolidate_patterns.py      # Consolidate patterns identified across tables
python exploration/unified_schema_35_tables.py  # Apply unified schema to all 35 tables
python exploration/identify_metrics_per_table.py # Identify and categorize metrics per table
python exploration/final_matrix_consolidated.py # Generate final consolidated matrix

# Metrics extraction scripts (VALIDATED - 51 metrics extracted)
python exploration/extract_all_metrics_detailed.py     # Extract all 51 unique metrics with detailed categorization
python exploration/extract_metrics_enhanced.py         # Enhanced analysis with 112% coverage validation
python exploration/validate_direct_metrics_only.py     # Validate only direct metrics (excludes calculated ones)
python exploration/validate_metrics_with_ine.py        # Cross-validate extracted metrics against INE methodology

# Data validation scripts (VALIDATED 16-ago-2025)
python exploration/check_all_endpoints.py       # Verify which tables have web endpoints (33/35 OK)
python exploration/validate_all_tables.py       # Run exhaustive validation - 100% success rate
python exploration/validate_specific_values.py  # Validate specific numeric values
python exploration/validate_precise_comparison.py # Precise value-by-value comparison
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

## Agent Processor Design (20-ago-2025)

### Purpose
Transform raw CSV data from 6 specific INE tables (6042-6046, 6063) into a unified analysis table for absenteeism reporting (Adecco/Randstad format).

### Input Tables (Tiempo de Trabajo only)
- **6042**: Nacional + Sectores B-S + Jornada
- **6043**: Nacional + Secciones CNAE + Jornada  
- **6044**: Nacional + Sectores B-S (sin jornada)
- **6045**: Nacional + Secciones CNAE (sin jornada)
- **6046**: Nacional + Divisiones CNAE (sin jornada)
- **6063**: CCAA + Sectores B-S + Jornada

### Output Table Structure: `observaciones_tiempo_trabajo`

**Primary Key**: `periodo + ambito_territorial + ccaa_codigo + cnae_nivel + cnae_codigo + tipo_jornada + metrica + causa`

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
| metrica | ENUM | YES | horas_pactadas, horas_efectivas, horas_extraordinarias, horas_no_trabajadas |
| causa | ENUM | NO | it_total, maternidad_paternidad, permisos_retribuidos, conflictividad, representacion_sindical, otros, vacaciones*, festivos*, erte_suspension*, NULL (*excluded from general absenteeism) |
| valor | DECIMAL | YES | Numeric value |
| es_total_ccaa | BOOLEAN | YES | TRUE if NAC |
| es_total_cnae | BOOLEAN | YES | TRUE if TOTAL level |
| es_total_jornada | BOOLEAN | YES | TRUE if NULL or TOTAL |
| rol_grano | ENUM | YES | NAC_TOTAL, NAC_TOTAL_JORNADA, NAC_SECTOR_BS, NAC_SECTOR_BS_JORNADA, NAC_SECCION, NAC_SECCION_JORNADA, NAC_DIVISION, CCAA_TOTAL, CCAA_TOTAL_JORNADA, CCAA_SECTOR_BS, CCAA_SECTOR_BS_JORNADA |
| version_datos | VARCHAR(10) | NO | INE data version (e.g., "2024T3") |
| fecha_carga | TIMESTAMP | YES | Load timestamp for audit |

### Key Design Decisions

1. **Heterogeneous Granularity Solution**: `rol_grano` field uniquely identifies each combination preventing invalid aggregations
2. **Double Counting Prevention**: Boolean flags (`es_total_*`) explicitly mark totals
3. **Jornada Handling**: NULL when not available (tables 6044-6046), with `es_total_jornada` flag
4. **Metrics Structure**: Separated into `metrica` (4 types) + `causa` (9 types for HNT)
5. **CCAA Limitation**: Only available in table 6063 at B-S level
6. **Ceuta/Melilla**: Integrated with Andalucía (INE decision maintained)

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