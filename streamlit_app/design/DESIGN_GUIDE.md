# 📐 GUÍA DE DISEÑO - Dashboard Absentismo
**Última actualización:** 29-11-2024  
**Estado:** DOCUMENTO MAESTRO - USAR COMO ÚNICA REFERENCIA

---

## ⚠️ IMPORTANTE: LEER PRIMERO

### PRINCIPIOS FUNDAMENTALES
1. **NO INVENTAR DISEÑO** - Todo debe venir del mockup o CSS de Figma
2. **TOKENS PRIMERO** - Actualizar tokens.json, no crear CSS inline
3. **VERIFICAR SIEMPRE** - Comparar con mockup antes de implementar

### FUENTES DE VERDAD (en orden de prioridad)
1. **Mockups PNG** en `docs/design/mockups/Main.png` - DISEÑO VISUAL REAL
2. **CSS Figma** en `docs/design/figma_export.css` - VALORES EXACTOS
3. **tokens.json** en `streamlit_app/design/tokens.json` - SISTEMA DE DISEÑO

---

## 📸 DISEÑO REAL (del mockup Main.png)

### ESTRUCTURA GENERAL
- **Ancho total**: 1440px
- **Sidebar**: 280px (FONDO BLANCO/GRIS CLARO)
- **Contenido**: 1120px
- **Fondo general**: #F9F9F9

### SIDEBAR (CORREGIDO - del mockup real)
```
CARACTERÍSTICAS REALES:
- Fondo: BLANCO (#FFFFFF) o GRIS MUY CLARO
- Logo: TESLA (rojo #CC0000)
- Texto: OSCURO sobre fondo claro
- Items del menú:
  * Reports (con gráfico de líneas azul)
  * Library 
  * People
  * Activities
- Sección Support con:
  * Get Started
  * Settings
- Usuario al final (Sam Wheeler)
```

### HEADER PRINCIPAL
```
- Título: "Reports" (grande, negro)
- Botón Download (arriba derecha)
- 3 Filtros dropdown:
  * Timeframe: All-time
  * People: All
  * Topic: All
```

### KPI CARDS (3 superiores)
```
Card 1: Active Users
- Valor: 27/80
- Mini gráfico línea azul debajo

Card 2: Questions Answered
- Valor: 3,298
- Mini gráfico línea azul debajo

Card 3: Av. Session Length
- Valor: 2m 34s
- Mini gráfico línea azul debajo
```

### KPI CARDS (3 inferiores con %)
```
Card 1: Starting Knowledge
- Valor: 64%
- Mini gráfico línea azul
- Fondo blanco

Card 2: Current Knowledge
- Valor: 86%
- Mini gráfico línea azul
- Fondo blanco

Card 3: Knowledge Gain
- Valor: +34%
- Mini gráfico línea azul
- Fondo blanco
```

### GRÁFICO PRINCIPAL
```
- Título: "Activity"
- Tipo: Barras verticales
- Color: Azul (#1B59F8)
- Eje X: Meses (JAN, FEB, MAR...)
- Selector "Month" arriba derecha
```

### SECCIONES INFERIORES (2 columnas)

#### COLUMNA IZQUIERDA
**Weakest Topics** (temas débiles)
- Food Safety: 74% (barra naranja→roja)
- Compliance Basics: 52% (barra naranja→roja)
- Company Networking: 36% (barra naranja→roja)

**User Leaderboard**
- Lista con avatares, nombres y puntos
- Flechas verdes/rojas indicando cambio

#### COLUMNA DERECHA
**Strongest Topics** (temas fuertes)
- Covid Protocols: 95% (barra verde)
- Cyber Security: 92% (barra verde)
- Social Media: 89% (barra verde)

**Groups Leaderboard**
- Similar al User Leaderboard

---

## 🎨 COLORES EXACTOS (del CSS Figma)

```json
{
  "backgrounds": {
    "main": "#F9F9F9",      // Fondo general
    "surface": "#FFFFFF",    // Cards y sidebar
    "divider": "rgba(0,0,0,0.1)"
  },
  "text": {
    "primary": "#000000",    // Títulos y valores
    "secondary": "#696974",  // Subtítulos
    "muted": "#808080"       // Texto deshabilitado
  },
  "accents": {
    "primary": "#1B59F8",    // Azul principal
    "success": "#1FE08F",    // Verde (positivo)
    "danger": "#FF3E13",     // Rojo (negativo)
    "tesla_red": "#CC0000"   // Logo Tesla
  }
}
```

---

## 🚫 ERRORES A EVITAR

1. **NO hacer el sidebar oscuro** - Es BLANCO/GRIS CLARO
2. **NO inventar colores** - Usar solo los del CSS Figma
3. **NO crear CSS inline** - Actualizar tokens.json primero
4. **NO añadir elementos** que no estén en el mockup

---

## ✅ PROCESO CORRECTO DE IMPLEMENTACIÓN

### PASO 1: Verificar en mockup
- Abrir `docs/design/mockups/Main.png`
- Identificar el componente exacto

### PASO 2: Buscar valores en CSS Figma
```bash
# Buscar en el CSS de Figma
grep "nombre_componente" docs/design/figma_export.css
```

### PASO 3: Actualizar tokens.json
```json
// streamlit_app/design/tokens.json
{
  "colors": {
    // Actualizar aquí primero
  }
}
```

### PASO 4: Regenerar theme.py
- El CSS debe generarse desde los tokens
- NO hardcodear valores

### PASO 5: Verificar resultado
- Comparar con mockup
- Ajustar si es necesario

---

## 📝 CHECKLIST ANTES DE IMPLEMENTAR

- [ ] ¿Revisé el mockup Main.png?
- [ ] ¿Busqué los valores en figma_export.css?
- [ ] ¿Actualicé tokens.json?
- [ ] ¿El CSS se genera desde tokens?
- [ ] ¿Se parece al diseño original?

---

## 🔄 ESTADO ACTUAL (29-11-2024)

### ✅ Completado
- Sistema de tokens básico
- Estructura de archivos

### ❌ ERRORES IMPLEMENTADOS (a corregir)
- Sidebar con fondo oscuro (debe ser claro)
- Colores inventados no del diseño
- CSS inline en lugar de tokens

### ⏳ Pendiente
- Corregir sidebar al diseño real
- Implementar KPI cards con mini-gráficos
- Ajustar gráfico principal
- Añadir rankings y leaderboards

---

## 📌 NOTAS PARA LA PRÓXIMA SESIÓN

1. **PRIMERO**: Corregir el sidebar (fondo claro, logo Tesla)
2. **SEGUNDO**: Ajustar KPI cards al diseño exacto
3. **TERCERO**: Implementar gráfico de barras azul
4. **SIEMPRE**: Verificar con mockup antes de codear