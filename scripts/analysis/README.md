# 📊 Módulo de Análisis - AbsentismoEspana

## Propósito
Este módulo contiene todos los scripts y herramientas para el análisis de los datos descargados del INE.

## Estructura

```
analysis/
├── exploratory/           # Scripts de análisis exploratorio
│   ├── reconocimiento_inicial.py
│   ├── analisis_exploratorio.py
│   └── utils_analysis.py
│
├── results/              # Resultados generados
│   ├── reconocimiento/   # Outputs del reconocimiento inicial
│   ├── exploratorio/     # Análisis detallados
│   └── visualizations/   # Gráficos y visualizaciones
│
└── README.md            # Esta documentación
```

## Flujo de trabajo

1. **Reconocimiento inicial**: Ejecutar `reconocimiento_inicial.py` para obtener una visión general
2. **Análisis exploratorio**: Usar `analisis_exploratorio.py` para análisis profundo
3. **Modelo dimensional**: Generar propuesta con `generar_modelo_dimensional.py`

## Notas importantes

- Los CSVs originales están en: `../../data/raw/csv/` (raíz del proyecto)
- Todos los resultados se guardan con fecha para mantener histórico
- Los scripts usan rutas relativas para portabilidad
