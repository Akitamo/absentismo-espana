# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
AbsentismoEspana v2 is a modular agent-based system for extracting and processing Spain's National Statistics Institute (INE) labor absenteeism data from the ETCL dataset (35 CSV tables with quarterly labor cost data).

## GitHub Repository
- **URL**: https://github.com/Akitamo/absentismo-espana
- **Main branch**: v1 original (monolithic architecture)
- **Active branch**: `v2-refactor` (new modular architecture)
- **Pull Request**: Create from https://github.com/Akitamo/absentismo-espana/pull/new/v2-refactor

## Current Status
- **Date**: August 12, 2025
- **Phase 1**: ✅ COMPLETED - Extraction Agent
- **Phase 2**: 🔄 PENDING - Processing Agent
- **Location**: Working in `v2-refactor` branch

## V2 Architecture (Active Development)

### Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Check for updates
python main.py --check

# Download all tables
python main.py --download-all

# Download specific table
python main.py --download 6042

# Get table info
python main.py --info 6042
```

### Current Structure
```
absentismo-espana/
├── agent_extractor/       # Extraction agent (Phase 1 - DONE)
│   ├── __init__.py       # Orchestrator
│   ├── ine_scraper.py    # Scrapes INE for updates
│   └── downloader.py      # Robust CSV download
├── config/
│   └── tables.json        # 35 table definitions
├── data/
│   ├── raw/              # Downloaded CSVs
│   └── metadata/         # Update detection
├── main.py               # CLI interface
├── requirements.txt      # Minimal dependencies
├── CLAUDE_PROJECT.md     # Claude Desktop context
└── CLAUDE_INIT_PROMPT.md # Claude Desktop initialization

```

### Phase 2: Processing Agent (NEXT TASK)
To implement:
- `agent_processor/`: Data cleaning and dimension/metric separation
- Automatic detection of dimensions vs metrics
- Metadata extraction from Phase 1 output
- Structured output to `data/processed/`

## Data Categories (35 Tables)
- **Tiempo de trabajo** (6): Hours worked/not worked
- **Costes básicos** (2): Basic costs per worker/hour
- **Series temporales** (2): Historical evolution
- **Costes detallados** (8): Detailed costs by sector
- **Costes salariales** (4): Salary costs by workday
- **Vacantes** (8): Job vacancies and reasons
- **Otros costes** (5): IT costs, overtime, regional

## Key Features
- **Update Detection**: Checks INE for new data releases
- **Robust Downloads**: 3-retry system with exponential backoff
- **Multi-encoding Support**: UTF-8, Latin-1, ISO-8859-1, CP1252
- **Modular Design**: Independent agents for extraction and processing

## Development Guidelines
- Use `Path(__file__).parent` for paths (no hardcoding)
- Each agent should be independent
- Maintain robust error handling
- Follow existing code patterns
- Test with 2-3 tables before full runs

## Next Session Context
When resuming work:
1. We're in `v2-refactor` branch
2. Phase 1 (Extractor) is complete and working
3. Next task: Implement Phase 2 (Processor Agent)
4. The processor should:
   - Read CSVs from `data/raw/`
   - Identify dimensions vs metrics
   - Clean and structure data
   - Output to `data/processed/`