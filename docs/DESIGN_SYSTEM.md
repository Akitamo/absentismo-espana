# DESIGN_SYSTEM.md

Fecha actualización: 03-09-2025
Propósito: especificaciones de diseño y pautas de implementación del dashboard en Dash.

---

## Regla Fundamental
1) Siempre validar contra mockups antes de implementar.
2) Siempre usar valores de `design/tokens.json` (tokens-first).
3) Sin CSS inline: solo clases + variables CSS en `apps/dash/assets/theme.css`.
4) No inventar elementos ajenos al diseño ni colores fuera de tokens.

---

## Inventario de Assets
- `design/tokens.json`: fuente de verdad de colores, tipografías, espaciados, radios, sombras.
- `apps/dash/assets/theme.css`: generado desde tokens (no editar a mano).
- `apps/dash/assets/z-overrides.css`: overrides manuales (sí editar aquí).
- `docs/CSS DISEÑO ABSENTISMO.txt`: referencia de export de Figma (no usar directamente).
- Mockups (imágenes/PDF en docs/): guía visual de layouts, estados y componentes.

---

## Tokens → CSS Variables
Ejemplo de mapeo en `theme.css`:
```
:root {
  --color-primary: #1B59F8;
  --color-success: #1FE08F;
  --color-danger:  #FF3E13;
  --color-surface: #FFFFFF;
  --color-border:  #ECECEC;
  --text-primary:  #000000;
  --text-secondary:#696974;

  --radius-xl: 20px;
  --spacing-lg: 16px;
  --card-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
```

No añadir variables ad-hoc sin actualizarlas en `tokens.json`.

Variables adicionales de layout:
```
:root {
  --sidebar-w: 240px;   /* ancho fijo de la barra lateral */
  --card-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06);
}
```

---

## Convenciones de Layout y Clases
### Shell
- `.sidebar`: fijo a la izquierda; navegación en columna; logo en cabecera.
- `.content`: desplazada (`margin-left: var(--sidebar-w)`).
- `.header`: barra fija superior (ancho completo a la derecha del sidebar).
  - `.topbar-inner`: contenedor interno con título, búsqueda, acciones y chip de usuario.
Estructura de una página tipo (Dashboard):
- `.page`: contenedor principal vertical.
- `.filters`: fila con 3 filtros (`Periodo`, `CCAA`, `Sector`).
- `.kpi-grid`: grid responsivo de 3–6 KPIs.
- `.kpi-card`: tarjeta KPI (título, valor, subtítulo opcional).
- `.main`: área con `dcc.Graph` y `dash_table.DataTable`.

Estilos base (sugerencia en overrides):
```
.filters { display:flex; gap:12px; margin: 8px 0 16px; }
.filter  { min-width: 220px; }
.kpi-grid { display:grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap:12px; }
.kpi-card { background: var(--color-surface); border:1px solid var(--color-border); border-radius: var(--radius-xl); box-shadow: var(--card-shadow); padding: var(--spacing-lg); }
.kpi-title{ color: var(--text-secondary); font-size: 12px; margin-bottom: 6px; }
.kpi-value{ color: var(--text-primary);  font-size: 22px; font-weight: 600; }
.kpi-subtitle{ color: var(--text-secondary); font-size: 11px; }
```

---

## Patrones de Implementación (Dash)
- IDs estables y legibles: `f-periodo`, `f-ccaa`, `f-sector`, `ranking-table`, `evolucion`.
- Callbacks puros: sin `print`/IO en callback; log fuera o bajo condicional.
- Estado con `dcc.Store` cuando necesite persistir entre páginas o recomputar.
- Carga de datos con `src/core/data_service.py` (sin dependencias de UI).

Ejemplo de callback (resumen):
```
@callback(
  Output("kpis","children"), Output("evolucion","figure"),
  Output("ranking-table","data"), Output("ranking-table","columns"),
  Input("f-periodo","value"), Input("f-ccaa","value"), Input("f-sector","value")
)
def update_dashboard(periodo, ccaa, sector):
    # Consultas vía DataService (KPI, evolución, ranking)
    ...
```

---

## Checklist de Implementación
- [ ] Verifiqué mockup de la vista.
- [ ] Usé valores desde `tokens.json` en `theme.css`.
- [ ] IDs consistentes y documentados.
- [ ] Callbacks con entradas/salidas mínimas necesarias.
- [ ] Sin CSS inline; clases reutilizables.
- [ ] Comprobé accesibilidad básica (contraste, tamaños, foco).

---

## Errores Comunes a Evitar
- Editar `theme.css` a mano (se regenera desde tokens).
- Duplicar estilos del shell (sidebar/header) en cada página.
- IDs poco descriptivos o inconsistentes.
- CSS inline.
- IDs duplicados o poco descriptivos en componentes.
- Calcular datos “grandes” dentro de callbacks sin cachear.
- Estilos embebidos en componentes (usar clases en `theme.css`).
- Dependencias circulares entre páginas/servicios.

---

## Flujo de Trabajo Propuesto
1) Definir estructura de la página y IDs (wireframe).
2) Verificar tokens y añadir los que faltan en `design/tokens.json`.
3) Regenerar `theme.css` si cambian tokens; aplicar overrides en `apps/dash/assets/z-overrides.css`.
4) Implementar layout y callbacks mínimos.
5) Conectar con `DataService` y validar datos.
6) QA visual y funcional (navegación, filtros, responsiveness).

## Herramientas de apoyo
- Overlay de diseño en la página Dashboard: controles de mostrar/opacidad/zoom/offset para alinear con el mockup (`design/Diseño dashboardFIN.jpg`).

---

## Responsive Guidelines

Enfoque: `design/tokens.json` → `apps/dash/assets/theme.css` (autogenerado) + `apps/dash/assets/z-overrides.css` (media queries y layout). No editar `theme.css` a mano.

Breakpoints de referencia: `lg ≤1200`, `md ≤992`, `sm/xs ≤768` (aprox.).

- Shell
  - Sidebar: 240px desktop; 64px icon-only en ≤1200px (labels ocultas, tooltip por `title`). Drawer en ≤768px (planificado) con `dcc.Store`.
  - Header: fijo a la derecha del sidebar; buscador 520→380→100% según breakpoint.
  - Content: `margin-left: var(--sidebar-w)` coherente.

- Grids
  - Filtros: 3 cols desktop → 2 cols (`lg`) → 1 col (`sm/xs`).
  - KPI grid: 4 → 3 (`lg`) → 2 (`md`) → 1 (`sm/xs`).
  - Main: 2 columnas → 1 (`md`).

- Componentes
  - Dropdown (react-select): control mínimo 44px en táctil; menú con sombra y hover/selected.
  - DataTable: `overflow-x:auto` en `sm/xs`; cabecera sticky opcional; columnas de baja prioridad ocultables (futuro).
  - Gráficos: `width:100%`, altura 280–360px; reducir leyenda y márgenes en `sm/xs`.

- Accesibilidad
  - Objetivo 44×44 px en controles táctiles; focus visible; contraste texto secundario.

La implementación base de estos puntos está en `z-overrides.css` y se ampliará en la Fase 2 (drawer móvil) y posteriores.
