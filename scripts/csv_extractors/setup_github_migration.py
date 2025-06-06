#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración a GitHub - Preparación de estructura
Crea la nueva estructura de directorios y prepara archivos para Git
"""

import os
import shutil
from pathlib import Path

def setup_github_structure():
    """Crea la estructura de directorios para GitHub"""
    
    # Directorio base para GitHub
    github_base = r"C:\Users\slunagda\GitHub"
    project_dir = os.path.join(github_base, "absentismo-espana")
    
    print("🔧 Creando estructura de directorios para GitHub...")
    
    # Crear directorio GitHub si no existe
    if not os.path.exists(github_base):
        os.makedirs(github_base)
        print(f"✅ Creado: {github_base}")
    
    # Estructura de directorios
    directories = [
        "data/raw/csv",
        "data/processed/dimensions", 
        "data/processed/unified",
        "scripts/extraction",
        "scripts/analysis", 
        "scripts/unification",
        "scripts/utils",
        "reports/html",
        "reports/excel",
        "docs",
        "config",
        "tests"
    ]
    
    for directory in directories:
        full_path = os.path.join(project_dir, directory)
        os.makedirs(full_path, exist_ok=True)
        print(f"✅ Creado: {directory}")
    
    return project_dir

def create_project_files(project_dir):
    """Crea archivos básicos del proyecto"""
    
    # .gitignore
    gitignore_content = """
# Datos sensibles y archivos grandes
data/raw/csv/*.csv
data/raw/xlsx/*.xlsx
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Reportes grandes
reports/html/*.html
reports/excel/*.xlsx

# Configuración local
config/local_config.py
"""
    
    # README.md
    readme_content = """# Análisis de Absentismo Laboral en España

Sistema de análisis de absentismo laboral en España basado en datos del INE (Encuesta Trimestral de Coste Laboral).

## 📊 Descripción

Este proyecto procesa y analiza datos de absentismo laboral del Instituto Nacional de Estadística (INE) para generar insights y visualizaciones en Power BI.

## 🗂️ Estructura del Proyecto

```
├── data/                   # Datos del proyecto
│   ├── raw/csv/           # Datos originales INE (no versionados)
│   └── processed/         # Datos procesados y limpios
├── scripts/               # Scripts de procesamiento
│   ├── extraction/        # Descarga de datos INE
│   ├── analysis/          # Análisis exploratorio
│   └── unification/       # Unificación de tablas
├── reports/               # Informes y resultados
├── docs/                  # Documentación
└── config/                # Configuración
```

## 🚀 Uso

1. Ejecutar scripts de extracción
2. Procesar y unificar datos
3. Generar informes

## 📈 Estado Actual

- ✅ 35 archivos CSV del INE descargados
- ✅ Análisis de estructura completado  
- ✅ Matriz de columnas generada
- 🔄 En progreso: Unificación de tablas dimensión

## 📝 Notas

Proyecto iniciado en mayo 2025 por Santiago Luna García.
"""
    
    # requirements.txt
    requirements_content = """pandas>=2.0.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
chardet>=5.1.0
python-dateutil>=2.8.0
numpy>=1.24.0
"""
    
    # config/__init__.py
    config_init = """# Configuración del proyecto"""
    
    # Escribir archivos
    files_to_create = [
        (".gitignore", gitignore_content),
        ("README.md", readme_content), 
        ("requirements.txt", requirements_content),
        ("config/__init__.py", config_init)
    ]
    
    for filename, content in files_to_create:
        file_path = os.path.join(project_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✅ Creado: {filename}")

def copy_essential_files(project_dir):
    """Copia archivos esenciales del proyecto actual"""
    
    source_dir = r"C:\Users\slunagda\AbsentismoEspana"
    
    # Archivos a copiar
    files_to_copy = [
        # Scripts esenciales
        ("scripts/csv_extractors/analisis_estructura_robusto.py", "scripts/analysis/"),
        ("scripts/csv_extractors/detector_absentismo.py", "scripts/analysis/"),
        ("scripts/csv_extractors/generar_informe_factibilidad_corregido.py", "scripts/analysis/"),
        ("scripts/csv_extractors/ejecutar_analisis_robusto.py", "scripts/analysis/"),
        
        # Resultados importantes (NO los CSV grandes)
        ("informes/matriz_columnas_powerbi.xlsx", "reports/excel/"),
        ("informes/analisis_estructura_robusto.json", "reports/"),
        ("informes/deteccion_absentismo_detallada.json", "reports/"),
    ]
    
    for source_rel, dest_rel in files_to_copy:
        source_path = os.path.join(source_dir, source_rel)
        dest_path = os.path.join(project_dir, dest_rel)
        
        if os.path.exists(source_path):
            # Crear directorio destino si no existe
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
                print(f"✅ Copiado: {source_rel} → {dest_rel}")
            else:
                print(f"⚠️  No es archivo: {source_path}")
        else:
            print(f"❌ No encontrado: {source_path}")

def main():
    """Función principal"""
    print("🚀 Iniciando migración a GitHub...")
    
    # Crear estructura
    project_dir = setup_github_structure()
    
    # Crear archivos del proyecto
    create_project_files(project_dir)
    
    # Copiar archivos esenciales
    copy_essential_files(project_dir)
    
    print(f"\n🎉 ¡Migración preparada!")
    print(f"📍 Nuevo directorio: {project_dir}")
    print(f"\n📋 Siguientes pasos:")
    print(f"1. Crear repositorio en GitHub: https://github.com/new")
    print(f"2. Clonar repo en: C:\\Users\\slunagda\\GitHub\\absentismo-espana")
    print(f"3. Mover archivos generados al repo clonado")
    print(f"4. Hacer primer commit")

if __name__ == "__main__":
    main()
