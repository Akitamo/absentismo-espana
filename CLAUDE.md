# CLAUDE.md

This file provides stable context and fundamental rules for Claude AI when working with this repository.

## Project Overview
**AbsentismoEspana** - Modular system for extracting and processing Spain's National Statistics Institute (INE) labor absenteeism data from the ETCL dataset.

## 📚 DOCUMENTATION MAP - ALWAYS CONSULT

### Critical Documents (MANDATORY READING)
- **`docs/DESIGN_SYSTEM.md`** - ALL UI/UX specifications, mockups, tokens, architecture
- **`docs/DATA_LESSONS_LEARNED.md`** - Data processing lessons, ETL issues resolved  
- **`CONTEXT.md`** - Current project state, sprint status, pending tasks

### When to Consult Each:
- **Before ANY UI work** → Read DESIGN_SYSTEM.md
- **Before data processing** → Read DATA_LESSONS_LEARNED.md
- **To check current status** → Read CONTEXT.md

## 🚫 FUNDAMENTAL RULES (NEVER BREAK)

1. **ALWAYS read docs/DESIGN_SYSTEM.md before ANY UI work**
2. **ALWAYS read docs/DATA_LESSONS_LEARNED.md before data processing**
3. **NEVER proceed without user approval** - Propose, then wait for "ok"
4. **CRITICALLY EVALUATE proposals** - Don't agree automatically. Analyze pros/cons, suggest alternatives if better solution exists

## Repository Structure
```
absentismo-espana/
├── agent_extractor/       # INE data extraction
├── agent_processor/       # ETL pipeline to DuckDB
├── streamlit_app/         # Dashboard application
│   ├── design/           # tokens.json & theme.py
│   ├── visualizations/   # Modular chart system
│   ├── components/       # chart_container.py with slots
│   └── pages/           # Including 03_galeria.py for QA
├── docs/                 # Critical documentation
├── data/                 # CSV files & analysis.db
└── config/              # 35 INE table definitions
```

## Key Commands
```bash
# Data pipeline
python main.py --check-smart      # Check for updates
python main.py --update-all       # Update all tables

# Dashboard
cd streamlit_app
streamlit run app.py              # Port 8505
```

## Technical Stack
- **Python 3.8+** with Pandas
- **DuckDB** for data (149,247 records)
- **Streamlit** with modular visualizations
- **Design**: Token-first architecture

## Database Path (Windows)
```python
db_path = r"C:\dev\projects\absentismo-espana\data\analysis.db"
```

## Quick Reference
- **GitHub**: https://github.com/Akitamo/absentismo-espana
- **Port**: 8505
- **Galería QA**: http://localhost:8505/galeria

## Remember
- This file = Instructions & rules only
- CONTEXT.md = Current state only
- docs/ = All specifications