# CONTEXT.md

## 📊 Estado del Proyecto

### Pipeline de Datos
- **Extractor**: ✅ 35 tablas INE, 51 métricas
- **Processor**: ✅ 149,247 registros en DuckDB
- **Validación**: ✅ 100% contra fuentes INE

### Dashboard Streamlit
- **Base**: ✅ Funcionando en puerto 8505
- **Diseño**: 🔄 Migrando a Tesla Dashboard (Figma)
- **Problema actual**: Sidebar oscuro inventado, debe ser blanco

## 🎯 Sesión Actual

### Objetivo
Implementar diseño Tesla Analytics Dashboard desde Figma

### Bloqueador
- Sidebar implementado con fondo oscuro (#171A20)
- Diseño real tiene fondo blanco (#FFFFFF)

### Próximos pasos
1. Corregir tokens.json → sidebar blanco
2. Implementar KPI cards con mini-gráficos
3. Adaptar métricas a absentismo

## 🔧 Configuración Activa
- DB: `C:\dev\projects\absentismo-espana\data\analysis.db`
- Dashboard: http://localhost:8505
- Diseño: Ver `docs/DASHBOARD_DESIGN.md`

## 📝 Notas Relevantes
- Sistema de tokens implementado
- NO usar CSS inline
- Verificar siempre contra mockup antes de implementar