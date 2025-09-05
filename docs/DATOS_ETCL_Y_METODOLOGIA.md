# Datos ETCL y Metodología (INE)

Este documento unifica las reglas de negocio, el modelo de datos final y los patrones de consulta usados en el proyecto. Sustituye y consolida contenidos previos dispersos en varios ficheros.

## 1) Tabla Final y Claves

- Tabla: `observaciones_tiempo_trabajo` (DuckDB)
- Campos principales (25):
  - Tiempo: `periodo (YYYYTQ)`, `periodo_inicio`, `periodo_fin`
  - Geografía: `ambito_territorial (NAC/CCAA)`, `ccaa_codigo`, `ccaa_nombre`, `es_total_ccaa`
  - Sector: `cnae_nivel (TOTAL/SECTOR_BS/SECCION/DIVISION)`, `cnae_codigo`, `cnae_nombre`, `jerarquia_sector_lbl`, `es_total_cnae`
  - Jornada: `tipo_jornada (TOTAL/COMPLETA/PARCIAL/NULL)`, `es_total_jornada`
  - Métrica: `metrica (horas_pactadas/…/horas_no_trabajadas)`, `causa` (it_total, vacaciones, …), `metrica_codigo`, `metrica_ine`, `valor`, `unidad`
  - Origen y control: `fuente_tabla (6042–6046,6063)`, `rol_grano`, `version_datos`, `fecha_carga`

Clave de negocio: combinación de tiempo + dimensiones + métrica/causa. Importante: el TOTAL nacional existe en varias fuentes (6042–6046, 6063); nunca sumar sin filtrar `fuente_tabla`.

## 2) Reglas por Nivel (fuente_tabla)

- Global (Total Nacional sin jornada): usar 6044. Es la fuente de verdad para KPI y series globales. Fallback 6042 (jornada TOTAL) sólo si 6044 no está disponible.
- Con jornada: 6042 (TOTAL/COMPLETA/PARCIAL). 
- Por CCAA: 6063 (con `tipo_jornada='TOTAL'` o `NULL`).
- Sector/Sección/División: 6043 (secciones con jornada), 6045 (secciones sin jornada), 6046 (divisiones).

Duplicados del TOTAL: las 6 tablas reportan el mismo TOTAL por diseño del INE. Para evitar multiplicar por 6, filtrar por una sola `fuente_tabla` adecuada al análisis.

## 3) Fórmulas validadas (Adecco/ETCL)

- HPE = `HP` + `HEXT` − (`Vacaciones` + `Festivos`) − `ERTE`
- HNTmo (motivos ocasionales) = `IT` + `Maternidad/Paternidad` + `Permisos` + `Compensación extras` + `Otras remuneradas` + `Pérdidas lugar trabajo` + `Conflictividad` + `Otras no remuneradas`
- Tasa de Absentismo (%) = 100 × HNTmo / HPE
- Tasa de IT (%) = 100 × IT / HPE

Ejemplo 2024T4 (6044, NAC/TOTAL):

![Cálculo 4T2024](Cálculo%20tasa%20absentismo%20IT%204T2024.png)

- HPE ≈ 137.2; HNTmo ≈ 10.2 → Tasa Absentismo ≈ 7.43%
- IT ≈ 7.9 → Tasa IT ≈ 5.8%

## 4) Patrones SQL (copiar/pegar)

- KPI global (último periodo):
```sql
WITH m AS (
  SELECT 
    SUM(CASE WHEN metrica='horas_pactadas' THEN valor END) hp,
    SUM(CASE WHEN metrica='horas_extraordinarias' THEN valor END) hext,
    COALESCE(
      SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='vacaciones_y_fiestas' THEN valor END),
      SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='vacaciones' THEN valor END) +
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='festivos' THEN valor END),0)
    ) vac_fest,
    SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='razones_tecnicas_economicas' THEN valor END) ertes,
    SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='it_total' THEN valor END) it,
    (
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='it_total' THEN valor END),0)+
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='maternidad_paternidad' THEN valor END),0)+
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='permisos_retribuidos' THEN valor END),0)+
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='compensacion_extras' THEN valor END),0)+
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='otras_remuneradas' THEN valor END),0)+
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='perdidas_lugar_trabajo' THEN valor END),0)+
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='conflictividad' THEN valor END),0)+
      COALESCE(SUM(CASE WHEN metrica='horas_no_trabajadas' AND causa='otras_no_remuneradas' THEN valor END),0)
    ) hntmo
  FROM observaciones_tiempo_trabajo
  WHERE periodo = ? AND ambito_territorial='NAC' AND cnae_nivel='TOTAL'
    AND fuente_tabla='6044' AND tipo_jornada IS NULL
)
SELECT 
  (hp + hext - vac_fest - ertes) AS hpe,
  hntmo,
  CASE WHEN (hp + hext - vac_fest - ertes)>0 THEN (hntmo/(hp + hext - vac_fest - ertes))*100 ELSE 0 END AS tasa_abs,
  CASE WHEN (hp + hext - vac_fest - ertes)>0 THEN (it/(hp + hext - vac_fest - ertes))*100 ELSE 0 END AS tasa_it
FROM m;
```

- Serie temporal global (últimos 12): igual anterior pero agrupando por `periodo` (fuente 6044, NAC/TOTAL).
- Ranking CCAA (periodo actual): `fuente_tabla='6063'`, `ambito_territorial='CCAA'`, `tipo_jornada='TOTAL' OR NULL`.

## 5) Operativa ETL y Carga

- CSV locales en `data/raw/csv/`.
- Carga completa (limpia y recarga todas las tablas 6042–6046 y 6063):
```
python agent_processor/scripts/load_all_tables.py --yes
```
- Esquema de la tabla incluye `metrica_codigo` y `metrica_ine`.

## 6) Dashboard (uso de datos)

- KPI y evolución usan 6044 (global). Fallback a 6042 si 6044 no está cargada.
- Sparkline de 12 trimestres; delta relativo vs trimestre anterior.
- Para vistas por CCAA y sector, emplear las tablas asignadas arriba.

