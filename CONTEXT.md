# PROJECT STATUS - AbsentismoEspana

## 📅 Última actualización
**Fecha:** 2024-11-28 (actualizado)
**Sesión:** Problema de duplicados del TOTAL resuelto - Documentación actualizada con lecciones aprendidas

## 🔧 Agent Processor: VALIDADO Y FUNCIONAL ✅

### Implementado ✅

1. **Pipeline ETL completo**
   - `agent_processor/etl/extractor.py`: Lee CSVs con detección automática de encoding
   - `agent_processor/etl/transformer.py`: Mapea dimensiones y pivota métricas (con detección B_S)
   - `agent_processor/etl/loader.py`: Carga a DuckDB con validaciones
   - `agent_processor/processor.py`: Orquestador principal del pipeline
   
2. **Base de datos DuckDB**
   - Tabla: `observaciones_tiempo_trabajo` (25 campos - incluye metrica_codigo y metrica_ine)
   - Esquema validado contra diseño Excel v3 y documento de referencia
   - Datos completos: 149,247 registros (2008T1-2025T1) para las 6 tablas
   - Sin duplicados en clave primaria
   - Campo `rol_grano` funcionando para prevenir agregaciones incorrectas
   - Nuevos campos `metrica_codigo` y `metrica_ine` para trazabilidad completa

3. **Configuración completamente validada**
   - `agent_processor/config/mappings.json`: Mapeos desde exploración agosto 2025
   - Valores almacenados TAL CUAL del INE (151 = 151 horas, NO 15.1)
   - Mapeos de tipo_jornada, sectores CNAE, CCAA confirmados
   - **CORREGIDO**: Horas pagadas ≠ Horas efectivas (son métricas diferentes)
   - **CORREGIDO**: Mapeos B_S para tablas 6043, 6045, 6046
   - **CORREGIDO**: Formato CCAA con prefijos numéricos ("01 Andalucía")

### Validaciones Realizadas ✅

#### Resumen Consolidado de Validación (25-ago-2025)
**Estado Global: 100% ÉXITO - 1,918 comparaciones totales validadas**

| Tabla | Descripción | Comparaciones | Tasa Éxito | Problemas Resueltos |
|-------|-------------|---------------|------------|---------------------|
| 6042 | Nacional + Sectores B-S + Jornada | 48 | 100% | Ninguno |
| 6043 | Nacional + Secciones CNAE + Jornada | 285 | 100% | Mapeos secciones G y O corregidos |
| 6044 | Nacional + Sectores B-S (sin jornada) | 20 | 100% | Ninguno |
| 6045 | Nacional + Secciones CNAE (sin jornada) | 95 | 100% | Reutilizó fix de 6043 |
| 6046 | Nacional + Divisiones CNAE (sin jornada) | 390 | 100% | Ninguno |
| 6063 | CCAA + Sectores B-S + Jornada | 1,080 | 100% | Ninguno |

**Archivos de validación generados:**
- `data/exploration_reports/validation_report_consolidated.xlsx`: Reporte Excel con 4 hojas de análisis
- `data/exploration_reports/validation_summary.json`: Resumen estructurado en JSON
- Scripts consolidados en `agent_processor/scripts/`
- 6 reportes Excel detallados por tabla

### Lecciones Aprendidas 📚

1. **SIEMPRE consultar EXPLORACION_VALIDADA.md antes de validar**: Contiene TODOS los valores ya verificados
2. **Horas pagadas ≠ Horas efectivas**: Son métricas diferentes (pagadas > efectivas siempre)
3. **Valores TAL CUAL del INE**: 151 = 151 horas (NO dividir por 10)
4. **Campo `rol_grano` NO previene duplicados entre tablas**: Solo identifica granularidad, no evita que el mismo TOTAL aparezca en múltiples tablas
5. **Mapeos desde exploración**: No crear nuevos mapeos, usar los validados de agosto 2025
6. **Detección B_S automática**: Transformer detecta prefijo B_S como TOTAL
7. **Problemas de encoding en mapeos**: Secciones G y O requerían texto exacto con comas (no punto y coma)
8. **Validación exhaustiva funciona**: 1,918 comparaciones individuales garantizan calidad de datos
9. **Scripts de validación reutilizables**: Patrón común aplicable a todas las tablas INE
10. **NUNCA usar AVG/MAX/MIN para duplicados** (28-nov-2024): Los "duplicados" del TOTAL son por diseño del INE. Solución: filtrar por `fuente_tabla`
11. **Las tablas INE incluyen TOTAL por diseño**: Es para facilitar validación y referencia, no un error
12. **Soluciones SQL son chapuzas**: Siempre corregir en origen o usar dimensiones correctamente

## 🎉 Sprint 1 Streamlit Dashboard: COMPLETADO (28-nov-2024)

### Logros del Sprint 1:
1. ✅ **Aplicación Streamlit funcional** en `streamlit_app/app.py`
2. ✅ **Cálculos correctos de tasas de absentismo**:
   - Tasa Absentismo General: 7.43% (coincide con Adecco 7.4%)
   - Tasa IT: 5.76% (coincide con Adecco 5.8%)
3. ✅ **Metodología Adecco implementada exactamente**
4. ✅ **Problema de duplicados resuelto CORRECTAMENTE**: Filtro por `fuente_tabla='6042'`
5. ✅ **Problema de rutas resuelto**: Ruta absoluta a BD
6. ✅ **6 pestañas de análisis** estructuradas (contenido básico)
7. ✅ **Filtro por periodo** funcional

### Problemas resueltos durante Sprint 1:
- **Duplicados del TOTAL nacional** (28-nov-2024): 
  - CAUSA: Las 6 tablas INE (6042-6046, 6063) incluyen todas el mismo TOTAL nacional por diseño del INE
  - SOLUCIÓN CORRECTA: Filtrar por `fuente_tabla='6042'` para evitar sumar 6 veces el mismo valor
  - NUNCA usar AVG, MAX, MIN o DISTINCT como parche - filtrar por dimensiones correctas
  - Campo `rol_grano` NO previene este tipo de duplicados entre tablas
- **Escala incorrecta**: Los valores ya están en la escala correcta (no dividir por 10)
- **Nivel de agregación**: Usar cnae_nivel = 'TOTAL', no SECTOR_BS
- **Ruta de BD en Windows**: Debe ser absoluta `r"C:\dev\projects\absentismo-espana\data\analysis.db"`
- **Caché de Streamlit**: Eliminado @st.cache_resource de conexión para evitar problemas

### Próximos Pasos Sprint 2 🚀

1. ⏳ **PENDIENTE**: Completar contenido de las 6 pestañas con gráficos y análisis
2. ⏳ **PENDIENTE**: Añadir comparación temporal (trimestre vs trimestre anterior)
3. ⏳ **PENDIENTE**: Implementar análisis por sectores (B-E, F, G-S)
4. ⏳ **PENDIENTE**: Añadir análisis por CCAA (tabla 6063)
5. ⏳ **PENDIENTE**: Exportación a Excel/PDF de reportes
6. ✅ **COMPLETADO**: Cargar datos históricos completos (2008T1-2025T1) - ya están
7. ⏳ **PENDIENTE**: Crear vistas de análisis en DuckDB
8. 🔄 **EN PROCESO**: Actualizar repositorio GitHub

## ✅ Completado anteriormente

### 🎯 DISEÑO AGENT PROCESSOR FINALIZADO (20-ago-2025)

#### Estructura de Tabla Definitiva Validada
- [x] **Tabla única `observaciones_tiempo_trabajo`** con 23 campos definidos
- [x] **Solo 6 tablas INE** necesarias: 6042-6046 y 6063 (todas de tiempo trabajo)
- [x] **Granularidad heterogénea resuelta** con campo `rol_grano` y flags `es_total_*`
- [x] **Prevención doble conteo** garantizada por diseño
- [x] **Clave primaria robusta**: 8 campos que garantizan unicidad

#### Documentación de Diseño Completada
- [x] **Informe funcional Adecco/Randstad** analizado y validado
- [x] **Documento consolidación final** (`Consolidacion_Final_ETCL_Absentismo.md`) revisado
- [x] **Excel diseño v3** (`ETCL_6042_6063_diseno_tabla_v3.xlsx`) con 7 pestañas procesado:
  - Diccionario: 23 campos definidos
  - Dominios: Valores permitidos para cada campo
  - Validaciones: 16 reglas de negocio
  - Jerarquía CNAE: 4 niveles (TOTAL → SECTOR_BS → SECCION → DIVISION)
  - Cobertura: Mapeo de dimensiones por tabla
- [x] **Configuración completa extraída** a `config/procesador_config_completo.json`

#### Decisiones de Diseño Clave
1. **Métricas separadas**: `metrica` (4 tipos) + `causa` (9 tipos para HNT)
2. **Jornada NULL**: Cuando no existe (tablas 6044-6046) con flag `es_total_jornada`
3. **CCAA solo en 6063**: Limitación aceptada del INE
4. **Ceuta/Melilla con Andalucía**: Mantener decisión INE
5. **No mezclar niveles**: Validación estricta por `cnae_nivel` y `ambito_territorial`

#### Validaciones Confirmadas
- [x] **Identidad HE**: HE ≈ HP + HEXT - HNT_total (±0.5)
- [x] **Suma causas**: Σ(HNT por causa) ≈ HNT_total (±0.5)
- [x] **Unicidad clave**: Sin duplicados en primary key
- [x] **Completitud**: causa requerida si metrica='horas_no_trabajadas'
- [x] **Coherencia dimensional**: No sumar diferentes niveles

### 🎯 EXTRACCIÓN Y VALIDACIÓN DE MÉTRICAS COMPLETADA (19-ago-2025)
- [x] **Agent Extractor 100% completado**: Sistema de extracción validado y funcional
- [x] **51 métricas únicas extraídas** de las 35 tablas del INE
- [x] **112% de cobertura** de métricas directas (51/45.5 esperadas)
- [x] **Validación contra metodología oficial INE**

## 📊 ESTRUCTURA TABLA PROCESADA FINAL

### Campos Clave (Primary Key)
```
periodo + ambito_territorial + ccaa_codigo + cnae_nivel + cnae_codigo + tipo_jornada + metrica + causa
```

### Esquema Validado
| Campo | Tipo | Req | Descripción |
|-------|------|-----|-------------|
| periodo | VARCHAR(6) | SÍ | Trimestre YYYYTQ |
| ambito_territorial | ENUM | SÍ | NAC o CCAA |
| ccaa_codigo | VARCHAR(2) | NO | Código INE o NULL |
| ccaa_nombre | VARCHAR(50) | NO | Nombre CCAA o NULL |
| cnae_nivel | ENUM | SÍ | TOTAL, SECTOR_BS, SECCION, DIVISION |
| cnae_codigo | VARCHAR(5) | NO | Código CNAE o NULL |
| cnae_nombre | VARCHAR(200) | NO | Descripción sector |
| jerarquia_sector_cod | VARCHAR(50) | NO | Path: TOTAL>SECCION>C>DIVISION>10 |
| jerarquia_sector_lbl | VARCHAR(100) | NO | Path: Total>Sección C>División 10 |
| tipo_jornada | ENUM | NO | TOTAL, COMPLETA, PARCIAL, NULL |
| metrica | ENUM | SÍ | horas_pactadas, horas_pagadas, horas_efectivas, horas_extraordinarias, horas_no_trabajadas |
| causa | VARCHAR(30) | NO | 14 valores: vacaciones, festivos, it_total, maternidad_paternidad, permisos_retribuidos, razones_tecnicas_economicas, compensacion_extras, otras_remuneradas, perdidas_lugar_trabajo, conflictividad, otras_no_remuneradas, representacion_sindical, pagadas_agregado, no_pagadas_agregado, vacaciones_y_fiestas, NULL |
| valor | DECIMAL | SÍ | Valor numérico |
| unidad | VARCHAR | SÍ | horas/mes por trabajador |
| fuente_tabla | VARCHAR(4) | SÍ | 6042-6046, 6063 |
| es_total_ccaa | BOOLEAN | SÍ | TRUE si NAC |
| es_total_cnae | BOOLEAN | SÍ | TRUE si TOTAL |
| es_total_jornada | BOOLEAN | SÍ | TRUE si NULL o TOTAL |
| rol_grano | VARCHAR(30) | SÍ | Identificador único grano |
| metrica_codigo | VARCHAR(10) | SÍ | Código estándar (HP, HE, HNTRa, etc.) |
| metrica_ine | VARCHAR(150) | SÍ | Nombre exacto del INE |

### Métricas y Causas Definidas

**MÉTRICAS (5):**
- horas_pactadas → DENOMINADOR para tasas
- horas_pagadas → CONTEXTO (incluye pagadas no trabajadas)
- horas_efectivas → CONTEXTO (solo trabajadas)
- horas_extraordinarias → CONTEXTO  
- horas_no_trabajadas → Desglosada por causa

**CAUSAS HNT (14 + NULL):**

**Remuneradas (9):**
- vacaciones (HNTRa)
- festivos (HNTRb)
- it_total (HNTRc)
- maternidad_paternidad (HNTRd)
- permisos_retribuidos (HNTRe)
- razones_tecnicas_economicas (HNTRf)
- compensacion_extras (HNTRg)
- perdidas_lugar_trabajo (HNTRh)
- otras_remuneradas (HNTRi)

**No Remuneradas (2):**
- conflictividad (HNTnR1)
- otras_no_remuneradas (HNTnR2)

**Agregados (3):**
- pagadas_agregado (HNTR)
- no_pagadas_agregado (HNTnR)
- vacaciones_y_fiestas (HNTRab)

**Otros (1):**
- representacion_sindical

### Cobertura por Tabla

| Tabla | CCAA | Jornada | Sector | rol_grano |
|-------|------|---------|--------|-----------|
| 6042 | No | Sí | B-S | NAC_SECTOR_BS |
| 6043 | No | Sí | Secciones | NAC_SECCION |
| 6044 | No | No | B-S | NAC_SECTOR_BS |
| 6045 | No | No | Secciones | NAC_SECCION |
| 6046 | No | No | Divisiones | NAC_DIVISION |
| 6063 | Sí | Sí | B-S | CCAA_TOTAL/CCAA_TOTAL_JORNADA |

## ✅ Agent Processor: IMPLEMENTADO Y VALIDADO

### Pipeline ETL Completado (25-ago-2025)
- ✅ Estructura de directorios agent_processor creada
- ✅ Clase ProcessorETCL implementada con todos los métodos:
  - `load_raw_csv()`: Detección automática de encoding
  - `map_dimensions()`: Mapeos validados desde exploración
  - `pivot_metrics()`: Conversión correcta de métricas
  - `calculate_flags()`: Flags es_total_* y rol_grano funcionales
  - `validate_data()`: Validaciones básicas implementadas
  - `export_table()`: Carga a DuckDB exitosa
- ✅ Integración con main.py (comando --process-test)
- ✅ Testing con 4 trimestres (2024T2-2025T1): 12,460 registros
- ✅ Validación exhaustiva: 1,918 comparaciones, 100% éxito

### Configuración Lista
- `config/procesador_config_completo.json`: Toda la configuración necesaria
- Mapeos INE → campos estándar definidos
- Dominios cerrados para todos los campos categóricos
- 16 reglas de validación documentadas

## 📁 Estructura actualizada
```
absentismo-espana/
├── agent_extractor/         # ✅ Completado y funcional
├── agent_processor/         # 🎯 En diseño - estructura definida
├── config/                  
│   ├── tables.json         # ✅ 35 tablas configuradas
│   └── procesador_config_completo.json # ✅ Configuración processor
├── data/
│   ├── raw/csv/            # ✅ 35 CSVs (solo usaremos 6)
│   ├── processed/          # 📁 Pendiente - aquí irá tabla unificada
│   └── exploration_reports/ # ✅ Análisis completos
├── docs/
│   ├── metodologia_ETCL_INE_2023.pdf # ✅ Referencia oficial
│   ├── Consolidacion_Final_ETCL_Absentismo.md # ✅ Diseño final
│   └── VALIDACION_ESTRUCTURA_FINAL.md # ✅ Validación completa
├── exploration/             # ✅ Scripts de exploración y validación
├── CLAUDE.md               # ✅ Actualizado con diseño processor
└── CONTEXT.md              # ✅ Este archivo
```

## 🎯 Estado del proyecto: PIPELINE ETL VALIDADO - LISTO PARA PRODUCCIÓN

**Hitos alcanzados (25-ago-2025)**: 
- ✅ Pipeline ETL completamente implementado y funcional
- ✅ 100% de validación en 1,918 comparaciones contra datos INE
- ✅ Corrección de mapeos para secciones G y O
- ✅ Documentación completa y actualizada
- ✅ Reportes de validación consolidados generados

**Próximo hito**:
- Implementación de vistas SQL para métricas calculadas (HPE, HNTmo, tasas)
- Implementación de dashboard de visualización
- Despliegue en producción

## 📊 Actualización 27-nov-2024: Nomenclatura y Códigos

### Cambios implementados:
1. ✅ **Separación correcta de causas**: Eliminado "otros", ahora 14 causas específicas
2. ✅ **Renombrado**: `erte_suspension` → `razones_tecnicas_economicas`
3. ✅ **Nuevos campos añadidos**:
   - `metrica_codigo`: Códigos estándar (HP, HPAG, HE, HEXT, HNT, HNTRa-i, HNTnR1-2)
   - `metrica_ine`: Nombre exacto tal como aparece en el INE
4. ✅ **Datos completos cargados**: 149,247 registros (2008T1-2025T1)
5. ✅ **Validaciones contra archivos INE**: 100% coherencia

### Estado actual de datos:
- **Total registros**: 149,247
- **Periodos**: 69 (2008T1 a 2025T1)
- **Tablas**: 6 (6042-6046, 6063)
- **Campos tabla**: 25 (incluye metrica_codigo y metrica_ine)
- **Causas HNT**: 14 específicas + NULL para totales

### IMPORTANTE - Métricas calculadas:
Las siguientes métricas NO están en la BD base, se calcularán cuando se necesiten:
- HPE (Horas Pactadas Efectivas) = HP + HEXT - HNTRa - HNTRb - HNTRf
- HNTmo (motivos ocasionales) = Suma HNT excepto vacaciones, festivos y razones técnicas
- Tasa_Adecco = (HNTmo / HPE) * 100
- Tasa_Randstad = ((HNT - HNTRa - HNTRb) / HP) * 100

La BD contiene SOLO métricas BASE del INE con nomenclatura exacta.