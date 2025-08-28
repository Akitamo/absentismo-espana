# Streamlit App - Absentismo Laboral España

## 🚀 Sprint 1 Completado

### Instalación y Ejecución

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá en: http://localhost:8501

## ✅ Funcionalidades Implementadas (Sprint 1)

### 1. **Estructura Base**
- ✓ Configuración de página wide layout
- ✓ Sistema de 6 pestañas (Vista General activa, resto placeholders)
- ✓ CSS personalizado para mejor UX
- ✓ Footer con información de actualización

### 2. **Conexión a Base de Datos**
- ✓ Conexión a DuckDB con caché de recursos
- ✓ Queries optimizadas con caché TTL de 1 hora
- ✓ Información de BD en sidebar (registros, periodos, etc.)

### 3. **Vista General - KPIs Principales**
- ✓ **Tasa de Absentismo General** con delta vs periodo anterior
- ✓ **Tasa de IT** (Incapacidad Temporal)
- ✓ **Horas No Trabajadas** totales
- ✓ **Horas Perdidas Anualizadas** (proyección)

### 4. **Métricas Secundarias**
- ✓ Horas Pactadas
- ✓ Horas Efectivas
- ✓ Horas Extraordinarias

### 5. **Visualizaciones**
- ✓ **Gráfico de barras** con distribución de horas
- ✓ **Gauge chart** para tasa de absentismo con zonas de color
- ✓ **Tabla resumen** con métricas principales

### 6. **Filtros Básicos**
- ✓ Selector de periodo (trimestre/año)
- ✓ Información de base de datos en sidebar
- ✓ Expander con información sobre los datos

## 📊 Estructura de Datos

La app consume datos de la tabla `observaciones_tiempo_trabajo` con:
- **149,247** registros totales
- **68** periodos (2008T1 - 2025T1)
- **17** CCAA + Total Nacional
- **5** métricas principales de tiempo de trabajo

## 🎯 KPIs Mostrados

1. **Tasa de Absentismo** = (Horas no trabajadas / Horas pactadas) × 100
2. **Tasa de IT** = (Horas IT / Horas pactadas) × 100
3. **Horas No Trabajadas** = Suma de todas las ausencias
4. **Horas Perdidas Anualizadas** = HNT trimestre × 4

## 🔄 Sistema de Caché

- `@st.cache_resource`: Conexión a BD (persistente)
- `@st.cache_data(ttl=3600)`: Queries con TTL de 1 hora
- Recarga automática cada hora para datos frescos

## 📁 Estructura de Archivos

```
streamlit_app/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias Python
└── README.md          # Esta documentación
```

## 🚦 Próximos Pasos (Sprint 2)

1. **Análisis Nacional Completo**
   - Desglose por causas de absentismo
   - Comparación por tipo de jornada
   - Gráficos adicionales

2. **Sistema de Filtros Avanzados**
   - Filtro de rango de fechas
   - Comparación entre periodos
   - Multi-selección de métricas

3. **Mejoras UX**
   - Dark mode
   - Exportación a Excel
   - Tooltips informativos

## 🐛 Problemas Conocidos

- Las tasas calculadas difieren de informes Adecco/Randstad (diferente metodología)
- Datos de CCAA solo disponibles para tabla 6063
- Sin datos de tamaño de empresa

## 📝 Notas Técnicas

- **Python**: 3.8+
- **Streamlit**: 1.28+
- **DuckDB**: 0.9+
- **Plotly**: 5.17+

## 📧 Soporte

Para problemas o sugerencias, crear issue en el repositorio.