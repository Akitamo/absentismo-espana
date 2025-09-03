# CLAUDE.md

Contexto estable y reglas para trabajar con este repositorio.

## Visión General
AbsentismoEspana: sistema modular para extraer, procesar y visualizar datos de absentismo (INE, ETCL).

## Frontend: Dash
- `apps/dash/app.py`: arranque, shell con sidebar fijo y header ancho completo.
- `apps/dash/pages/`: páginas (`dashboard.py`, `analisis.py`, `comparativas.py`, `exportar.py`).
- `apps/dash/assets/theme.css`: generado desde tokens (NO editar a mano).
- `apps/dash/assets/z-overrides.css`: overrides manuales persistentes (SÍ editar aquí).
- `design/tokens.json`: fuente de verdad del diseño (tokens-first).
- `src/core/data_service.py`: servicio de datos (DuckDB), agnóstico del frontend.

### Componentes UI reutilizables
- `apps/dash/components/ui.py` → `card(...)`: wrapper genérico para gráficas/tablas/bloques con header/body/footer y variantes (`card--compact`, `card--scroll`).
  - Usar siempre para nuevos bloques visuales; evita divergencias de paddings, sombras y radios.

## Cómo ejecutar (resumen)
- `pip install -r requirements/base.txt -r requirements/dash.txt`
- Configurar `.env` con `APP_DB_PATH=data/analysis.db` (o ruta absoluta)
- Inicializar DB demo (opcional): `python scripts/init_db.py`
- Ejecutar: `python apps/dash/app.py`  → http://127.0.0.1:8050
- Guía: `apps/dash/README.md`

## Mapa de Documentación (consulta frecuente)
- docs/DESIGN_SYSTEM.md: especificaciones de UI/UX y tokens para Dash.
- docs/DATA_LESSONS_LEARNED.md: lecciones de procesamiento de datos.
- CONTEXT.md: estado actual, próximos pasos, enlaces operativos.
- docs/LECCIONES_APRENDIDAS_DUPLICADOS.md: pauta para evitar duplicados del TOTAL (fuente_tabla).

## Reglas Fundamentales (Dash)
- Sin CSS inline. Tokens-first: editar `design/tokens.json` y regenerar `theme.css` con `python scripts/tokens_to_css.py`.
- No editar `theme.css` a mano; poner estilos manuales en `apps/dash/assets/z-overrides.css`.
- Sidebar/Header: respetar `--sidebar-w` y clases `.sidebar`, `.header`, `.content`.
- IDs y estado: IDs estables; estado con `dcc.Store` cuando aplique.
- Callbacks puros: `@callback` con `Input`/`Output`/`State`; sin efectos laterales.
- Datos: usar `src/core/data_service.py`; sin dependencias de Streamlit en `main`.

## Histórico
- La implementación anterior en Streamlit está archivada en la rama `archive/streamlit-final` (tag `v0.1-streamlit`). No mezclar código o patrones de Streamlit en `main`.

## Herramientas de apoyo (UX)
- Referencia visual en `design/Diseño dashboardFIN.jpg`. El overlay en app se retiró tras la fase de alineación inicial.

## Responsive (política y pautas)
- Enfoque: tokens → `theme.css` (autogenerado) + `z-overrides.css` (media queries y layout). No editar `theme.css`.
- Breakpoints: `lg ≤1200`, `md ≤992`, `sm/xs ≤768` (aprox.).
- Sidebar:
  - Desktop: ancho `--sidebar-w: 240px`.
  - ≤1200px: modo icon-only (`--sidebar-w: 64px`), labels ocultas, tooltips por `title`.
  - ≤768px: futuro drawer superpuesto (toggle en header) — planificado.
- Header: fijo y a la derecha del sidebar; buscador reduce anchura en `lg/md` y 100% en `sm/xs`.
- Grids:
  - Filtros: 3 → 2 cols (`lg`) → 1 col (`sm/xs`).
  - KPIs: 4 → 3 (`lg`) → 2 (`md`) → 1 (`sm/xs`).
  - Main: 2 columnas desktop → 1 columna en `md`.
- DataTable: `overflow-x:auto` en `sm/xs` (opcional: ocultar columnas de baja prioridad más adelante).

## Estado actual (UI)
- Sidebar y header implementados según template base.
- Responsive baseline activo (media queries en `z-overrides.css`).
- Card wrapper aplicado en Dashboard (Evolución, Ranking); extender a KPIs de forma progresiva.
