# Migración a Dash y Reorientación del Proyecto

Este documento define el plan de migración desde la aplicación actual en Streamlit hacia un nuevo frontend en Dash + Plotly, manteniendo como copia de seguridad la versión actual y arrancando en `main` una base limpia con sólo lo necesario.

## Objetivos
- Aislar la lógica de datos y conservarla.
- Retirar del `main` todo lo específico de Streamlit.
- Crear un esqueleto mínimo de Dash (layout, filtros, KPIs, un gráfico, tabla) sobre el que reconstruir el dashboard.
- Mantener una rama de archivo con la versión funcional en Streamlit.

## Alcance
- Se conserva: `agent_processor/`, `agent_extractor/`, `config/`, `data/`, `docs/`, `scripts/`, `exploration/`, y cualquier artefacto de datos/validación.
- Se archiva (en rama backup): todo lo de `streamlit_app/` y utilidades Streamlit relacionadas.
- Se elimina de `main`: código y assets sólo útiles para Streamlit.
- Se crea: estructura mínima de app Dash y un módulo `core` agnóstico de framework.

## Estrategia de ramas y versionado
- Crear rama de archivo con el estado actual: `archive/streamlit-final`.
- (Opcional) Tag del último estado Streamlit: `v0.1-streamlit`.
- Mantener `main` como rama de trabajo para Dash.

Comandos sugeridos:
```
# Crear rama de archivo y subir
git switch -c archive/streamlit-final
git push -u origin archive/streamlit-final

# (Opcional) Tag
git tag v0.1-streamlit
git push origin v0.1-streamlit

# Volver a main para iniciar la migración
git switch main
```

## Cambios estructurales (estado futuro del repo)
```
apps/
  dash/
    app.py
    pages/
      dashboard.py
    assets/
      theme.css
src/
  core/
    data_service.py
design/
  tokens.json  # (opcional: centralizar tokens aquí)
requirements/
  base.txt
  dash.txt
.env.example
```

Notas:
- `design/tokens.json` puede moverse a `design/` si hoy está bajo `streamlit_app/design/`.
- `src/core/` contendrá lógica reutilizable sin dependencias de frontend.

## Limpieza de Streamlit en main
Archivar previamente y luego eliminar del `main`:
- Directorios/archivos principales a eliminar:
  - `streamlit_app/`
  - `streamlit_app_structure.md`
  - `streamlit_adecco_report.py`
  - Utilidades exclusivas de Streamlit: `streamlit_app/README.md`, `streamlit_app/requirements.txt`, `streamlit_app/test_db_connection.py`, `streamlit_app/take_screenshot.py`, `streamlit_app/pages/*`, `streamlit_app/design/*` (si ya se migran tokens)

Comando orientativo:
```
git rm -r streamlit_app
[ -f streamlit_app_structure.md ] && git rm streamlit_app_structure.md || true
[ -f streamlit_adecco_report.py ] && git rm streamlit_adecco_report.py || true
```

## Extracción y adaptación de core de datos
Mover y adaptar el servicio de datos para hacerlo agnóstico del framework:
- Nuevo archivo: `src/core/data_service.py`
- Cambios clave respecto a `streamlit_app/services/data_service.py`:
  - Eliminar dependencias de Streamlit (`import streamlit as st`, `st.error`, `@st.cache_data`).
  - Configurar la ruta a DuckDB vía variable de entorno `APP_DB_PATH` con fallback a `data/analysis.db`.
  - Usar `functools.lru_cache` o `flask_caching` más adelante para caché.
  - Mantener métodos actuales: `get_available_periods`, `get_ccaa_list`, `get_sectors_list`, `get_kpis`, `get_evolution_data`, `get_ranking_ccaa`.
  - Conexión `duckdb.connect(..., read_only=True)`. Abrir por uso o manejar singleton simple y seguro.
  - Manejo de errores con `logging` y excepciones; el frontend decide cómo mostrarlos.

Ejemplo de configuración en `.env.example`:
```
APP_DB_PATH=data/analysis.db
```

## Scaffold de la app Dash (MVP)
- `apps/dash/app.py`:
  - Inicializa `Dash(__name__, use_pages=True, suppress_callback_exceptions=True)`.
  - Layout con sidebar simple (3 `dcc.Dropdown` para periodo, CCAA, sector), un contenedor para KPIs, `dcc.Graph` para evolución y una `dash_table.DataTable` para ranking.
  - `dcc.Store` opcional para estado compartido.
- `apps/dash/pages/dashboard.py`:
  - `dash.register_page(__name__, path="/")`.
  - Define layout y callbacks:
    - Inputs: dropdowns de filtros.
    - Outputs: KPIs (children), figura de evolución, data/columns de la tabla.
  - Llamadas a `DataService` (desde `src/core/`).
- `apps/dash/assets/theme.css`:
  - CSS mínimo inicial (colores, tipografías, espaciado).
  - Posteriormente, generar desde `design/tokens.json`.

## Estilos y tema
- Mantener un único `design/tokens.json`.
- Añadir script futuro para generar `apps/dash/assets/theme.css` desde tokens.
- Evitar selectores específicos del DOM de Streamlit; usar clases propias y variables CSS.

## Requisitos y ejecución
- `requirements/base.txt`: `pandas`, `duckdb`, `plotly`, `python-dotenv`.
- `requirements/dash.txt`: `dash`, `dash-table` (opcional: `dash-bootstrap-components`).

Ejecución local (ejemplo):
```
python -m venv .venv
. .venv/bin/activate  # (Windows PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements/base.txt -r requirements/dash.txt
# Configurar APP_DB_PATH en entorno o crear .env
python apps/dash/app.py
```

## Plan de implementación (commits/PRs)
1) Backup de Streamlit
- Crear rama `archive/streamlit-final` y tag `v0.1-streamlit` (opcional).
- Commit: "chore: archive Streamlit code"

2) Limpieza de `main`
- Eliminar `streamlit_app/` y archivos exclusivos de Streamlit.
- Commit: "chore: clean main for Dash migration"

3) Scaffold Dash
- Añadir `apps/dash/` con `app.py`, `pages/dashboard.py`, `assets/theme.css` mínimos.
- Añadir `requirements/` y `.env.example`.
- Commit: "feat(dash): scaffold dash app and requirements"

4) Extraer y adaptar DataService
- Crear `src/core/data_service.py`, mover lógica, parametrizar DB, logging.
- Wirear `dashboard.py` con `DataService`.
- Commit: "refactor(core): extract DataService and connect dash page"

5) Pulido inicial y docs
- README de ejecución, validaciones rápidas, pequeños ajustes de tema/KPI.
- Commit: "docs: update run instructions and initial theme"

(Se pueden agrupar en un PR único o varios para revisión incremental.)

## Validación y criterios de aceptación
- La app Dash arranca sin errores y muestra:
  - Dropdowns de Periodo/CCAA/Sector poblados desde DuckDB.
  - 4 KPIs con valores coherentes para el filtro por defecto.
  - Un gráfico de evolución temporal con datos reales o fallback.
  - Un ranking de CCAA en tabla para el periodo seleccionado.
- Sin dependencias de `streamlit` en `main`.
- `APP_DB_PATH` configurable por entorno.

## Estimación
- 3–6 días efectivos para el MVP Dash equivalente a la vista "Dashboard" actual.

## Riesgos y mitigación
- Conexión DuckDB concurrente: abrir por callback o pool simple (read-only).
- CSS inicial limitado: comenzar simple y evolucionar con tokens.
- Import paths tras reestructura: usar `src/` en PYTHONPATH o paquete editable más adelante.

## Plan de rollback
- Si algo bloquea, revertir `main` al tag `v0.1-streamlit` o crear una rama desde `archive/streamlit-final` y promoverla a `main`.

## Backlog post-MVP (no bloqueante)
- Multipage Dash (Análisis, Comparativas, Exportar) con placeholders.
- Generación de `theme.css` desde tokens por script.
- Caché con `flask_caching` si fuese necesario.
- Dockerfile y pipeline de despliegue.
