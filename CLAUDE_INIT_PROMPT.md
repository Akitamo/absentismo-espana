# Prompt de Inicialización para Claude Desktop

## Para crear un nuevo proyecto en Claude Desktop, usa este prompt:

---

Quiero que me ayudes a continuar desarrollando un proyecto de extracción y análisis de datos del INE de España. 

El proyecto está en GitHub: https://github.com/Akitamo/absentismo-espana (branch v2-refactor)

## Contexto:
Es un sistema modular con agentes especializados para descargar y procesar 35 tablas de datos de absentismo laboral del Instituto Nacional de Estadística (INE) de España.

## Estado actual:
- **Fase 1 COMPLETADA**: Agente Extractor que descarga CSVs del INE con reintentos robustos
- **Fase 2 PENDIENTE**: Agente Procesador para limpiar datos y separar dimensiones de métricas

## Estructura del proyecto:
```
absentismo-espana/
├── agent_extractor/     # Descarga datos del INE
├── config/tables.json   # 35 tablas configuradas
├── data/raw/           # CSVs descargados
└── main.py             # CLI principal
```

## Lo que necesito:
[ESPECIFICA AQUÍ TU TAREA ESPECÍFICA]

Por ejemplo:
- Implementar la Fase 2: Agente Procesador
- Añadir nueva funcionalidad al extractor
- Crear tests para los agentes
- Documentar el código
- Optimizar el rendimiento
- Etc.

## Comandos útiles:
```bash
# Verificar actualizaciones
python main.py --check

# Descargar todas las tablas
python main.py --download-all
```

Por favor, analiza primero el código existente en el repositorio para entender la arquitectura actual antes de proponer cambios.

---

## Notas para el usuario:

1. **Copia el prompt anterior** y pégalo en Claude Desktop
2. **Reemplaza** la sección "Lo que necesito" con tu tarea específica
3. **Claude analizará** el repositorio y te ayudará con el desarrollo
4. **Recuerda mencionar** el branch v2-refactor si es necesario

## Tips adicionales:

- Si quieres que Claude clone el repo localmente, añade: "Por favor, clona el repositorio y trabaja en local"
- Si necesitas que revise algo específico, añade: "Enfócate especialmente en [archivo/módulo]"
- Si quieres tests, añade: "Incluye tests unitarios para el código nuevo"

## Ejemplo de tarea específica:

```markdown
## Lo que necesito:
Implementar el Agente Procesador (Fase 2) que debe:
1. Leer los CSVs descargados de data/raw/
2. Identificar automáticamente qué columnas son dimensiones (categorías) y cuáles son métricas (valores numéricos)
3. Generar un reporte con la estructura de cada tabla
4. Guardar los datos procesados en data/processed/
5. Mantener la misma arquitectura modular que el agent_extractor
```