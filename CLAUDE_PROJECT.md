# CLAUDE_PROJECT.md

## Configuración para proyecto en Claude Desktop

Este archivo contiene la configuración necesaria para trabajar con este proyecto en Claude Desktop.

## Información del Proyecto

**Nombre**: AbsentismoEspana v2
**Repositorio**: https://github.com/Akitamo/absentismo-espana
**Branch activo**: v2-refactor
**Descripción**: Sistema modular de agentes para extraer y procesar datos de absentismo laboral del INE de España

## Contexto del Proyecto

Este es un sistema que descarga y analiza datos de absentismo laboral de España desde el Instituto Nacional de Estadística (INE). Utiliza una arquitectura modular con agentes especializados:

1. **Agente Extractor** (Fase 1 - Completada): Descarga 35 tablas CSV del INE con sistema robusto de reintentos
2. **Agente Procesador** (Fase 2 - Pendiente): Limpiará datos y separará dimensiones de métricas

## Estructura del Proyecto

```
absentismo-espana/
├── agent_extractor/       # Agente de extracción (Fase 1)
│   ├── __init__.py       # Orquestador del agente
│   ├── ine_scraper.py    # Detecta actualizaciones
│   └── downloader.py     # Descarga robusta
├── config/
│   └── tables.json       # 35 tablas del INE configuradas
├── data/
│   ├── raw/             # CSVs descargados
│   └── metadata/        # Información de actualizaciones
├── main.py              # CLI principal
└── requirements.txt     # Dependencias mínimas
```

## Comandos Principales

```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar actualizaciones del INE
python main.py --check

# Descargar todas las tablas
python main.py --download-all

# Descargar tabla específica
python main.py --download 6042

# Obtener información de tabla
python main.py --info 6042
```

## Estado Actual

### ✅ Completado (Fase 1)
- Scraper para detectar actualizaciones del INE
- Downloader con reintentos y manejo de encodings
- Configuración JSON de 35 tablas
- CLI funcional

### 🔄 Pendiente (Fase 2)
- Agente procesador de datos
- Separación dimensiones/métricas
- Análisis avanzado de metadata

## Reglas de Desarrollo

1. **Arquitectura modular**: Cada agente es independiente
2. **Sin hardcoding de rutas**: Usar `Path(__file__).parent`
3. **Manejo robusto de errores**: Reintentos y validación
4. **Logging detallado**: Para debugging y auditoría
5. **Configuración centralizada**: Todo en JSON

## Datos que Maneja

35 tablas del INE en 7 categorías:
- Tiempo de trabajo (6 tablas)
- Costes básicos (2 tablas)
- Series temporales (2 tablas)
- Costes detallados (8 tablas)
- Costes salariales (4 tablas)
- Vacantes (8 tablas)
- Otros costes (5 tablas)

## Notas Técnicas

- **Encodings soportados**: UTF-8, Latin-1, ISO-8859-1, CP1252
- **Formato temporal**: Trimestres (2024T1, 2024T2, etc.)
- **Tamaño aproximado**: ~2MB por CSV, ~70MB total
- **Frecuencia actualización INE**: Trimestral

## Próximos Pasos

1. Implementar Fase 2: Agente Procesador
2. Añadir detección automática de dimensiones vs métricas
3. Crear sistema de alertas para nuevos datos
4. Integración con base de datos
5. API REST para consumo de datos