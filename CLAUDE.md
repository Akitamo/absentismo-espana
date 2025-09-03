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
- Overlay de diseño: en `Dashboard` hay un overlay con controles (mostrar, opacidad, zoom y offsets) para alinear la vista con el mockup base (`design/Diseño dashboardFIN.jpg`).
