# Log de Validaciones Agent Processor

## Objetivo
Tracking detallado de todas las validaciones realizadas contra los datos oficiales del INE para garantizar la integridad del pipeline ETL.

## Estado General
- **Tablas procesadas**: 6/6 (6042-6046, 6063)
- **Tablas validadas**: 1/6 parcialmente
- **Datos cargados**: Solo test (2024T2-2025T1)
- **Pendiente**: Validación completa antes de carga histórica

---

## 2025-08-21 - Validación Inicial

### Tabla 6042: Tiempo trabajo por sectores y jornada
**URL INE**: https://www.ine.es/jaxiT3/Datos.htm?t=6042

#### Valores Validados ✅
| Periodo | Dimensiones | Métrica | Valor BD | Valor INE | Estado |
|---------|-------------|---------|----------|-----------|--------|
| 2025T1 | Total B-S, Ambas jornadas | horas_pactadas | 151.0 | 151.0 | ✅ OK |
| 2025T1 | Total B-S, Ambas jornadas | horas_efectivas | 151.4 | 151.4 | ✅ OK |
| 2025T1 | Total B-S, Ambas jornadas | HNT IT | 8.3 | 8.3 | ✅ OK |
| 2025T1 | Total B-S, Jornada completa | horas_pactadas | 168.4 | 168.4 | ✅ OK |
| 2025T1 | Total B-S, Jornada parcial | horas_pactadas | 89.3 | 89.3 | ✅ OK |

#### Discrepancias ❌
| Periodo | Dimensiones | Métrica | Valor BD | Valor Esperado | Diferencia |
|---------|-------------|---------|----------|----------------|------------|
| 2025T1 | Industria B-E, Ambas jornadas | horas_pactadas | 165.1 | 152.4 | +12.7 |

**Análisis**: El valor 165.1 viene directamente del CSV. Necesita verificación contra web INE.

### Tablas 6043-6046, 6063: PENDIENTES
- No validadas aún
- Requieren verificación contra sus respectivas URLs del INE

---

## Próximas Validaciones Requeridas

### CRÍTICO - Antes de carga completa:

1. **Resolver discrepancia Industria B-E en tabla 6042**
   - Verificar valor correcto en https://www.ine.es/jaxiT3/Datos.htm?t=6042

2. **Validar tablas restantes (6043-6046, 6063)**
   - Cada tabla debe tener mínimo 3-5 valores validados
   - URLs disponibles en README.md

---

## Criterios de Éxito

Para proceder con carga completa, TODAS las tablas deben cumplir:
- [ ] Mínimo 3 valores validados por tabla
- [ ] Sin discrepancias mayores a 0.1
- [ ] Totales nacionales coinciden exactamente
- [ ] Tasas de absentismo calculadas correctamente

---

## Notas

- Este log debe actualizarse después de cada sesión de validación
- Los valores se almacenan tal cual del INE (151 = 15.1 horas)
- Usar trabajo de exploración agosto 2025 como fuente de verdad