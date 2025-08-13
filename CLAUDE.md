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
└── Agent Processor: Cleans and structures data (dimensions/metrics)
```

## Project Structure
```
absentismo-espana/
├── agent_extractor/     # Data extraction from INE
├── agent_processor/     # Data processing and cleaning
├── config/              # Configuration files
│   └── tables.json      # 35 INE table definitions
├── data/
│   ├── raw/            # Original CSV files from INE
│   ├── processed/      # Cleaned and structured data
│   └── metadata/       # Update tracking
├── main.py             # CLI interface
├── requirements.txt    # Python dependencies
├── README.md          # User documentation
├── CLAUDE.md          # This file (stable context)
└── CONTEXT.md         # Dynamic project status
```

## Key Commands
```bash
# Check for updates
python main.py --check

# Download data
python main.py --download-all
python main.py --download [table_id]

# Process data (when implemented)
python main.py --process-all
python main.py --process [table_id]
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

## Development Guidelines
1. Each agent must be independent and self-contained
2. Follow existing code patterns and conventions
3. Test with subset (2-3 tables) before full runs
4. Maintain backward compatibility with existing data
5. Document all new functionality in docstrings

## Important Notes
- Always check CONTEXT.md for current project status
- INE updates data quarterly (verify with --check command)
- Preserve original CSV encoding when processing
- Handle missing values and data anomalies gracefully