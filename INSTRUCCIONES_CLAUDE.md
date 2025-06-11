# CONTINUACIÓN PROYECTO AbsentismoEspana

## CONTEXTO PREVIO
Proyecto AbsentismoEspana en C:\Users\%USERPROFILE%\AbsentismoEspana\
Ver archivo adjunto "ESPECIFICACIONES_TECNICAS_V2.md" para contexto completo.

## ESTADO ACTUAL (11/06/2025)
1. ✅ Sistema de descarga de CSVs del INE funcionando
2. ✅ 35 archivos CSV descargados exitosamente (37.2 MB) 
3. ✅ Sistema de snapshots implementado con análisis de periodos
4. ✅ Comparador de snapshots para detectar nuevos trimestres
5. ✅ Documentación completa y código limpio en GitHub
6. ✅ ESTRUCTURA REORGANIZADA Y SIMPLIFICADA (11/06/2025)

## ESTRUCTURA ACTUAL SIMPLIFICADA
```
absentismoespana/
├── data/
│   ├── raw/
│   │   └── csv/                    # 35 CSVs del INE
│   └── processed/
│       ├── analisis/               # Resultados de análisis
│       └── comparaciones/          # Comparaciones entre snapshots
│
├── scripts/
│   ├── descarga/                   # Scripts de descarga
│   ├── procesamiento/              # Scripts de análisis
│   └── utilidades/                 # Config y helpers
│
├── snapshots/                      # Histórico de descargas
├── backups/                        # Respaldos
└── logs/                          # Registros
```

## ÚLTIMO PERIODO DETECTADO
- **2024T4** (4º trimestre 2024)
- Próxima actualización esperada: Julio 2025 (T1 2025)

## COMANDOS PRINCIPALES
```bash
# Descarga completa con análisis
cd scripts\descarga
python ejecutar_descarga_completa.py

# Comparar snapshots
cd scripts\procesamiento
python comparar_snapshots.py --fecha1 2025-06-10 --ultimo

# Análisis exploratorio
python TEST_reconocimiento_inicial.py
```

## PRÓXIMAS TAREAS PENDIENTES
1. [ ] Análisis profundo de métricas de absentismo
2. [ ] Implementar base de datos PostgreSQL
3. [ ] Crear API REST básica
4. [ ] Automatizar descarga mensual
5. [ ] Sistema de notificaciones
6. [ ] Dashboard PowerBI

## REGLAS CRÍTICAS
- **NUNCA** usar rutas hardcodeadas (C:\Users\aluni\...)
- **SIEMPRE** usar Path(__file__).parent o %USERPROFILE%
- Los CSVs NO van a Git (están en .gitignore)
- Solo los JSONs de snapshots van a Git

## 🧪 REGLA OBLIGATORIA PARA NUEVOS SCRIPTS
**TODO script nuevo DEBE**:
1. Crearse con prefijo `TEST_` (ej: `TEST_analizar_tendencias.py`)
2. Una vez validado, renombrarse sin el prefijo
3. Borrar la versión TEST_

**Claude DEBE SIEMPRE**:
- Preguntar antes de crear un script: "¿Es un script nuevo? Lo crearé como TEST_nombre.py"
- Recordar al usuario renombrar cuando esté validado

## ARCHIVOS DE REFERENCIA
- Especificaciones completas: `ESPECIFICACIONES_TECNICAS_V2.md` (actualizado 11/06)
- Resumen reorganización: `RESUMEN_REORGANIZACION.md`
- README del proyecto: `README.md`
- Configuración: `scripts/utilidades/config.py`
- Informe Adecco de referencia incluido como documento

## NOMBRES DE ARCHIVOS ACTUALIZADOS (11/06)
- `descargar_ine.py` (antes extractor_csv_ine.py)
- `ejecutar_descarga_completa.py` (antes ejecutar_descarga_masiva.py)
- `comparar_snapshots.py` (antes comparar_periodos.py)
- `helpers.py` (antes utils_csv.py)
- `config.py` (antes config_csv.json)

## 🎯 CÓMO GARANTIZAR QUE CLAUDE SIGA LAS INSTRUCCIONES

**ANTES de CUALQUIER acción, Claude debe**:
1. Revisar `ESPECIFICACIONES_TECNICAS_V2.md`
2. Verificar `INSTRUCCIONES_CLAUDE.md`
3. Comprobar si existe `RESUMEN_REORGANIZACION.md` para cambios recientes

**AL CREAR cualquier código**:
- Verificar estructura de carpetas actual
- Usar siempre rutas relativas
- Aplicar la regla TEST_ para scripts nuevos
- Verificar que los imports usen las rutas correctas

**RECORDATORIO**: Las especificaciones técnicas son la única fuente de verdad. Si hay dudas, siempre prevalecen sobre cualquier memoria de conversaciones anteriores.
