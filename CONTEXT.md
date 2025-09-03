# CONTEXT.md

Última actualización: 03-09-2025 (noche)

## Estado Actual: Frontend en Dash
- El dashboard se ejecuta con Dash (Plotly) en `apps/dash/`.
- La implementación previa en Streamlit está archivada en `archive/streamlit-final` (tag `v0.1-streamlit`).
- `main` no contiene dependencias ni utilidades de Streamlit.

---

## Pipeline de Datos
- 35 tablas INE descargadas/procesadas (ETL validado).
- 51 métricas únicas validadas, persistencia en DuckDB (`data/analysis.db`).
- Servicio de datos agnóstico: `src/core/data_service.py`.

---

## Dashboard Dash (estado actual)
- Puerto: 8050 — URL: http://127.0.0.1:8050
- Páginas: Dashboard (inicio), Análisis, Comparativas, Exportar
- Shell UI: sidebar fijo (logo Ibermutua, navegación en columna) + header ancho completo (búsqueda, acciones, usuario)
- Referencia visual: `design/Diseño dashboardFIN.jpg` (el overlay en app se retiró)
- Arranque: `pip install -r requirements/base.txt -r requirements/dash.txt && python apps/dash/app.py`
- Guía rápida: `apps/dash/README.md`

### Componentes
- Card wrapper (`apps/dash/components/ui.py`): contenedor unificado para bloques (gráficas, tablas, KPIs) con header/body/footer y variantes (`compact`, `scroll`). Evolución (Plotly) y Ranking CCAA (DataTable) lo usan.

Estructura base de la página principal (dashboard):
- Filtros: Periodo, CCAA, Sector (`dcc.Dropdown`).
- KPIs: tarjetas con valores clave (clase `.kpi-card`).
- Evolución: `dcc.Graph` (línea con relleno) usando `DataService.get_evolution_data`.
- Ranking CCAA: `dash_table.DataTable` (ordenado) con `DataService.get_ranking_ccaa`.

Callbacks (patrón):
```
@callback(
  Output("kpis","children"), Output("evolucion","figure"),
  Output("ranking-table","data"), Output("ranking-table","columns"),
  Input("f-periodo","value"), Input("f-ccaa","value"), Input("f-sector","value")
)
def update_dashboard(periodo, ccaa, sector):
    # usar src/core/data_service.py
    ...
```

---

## Próximos Pasos (UI)
1. Filtros (Dropdown react-select): borde/hover/selected según template.
2. KPI cards: jerarquía tipográfica, padding, sombra y radios.
3. DataTable: contenedor con borde+radio; cabecera y celdas con tipografías correctas.
4. Trazas Plotly: tema de colores y márgenes acorde a diseño.
5. Responsive Fase 2: drawer de sidebar en ≤768px con `dcc.Store` y backdrop.
6. Export (CSV/Excel) desde tabla o endpoint.

---

## Enlaces útiles
- Guía Dash: `apps/dash/README.md`
- Diseño y tokens: `docs/DESIGN_SYSTEM.md`, `design/tokens.json`
- Lecciones de datos (duplicados TOTAL): `docs/LECCIONES_APRENDIDAS_DUPLICADOS.md`

## Notas operativas
- `scripts/tokens_to_css.py` regenera `apps/dash/assets/theme.css` desde tokens. Para estilos manuales, usar `apps/dash/assets/z-overrides.css`.
- `scripts/init_db.py` crea `data/analysis.db` con datos demo (para smoke tests y desarrollo local).

## Responsive (baseline vigente)
- Media queries en `apps/dash/assets/z-overrides.css`.
- `--sidebar-w`: gobierna sidebar/header/content (240px desktop; 64px icon-only ≤1200px).
- Grids adaptativos: filtros 3→2→1; KPIs 4→3→2→1; main 2→1.
- DataTable con `overflow-x:auto` en `sm/xs`.
