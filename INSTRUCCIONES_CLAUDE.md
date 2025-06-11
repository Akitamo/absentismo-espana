# CONTINUACIÓN PROYECTO AbsentismoEspana

## CONTEXTO PREVIO
Proyecto AbsentismoEspana en C:\Users\%USERPROFILE%\AbsentismoEspana\
Ver archivo adjunto "ESPECIFICACIONES_TECNICAS_V2.md" para contexto completo.

## ESTADO ACTUAL (10/06/2025)
1. ✅ Sistema de descarga de CSVs del INE funcionando
2. ✅ 35 archivos CSV descargados exitosamente (37.2 MB) 
3. ✅ Sistema de snapshots implementado con análisis de periodos
4. ✅ Comparador de snapshots para detectar nuevos trimestres
5. ✅ Documentación completa y código limpio en GitHub

## ÚLTIMO PERIODO DETECTADO
- **2024T4** (4º trimestre 2024)
- Próxima actualización esperada: Julio 2025 (T1 2025)

## UBICACIONES CLAVE (RUTAS RELATIVAS)
- Scripts principales: `scripts/extractors/`
- CSVs descargados: `data/raw/csv/` (en la RAÍZ del proyecto, NO en scripts/extractors)
- Snapshots: `snapshots/YYYY-MM-DD/`
- Comparaciones: `scripts/extractors/comparaciones/`
- Configuración: `scripts/extractors/config_csv.json`
- Scripts de análisis: `scripts/analysis/exploratory/`
- Resultados análisis: `scripts/analysis/results/`

## COMANDOS RÁPIDOS
```bash
# Descarga completa con análisis
cd scripts/extractors
python ejecutar_descarga_masiva.py

# Comparar snapshots
python comparar_periodos.py --fecha1 2025-06-10 --ultimo

# Ver snapshots disponibles  
python comparar_periodos.py --listar
```

## PRÓXIMAS TAREAS PENDIENTES
1. [ ] Implementar base de datos PostgreSQL
2. [ ] Crear API REST básica
3. [ ] Automatizar descarga mensual
4. [ ] Sistema de notificaciones
5. [ ] Dashboard PowerBI

## REGLAS CRÍTICAS
- **NUNCA** usar rutas hardcodeadas (C:\Users\aluni\...)
- **SIEMPRE** usar Path(__file__).parent o %USERPROFILE%
- Los CSVs NO van a Git (están en .gitignore)
- Solo los JSONs de snapshots van a Git

## ARCHIVOS DE REFERENCIA
- Especificaciones completas: `ESPECIFICACIONES_TECNICAS_V2.md`
- README del proyecto: `README.md`
- Configuración: `scripts/extractors/config_csv.json`
