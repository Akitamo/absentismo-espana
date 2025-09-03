# CLAUDE.md

Contexto estable y reglas para trabajar con este repositorio.

## Visión General
AbsentismoEspana: sistema modular para extraer, procesar y visualizar datos de absentismo (INE, ETCL).

## Frontend: Dash
- apps/dash/app.py: arranque y navegación (`use_pages=True`).
- apps/dash/pages/: páginas (`dashboard.py`, `analisis.py`, `comparativas.py`, `exportar.py`).
- apps/dash/assets/theme.css: estilos generados desde tokens.
- design/tokens.json: fuente de verdad del diseño.
- src/core/data_service.py: servicio de datos (DuckDB), agnóstico del frontend.

## Cómo ejecutar (resumen)
- pip install -r requirements/base.txt -r requirements/dash.txt
- Configurar `.env` con `APP_DB_PATH=data/analysis.db` (o ruta absoluta)
- python apps/dash/app.py  → http://127.0.0.1:8050
- Guía: apps/dash/README.md

## Mapa de Documentación (consulta frecuente)
- docs/DESIGN_SYSTEM.md: especificaciones de UI/UX y tokens para Dash.
- docs/DATA_LESSONS_LEARNED.md: lecciones de procesamiento de datos.
- CONTEXT.md: estado actual, próximos pasos, enlaces operativos.
- docs/LECCIONES_APRENDIDAS_DUPLICADOS.md: pauta para evitar duplicados del TOTAL (fuente_tabla).

## Reglas Fundamentales (Dash)
- Sin CSS inline: usar clases y variables en `apps/dash/assets/theme.css` derivadas de `design/tokens.json`.
- IDs y estado: IDs estables; estado global/local con `dcc.Store`; nada de `st.session_state`.
- Callbacks: `@callback` con `Input`, `Output` y `State`; sin efectos laterales inesperados.
- Datos: usar `src/core/data_service.py`; no dependencias de Streamlit en `main`.
- Diseño: tokens-first; si no existe un valor en tokens, proponlo antes de codificar.

## Histórico
- La implementación anterior en Streamlit está archivada en la rama `archive/streamlit-final` (tag `v0.1-streamlit`). No mezclar código o patrones de Streamlit en `main`.
