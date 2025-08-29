# CLAUDE.md

This file provides stable context for Claude AI when working with this repository.

## Project Overview
**AbsentismoEspana** - Modular system for extracting and processing Spain's National Statistics Institute (INE) labor absenteeism data from the ETCL (Encuesta Trimestral de Coste Laboral) dataset.

## Repository Information
- **GitHub:** https://github.com/Akitamo/absentismo-espana
- **Language:** Python 3.8+
- **License:** MIT
- **Database:** DuckDB for data analysis

## Architecture
```
Modular Agent-Based System:
├── Agent Extractor: Downloads and validates CSV data from INE
│   ├── INEScraper: Checks for updates
│   ├── Downloader: Robust CSV download with retries
│   ├── MetadataManager: Version tracking
│   └── MetricsExtractor: 51 unique metrics identified
│
├── Agent Processor: Transforms raw data into unified table
│   ├── ETL Pipeline: Extract, Transform, Load
│   ├── DuckDB Integration: 149,247 records processed
│   └── Validation: 100% accuracy against INE sources
│
└── Streamlit Dashboard: Interactive visualization
    ├── KPI Cards: Key metrics display
    ├── Charts: Trend analysis
    └── Filters: Period and dimension selection
```

## Project Structure
```
absentismo-espana/
├── agent_extractor/        # Data extraction from INE
├── agent_processor/        # Data processing pipeline
│   └── scripts/           # Utility scripts
├── config/                # Configuration files
│   ├── tables.json        # 35 INE table definitions
│   └── procesador_config_completo.json
├── data/
│   ├── raw/csv/          # Original CSV files from INE
│   ├── analysis.db       # DuckDB database
│   ├── metadata/         # Update tracking
│   └── backups/          # Automatic backups
├── exploration/           # Data exploration scripts
├── streamlit_app/         # Dashboard application
│   ├── app.py            # Main application
│   ├── design/           # Design system
│   │   ├── tokens.json   # Design tokens
│   │   └── theme.py      # CSS generator
│   └── pages/            # Dashboard pages
├── docs/                  # Documentation
│   ├── DATA_LESSONS_LEARNED.md    # Data processing lessons
│   ├── DASHBOARD_DESIGN.md        # Design specifications
│   └── metodologia_ETCL_INE_2023.pdf
├── scripts/              # Utility scripts
├── main.py              # CLI interface
├── requirements.txt     # Python dependencies
├── README.md           # User documentation
├── CLAUDE.md          # This file
└── CONTEXT.md         # Dynamic project status
```

## Key Commands

### Data Management
```bash
# Download data
python main.py --download-all       # Download all tables
python main.py --download [table_id] # Download specific table

# Smart updates (recommended)
python main.py --check-smart        # Fast update check
python main.py --update-all         # Update all tables

# Process data
python agent_processor/scripts/load_all_tables.py  # Load to DuckDB
```

### Dashboard
```bash
# Run dashboard
cd streamlit_app
streamlit run app.py

# Access at: http://localhost:8505
```

## Data Sources
- **35 ETCL tables** from INE
- **Period coverage**: 2008T1 to present (quarterly)
- **6 key tables** for time metrics (6042-6046, 6063)
- **Database**: `data/analysis.db` (DuckDB)

## Critical Documentation - READ FIRST

### Design System (MANDATORY before UI work)
- **Design Rules**: `docs/DASHBOARD_DESIGN.md` - NUNCA inventar diseño
- **Design Tokens**: `streamlit_app/design/tokens.json` - Todos los valores
- **Theme CSS**: `streamlit_app/design/theme.py` - Variables CSS

### Data Processing
- **Lessons Learned**: `docs/DATA_LESSONS_LEARNED.md` - Problemas resueltos

## Development Guidelines

### General Rules
1. **ALWAYS propose actions before implementing** - Never proceed without explicit "ok"
2. **Each agent must be independent** and self-contained
3. **Follow existing patterns** and conventions
4. **Test with subset** before full runs
5. **Maintain backward compatibility**
6. **Document new functionality** in docstrings

### Code Quality
- **Path handling**: Use `Path(__file__).parent` (no hardcoding)
- **Error handling**: Comprehensive try-except blocks
- **Encoding**: Multi-encoding support for INE files
- **Windows compatibility**: ASCII output, absolute paths

### Documentation
- **Update README.md** for new features
- **Comment non-obvious code**
- **Add `# Reason:` comments** for complex logic
- **Keep documentation current**

## Technical Stack
- **Python 3.8+**: Core language
- **Pandas**: Data manipulation
- **DuckDB**: SQL analytics
- **Streamlit**: Dashboard framework
- **Requests**: HTTP operations
- **BeautifulSoup4**: Web scraping

## Important Notes

### Database Connection
```python
# Always use absolute path in Windows
db_path = r"C:\dev\projects\absentismo-espana\data\analysis.db"
```

### INE Data Behavior
- Downloads complete historical files (not incremental)
- Updates quarterly
- Multiple encodings possible
- Filename patterns may change

### Related Documentation
- **Data Processing**: See `docs/DATA_LESSONS_LEARNED.md`
- **Dashboard Design**: See `docs/DASHBOARD_DESIGN.md`
- **Current Status**: See `CONTEXT.md`
- **INE Methodology**: See `docs/metodologia_ETCL_INE_2023.pdf`

## Contact
For project-specific questions, refer to the documentation files or GitHub issues.