# PROJECT STATUS - AbsentismoEspana

## 📅 Última actualización
**Fecha:** 2025-08-13 16:30
**Sesión:** Configuración de herramientas de desarrollo (MCP DuckDB)

## ✅ Completado recientemente
- [x] Limpieza masiva de archivos (~80% eliminado)
- [x] Merge v2-refactor → main y eliminación de branch
- [x] Creación de sistema de documentación dual (CLAUDE.md estático + CONTEXT.md dinámico)
- [x] Instalación y configuración de MCP DuckDB para exploración de datos
- [x] Agent Extractor (Fase 1) implementado y funcionando
- [x] Sistema de descarga robusto con reintentos
- [x] 35 tablas INE configuradas en config/tables.json

## 🔄 En progreso
- [ ] Implementación del Agent Processor (Fase 2)
  - [ ] Crear estructura base del módulo
  - [ ] Detector de dimensiones vs métricas
  - [ ] Limpieza y transformación de datos
  - [ ] Sistema de salida estructurada

## 📋 Próximos pasos
1. Crear carpeta agent_processor con módulos necesarios
2. Implementar detector automático de dimensiones/métricas
3. Integrar procesador en main.py con nuevos comandos CLI
4. Probar con tablas piloto: 6042, 6043, 6044
5. Documentar formato de salida en data/processed/
6. Merge v2-refactor → main y eliminar branch

## 🔧 Decisiones técnicas tomadas
- **Arquitectura:** Sistema modular con agentes independientes
- **Extracción:** Multi-encoding support (UTF-8, Latin-1, ISO-8859-1, CP1252)
- **Procesamiento:** Usar pandas para manipulación de datos
- **Dimensiones:** Detectar automáticamente columnas categóricas
- **Métricas:** Identificar columnas numéricas con valores
- **CLI:** Interfaz unificada en main.py
- **Desarrollo:** MCP DuckDB para exploración SQL durante desarrollo
- **Producción:** Todo el código final en Python puro (sin MCP)

## ⚠️ Problemas conocidos
- CSVs del INE usan diferentes encodings según la tabla
- Algunos valores numéricos usan "." como separador de miles
- Períodos en formato "YYYYTQ" requieren parsing especial
- Nombres de columnas inconsistentes entre tablas

## 📊 Estado de los datos
- **Raw CSVs:** 35/35 tablas descargadas en data/raw/csv/
- **Procesados:** 0/35 (pendiente implementar processor)
- **Última descarga:** Junio 2025
- **Próxima actualización INE:** Verificar con --check

## 🛠️ Herramientas disponibles
- **MCP DuckDB:** Servidor configurado para consultas SQL sobre CSVs
  - Comando: `claude mcp list` para verificar estado
  - Base de datos: `data/analysis.db`
  - Uso: Exploración y análisis rápido durante desarrollo

## 💡 Notas para la próxima sesión
- Usar MCP DuckDB para explorar estructura de datos antes de implementar agent_processor
- Identificar patrones comunes entre las 35 tablas con SQL
- Revisar si hay actualizaciones en INE con `python main.py --check`
- Implementar agent_processor basándose en los hallazgos de la exploración

## 🚀 Comandos disponibles actualmente
```bash
python main.py --check           # Verificar actualizaciones
python main.py --download-all    # Descargar todas las tablas
python main.py --download 6042   # Descargar tabla específica
python main.py --info 6042       # Info de tabla
```

## 📝 Comandos pendientes de implementar
```bash
python main.py --process-all     # Procesar todas las tablas
python main.py --process 6042    # Procesar tabla específica
python main.py --analyze 6042    # Análisis detallado
```