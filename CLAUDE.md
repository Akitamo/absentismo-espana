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

---

## Estado Actual (2025-09-03)

- Shell UI:
  - Sidebar fijo en desktop (240px) y drawer en móvil (≤768px) con `dcc.Store` + backdrop.
  - Header full width (a la derecha del sidebar) con búsqueda y acciones.
- KPI iniciales: 2 KPIs (Tasa de Absentismo e IT) con icono y delta vs periodo anterior.
- Cards: wrapper genérico `apps/dash/components/ui.py:card(...)` aplicado a Evolución y Ranking.
- Tablas en móvil: scroll horizontal con sombras laterales y header sticky.
- Gráficos: tema Plotly centralizado (`apps/dash/plotly_theme.py`) a partir de tokens.
- Responsive baseline en `apps/dash/assets/z-overrides.css` (no tocar `theme.css`).

### Convenciones clave
- No editar `apps/dash/assets/theme.css`; se regenera desde `design/tokens.json` con `python scripts/tokens_to_css.py`.
- Estilos manuales y media queries: `apps/dash/assets/z-overrides.css`.
- Contenedores homogéneos: `card(title, body, footer, variant)`.
- Tokens-first: cualquier nuevo color/espaciado debería incorporarse a `design/tokens.json`.

### Iconografía (SVG)
- Preferir SVG inline sobre emoji para nitidez y control de color/tamaño.
- Ubicación sugerida: `design/icons/` y helper simple para inyectar SVG si es necesario.
- Tamaños recomendados: 16–20 px en títulos/acciones; 24–28 px en KPIs.
- Colores por tokens (`--color-primary`, `--color-muted`).

### Do / Don't (rápido)
- Do: usar `card(...)`, `plotly_template()` y `z-overrides.css` para estilos.
- Do: mantener responsive con las media queries existentes.
- Don't: editar `theme.css` a mano o introducir CSS inline.
- Don't: acoplar lógica de datos a UI; seguir usando `src/core/data_service.py`.

### Backlog inmediato
- Sustituir iconos por SVG (sidebar, KPIs, acciones).
- Afinar tema Plotly por tipo de gráfico.
- (Opcional) columnas low-priority ocultables en móvil.

---

## Runbook de Desarrollo (rápido)

1) Lanzar dashboard:
   - `pip install -r requirements/base.txt -r requirements/dash.txt`
   - (opcional) `python scripts/init_db.py`
   - `python apps/dash/app.py` → http://127.0.0.1:8050

2) Estructura UI:
   - Sidebar: controlar con `ui-store.sidebar_open`; botón ☰ en móvil.
   - Cards: `from apps.dash.components.ui import card`.
   - Gráficos: `template=plotly_template()`.

3) Dónde tocar:
   - Tokens: `design/tokens.json` → `python scripts/tokens_to_css.py`.
   - Overrides/Responsive: `apps/dash/assets/z-overrides.css`.
   - Datos: `src/core/data_service.py` (agnóstico de frontend).

4) QA manual rápida:
   - Desktop (≥1280): sidebar fijo; header completo; KPIs 2 columnas; cards correctos.
   - Tablet (992–1200): sidebar icon-only; tabla legible; KPIs 2 columnas.
   - Móvil (≤768): drawer sidebar; header compacto; KPIs 1 columna; tabla con scroll y header sticky.


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
