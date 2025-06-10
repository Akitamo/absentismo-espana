# Sistema de Análisis de Absentismo España 📊

Sistema automatizado para el análisis de datos de absentismo y siniestralidad laboral en España, basado en datos públicos del INE (Instituto Nacional de Estadística).

## 📋 Descripción

Este proyecto extrae, procesa y analiza datos de la Encuesta Trimestral de Coste Laboral (ETCL) del INE para generar informes sobre:
- Tasas de absentismo laboral por sectores y comunidades autónomas
- Análisis de siniestralidad laboral
- Enfermedades profesionales (CEPROSS)
- Tendencias temporales y comparativas

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- Git
- PostgreSQL (opcional, para almacenamiento de datos)

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/absentismoespana.git
cd absentismoespana
```

2. **Crear entorno virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos (opcional)**
```bash
# Copiar template de configuración
cp config/database.env.template config/database.env

# Editar config/database.env con tus credenciales
```

## 🛠️ Estructura del Proyecto

```
absentismoespana/
├── config/                 # Archivos de configuración
│   └── database.env.template
├── scripts/               # Scripts principales
│   ├── csv_extractors/    # Extractores de datos CSV
│   ├── json_extractors/   # Extractores de datos JSON
│   └── shared/           # Utilidades compartidas
├── data/                  # Datos (no incluidos en git)
│   ├── raw/              # Datos originales
│   └── processed/        # Datos procesados
├── informes/             # Informes generados
├── backups_historicos/   # Respaldos históricos
├── requirements.txt      # Dependencias Python
├── config_paths.py       # Configuración de rutas
└── README.md            # Este archivo
```

## 📊 Uso Básico

### 1. Descargar datos del INE

```bash
cd scripts/csv_extractors
python ejecutar_descarga_masiva.py
```

### 2. Analizar estructura de datos

```bash
python ejecutar_analisis_completo.py
```

### 3. Generar informes

```bash
python generar_informe_factibilidad.py
```

Los informes se generarán en la carpeta `informes/` en formato HTML y JSON.

## 🔧 Configuración

### Rutas del proyecto

Todas las rutas son relativas al directorio del proyecto. El archivo `config_paths.py` gestiona automáticamente las rutas para que funcionen en cualquier sistema.

### Variables de entorno

Para configuración sensible (credenciales de base de datos), usa el archivo `config/database.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=absentismo_db
DB_USER=tu_usuario
DB_PASSWORD=tu_password
```

## 📈 Fuentes de Datos

- **INE - Encuesta Trimestral de Coste Laboral (ETCL)**
- **Ministerio de Trabajo - Estadística de Accidentes de Trabajo**
- **Observatorio de Contingencias Profesionales - CEPROSS**

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Notas Importantes

- Los datos descargados del INE pueden ser grandes (>100MB), por lo que no se incluyen en el repositorio
- Asegúrate de tener suficiente espacio en disco para los datos descargados
- La primera ejecución puede tardar varios minutos en descargar todos los datos

## 🐛 Solución de Problemas

### Error: "No module named 'pandas'"
```bash
# Asegúrate de tener el entorno virtual activado
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Path not found"
```bash
# Ejecutar el script de corrección de rutas
python fix_paths.py
```

## 📄 Licencia

Este proyecto está licenciado bajo MIT License - ver el archivo LICENSE para más detalles.

## 👥 Autores

- Sistema desarrollado para el análisis de datos públicos de absentismo laboral en España

## 🙏 Agradecimientos

- Instituto Nacional de Estadística (INE) por proporcionar los datos públicos
- Adecco Group Institute por el modelo de referencia de análisis
