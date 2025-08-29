# CONTEXT.md

**Última actualización:** 29-11-2024 14:00

## 📊 Estado del Proyecto

### Pipeline de Datos
- **Extractor**: ✅ 35 tablas INE, 51 métricas
- **Processor**: ✅ 149,247 registros en DuckDB
- **Validación**: ✅ 100% contra fuentes INE

### Dashboard Streamlit
- **Puerto**: 8506
- **Sidebar**: ✅ Rediseñado con logo Ibermutua, tema claro
- **Visualizaciones**: ✅ Sistema modular implementado

## 🎯 Último Sprint Completado

### Sistema Modular de Visualizaciones
- ✅ Arquitectura base con `BaseVisualization`
- ✅ Registry central para registro de charts
- ✅ Container estándar para diseño consistente
- ✅ 2 visualizaciones Plotly funcionando
- ✅ Integración con tokens.json

## 🚀 Próximos Pasos
1. Conectar visualizaciones con datos reales DuckDB
2. Implementar más tipos: barras, heatmaps, mapas
3. Agregar Altair y ECharts como librerías
4. Crear galería de visualizaciones

## 🔧 Para Agregar Nueva Visualización
1. Crear clase en `visualizations/charts/`
2. Heredar de `BaseVisualization`
3. Registrar en `registry.py`
4. Usar: `get_visualization('nombre', data, config)`

## 📝 Reglas Críticas
- **NUNCA hardcodear estilos** - usar tokens.json
- **SIEMPRE heredar de BaseVisualization**
- **Registrar todas las visualizaciones**