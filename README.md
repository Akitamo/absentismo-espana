# AbsentismoEspana

Sistema modular para la extracción y procesamiento de datos de absentismo laboral del Instituto Nacional de Estadística (INE) de España.

## 📊 Descripción

Este proyecto automatiza la descarga y procesamiento de los datos de la Encuesta Trimestral de Coste Laboral (ETCL) del INE, específicamente las 35 tablas relacionadas con costes laborales, tiempo de trabajo y absentismo en España.

## 🚀 Características

- **Extracción automática** de 35 tablas del INE
- **Detección de actualizaciones** en los datos fuente
- **Procesamiento robusto** con soporte multi-encoding
- **Arquitectura modular** con agentes independientes
- **CLI intuitiva** para todas las operaciones

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/Akitamo/absentismo-espana.git
cd absentismo-espana
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Verificar actualizaciones en INE
```bash
python main.py --check
```

### Descargar datos

Todas las tablas:
```bash
python main.py --download-all
```

Tabla específica:
```bash
python main.py --download 6042
```

### Obtener información de una tabla
```bash
python main.py --info 6042
```

### Procesar datos (próximamente)
```bash
python main.py --process-all
python main.py --process 6042
```

## 📁 Estructura del Proyecto

```
absentismo-espana/
├── agent_extractor/    # Módulo de extracción de datos
├── agent_processor/    # Módulo de procesamiento (en desarrollo)
├── config/            # Configuración de tablas
├── data/
│   ├── raw/          # CSVs originales del INE
│   ├── processed/    # Datos procesados
│   └── metadata/     # Información de actualizaciones
├── main.py           # Interfaz CLI principal
└── requirements.txt  # Dependencias Python
```

## 📊 Datos Disponibles

El sistema procesa 35 tablas del INE organizadas en 7 categorías:

- **Tiempo de trabajo** (6 tablas): Horas trabajadas y no trabajadas
- **Costes básicos** (2 tablas): Costes por trabajador y hora
- **Series temporales** (2 tablas): Evolución histórica
- **Costes detallados** (8 tablas): Desglose por sector y actividad
- **Costes salariales** (4 tablas): Costes por tipo de jornada
- **Vacantes** (8 tablas): Puestos vacantes y motivos
- **Otros costes** (5 tablas): IT, horas extra, regional

## 🔄 Estado del Proyecto

- ✅ **Fase 1:** Extractor de datos (completado)
- 🔄 **Fase 2:** Procesador de datos (en desarrollo)
- ⏳ **Fase 3:** Análisis y visualización (planificado)

Para ver el estado detallado del proyecto, consultar [CONTEXT.md](CONTEXT.md).

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🔗 Enlaces

- [Instituto Nacional de Estadística (INE)](https://www.ine.es)
- [Encuesta Trimestral de Coste Laboral](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736045053&menu=ultiDatos&idp=1254735976596)

## 📧 Contacto

Para preguntas o sugerencias sobre este proyecto, por favor abrir un [issue](https://github.com/Akitamo/absentismo-espana/issues) en GitHub.

---

**Nota:** Este proyecto no está afiliado con el Instituto Nacional de Estadística. Es una herramienta independiente para facilitar el acceso y procesamiento de datos públicos.
