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
├── Agent Extractor: Downloads and validates CSV data from INE
│   ├── INEScraper: Checks for updates from INE website
│   ├── Downloader: Robust CSV download with retries
│   ├── MetadataManager: Version tracking and hash validation
│   └── UpdateManager: Smart incremental updates
└── Agent Processor: Cleans and structures data (dimensions/metrics) [TODO]
```

## Project Structure
```
absentismo-espana/
├── agent_extractor/     # Data extraction from INE
├── agent_processor/     # Data processing and cleaning [TODO]
├── config/              # Configuration files
│   └── tables.json      # 35 INE table definitions
├── data/
│   ├── raw/csv/        # 35 Original CSV files from INE (one per table)
│   ├── metadata/       # Update tracking and version control
│   ├── backups/        # Automatic backups with timestamps
│   └── exploration_reports/ # Analysis reports and Excel matrices
│       ├── structure/  # Individual table structure analysis (JSON)
│       ├── *.json      # Comprehensive analysis data
│       └── *.xlsx      # Excel reports with column matrices
├── exploration/         # Data exploration scripts and tools
│   ├── csv_explorer.py     # Basic CSV structure analysis
│   ├── columns_analyzer.py # Mass analysis and Excel generation
│   └── report_viewer.py    # HTML report generation [WIP]
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
python exploration/csv_explorer.py       # Analyze CSV structure and identify dimensions/metrics
python exploration/columns_analyzer.py   # Mass analysis of all 35 tables with Excel output
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
- **Pandas integration:** Deep analysis with encoding detection and data profiling
- **Excel output:** Comprehensive column matrices for agent_processor design
- **JSON reports:** Structured analysis data for programmatic consumption

## Important Notes
- Always check CONTEXT.md for current project status
- **INE Data Logic:** Each CSV contains COMPLETE historical data from 2008T1 to latest quarter
- **Update Behavior:** When new data is available, INE provides the entire updated file
- **File Management:** System creates backups and replaces old files to prevent duplicates
- INE updates data quarterly (verify with --check-smart command)
- Preserve original CSV encoding when processing
- Handle missing values and data anomalies gracefully
- Use pattern matching ({codigo}_*.csv) to handle INE filename variations