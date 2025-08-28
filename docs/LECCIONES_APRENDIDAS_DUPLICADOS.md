# LECCIONES APRENDIDAS: Problema de Duplicados del TOTAL Nacional

## Fecha: 28 de noviembre de 2024

## Resumen Ejecutivo
Se identificó que el valor TOTAL nacional aparecía multiplicado por 6 en las consultas agregadas. La investigación reveló que NO era un error en los datos, sino una característica del diseño del INE donde cada tabla incluye el mismo TOTAL para facilitar validación y referencia.

## El Problema Identificado

### Síntoma
Al ejecutar consultas agregadas sobre la tabla `observaciones_tiempo_trabajo`, los valores del TOTAL nacional aparecían multiplicados por 6:
- Valor esperado (INE): 151.4 horas pactadas
- Valor obtenido (SUM): 908.6 horas (6 × 151.4)

### Definición del TOTAL Nacional en el INE
El TOTAL nacional se identifica cuando las dimensiones tienen estos valores específicos:
- **TIPO JORNADA**: "AMBAS JORNADAS" o "TOTAL" (o NULL en tablas sin jornada)
- **Secciones de la CNAE-09**: "B_S Industria, construcción y servicios..." (texto completo)
- **Sectores de actividad CNAE 2009**: "B_S Industria, construcción y servicios..." (texto completo)
- **Comunidades y Ciudades Autónomas**: "Total nacional"

En nuestra base de datos, esto se traduce a:
- `cnae_nivel = 'TOTAL'` 
- `cnae_codigo IS NULL` o `cnae_codigo = 'B-S'` (cuando aparece solo)
- `ambito_territorial = 'NAC'`
- `tipo_jornada = 'TOTAL'` o `tipo_jornada = 'AMBAS'` o `tipo_jornada IS NULL`

### Causa Raíz
Las 6 tablas del INE (6042, 6043, 6044, 6045, 6046, 6063) incluyen todas el mismo valor TOTAL nacional. Esto es **por diseño del INE**, no un error:
- Cada tabla calcula su propio TOTAL basado en los datos que contiene
- Para cada métrica y cada trimestre, el TOTAL aparece en todas las tablas
- Facilita la validación cruzada entre tablas
- Permite usar cada tabla de forma independiente
- Asegura coherencia en los reportes

### Por qué el campo `rol_grano` no lo previene
El campo `rol_grano` fue diseñado para identificar diferentes granularidades (NAC_TOTAL, NAC_SECTOR_BS, etc.), pero NO para prevenir que el mismo dato aparezca en múltiples tablas fuente. La clave primaria no incluye `fuente_tabla`, por lo que el mismo registro TOTAL aparece 6 veces con la misma clave.

## Soluciones Incorrectas Intentadas (NO HACER)

### ❌ Usar AVG en lugar de SUM
```sql
-- INCORRECTO - "chapuza" que oculta el problema
SELECT AVG(valor) as hp FROM observaciones_tiempo_trabajo
WHERE cnae_nivel = 'TOTAL'
```
**Por qué está mal**: Asume que siempre habrá exactamente 6 duplicados, lo cual es frágil y confuso.

### ❌ Usar MAX o MIN
```sql
-- INCORRECTO - toma un valor arbitrario
SELECT MAX(valor) as hp FROM observaciones_tiempo_trabajo
WHERE cnae_nivel = 'TOTAL'
```
**Por qué está mal**: Funciona solo porque todos los valores son idénticos, pero es conceptualmente incorrecto.

### ❌ Usar DISTINCT ON
```sql
-- INCORRECTO - parche SQL que complica las queries
WITH datos_unicos AS (
    SELECT DISTINCT ON (periodo, ambito_territorial, ...) *
    FROM observaciones_tiempo_trabajo
)
SELECT SUM(valor) FROM datos_unicos
```
**Por qué está mal**: Añade complejidad innecesaria y no aborda el problema real.

## Solución Correcta

### ✅ Filtrar por fuente_tabla específica
```sql
-- CORRECTO - usa dimensiones para obtener el valor correcto
SELECT SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp
FROM observaciones_tiempo_trabajo
WHERE periodo = '2024T4'
    AND ambito_territorial = 'NAC'
    AND cnae_nivel = 'TOTAL'
    AND fuente_tabla = '6042'  -- Filtrar por UNA tabla específica
    AND tipo_jornada = 'TOTAL'
```

### Regla de Negocio Establecida
Para consultas del TOTAL nacional, usar estas prioridades:
1. **TOTAL con jornada**: usar tabla 6042
2. **TOTAL sin jornada**: usar tabla 6044
3. **SECCIONES con jornada**: usar tabla 6043
4. **SECCIONES sin jornada**: usar tabla 6045
5. **DIVISIONES**: usar tabla 6046
6. **Por CCAA**: usar tabla 6063

## Verificaciones Realizadas

### 1. Coherencia entre tablas
Se verificó que todas las tablas tienen el mismo valor TOTAL:
```sql
-- Todas devuelven 151.4 para HP en 2024T4
SELECT fuente_tabla, valor 
FROM observaciones_tiempo_trabajo
WHERE periodo = '2024T4' 
    AND cnae_nivel = 'TOTAL'
    AND metrica = 'horas_pactadas'
```
Resultado: Los 6 registros tienen valor = 151.4 ✅

**Importante**: Este mismo patrón se repite para:
- **Cada métrica** (horas_pactadas, horas_efectivas, horas_extraordinarias, etc.)
- **Cada trimestre** (2008T1 hasta 2025T1)
- **Cada causa de horas no trabajadas** cuando aplica

Es decir, el TOTAL nacional se calcula y almacena en cada tabla para cada combinación de periodo + métrica + causa.

### 2. Análisis de claves primarias
```sql
-- 4,968 combinaciones de clave primaria aparecen múltiples veces
SELECT COUNT(*) FROM (
    SELECT periodo, ambito_territorial, ccaa_codigo, cnae_nivel, 
           cnae_codigo, tipo_jornada, metrica, causa,
           COUNT(*) as num_duplicados
    FROM observaciones_tiempo_trabajo
    GROUP BY 1,2,3,4,5,6,7,8
    HAVING COUNT(*) > 1
)
```

### 3. Validación con valores INE
Los valores obtenidos con el filtro `fuente_tabla='6042'` coinciden exactamente con los publicados por el INE.

## Principios Establecidos

1. **Los datos del INE son correctos**: No hay error en los datos originales
2. **No usar trucos SQL**: Evitar AVG, MAX, MIN, DISTINCT como soluciones
3. **Usar dimensiones correctamente**: Filtrar por fuente_tabla cuando sea necesario
4. **Documentar el comportamiento**: Este es un comportamiento esperado, no un bug
5. **No modificar datos en origen**: Los datos deben mantenerse tal como vienen del INE

## Impacto en el Código

### Archivos Actualizados
1. **`streamlit_app/app.py`**: Queries modificadas para incluir `fuente_tabla = '6042'`
2. **`CLAUDE.md`**: Documentación actualizada con la solución correcta
3. **`CONTEXT.md`**: Lecciones aprendidas añadidas
4. **Este documento**: Nueva documentación específica del problema

### Cambios en Queries
```python
# ANTES (incorrecto)
query = """
    SELECT AVG(CASE WHEN metrica = 'horas_pactadas' THEN valor END) as hp
    FROM observaciones_tiempo_trabajo
    WHERE periodo = ? AND cnae_nivel = 'TOTAL'
"""

# DESPUÉS (correcto)
query = """
    SELECT SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor END) as hp
    FROM observaciones_tiempo_trabajo
    WHERE periodo = ? 
        AND cnae_nivel = 'TOTAL'
        AND fuente_tabla = '6042'  -- Crítico para evitar duplicados
"""
```

## Recomendaciones para el Futuro

1. **Considerar añadir fuente_tabla a la clave primaria**: Esto eliminaría el problema de raíz
2. **Crear vistas materializadas**: Con los datos ya filtrados por fuente apropiada
3. **Documentar en el ETL**: Añadir comentarios explicando por qué cada tabla incluye el TOTAL
4. **Validación en carga**: Verificar que los TOTALES son coherentes entre tablas

## Conclusión

El problema de "duplicados" no era realmente un problema de datos duplicados, sino una característica del diseño del INE que no habíamos entendido correctamente. La solución no es aplicar parches SQL, sino entender y usar correctamente las dimensiones de los datos.

**Lección clave**: Cuando encuentres datos que parecen duplicados, investiga primero si es por diseño antes de aplicar soluciones técnicas.