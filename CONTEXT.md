# CONTEXT.md

Última actualización: 03-09-2025

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

## Dashboard Dash
- Puerto: 8050
- URL: http://127.0.0.1:8050
- Páginas: Dashboard (inicio), Análisis, Comparativas, Exportar
- Arranque: `pip install -r requirements/base.txt -r requirements/dash.txt && python apps/dash/app.py`
- Guía rápida: `apps/dash/README.md`

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

## Próximos Pasos
1. Afinar estilos en `apps/dash/assets/theme.css` desde `design/tokens.json`.
2. Añadir `dcc.Store` para estado de filtros global (persistencia opcional).
3. Export CSV/Excel desde tabla/endpoint.
4. Páginas de detalle (drill-down) por CCAA/sector.

---

## Enlaces útiles
- Guía Dash: `apps/dash/README.md`
- Diseño y tokens: `docs/DESIGN_SYSTEM.md`, `design/tokens.json`
- Lecciones de datos (duplicados TOTAL): `docs/LECCIONES_APRENDIDAS_DUPLICADOS.md`
