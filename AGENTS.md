# Repository Guidelines

## Project Structure & Modules
- `agent_extractor/`: descarga del INE (CSV/JSON), metadata y actualizaciones.
- `agent_processor/`: ETL (extractor/transformer/loader), validaciones y orquestación.
- `apps/dash/`: app Dash (UI, assets, pages, components).
- `data/`: `raw/` (fuente INE), `metadata/`, `backups/`, `analysis.db` (DuckDB).
- `scripts/`: utilidades (init, smoke, metadata, Dash runner).
- `src/`: utilidades core compartidas. Entrada CLI en `main.py`.

## Build, Test, and Dev Commands
- `pip install -r requirements.txt`: instala dependencias.
- `python main.py --check-smart`: verifica actualizaciones con metadata local.
- `python main.py --download-all` | `--download 6042`: descarga masiva o tabla.
- `python agent_processor/processor.py --test | --full`: carga ETL parcial o histórica.
- `python scripts/init_db.py`: prepara `data/analysis.db` (DuckDB) si aplica.
- `python scripts/run_dash.py`: arranca la app Dash local.
- `python scripts/smoke_core.py`: smoke de extract/ETL; use antes de PR.

## Coding Style & Naming
- Python 3.8+: sigue PEP 8, 4 espacios, 79–100 cols.
- Nombres: `snake_case` funciones/variables, `CamelCase` clases, módulos claros.
- Tipado: añade type hints en funciones públicas y retornos.
- Docstrings: formato breve en módulos/públicos (qué hace, inputs/outputs).
- Mantén I/O en `data/` y no hardcodees rutas; usa `pathlib`.

## Testing Guidelines
- Prioriza “smoke” (`scripts/smoke_core.py`) y validaciones en `agent_processor/validators/`.
- Añade tests como `tests/test_*.py` o junto al módulo si son unitarios pequeños.
- Convención: `test_<funcion>_<caso>()`; datos de prueba en `data/processed/` cuando aplique.
- Cobertura objetivo: valida paths críticos de descarga, parsing, mapping y carga.

## Commit & Pull Request Guidelines
- Mensajes: estilo convencional (`feat:`, `fix:`, `docs:`, `chore:`, `ui:`). Ej.: `feat(extractor): reintentos y backoff`.
- PRs: descripción clara, issue vinculada, pasos de prueba, riesgos/roll-back. UI: incluye screenshots “antes/después”.
- Checklist: `smoke_core` ok, datos no versionados, `.env` no incluido, scripts reproducibles.

## Security & Config
- Variables en `.env` (ver `.env.example`). No subas credenciales ni datos sensibles.
- Escribe en `data/` únicamente; respeta `backups/` y `metadata/` en operaciones de update.
- Red: maneja errores/timeout del INE; implementa reintentos con límites.

