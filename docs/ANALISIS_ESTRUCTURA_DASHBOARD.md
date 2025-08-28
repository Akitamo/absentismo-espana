# ANÁLISIS DE LA ESTRUCTURA DE DATOS PARA DASHBOARD
## Configuración Actual y Capacidades

Fecha: 28-nov-2024

## 1. ESTRUCTURA ACTUAL DE LA TABLA

### Tabla: `observaciones_tiempo_trabajo` (25 campos)

#### Campos de Dimensiones (11 campos)
```sql
periodo               VARCHAR   -- YYYYTQ (2008T1 a 2025T1)
periodo_inicio        DATE      -- Fecha inicio trimestre
periodo_fin           DATE      -- Fecha fin trimestre
ambito_territorial    VARCHAR   -- NAC / CCAA
ccaa_codigo          VARCHAR   -- 01-19 o NULL
ccaa_nombre          VARCHAR   -- "01 Andalucía", etc.
cnae_nivel           VARCHAR   -- TOTAL / SECTOR_BS / SECCION / DIVISION
cnae_codigo          VARCHAR   -- B-E, F, G-S, C, 10, etc.
cnae_nombre          VARCHAR   -- Descripción del sector
jerarquia_sector_cod VARCHAR   -- Path: TOTAL>SECCION>C>DIVISION>10
jerarquia_sector_lbl VARCHAR   -- Path con nombres
tipo_jornada         VARCHAR   -- TOTAL / COMPLETA / PARCIAL / NULL
```

#### Campos de Métricas (4 campos)
```sql
metrica              VARCHAR   -- horas_pactadas, horas_efectivas, etc. (5 tipos)
causa                VARCHAR   -- 14 causas específicas + NULL
metrica_codigo       VARCHAR   -- HP, HE, HNTRa, etc. (códigos estándar)
metrica_ine          VARCHAR   -- Nombre exacto del INE
```

#### Campos de Valores (2 campos)
```sql
valor                DECIMAL(12,3)  -- Valor numérico
unidad               VARCHAR        -- "horas/mes por trabajador"
```

#### Campos de Control (8 campos)
```sql
fuente_tabla         VARCHAR   -- 6042-6046, 6063 (CRÍTICO para evitar duplicados)
es_total_ccaa        BOOLEAN   -- TRUE si ambito='NAC'
es_total_cnae        BOOLEAN   -- TRUE si cnae_nivel='TOTAL'
es_total_jornada     BOOLEAN   -- TRUE si tipo_jornada='TOTAL' o NULL
rol_grano            VARCHAR   -- Identificador de granularidad
version_datos        VARCHAR   -- Version INE (ej: "2024T3")
fecha_carga          TIMESTAMP -- Auditoría
```

## 2. CAPACIDADES ACTUALES DEL DISEÑO

### ✅ FORTALEZAS

#### 1. Estructura Normalizada tipo FACT TABLE
- **Una fila = un hecho medible**: Cada registro representa UN valor de UNA métrica
- **Dimensiones claramente separadas**: periodo, geografía, sector, jornada
- **Métricas atomizadas**: No hay agregaciones precalculadas

#### 2. Sistema de Códigos Duales
```sql
metrica_codigo: HP, HNTRa, HNTRb...  -- Para cálculos programáticos
metrica_ine: "Horas pactadas"...     -- Para mostrar al usuario
```
Esto permite:
- Queries simples con códigos estándar
- Presentación con nombres oficiales INE

#### 3. Jerarquías Explícitas
```sql
cnae_nivel: TOTAL → SECTOR_BS → SECCION → DIVISION
jerarquia_sector_cod: "TOTAL>SECCION>C>DIVISION>10"
```
Facilita:
- Navegación drill-down/roll-up
- Validación de agregaciones correctas

#### 4. Flags de Control para Agregación
```sql
es_total_ccaa, es_total_cnae, es_total_jornada
```
Previenen:
- Doble conteo en agregaciones
- Mezcla incorrecta de niveles

#### 5. Control de Duplicados del TOTAL
```sql
fuente_tabla = '6042'  -- Filtro crítico para evitar sumar 6 veces el TOTAL
```

### 🎯 QUERIES SIMPLIFICADAS RESULTANTES

#### Ejemplo 1: Tasa de Absentismo Nacional
```sql
-- Query actual: Simple y directa
WITH metricas AS (
    SELECT 
        SUM(CASE WHEN metrica_codigo = 'HP' THEN valor END) as HP,
        SUM(CASE WHEN metrica_codigo = 'HEXT' THEN valor END) as HEXT,
        SUM(CASE WHEN metrica_codigo = 'HNTRa' THEN valor END) as Vacaciones,
        SUM(CASE WHEN metrica_codigo = 'HNTRb' THEN valor END) as Festivos,
        SUM(CASE WHEN metrica_codigo = 'HNTRc' THEN valor END) as IT
    FROM observaciones_tiempo_trabajo
    WHERE periodo = '2024T4'
        AND ambito_territorial = 'NAC'
        AND cnae_nivel = 'TOTAL'
        AND fuente_tabla = '6042'  -- Evita duplicados
        AND tipo_jornada = 'TOTAL'
)
SELECT 
    HP + HEXT - Vacaciones - Festivos as HPE,
    IT / (HP + HEXT - Vacaciones - Festivos) * 100 as Tasa_IT
FROM metricas
```

#### Ejemplo 2: Comparación por Sectores
```sql
-- Directo sin JOINs complejos
SELECT 
    cnae_codigo,
    cnae_nombre,
    SUM(CASE WHEN metrica_codigo = 'HP' THEN valor END) as HP,
    SUM(CASE WHEN metrica_codigo = 'HNTRc' THEN valor END) as IT,
    ROUND(SUM(CASE WHEN metrica_codigo = 'HNTRc' THEN valor END) / 
          SUM(CASE WHEN metrica_codigo = 'HP' THEN valor END) * 100, 2) as Tasa_IT
FROM observaciones_tiempo_trabajo
WHERE periodo = '2024T4'
    AND cnae_nivel = 'SECTOR_BS'  -- Solo sectores B-E, F, G-S
    AND fuente_tabla = '6042'
GROUP BY cnae_codigo, cnae_nombre
```

#### Ejemplo 3: Serie Temporal
```sql
-- Evolución trimestral directa
SELECT 
    periodo,
    SUM(CASE WHEN metrica_codigo = 'HNTRc' THEN valor END) / 
    SUM(CASE WHEN metrica_codigo = 'HP' THEN valor END) * 100 as Tasa_IT
FROM observaciones_tiempo_trabajo
WHERE ambito_territorial = 'NAC'
    AND cnae_nivel = 'TOTAL'
    AND fuente_tabla = '6042'
    AND periodo >= '2023T1'
GROUP BY periodo
ORDER BY periodo
```

## 3. VENTAJAS PARA EL DASHBOARD

### 1. NO Necesita JOINs Complejos
- Toda la información está en una tabla
- Las dimensiones están desnormalizadas (tienen código Y nombre)

### 2. Agregaciones Naturales
```sql
-- Por CCAA
GROUP BY ccaa_nombre

-- Por Sector
GROUP BY cnae_codigo, cnae_nombre  

-- Por Jornada
GROUP BY tipo_jornada

-- Por Trimestre
GROUP BY periodo
```

### 3. Cálculos On-the-Fly
Las métricas calculadas (HPE, HNTmo, tasas) se calculan en el momento:
- No hay valores precalculados que mantener
- Siempre coherentes con los datos base
- Flexibilidad total para nuevas fórmulas

### 4. Filtros Simples
```sql
WHERE periodo = ?           -- Selector de periodo
  AND ccaa_codigo = ?       -- Selector de CCAA
  AND cnae_nivel = ?        -- Nivel de detalle
  AND tipo_jornada = ?      -- Tipo de jornada
```

## 4. PATRONES DE USO RECOMENDADOS

### Para Totales Nacionales
```sql
WHERE ambito_territorial = 'NAC'
  AND cnae_nivel = 'TOTAL'
  AND fuente_tabla = '6042'  -- SIEMPRE para evitar duplicados
```

### Para Análisis por CCAA
```sql
WHERE ambito_territorial = 'CCAA'
  AND fuente_tabla = '6063'  -- Única tabla con CCAA
```

### Para Drill-Down Sectorial
```sql
-- Nivel 1: Sectores
WHERE cnae_nivel = 'SECTOR_BS'

-- Nivel 2: Secciones
WHERE cnae_nivel = 'SECCION'

-- Nivel 3: Divisiones  
WHERE cnae_nivel = 'DIVISION'
```

### Para Series Temporales
```sql
GROUP BY periodo
ORDER BY periodo
```

## 5. PROPUESTAS DE MEJORA

### OPCIÓN 1: Vistas Materializadas (Recomendado)

#### Vista 1: Métricas Base Pivotadas
```sql
CREATE VIEW v_metricas_base AS
SELECT 
    periodo,
    ambito_territorial,
    ccaa_codigo,
    ccaa_nombre,
    cnae_nivel,
    cnae_codigo,
    cnae_nombre,
    tipo_jornada,
    MAX(CASE WHEN metrica_codigo = 'HP' THEN valor END) as HP,
    MAX(CASE WHEN metrica_codigo = 'HPAG' THEN valor END) as HPAG,
    MAX(CASE WHEN metrica_codigo = 'HE' THEN valor END) as HE,
    MAX(CASE WHEN metrica_codigo = 'HEXT' THEN valor END) as HEXT,
    MAX(CASE WHEN metrica_codigo = 'HNTRa' THEN valor END) as Vacaciones,
    MAX(CASE WHEN metrica_codigo = 'HNTRb' THEN valor END) as Festivos,
    MAX(CASE WHEN metrica_codigo = 'HNTRc' THEN valor END) as IT,
    -- ... resto de métricas
FROM observaciones_tiempo_trabajo
WHERE fuente_tabla = CASE 
    WHEN ambito_territorial = 'NAC' AND cnae_nivel = 'TOTAL' THEN '6042'
    WHEN ambito_territorial = 'NAC' AND cnae_nivel = 'SECTOR_BS' THEN '6042'
    WHEN ambito_territorial = 'NAC' AND cnae_nivel = 'SECCION' THEN '6043'
    WHEN ambito_territorial = 'NAC' AND cnae_nivel = 'DIVISION' THEN '6046'
    WHEN ambito_territorial = 'CCAA' THEN '6063'
END
GROUP BY periodo, ambito_territorial, ccaa_codigo, ccaa_nombre,
         cnae_nivel, cnae_codigo, cnae_nombre, tipo_jornada;
```

#### Vista 2: Métricas Calculadas
```sql
CREATE VIEW v_metricas_calculadas AS
SELECT 
    *,
    HP + HEXT - Vacaciones - Festivos - ERTEs as HPE,
    IT + Maternidad + Permisos + CompensacionExtras + OtrasRem as HNTmo,
    ROUND((IT + Maternidad + Permisos + CompensacionExtras + OtrasRem) / 
          NULLIF(HP + HEXT - Vacaciones - Festivos - ERTEs, 0) * 100, 2) as Tasa_Absentismo,
    ROUND(IT / NULLIF(HP + HEXT - Vacaciones - Festivos - ERTEs, 0) * 100, 2) as Tasa_IT
FROM v_metricas_base;
```

### OPCIÓN 2: Tabla de Agregados Pre-calculados

Para dashboards con mucho tráfico, crear tabla agregada nocturna:

```sql
CREATE TABLE metricas_agregadas AS
SELECT 
    periodo,
    ambito_territorial,
    ccaa_codigo,
    cnae_nivel,
    cnae_codigo,
    tipo_jornada,
    -- Métricas base
    SUM(HP) as HP,
    SUM(HEXT) as HEXT,
    -- Métricas calculadas
    SUM(HPE) as HPE,
    SUM(HNTmo) as HNTmo,
    -- Tasas
    AVG(Tasa_Absentismo) as Tasa_Absentismo,
    AVG(Tasa_IT) as Tasa_IT
FROM v_metricas_calculadas
GROUP BY periodo, ambito_territorial, ccaa_codigo, 
         cnae_nivel, cnae_codigo, tipo_jornada;
```

## 6. CONCLUSIÓN

### ✅ El diseño actual es ÓPTIMO para dashboards porque:

1. **Estructura tipo FACT TABLE**: Ideal para BI y agregaciones
2. **Sin JOINs necesarios**: Todo en una tabla
3. **Códigos duales**: Facilitan cálculos y presentación
4. **Jerarquías explícitas**: Navegación dimensional natural
5. **Flags de control**: Previenen errores de agregación
6. **Solución al TOTAL duplicado**: Con filtro fuente_tabla

### 📊 Complejidad de Queries: BAJA

- Queries típicas: 10-20 líneas SQL
- Sin JOINs complejos
- Pattern simple: WHERE + GROUP BY + SUM(CASE)
- Mantenible y entendible

### 🚀 Rendimiento Esperado: EXCELENTE

- Índices en campos de dimensión
- Agregaciones simples sobre columnas indexadas
- 149K registros es volumen manejable
- DuckDB optimizado para analytics

### 💡 Recomendación Final

El diseño actual **NO necesita cambios estructurales**. Las queries son suficientemente simples. 

Si se necesita más simplicidad, implementar las vistas propuestas que:
1. Pre-pivotan las métricas (vista base)
2. Pre-calculan las tasas (vista calculada)
3. Mantienen la flexibilidad del modelo actual