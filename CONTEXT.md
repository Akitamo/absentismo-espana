# PROJECT STATUS - AbsentismoEspana

## 📅 Última actualización
**Fecha:** 2025-08-25
**Sesión:** Validación completa tabla 6042 y consolidación documentación

## 🔧 Agent Processor: EN IMPLEMENTACIÓN (90%)

### Implementado ✅

1. **Pipeline ETL completo**
   - `agent_processor/etl/extractor.py`: Lee CSVs con detección automática de encoding
   - `agent_processor/etl/transformer.py`: Mapea dimensiones y pivota métricas (con detección B_S)
   - `agent_processor/etl/loader.py`: Carga a DuckDB con validaciones
   - `agent_processor/processor.py`: Orquestador principal del pipeline
   
2. **Base de datos DuckDB**
   - Tabla: `observaciones_tiempo_trabajo` (24 campos - incluye horas_pagadas)
   - Esquema validado contra diseño Excel v3
   - Datos test: ~8,460 registros (2024T2-2025T1) para las 6 tablas
   - Sin duplicados en clave primaria
   - Campo `rol_grano` funcionando para prevenir agregaciones incorrectas

3. **Configuración completamente validada**
   - `agent_processor/config/mappings.json`: Mapeos desde exploración agosto 2025
   - Valores almacenados TAL CUAL del INE (151 = 151 horas, NO 15.1)
   - Mapeos de tipo_jornada, sectores CNAE, CCAA confirmados
   - **CORREGIDO**: Horas pagadas ≠ Horas efectivas (son métricas diferentes)
   - **CORREGIDO**: Mapeos B_S para tablas 6043, 6045, 6046
   - **CORREGIDO**: Formato CCAA con prefijos numéricos ("01 Andalucía")

### Validaciones Realizadas ✅

| Tabla | Estado | Valores Validados | Registros Cargados | URL INE |
|-------|--------|-------------------|-------------------|---------|
| 6042 | ✅ VALIDADA | 12/12 valores perfectos:<br>• Total B-S: 151.0 ✅<br>• Completa: 168.4 ✅<br>• Parcial: 89.3 ✅<br>• Industria B-E: 165.1 ✅ | 3,120 | [Ver datos](https://www.ine.es/jaxiT3/Datos.htm?t=6042) |
| 6043 | ✅ VALIDADA | Total B-S, Secciones CNAE | 1,920 | [Ver datos](https://www.ine.es/jaxiT3/Datos.htm?t=6043) |
| 6044 | ✅ VALIDADA | Sectores sin jornada | 240 | [Ver datos](https://www.ine.es/jaxiT3/Datos.htm?t=6044) |
| 6045 | ✅ VALIDADA | Secciones sin jornada | 480 | [Ver datos](https://www.ine.es/jaxiT3/Datos.htm?t=6045) |
| 6046 | ✅ VALIDADA | Divisiones sin jornada | 2,380 | [Ver datos](https://www.ine.es/jaxiT3/Datos.htm?t=6046) |
| 6063 | ✅ VALIDADA | CCAA + Sectores + Jornada | 4,320 | [Ver datos](https://www.ine.es/jaxiT3/Datos.htm?t=6063) |

**TOTAL**: 8,460 registros cargados exitosamente en modo test (4 trimestres)

### Lecciones Aprendidas 📚

1. **SIEMPRE consultar EXPLORACION_VALIDADA.md antes de validar**: Contiene TODOS los valores ya verificados
2. **Horas pagadas ≠ Horas efectivas**: Son métricas diferentes (pagadas > efectivas siempre)
3. **Valores TAL CUAL del INE**: 151 = 151 horas (NO dividir por 10)
4. **Prevención duplicados**: Campo `rol_grano` implementado y funcional
5. **Mapeos desde exploración**: No crear nuevos mapeos, usar los validados de agosto 2025
6. **Detección B_S automática**: Transformer detecta prefijo B_S como TOTAL

### Próximos Pasos 🚀

1. ✅ **COMPLETADO**: Todas las tablas validadas y cargando correctamente
2. ✅ **COMPLETADO**: Documentación consolidada en EXPLORACION_VALIDADA.md
3. 🔄 **EN PROCESO**: Generar reporte final consolidado
4. ⏳ **PENDIENTE**: Cargar datos históricos completos (2008T1-2025T1)
5. ⏳ **PENDIENTE**: Crear vistas de análisis en DuckDB
6. ⏳ **PENDIENTE**: Implementar dashboard Streamlit con NL2SQL
7. ⏳ **PENDIENTE**: Actualizar repositorio GitHub

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
| causa | ENUM | NO | it_total, maternidad_paternidad, permisos_retribuidos, conflictividad, representacion_sindical, otros, vacaciones, festivos, erte_suspension, NULL |
| valor | DECIMAL | SÍ | Valor numérico |
| unidad | VARCHAR | SÍ | horas/mes por trabajador |
| fuente_tabla | VARCHAR(4) | SÍ | 6042-6046, 6063 |
| es_total_ccaa | BOOLEAN | SÍ | TRUE si NAC |
| es_total_cnae | BOOLEAN | SÍ | TRUE si TOTAL |
| es_total_jornada | BOOLEAN | SÍ | TRUE si NULL o TOTAL |
| rol_grano | ENUM | SÍ | Identificador único grano |

### Métricas y Causas Definidas

**MÉTRICAS (5):**
- horas_pactadas → DENOMINADOR para tasas
- horas_pagadas → CONTEXTO (incluye pagadas no trabajadas)
- horas_efectivas → CONTEXTO (solo trabajadas)
- horas_extraordinarias → CONTEXTO  
- horas_no_trabajadas → Desglosada por causa

**CAUSAS HNT (9):**
- **Incluir en absentismo**: it_total, maternidad_paternidad, permisos_retribuidos, conflictividad, representacion_sindical, otros
- **Excluir de absentismo**: vacaciones, festivos, erte_suspension

### Cobertura por Tabla

| Tabla | CCAA | Jornada | Sector | rol_grano |
|-------|------|---------|--------|-----------|
| 6042 | No | Sí | B-S | NAC_SECTOR_BS |
| 6043 | No | Sí | Secciones | NAC_SECCION |
| 6044 | No | No | B-S | NAC_SECTOR_BS |
| 6045 | No | No | Secciones | NAC_SECCION |
| 6046 | No | No | Divisiones | NAC_DIVISION |
| 6063 | Sí | Sí | B-S | CCAA_TOTAL/CCAA_TOTAL_JORNADA |

## 🚧 Siguiente Fase: Implementación Agent Processor

### Tareas Pendientes
- [ ] Crear estructura de directorios agent_processor
- [ ] Implementar clase ProcessorETCL con métodos:
  - `load_raw_csv()`: Cargar CSVs con encoding correcto
  - `map_dimensions()`: Mapear columnas INE → campos estándar
  - `pivot_metrics()`: Convertir "Tiempo de trabajo" → metrica + causa
  - `calculate_flags()`: Calcular es_total_*, rol_grano
  - `validate_data()`: Aplicar 16 reglas de validación
  - `export_table()`: Guardar en CSV/Parquet
- [ ] Integrar con main.py (comandos --process-all, --process)
- [ ] Testing con subset de datos (2025T1)
- [ ] Validación completa con identidad HE y suma causas

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

## 🎯 Estado del proyecto: DISEÑO COMPLETADO - LISTO PARA IMPLEMENTACIÓN

**Hito alcanzado**: 
- Estructura de tabla definitiva validada contra todos los requisitos
- Configuración completa extraída y documentada
- Decisiones de diseño tomadas y justificadas
- Validaciones matemáticas y de negocio definidas

**Próximo hito**:
- Implementación del Agent Processor con la estructura validada
- Primera carga de datos y validación de resultados