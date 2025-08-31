# Estructura Propuesta - App Streamlit Absentismo España

## 🎯 Objetivo Principal
Dashboard interactivo para analizar datos de absentismo laboral del INE y comparar con informes de referencia (Adecco, Randstad).

## 📊 Arquitectura de la Aplicación

### A. ESTRUCTURA DE NAVEGACIÓN (Pestañas)

```
┌─────────────────────────────────────────────────────────────┐
│                    ABSENTISMO LABORAL ESPAÑA                 │
├───────┬──────────┬────────────┬──────────┬────────┬────────┤
│ Vista │ Nacional │ Territorial│ Sectorial│ Temporal│Comparar│
│General│          │            │          │         │        │
└───────┴──────────┴────────────┴──────────┴────────┴────────┘
```

#### 1. **Vista General** 📈
- KPIs principales (cards)
- Resumen ejecutivo
- Alertas y tendencias clave
- Última actualización de datos

#### 2. **Análisis Nacional** 🇪🇸
- Métricas agregadas nacionales
- Desglose por tipo de ausencia
- Distribución de horas (pactadas, efectivas, no trabajadas)
- Comparación por tipo de jornada

#### 3. **Análisis Territorial** 🗺️
- Mapa interactivo de CCAA
- Ranking de comunidades
- Comparativas regionales
- Drill-down por provincia (si disponible)

#### 4. **Análisis Sectorial** 🏭
- Por sectores principales (Industria, Construcción, Servicios)
- Por secciones CNAE (21 categorías)
- Por divisiones CNAE (82 categorías)
- Heatmap de sectores vs métricas

#### 5. **Series Temporales** 📅
- Evolución histórica (2008-presente)
- Análisis de tendencias
- Estacionalidad
- Proyecciones

#### 6. **Comparativa** 🔍
- Comparación con Adecco
- Comparación con Randstad
- Benchmarking europeo (si disponible)
- Análisis de discrepancias

### B. SISTEMA DE FILTROS GLOBALES

```yaml
Filtros Superiores (Sidebar):
  Temporales:
    - Año: [2024, 2023, 2022, ...]
    - Trimestre: [T1, T2, T3, T4, Todos]
    - Rango personalizado: [fecha_inicio - fecha_fin]
    
  Geográficos:
    - Ámbito: [Nacional, CCAA, Comparar CCAA]
    - CCAA: [multiselect o "Todas"]
    
  Sectoriales:
    - Nivel CNAE: [Total, Sectores B-S, Secciones, Divisiones]
    - Sectores: [multiselect según nivel]
    
  Laborales:
    - Tipo Jornada: [Todas, Completa, Parcial]
    - Tipo Métrica: [multiselect de métricas disponibles]

Filtros Contextuales (por pestaña):
  - Específicos según el análisis
  - Opciones de visualización
  - Exportación de datos
```

### C. COMPONENTES REUTILIZABLES

```python
componentes/
├── metrics_cards.py      # KPIs en formato card
├── comparison_table.py   # Tablas comparativas
├── time_series_chart.py  # Gráficos temporales
├── ccaa_map.py           # Mapa interactivo
├── sector_heatmap.py     # Heatmap sectorial
├── data_filters.py       # Sistema de filtros
└── export_utils.py       # Exportación datos/PDF
```

## 📋 Plan de Construcción Progresivo

### FASE 1: Base y Primera Pestaña (2-3 días)
```
Sprint 1.1: Configuración inicial
- [ ] Setup proyecto Streamlit
- [ ] Conexión a DuckDB
- [ ] Sistema de caché básico
- [ ] Layout principal con tabs

Sprint 1.2: Vista General
- [ ] Diseño de KPIs cards
- [ ] Cálculo métricas principales
- [ ] Resumen ejecutivo automático
- [ ] Indicadores de actualización
```

### FASE 2: Análisis Nacional (2 días)
```
Sprint 2.1: Métricas nacionales
- [ ] Queries para agregados nacionales
- [ ] Tablas de distribución de horas
- [ ] Desglose por causas de absentismo

Sprint 2.2: Visualizaciones
- [ ] Gráficos de barras comparativos
- [ ] Pie charts de distribución
- [ ] Tablas interactivas
```

### FASE 3: Sistema de Filtros (2 días)
```
Sprint 3.1: Filtros globales
- [ ] Sidebar con filtros temporales
- [ ] Filtros geográficos
- [ ] Filtros sectoriales
- [ ] Aplicación de filtros a queries

Sprint 3.2: Persistencia y UX
- [ ] Guardar estado de filtros
- [ ] Reset de filtros
- [ ] Indicadores de filtros activos
```

### FASE 4: Análisis Territorial (3 días)
```
Sprint 4.1: Datos por CCAA
- [ ] Queries optimizadas por región
- [ ] Ranking de comunidades
- [ ] Comparativas regionales

Sprint 4.2: Visualización geográfica
- [ ] Mapa de España con métricas
- [ ] Tooltips informativos
- [ ] Drill-down interactivo
```

### FASE 5: Análisis Sectorial (2 días)
```
Sprint 5.1: Análisis por sectores
- [ ] Queries por nivel CNAE
- [ ] Agregaciones jerárquicas
- [ ] Comparativas sectoriales

Sprint 5.2: Visualizaciones sectoriales
- [ ] Heatmap sectores vs métricas
- [ ] Treemap de sectores
- [ ] Tablas pivotadas
```

### FASE 6: Series Temporales (2 días)
```
Sprint 6.1: Análisis temporal
- [ ] Queries históricas optimizadas
- [ ] Cálculo de tendencias
- [ ] Detección de estacionalidad

Sprint 6.2: Visualizaciones temporales
- [ ] Line charts interactivos
- [ ] Análisis YoY y QoQ
- [ ] Proyecciones básicas
```

### FASE 7: Comparativa Externa (3 días)
```
Sprint 7.1: Integración Adecco
- [ ] Mapeo de métricas Adecco
- [ ] Tablas comparativas
- [ ] Análisis de discrepancias

Sprint 7.2: Integración Randstad
- [ ] Mapeo de métricas Randstad
- [ ] Comparativa múltiple
- [ ] Recomendaciones automáticas
```

### FASE 8: Optimización y Polish (2 días)
```
Sprint 8.1: Performance
- [ ] Optimización de queries
- [ ] Caché avanzado
- [ ] Lazy loading

Sprint 8.2: UX/UI
- [ ] Temas y estilos
- [ ] Responsividad
- [ ] Exportación PDF/Excel
- [ ] Documentación usuario
```

## 🚀 Orden de Implementación Recomendado

### Semana 1
1. **Día 1-2**: Setup + Vista General básica
2. **Día 3-4**: Análisis Nacional completo
3. **Día 5**: Sistema de filtros básicos

### Semana 2
4. **Día 6-7**: Análisis Territorial
5. **Día 8-9**: Análisis Sectorial
6. **Día 10**: Integración y testing

### Semana 3
7. **Día 11-12**: Series Temporales
8. **Día 13-14**: Comparativa Adecco/Randstad
9. **Día 15**: Optimización y deployment

## 🔧 Stack Técnico

```yaml
Frontend:
  - Streamlit 1.28+
  - Plotly para gráficos interactivos
  - Folium para mapas
  - AgGrid para tablas avanzadas

Backend:
  - DuckDB para queries
  - Pandas para manipulación
  - NumPy para cálculos
  - Scikit-learn para proyecciones

Utilidades:
  - streamlit-extras para componentes
  - st_pages para navegación
  - xlsxwriter para exports
  - reportlab para PDF
```

## 📦 Estructura de Archivos Propuesta

```
streamlit_app/
├── app.py                    # Aplicación principal
├── config.py                 # Configuración
├── requirements.txt          # Dependencias
│
├── pages/                    # Pestañas
│   ├── 1_vista_general.py
│   ├── 2_nacional.py
│   ├── 3_territorial.py
│   ├── 4_sectorial.py
│   ├── 5_temporal.py
│   └── 6_comparativa.py
│
├── components/               # Componentes reutilizables
│   ├── __init__.py
│   ├── filters.py
│   ├── metrics.py
│   ├── charts.py
│   └── tables.py
│
├── data/                     # Capa de datos
│   ├── __init__.py
│   ├── connection.py
│   ├── queries.py
│   └── cache.py
│
├── utils/                    # Utilidades
│   ├── __init__.py
│   ├── formatters.py
│   ├── exporters.py
│   └── calculations.py
│
└── assets/                   # Recursos estáticos
    ├── styles.css
    ├── logo.png
    └── spain_regions.json
```

## 🎯 Métricas Clave a Mostrar

### Nivel 1 - KPIs Principales
- Tasa de absentismo general (%)
- Tasa de IT (%)
- Horas perdidas por trabajador
- Coste estimado del absentismo

### Nivel 2 - Métricas Detalladas
- Horas pactadas vs efectivas
- Distribución por causas
- Tendencias trimestrales
- Comparativas regionales/sectoriales

### Nivel 3 - Análisis Avanzado
- Correlaciones
- Estacionalidad
- Proyecciones
- Benchmarking

## 🎨 Consideraciones de Diseño

1. **Mobile-first**: Diseño responsivo
2. **Dark/Light mode**: Selector de tema
3. **Exportable**: Todos los datos descargables
4. **Interactivo**: Filtros dinámicos y drill-down
5. **Performance**: Caché y lazy loading
6. **Accesible**: WCAG 2.1 AA compliance

## ✅ Criterios de Éxito

- [ ] Carga inicial < 3 segundos
- [ ] Todas las métricas validadas vs fuente
- [ ] Exportación funcional a Excel/PDF
- [ ] Filtros intuitivos y rápidos
- [ ] Visualizaciones claras y accionables
- [ ] Comparativas Adecco/Randstad precisas