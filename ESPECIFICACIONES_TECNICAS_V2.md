# 📋 **ESPECIFICACIONES TÉCNICAS PROYECTO ABSENTISMO v2.1**
**Última actualización: 10 de junio de 2025**

## **PROYECTO: AbsentismoEspana - Sistema de Análisis de Datos ETCL del INE**

### **📁 UBICACIÓN Y ESTRUCTURA ACTUALIZADA**

```
C:\Users\%USERPROFILE%\absentismoespana\
├── convert_docx_to_json_enhanced.py    # Genera URLs desde DOCX del INE
├── urls_etcl_completo.json             # 35 URLs de tablas ETCL
├── setup_proyecto.bat                  # Setup inicial para nuevos usuarios
├── actualizar_github.bat               # Script genérico para commits
├── data/                               # 📁 Datos descargados (raíz del proyecto)
│   ├── raw/
│   │   └── csv/                        # 📊 35 CSVs del INE (~37MB)
│   └── processed/                      # Para futuros datos procesados
├── scripts/
│   ├── extractors/                     # Motor de descarga y análisis
│   │   ├── extractor_csv_ine.py        # Clase principal de descarga
│   │   ├── ejecutar_descarga_masiva.py # Script de ejecución con análisis
│   │   ├── analizar_periodos.py        # 🆕 Analizador de periodos temporales
│   │   ├── comparar_periodos.py        # 🆕 Comparador de snapshots
│   │   ├── config_csv.json             # Configuración de tablas
│   │   ├── utils_csv.py                # Utilidades auxiliares
│   │   ├── descarga_masiva.bat         # Batch para Windows
│   │   └── comparaciones/              # 🆕 Resultados de comparaciones
│   │       ├── YYYY-MM-DD_vs_YYYY-MM-DD.json
│   │       └── YYYY-MM-DD_vs_YYYY-MM-DD.md
│   └── analysis/                       # 🆕 Módulo de análisis exploratorio
│       ├── exploratory/                # Scripts de análisis
│       └── results/                    # Resultados de análisis
├── snapshots/                          # 🆕 Histórico de descargas
│   └── YYYY-MM-DD/                     # Un snapshot por fecha
│       ├── metadata.json               # Info general de la descarga
│       ├── checksums.json              # Tamaños y fechas de archivos
│       ├── summary.json                # Resumen por categorías
│       └── periodos.json               # 🆕 Análisis de periodos temporales
├── logs/                               # Logs detallados
├── backups/                            # Backups automáticos
├── requirements.txt                    # Dependencias (incluye tabulate)
├── README.md                           # Documentación completa
└── .gitignore                          # CSVs y temporales excluidos

### **🚨 REGLAS DE PORTABILIDAD**
1. **NUNCA** usar rutas como `C:\Users\aluni\...`
2. **SIEMPRE** usar:
   - `Path(__file__).parent` en Python
   - `%USERPROFILE%` en documentación
   - Rutas relativas desde la raíz del proyecto
3. **El código debe funcionar** en cualquier equipo sin modificaciones
```

### **🎯 OBJETIVO DEL PROYECTO**

Sistema automatizado para:
1. Descargar los 35 archivos CSV de la ETCL del INE
2. **NUEVO**: Detectar automáticamente nuevos periodos (trimestres)
3. **NUEVO**: Comparar snapshots para identificar actualizaciones
4. Mantener histórico completo de cambios
5. Base para futura integración con BD, API y dashboards

### **🔧 STACK TECNOLÓGICO**

- **Python 3.8+** con dependencias mínimas:
  - pandas (procesamiento CSV)
  - requests (descargas HTTP)
  - python-docx (lectura DOCX)
  - tabulate (formato de tablas)
- **Git** para control de versiones
- **GitHub** como repositorio remoto
- **Diseño portable** sin dependencias del sistema

### **📋 FUNCIONALIDADES IMPLEMENTADAS**

#### **1. Sistema de Descarga**
- ✅ Extracción automática de URLs desde DOCX del INE
- ✅ Descarga de 35 tablas con reintentos inteligentes
- ✅ Validación de integridad de CSVs
- ✅ Sistema de backups automáticos
- ✅ Logs detallados con rotación
- ✅ Configuración por categorías

#### **2. Sistema de Snapshots** 🆕
- ✅ Generación automática post-descarga
- ✅ Metadatos completos de cada descarga
- ✅ Checksums para verificar cambios
- ✅ Versionado en Git (JSON, no CSVs)

#### **3. Análisis de Periodos** 🆕
- ✅ Detección automática de columnas temporales
- ✅ Extracción de último periodo disponible
- ✅ Soporte para formatos: 2024T4, T4 2024, 2024-03
- ✅ Conteo de filas por periodo

#### **4. Comparador de Snapshots** 🆕
- ✅ Detección de nuevos trimestres
- ✅ Identificación de revisiones de datos
- ✅ Informes en JSON y Markdown
- ✅ Histórico de cambios

### **🚀 COMANDOS PRINCIPALES**

#### **Setup inicial (solo primera vez)**
```batch
setup_proyecto.bat
```

#### **Descargar todos los CSVs con análisis**
```batch
cd scripts\extractors
python ejecutar_descarga_masiva.py
```

#### **Comparar snapshots** 🆕
```batch
# Ver snapshots disponibles
python comparar_periodos.py --listar

# Comparar dos fechas
python comparar_periodos.py --fecha1 2025-06-10 --fecha2 2025-06-11

# Comparar con el más reciente
python comparar_periodos.py --fecha1 2025-06-10 --ultimo

# Ver histórico de cambios
python comparar_periodos.py --historico
```

#### **Opciones avanzadas**
```batch
python extractor_csv_ine.py --help
python extractor_csv_ine.py --listar
python extractor_csv_ine.py --verificar-sistema
python extractor_csv_ine.py --activar [categoria]
```

### **📊 DATOS QUE GESTIONA**

#### **35 tablas ETCL en 7 categorías:**
1. **Tiempo de trabajo** (6 tablas) - Horas trabajadas/no trabajadas
2. **Costes básicos** (2 tablas) - Costes por trabajador y hora
3. **Series temporales** (2 tablas) - Evolución histórica
4. **Costes detallados** (8 tablas) - Por sectores/CNAE
5. **Costes salariales** (4 tablas) - Salarios por tipo jornada
6. **Vacantes** (8 tablas) - Puestos vacantes y motivos
7. **Otros costes** (5 tablas) - IT, horas extra, CCAA

#### **Información temporal detectada:**
- **Último periodo disponible**: 2024T4 (4º trimestre 2024)
- **Formato**: Trimestral (T1, T2, T3, T4)
- **Actualización esperada**: Julio 2025 (datos T1 2025)

### **🔍 FLUJO DE TRABAJO ACTUAL**

1. **Descarga inicial** → 35 CSVs + snapshot
2. **Análisis automático** → Detecta periodo 2024T4
3. **Esperar 3 meses** → INE publica nuevos datos
4. **Nueva descarga** → Detecta cambio a 2025T1
5. **Comparación** → Informe de nuevos periodos
6. **Notificación** → (próxima funcionalidad)

### **⚠️ CONSIDERACIONES IMPORTANTES**

#### **Portabilidad**
- NO hardcodear rutas con usuarios específicos
- Usar siempre paths relativos
- Probar en diferentes equipos

#### **Gestión de datos**
- Los CSVs se descargan a `data/raw/csv/` en la RAÍZ del proyecto
- CSVs en .gitignore (37MB, muy grandes para Git)
- Solo JSONs de snapshots van a Git
- Backups locales automáticos

⚠️ **IMPORTANTE SOBRE UBICACIÓN DE DATOS**:
- Los 35 CSVs se guardan en: `C:\Users\%USERPROFILE%\absentismoespana\data\raw\csv\`
- NO en: `scripts/extractors/data/raw/csv/` (esta carpeta no se usa)
- El config usa rutas relativas: `../../data/raw/csv/` (desde scripts/extractors/)

#### **Actualizaciones del INE**
- Datos trimestrales (4 veces al año)
- Pueden revisar datos históricos
- Formatos pueden cambiar sin aviso

### **🐛 PROBLEMAS CONOCIDOS Y SOLUCIONES**

1. **Encoding variable en CSVs**
   - Solución: Probar utf-8, latin1, cp1252, iso-8859-1

2. **Timeouts en descargas**
   - Solución: Sistema de 3 reintentos con backoff

3. **Cambios de formato INE**
   - Solución: Validación post-descarga

4. **Detección de periodos**
   - 31/35 archivos tienen periodos detectables
   - 4 archivos sin columna temporal clara

### **🔄 PRÓXIMOS DESARROLLOS**

#### **Fase 1: Base de Datos** (Próximo)
- PostgreSQL para histórico
- Migración de CSVs existentes
- Actualización incremental

#### **Fase 2: API REST**
- FastAPI/Flask
- Endpoints: /ultimo-periodo, /cambios
- Autenticación con API keys

#### **Fase 3: Automatización**
- Scheduler para descarga mensual
- Notificaciones email/Slack
- Ejecución sin supervisión

#### **Fase 4: Dashboard PowerBI**
- Conexión directa a PostgreSQL
- Visualizaciones interactivas
- Publicación web automática

#### **Fase 5: IA para Análisis**
- Chat con los datos
- Predicciones y tendencias
- Detección de anomalías

### **💻 ESTADO ACTUAL DEL CÓDIGO**

- **Rama**: main
- **Último commit**: Limpieza y documentación completa
- **Tests**: Manuales (automatizar pendiente)
- **Cobertura**: Funcionalidades core 100%
- **Documentación**: README actualizado, código comentado

### **📝 PARA NUEVOS DESARROLLADORES**

1. **Clonar y configurar**:
   ```batch
   git clone https://github.com/Akitamo/absentismo-espana.git
   cd absentismo-espana
   setup_proyecto.bat
   ```

2. **Hacer cambios**:
   - Crear rama: `git checkout -b feature/nueva-funcionalidad`
   - Desarrollar con rutas relativas
   - Probar descarga y comparación
   - Commit con mensajes descriptivos

3. **Subir cambios**:
   ```batch
   actualizar_github.bat
   ```

### **🎯 MÉTRICAS DEL PROYECTO**

- **Archivos gestionados**: 35 CSVs
- **Tamaño total**: ~37MB por descarga
- **Tiempo descarga**: ~3-5 minutos
- **Histórico**: Desde 2025-06-10
- **Precisión detección**: 31/35 archivos (88%)

### **📞 INFORMACIÓN DEL REPOSITORIO**

- **GitHub**: https://github.com/Akitamo/absentismo-espana
- **Visibilidad**: Público
- **Licencia**: MIT
- **Maintainer**: Usuario principal del proyecto

---

**NOTA PARA CLAUDE**: Este documento contiene TODA la información necesaria para continuar el desarrollo. Ante dudas, referirse a esta especificación antes que a memoria de conversaciones anteriores.
