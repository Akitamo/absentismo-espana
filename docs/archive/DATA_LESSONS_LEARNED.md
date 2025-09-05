# DATA_LESSONS_LEARNED.md

**Fecha creación:** 29-11-2024  
**Propósito:** Documentar todas las lecciones aprendidas en la extracción, procesamiento y modelado de datos del proyecto Absentismo España.

---

## 📊 AGENT EXTRACTOR - Lecciones Aprendidas

### Estado: COMPLETADO Y VALIDADO ✅
- **51 métricas únicas extraídas** de 35 tablas INE
- **112% cobertura** respecto a metodología INE (51/45.5 esperadas)
- **100% validación** contra endpoints web INE
- **Confidence level: Maximum** - Agent Extractor listo para producción

### Métricas Extraídas y Validadas (19-ago-2025)

**Cobertura por Categoría:**
- **COSTES LABORALES**: 16/18 métricas directas (88.9%)
- **TIEMPO DE TRABAJO**: 18/13 métricas (138.5% - mayor detalle que esperado)  
- **COSTE SALARIAL**: 4/4 métricas (100% - completo)
- **VACANTES**: 3/2 métricas (150% - incluye sub-métricas)
- **SERIES TEMPORALES**: Valores, índices y tasas de variación

### Lecciones Clave:
1. **Multi-encoding support necesario**: UTF-8, Latin-1, ISO-8859-1, CP1252
2. **INE actualiza trimestralmente** - Verificar con --check-smart
3. **Cada CSV contiene histórico COMPLETO** desde 2008T1
4. **Anti-duplicación crítica**: Pattern matching para nombres variables INE

---

## 🔄 AGENT PROCESSOR - Lecciones Aprendidas

### Estado: COMPLETADO Y VALIDADO ✅ (27-nov-2024)
- ✅ Pipeline ETL completamente funcional
- ✅ DuckDB integrado con esquema de 25 campos
- ✅ 149,247 registros procesados (2008T1-2025T1)
- ✅ Sin duplicados, prevención de agregaciones incorrectas

### Estructura Tabla Final: `observaciones_tiempo_trabajo`

**Primary Key**: `periodo + ambito_territorial + ccaa_codigo + cnae_nivel + cnae_codigo + tipo_jornada + metrica + causa`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| periodo | VARCHAR(6) | Trimestre (YYYYTQ) |
| ambito_territorial | ENUM | NAC o CCAA |
| ccaa_codigo | VARCHAR(2) | Código INE o NULL |
| cnae_nivel | ENUM | TOTAL, SECTOR_BS, SECCION, DIVISION |
| cnae_codigo | VARCHAR(5) | Código CNAE o NULL |
| tipo_jornada | ENUM | TOTAL, COMPLETA, PARCIAL, NULL |
| metrica | VARCHAR(30) | 5 tipos: horas_pactadas, horas_pagadas, horas_efectivas, horas_extraordinarias, horas_no_trabajadas |
| causa | VARCHAR(30) | 14 valores para HNT |
| metrica_codigo | VARCHAR(10) | Códigos estándar: HP, HPAG, HE, HEXT, HNT |
| metrica_ine | VARCHAR(150) | Nombre exacto INE |
| valor | DECIMAL | Valor numérico |
| es_total_ccaa | BOOLEAN | TRUE si NAC |
| es_total_cnae | BOOLEAN | TRUE si TOTAL |
| es_total_jornada | BOOLEAN | TRUE si NULL o TOTAL |
| rol_grano | ENUM | 11 combinaciones de granularidad |
| fuente_tabla | VARCHAR(4) | 6042-6046, 6063 |
| fecha_carga | TIMESTAMP | Auditoría |

**Total: 25 campos**

---

## ⚠️ PROBLEMA CRÍTICO: Duplicados del TOTAL Nacional

### El Problema
Las 6 tablas INE (6042-6046, 6063) incluyen TODAS el mismo valor TOTAL nacional. Esto es por diseño del INE para facilitar referencia, pero causa multiplicación x6 en queries.

### Ejemplo del Problema
```sql
-- MAL: Suma el TOTAL 6 veces
SELECT SUM(valor) FROM observaciones_tiempo_trabajo 
WHERE cnae_nivel = 'TOTAL'
-- Resultado: 906 (151 x 6) ❌

-- BIEN: Filtrar por una tabla
SELECT SUM(valor) FROM observaciones_tiempo_trabajo 
WHERE cnae_nivel = 'TOTAL' AND fuente_tabla = '6042'
-- Resultado: 151 ✅
```

### SOLUCIÓN CORRECTA
**SIEMPRE filtrar por `fuente_tabla`** cuando se trabaje con TOTAL nacional:
- Usar tabla 6042 para TOTAL con jornada
- Usar tabla 6044 para TOTAL sin jornada
- Usar tabla 6063 para TOTAL por CCAA

### NUNCA HACER
- ❌ NO usar AVG para "promediar" duplicados
- ❌ NO usar MAX/MIN arbitrariamente
- ❌ NO usar DISTINCT ON como parche
- ❌ NO modificar datos originales del INE

---

## 📈 Metodología de Cálculo Validada

### Metodología Adecco (Q4 2024)
```python
# 1. Horas Pactadas Efectivas (HPE)
HPE = HP + HEXT - Vacaciones - Festivos - ERTEs
# Q4 2024: 137.2 horas

# 2. Horas No Trabajadas Motivos Ocasionales (HNTmo)
HNTmo = IT + Maternidad + Permisos + Compensación + Otras_rem + Pérdidas + Conflictividad + Otras_no_rem
# Q4 2024: 10.2 horas

# 3. Tasa de Absentismo General
Tasa_Absentismo = (HNTmo / HPE) × 100
# Q4 2024: 7.43% (Adecco reporta 7.4%) ✅

# 4. Tasa de IT
Tasa_IT = (IT / HPE) × 100  
# Q4 2024: 5.76% (Adecco reporta 5.8%) ✅
```

### Diferencia CRÍTICA: Horas Pagadas vs Efectivas
- **Horas pagadas**: Todas las horas por las que se paga (incluye vacaciones, permisos)
- **Horas efectivas**: Solo las horas realmente trabajadas
- **Relación**: Horas pagadas > Horas efectivas (SIEMPRE)
- **Ejemplo**: Industria 2025T1: Pagadas=166.0, Efectivas=144.2

---

## 🔍 Reglas de Validación de Datos

### Fuentes de Verdad (por orden)
1. **Scripts de exploración validados** (agosto 2025)
   - `exploration/validate_specific_values.py`
   - `exploration/validate_all_tables.py`
2. **Web INE** (https://www.ine.es/jaxiT3/Datos.htm?t={codigo})
3. **Metodología INE** (docs/metodologia_ETCL_INE_2023.pdf)

### Validaciones Matemáticas
1. **Coherencia**: HE ≈ HP + HEXT - HNT_total (±0.5)
2. **Suma causas**: Σ(HNT por causa) ≈ HNT_total (±0.5)
3. **No mezclar niveles**: Nunca sumar diferentes cnae_nivel

### NUNCA usar como fuente primaria
- ❌ CSVs directamente (ya validados)
- ❌ Valores hardcodeados sin verificar

---

## 📝 Nomenclatura y Códigos de Métricas

### Códigos Estándar (metrica_codigo)

**Base:**
- `HP` - Horas pactadas
- `HPAG` - Horas pagadas
- `HE` - Horas efectivas
- `HEXT` - Horas extraordinarias
- `HNT` - Horas no trabajadas (total)

**HNT Remuneradas:**
- `HNTRa` - Vacaciones
- `HNTRb` - Festivos
- `HNTRc` - I.T. (Incapacidad Temporal)
- `HNTRd` - Maternidad/Paternidad
- `HNTRe` - Permisos remunerados
- `HNTRf` - Razones técnicas/económicas
- `HNTRg` - Compensación horas extras
- `HNTRh` - Pérdidas lugar trabajo
- `HNTRi` - Otras remuneradas

**HNT No Remuneradas:**
- `HNTnR1` - Conflictividad laboral
- `HNTnR2` - Otras no remuneradas

**Especial:**
- `HNTRab` - Vacaciones y festivos (agregado)

---

## 💡 Decisiones Técnicas Validadas

1. **VALORES TAL CUAL DEL INE**: NO dividir por 10 (151 = 15.1 horas)
2. **Mapeos confirmados** desde exploración (NO re-mapear)
3. **Campo rol_grano**: Previene agregaciones incorrectas
4. **Windows compatibility**: No emojis en console output
5. **Backup automático**: Antes de cada actualización

---

## 📌 Documentación de Exploración Crítica

**ARCHIVO CLAVE**: `docs/EXPLORACION_VALIDADA.md`
- Contiene TODOS los valores validados
- Mapeos confirmados
- Lecciones aprendidas
- Consultar SIEMPRE antes de cualquier validación