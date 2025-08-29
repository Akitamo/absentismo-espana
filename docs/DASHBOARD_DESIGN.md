# DASHBOARD_DESIGN.md

**Fecha creación:** 29-11-2024  
**Propósito:** Documentación completa del diseño y estilo del Dashboard de Absentismo

---

## 🎨 FUENTES DE DISEÑO (Orden de Prioridad)

### 1. Mockup Visual (Referencia Visual)
- **Archivo**: `docs/design/mockups/Main.png`
- **Uso**: Verificar apariencia visual exacta
- **Contenido**: Dashboard completo estilo Tesla Analytics

### 2. CSS Figma (Valores Exactos)
- **Archivo**: `docs/design/figma_export.css`
- **Uso**: Extraer valores exactos (colores, tamaños, fuentes)
- **Contenido**: 7000+ líneas de CSS con especificaciones precisas

### 3. Sistema de Tokens (Implementación)
- **Archivo**: `streamlit_app/design/tokens.json`
- **Uso**: Sistema de diseño implementado
- **IMPORTANTE**: DEBE reflejar valores de figma_export.css

---

## 🚫 REGLA FUNDAMENTAL

### NUNCA INVENTAR DISEÑO
1. **SIEMPRE** verificar primero en el mockup
2. **SIEMPRE** buscar valores en figma_export.css
3. **SIEMPRE** actualizar tokens.json antes de CSS
4. **NUNCA** crear estilos inline
5. **NUNCA** asumir colores o estilos

---

## 🎨 DISEÑO REAL (del mockup Main.png)

### Estructura General
- **Ancho total**: 1440px
- **Sidebar**: 280px ancho
- **Contenido principal**: 1120px
- **Fondo general**: #F9F9F9

### Sidebar (DISEÑO CORRECTO)
```css
/* Del figma_export.css línea 3739 */
background: #FFFFFF;  /* BLANCO, NO oscuro */
```

**Características reales:**
- **Fondo**: BLANCO (#FFFFFF) 
- **Logo**: TESLA rojo (#E51837)
- **Texto**: OSCURO sobre fondo claro (rgba(0, 0, 0, 0.7))
- **Hover**: Fondo azul claro (rgba(27, 89, 248, 0.1))
- **Items del menú**:
  * Reports (con gráfico azul)
  * Library 
  * People
  * Activities
- **Sección Support**:
  * Get Started
  * Settings
- **Usuario al final**: Sam Wheeler con foto

### Header Principal
- **Título**: "Reports" (grande, negro)
- **Botón**: "Download" (arriba derecha)
- **3 Filtros dropdown**:
  * Timeframe: All-time
  * People: All
  * Topic: All

### KPI Cards (6 métricas principales)
**Fila superior:**
1. Active Users: 27/80
2. Questions Answered: 3,298
3. Av. Session Length: 2m 34s

**Fila inferior:**
1. Starting Knowledge: 64%
2. Current Knowledge: 86%
3. Knowledge Gain: +34%

**Características:**
- Fondo blanco
- Mini gráfico línea azul debajo
- Sombra sutil
- Bordes redondeados (20px)

### Gráfico Principal
- **Título**: "Activity"
- **Tipo**: Barras verticales
- **Color**: Azul (#1B59F8)
- **Eje X**: Meses (JAN, FEB, MAR...)
- **Selector**: "Month" arriba derecha

### Secciones Inferiores (2 columnas)

**Columna Izquierda:**
- Weakest Topics (barras naranja→roja)
- User Leaderboard (con avatares)

**Columna Derecha:**
- Strongest Topics (barras verdes)
- Groups Leaderboard

---

## 🎨 PALETA DE COLORES (Valores Exactos)

```json
{
  "backgrounds": {
    "main": "#F9F9F9",        // Fondo general
    "surface": "#FFFFFF",      // Cards y sidebar
    "divider": "rgba(0,0,0,0.1)"
  },
  "text": {
    "primary": "#000000",      // Títulos
    "secondary": "#696974",    // Subtítulos
    "muted": "#808080",        // Deshabilitado
    "subtle": "rgba(0,0,0,0.5)" // Texto sutil
  },
  "accents": {
    "primary": "#1B59F8",      // Azul principal
    "success": "#1FE08F",      // Verde
    "danger": "#FF3E13",       // Rojo
    "tesla_red": "#E51837",    // Logo Tesla
    "warning": "#FFA500"       // Naranja
  },
  "charts": {
    "blue": "#1B59F8",
    "green": "#1FE08F",
    "red": "#FF3E13",
    "gradient_orange": "linear-gradient(143.13deg, #FFBF1A 5.36%, #FF4080 94.64%)",
    "gradient_green": "linear-gradient(270deg, #2FEA9B 15.5%, #7FDD53 85.5%)"
  }
}
```

---

## 📐 TIPOGRAFÍA

```json
{
  "fontFamily": "'Inter', -apple-system, sans-serif",
  "fontSize": {
    "xs": "0.75rem",   // 12px
    "sm": "0.875rem",  // 14px
    "base": "1rem",    // 16px
    "lg": "1.125rem",  // 18px
    "xl": "1.5rem",    // 24px
    "2xl": "2rem",     // 32px
    "3xl": "2.5rem"    // 40px
  },
  "fontWeight": {
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700
  }
}
```

---

## 📦 COMPONENTES STREAMLIT

### Arquitectura de Componentes
```
streamlit_app/
├── app.py                  # Aplicación principal
├── design/
│   ├── tokens.json        # Sistema de diseño
│   ├── theme.py           # Generador de CSS desde tokens
│   └── DESIGN_GUIDE.md    # Guía rápida de diseño
├── pages/
│   └── dashboard.py       # Dashboard principal
├── components/
│   ├── sidebar.py         # Sidebar con navegación
│   ├── kpi_cards.py      # Cards de métricas
│   ├── charts.py          # Gráficos
│   └── filters.py         # Filtros superiores
└── utils/
    └── data_loader.py     # Conexión a DuckDB
```

### Proceso de Implementación

#### PASO 1: Verificar en mockup
```bash
# Abrir docs/design/mockups/Main.png
# Identificar el componente exacto
```

#### PASO 2: Buscar valores en CSS
```bash
grep "sidebar\|navigation" docs/design/figma_export.css
```

#### PASO 3: Actualizar tokens.json
```json
// streamlit_app/design/tokens.json
{
  "colors": {
    "sidebar_bg": "#FFFFFF"  // Valor del CSS
  }
}
```

#### PASO 4: Regenerar theme.py
```python
def apply_theme():
    tokens = load_tokens()
    css = generate_css_from_tokens(tokens)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

#### PASO 5: Verificar resultado
- Comparar con mockup
- Ajustar si necesario

---

## ⚠️ ERRORES COMUNES A EVITAR

### 1. Sidebar Oscuro (ERROR FRECUENTE)
❌ **INCORRECTO**:
```json
"sidebar_bg": "#171A20"  // Oscuro inventado
```

✅ **CORRECTO**:
```json
"sidebar_bg": "#FFFFFF"  // Blanco del diseño real
```

### 2. CSS Inline
❌ **INCORRECTO**:
```python
st.markdown('<div style="color: red">...</div>')
```

✅ **CORRECTO**:
```python
# Actualizar tokens.json y usar clases CSS
```

### 3. Inventar Elementos
❌ **INCORRECTO**: Añadir elementos que no están en el mockup
✅ **CORRECTO**: Solo implementar lo que aparece en el diseño

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

Antes de implementar cualquier componente:

- [ ] ¿Revisé el mockup Main.png?
- [ ] ¿Busqué los valores en figma_export.css?
- [ ] ¿Actualicé tokens.json con valores reales?
- [ ] ¿El CSS se genera desde tokens?
- [ ] ¿Se parece al diseño original?
- [ ] ¿Evité crear estilos inline?

---

## 🚀 ESTADO ACTUAL DEL DASHBOARD

### ✅ Completado
- Sistema de tokens básico
- Estructura de archivos
- Dashboard básico funcionando
- Conexión a base de datos

### ❌ Errores Implementados (a corregir)
- Sidebar con fondo oscuro (debe ser blanco)
- Colores inventados no del diseño
- CSS inline en lugar de tokens

### ⏳ Pendiente
- Corregir sidebar al diseño real (fondo blanco)
- Implementar KPI cards con mini-gráficos
- Ajustar gráfico principal de barras
- Añadir rankings y leaderboards
- Adaptar a datos de absentismo

---

## 📌 PRÓXIMOS PASOS

1. **URGENTE**: Corregir sidebar (fondo blanco #FFFFFF)
2. Implementar KPI cards exactas del diseño
3. Crear gráfico de barras azul
4. Adaptar textos y métricas a absentismo
5. Verificar todo contra mockup

---

## 🔧 COMANDOS ÚTILES

```bash
# Ejecutar dashboard
cd streamlit_app
streamlit run app.py

# Ver en navegador
http://localhost:8505

# Tomar screenshot (cuando Playwright esté instalado)
python take_screenshot.py

# Limpiar caché de Streamlit
streamlit cache clear
```

---

## 📝 NOTAS IMPORTANTES

- **Token-first approach**: Siempre actualizar tokens.json primero
- **No hardcodear**: Todos los valores deben venir de tokens
- **Verificar siempre**: Comparar con mockup antes de dar por terminado
- **Documentar cambios**: Actualizar este archivo con nuevos componentes