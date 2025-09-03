# Dash App — Absentismo España

Guía rápida para levantar el nuevo frontend en Dash.

## Requisitos
- Python 3.11+/3.12+
- pip

## Instalación
- `pip install -r requirements/base.txt -r requirements/dash.txt`

## Configuración de base de datos
- Copia `.env.example` a `.env` y ajusta `APP_DB_PATH` si es necesario (por defecto `data/analysis.db`).
- (Opcional) inicializa una DB de ejemplo: `python scripts/init_db.py`.

## Tema (tokens de diseño)
- Edita `design/tokens.json` y genera CSS: `python scripts/tokens_to_css.py`.
- El CSS se escribe en `apps/dash/assets/theme.css` (no lo edites a mano).
- Para estilos manuales puntuales usa `apps/dash/assets/z-overrides.css`.

## Ejecución
- Ejecuta: `python apps/dash/app.py`
- URL: `http://127.0.0.1:8050`

Alternativas
- Script con logs: `python scripts/run_dash.py`
- PowerShell en background (Windows): `scripts/start_dash.ps1`

## Estructura mínima
- `apps/dash/app.py`: aplicación principal y navegación.
- `apps/dash/pages/`: páginas (Dashboard, Análisis, Comparativas, Exportar).
- `apps/dash/assets/theme.css`: estilos generados desde tokens.
- `apps/dash/assets/z-overrides.css`: overrides manuales.
- `apps/dash/components/ui.py`: `card(...)` wrapper UI para contenedores homogéneos.
- `src/core/data_service.py`: servicio de datos (DuckDB), agnóstico de frontend.

## Notas
- Si no existe la DB, `DataService` usa valores de ejemplo/fallback.
- Para parar un proceso lanzado con `start_dash.ps1`, usa `Stop-Process -Id <PID>`.

## Uso de card(...)
```python
from apps.dash.components.ui import card

card(
  title="Mi bloque",
  body=dcc.Graph(...),
  footer=html.Small("Fuente: INE"),
  variant="compact",
)
```

## KPIs
- Los KPI tiles no llevan cabecera; usan `.kpi-card` con `.kpi-head` (icono + título), valor destacado y tendencia opcional.
- Títulos de KPI y cards unificados: 16px, 700 (negrita) para consistencia visual.

## Herramientas de diseño
- Usa `design/Diseño dashboardFIN.jpg` como referencia visual. El overlay fue retirado tras la fase inicial de alineación.

## Responsive
- Baseline en `apps/dash/assets/z-overrides.css` (no tocar `theme.css`).
- Breakpoints: `lg ≤1200`, `md ≤992`, `sm/xs ≤768`.
- Sidebar: 240px desktop; 64px icon-only en ≤1200px (labels ocultas, tooltips). Drawer móvil (planificado).
- Grids: Filtros 3→2→1; KPI 4→3→2→1; Main 2→1.
- DataTable: scroll horizontal en `sm/xs`.
