# Validación y Lecciones Aprendidas

Este documento resume la validación del pipeline y las lecciones clave para evitar errores habituales al consultar los datos.

## 1) Validación (resumen)

- Tablas procesadas: 6042–6046 y 6063 (2008T1–2025T1).
- Total registros (carga completa reciente): 149,247.
- Consistencias verificadas:
  - Claves de negocio coherentes; sin nulos en campos críticos.
  - Métricas: `horas_pactadas/efectivas/pagadas/extraordinarias` y `horas_no_trabajadas` por causa.
  - 6044 (global, sin jornada) contiene todas las causas necesarias para HNTmo; 6063 válido para CCAA.
- Checks de cálculo:
  - HPE ≈ HP + HEXT − (Vacaciones + Festivos) − ERTE (tolerancia ±0.5).
  - HNTmo coherente con la suma de causas.
  - 2024T4 (6044, NAC/TOTAL): Tasa Absentismo ≈ 7.43%; Tasa IT ≈ 5.8%.

## 2) Lecciones clave

1. TOTAL nacional duplicado por diseño del INE (aparece en 6042–6046, 6063). Nunca sumar varios orígenes: filtra por `fuente_tabla`.
2. Para KPI/serie global usa 6044 (sin jornada). 6042 (TOTAL) sólo para jornada o como fallback.
3. No “corregir” duplicados con AVG/MAX/MIN: elige la fuente correcta. 
4. No mezclar niveles (TOTAL/SECTOR/SECCIÓN/DIVISIÓN) ni geografías (NAC/CCAA) en una misma agregación.

## 3) Queries de verificación rápidas

- Conteos por `fuente_tabla`:
```sql
SELECT fuente_tabla, COUNT(*) FROM observaciones_tiempo_trabajo GROUP BY 1 ORDER BY 1;
```

- Causas presentes en 6044 (NAC/TOTAL):
```sql
SELECT DISTINCT causa FROM observaciones_tiempo_trabajo
WHERE fuente_tabla='6044' AND ambito_territorial='NAC' AND cnae_nivel='TOTAL'
  AND metrica='horas_no_trabajadas' ORDER BY 1;
```

- KPI global (ver sección “Patrones SQL” en DATOS_ETCL_Y_METODOLOGIA.md).

## 4) Registro de cambios (breve)

- 2025-09: Consolidación de reglas — 6044 establecida como fuente de verdad para KPI/series globales; DataService y dashboard alineados. 
- 2025-09: Loader recrea tabla en carga completa y asegura `metrica_codigo/metrica_ine`.

