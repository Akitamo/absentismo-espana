# DESIGN_SYSTEM.md

**Fecha actualización:** 31-12-2024  
**Propósito:** Documento unificado con TODAS las especificaciones de diseño del dashboard

---

## 🎯 REGLA FUNDAMENTAL: NUNCA INVENTAR DISEÑO

1. **SIEMPRE** verificar en mockups antes de implementar
2. **SIEMPRE** usar valores de tokens.json
3. **NUNCA** CSS inline - solo clases y variables CSS
4. **NUNCA** crear elementos que no estén en el diseño

---

## 📂 INVENTARIO DE ASSETS

### Ubicación de Recursos
```
📁 docs/
├── 📄 CSS DISEÑO ABSENTISMO.txt      # CSS exportado de Figma (7000+ líneas)
├── 📁 design/
│   ├── mockups/
│   │   └── Main.png                  # Mockup principal de referencia
│   └── figma_export.css              # CSS completo de Figma
└── 📁 Analytics Dashboard DESIGN/     # Assets visuales del diseño
```

### Mockup Principal (Main.png)
- **Dimensiones**: 1440x1162px
- **Sidebar**: 280px ancho, fondo BLANCO (#FFFFFF)
- **Contenido**: 1120px ancho
- **Fondo general**: #F9F9F9

---

## 🎨 SISTEMA DE TOKENS

### Ubicación y Uso
- **Archivo**: `streamlit_app/design/tokens.json`
- **Aplicación**: `streamlit_app/design/theme.py`
- **REGLA**: Todos los valores deben venir de tokens

### Estructura de Tokens
```json
{
  "colors": {
    "primary": "#1B59F8",
    "surface": "#FFFFFF",
    "sidebar_bg": "#FFFFFF",    // BLANCO, no oscuro
    "background": "#F9F9F9"
  },
  "typography": {
    "fontFamily": "'Inter', sans-serif",
    "fontSize": { /* xs hasta 3xl */ }
  },
  "spacing": { /* xs hasta 2xl */ },
  "borders": { /* radius sm hasta 2xl */ },
  "shadows": { /* sm hasta xl */ }
}
```

---

## 🏗️ ARQUITECTURA DE COMPONENTES

### Sistema Modular de Visualizaciones

#### 1. Container con Slots (OBLIGATORIO)
```python
# Estructura de slots para TODA visualización:
container = ChartContainer(viz_id="unique_id")

with container.header(title, subtitle):
    # Título y subtítulo
    
with container.controls():
    # Filtros y controles locales
    
with container.body():
    # Visualización principal
    
with container.footer():
    # Metadatos o información adicional
```

#### 2. BaseVisualization (OBLIGATORIO heredar)
- Gestión automática de tokens
- Namespacing de estado con `viz:{id}`
- Métodos: `get_state()`, `set_state()`, `clear_state()`

#### 3. Registry Central
- Registro: `register_visualization('nombre', ClaseViz)`
- Uso: `get_visualization('nombre', data, config, viz_id)`

#### 4. Página Galería (QA Visual)
- Ubicación: `streamlit_app/pages/03_galeria.py`
- Auto-discovery de todas las visualizaciones
- Testing visual con datos de muestra

---

## 🎨 DISEÑO VISUAL REAL (del Mockup)

### Estructura General
1. **Header Principal**
   - Título "Reports" grande
   - Botón "Download" arriba derecha
   - 3 filtros dropdown

2. **KPI Cards** (6 métricas)
   - Fondo blanco con sombra sutil
   - Mini gráfico línea azul debajo
   - Bordes redondeados (20px)

3. **Gráfico Principal**
   - Tipo: Barras verticales
   - Color: Azul (#1B59F8)
   - Título: "Activity"

4. **Sidebar** (IMPORTANTE: FONDO BLANCO)
   - Logo Tesla rojo (#E51837)
   - Texto oscuro sobre fondo claro
   - Hover: fondo azul claro rgba(27, 89, 248, 0.1)

### Paleta de Colores Exacta
```json
{
  "primary": "#1B59F8",      // Azul principal
  "success": "#1FE08F",      // Verde
  "danger": "#FF3E13",       // Rojo
  "tesla_red": "#E51837",    // Logo
  "text_primary": "#000000",
  "text_secondary": "#696974"
}
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

Antes de implementar CUALQUIER componente:

- [ ] ¿Revisé el mockup Main.png?
- [ ] ¿Los valores están en tokens.json?
- [ ] ¿Uso ChartContainer con slots?
- [ ] ¿Heredé de BaseVisualization?
- [ ] ¿Usé namespacing con viz_id?
- [ ] ¿Registré en registry.py?
- [ ] ¿Verifiqué en página Galería?
- [ ] ¿Sin CSS inline?

---

## ⚠️ ERRORES COMUNES A EVITAR

### ❌ INCORRECTO
```python
# CSS inline
st.markdown('<div style="color: red">...</div>')

# Sidebar oscuro inventado
"sidebar_bg": "#171A20"

# Sin slots
st.plotly_chart(fig)

# Sin namespacing
st.session_state['filter'] = value
```

### ✅ CORRECTO
```python
# Clases CSS con tokens
st.markdown('<div class="chart-header">...</div>')

# Sidebar blanco del diseño
"sidebar_bg": "#FFFFFF"

# Con slots
with container.body():
    container.render_visualization(fig, 'plotly')

# Con namespacing
viz.set_state('filter', value)
```

---

## 🔧 FLUJO DE TRABAJO

### Para Crear Nueva Visualización:

1. **Crear clase** en `visualizations/charts/mi_chart.py`
```python
class MiChart(BaseVisualization):
    def __init__(self, data, config=None, viz_id=None):
        super().__init__(data, config, viz_id)
```

2. **Implementar render()**
```python
def render(self):
    # Usar self.tokens para colores
    # Usar self.get_state() para valores
    return figura
```

3. **Registrar** en `registry.py`
```python
register_visualization('mi_chart', MiChart)
```

4. **Usar** en dashboard
```python
container = ChartContainer("mi_viz_1")
with container.body():
    viz = get_visualization('mi_chart', data, config, "mi_viz_1")
    chart = viz.render()
    container.render_visualization(chart, viz.get_library())
```

5. **Verificar** en Galería (`/pages/03_galeria.py`)

---

## 🎯 ARQUITECTURA DE CARDS (SOLUCIÓN FINAL)

### Problema: No-Wrapping en Streamlit
Streamlit no permite envolver sus componentes nativos (st.plotly_chart, st.dataframe) en HTML custom. Los intentos con divs fallan porque el contenido se renderiza fuera.

### Solución Adoptada: Containers Nativos
Usar `st.container(border=True)` con CSS mínimo y estable.

#### Componente Card (`components/native_card.py`)
```python
from contextlib import contextmanager

@contextmanager
def card(title: str | None = None, subtitle: str | None = None):
    c = st.container(border=True)  # nativo
    with c:
        if title: st.markdown(f"### {title}")
        if subtitle: st.caption(subtitle)
        yield
```

#### CSS Estable (`design/theme.py`)
```css
/* Un solo selector, estable para Streamlit 1.30+ */
.stContainer > div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    box-shadow: var(--card-shadow);
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
}
```

#### Uso en Dashboard
```python
from components.native_card import card

with card("📊 Evolución Temporal", "Tasa trimestral"):
    st.plotly_chart(fig, use_container_width=True)

with card("🏆 Ranking CCAA", "Top 10"):
    st.dataframe(df, use_container_width=True)
```

### Principios Aplicados
1. **No hacks**: Sin `:has()`, `[style*="border"]`, o marcadores invisibles
2. **Tokens-first**: Todos los valores desde `tokens.json`
3. **Mínimo CSS**: Un selector específico y estable
4. **Nativo**: Usar lo que Streamlit proporciona

### Si Necesitas Fidelidad 100%
Para replicar exactamente el template Tesla, la única opción es crear un **componente React custom** que renderice los gráficos internamente (pasando `fig.to_json()`).

---

## 📌 REFERENCIAS RÁPIDAS

- **Mockup principal**: `docs/design/mockups/Main.png`
- **CSS Figma**: `docs/design/figma_export.css`
- **Tokens**: `streamlit_app/design/tokens.json`
- **Container**: `streamlit_app/components/chart_container.py`
- **Base clase**: `streamlit_app/visualizations/base.py`
- **Galería QA**: `streamlit_app/pages/03_galeria.py`

---

## 🚀 COMANDOS ÚTILES

```bash
# Ejecutar dashboard
cd streamlit_app
streamlit run app.py

# Puerto por defecto
http://localhost:8505

# Página Galería
http://localhost:8505/galeria
```

---

## 📦 EXPERIMENTAL: Custom Component UI Card

> ⚠️ **NOTA**: Esta es una prueba experimental (2025-01-02) para evaluar viabilidad de componentes custom.
> Si se descarta, eliminar esta sección completa.

### Componente UI Card
- **Ubicación**: `streamlit_app/components/ui_card/`
- **Tecnología**: React + TypeScript + Vite + streamlit-component-lib
- **Demo**: `pages/100_Demo_UI_Card.py` (puerto 8512)
- **Comparación**: `pages/99_Demo_CRM.py` (versión nativa)

### Ventajas observadas
- Control pixel-perfect del renderizado
- Sombras y bordes consistentes
- Integración Plotly dentro del card
- Hover effects nativos
- Independiente del DOM de Streamlit

### Problemas resueltos
- No más dependencia de selectores CSS frágiles
- Renderizado consistente entre recargas
- Control total sobre estilos y comportamiento

### Compilación del componente
```bash
cd streamlit_app/components/ui_card/frontend
npm install
npm run build
```

### Decisión pendiente
- [ ] Adoptar para todo el proyecto
- [ ] Descartar y volver a containers nativos
- [ ] Híbrido: usar solo para casos críticos