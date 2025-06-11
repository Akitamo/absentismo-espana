#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
reconocimiento_inicial.py
------------------------
Script de reconocimiento rápido de los 35 archivos CSV del INE.
Objetivo: Obtener una visión general antes del análisis profundo.

Autor: Sistema de Análisis AbsentismoEspana
Fecha: 2025-06-11
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Añadir el directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))

# Importar utilidades del extractor si las necesitamos
try:
    from scripts.extractors.utils_csv import detectar_encoding
except ImportError:
    print("No se pudo importar utils_csv, usando detección básica de encoding")
    
    def detectar_encoding(filepath: str) -> str:
        """Detección básica de encoding si no tenemos utils_csv"""
        encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    f.read(1000)
                return enc
            except:
                continue
        return 'utf-8'


class ReconocimientoInicial:
    """Clase para realizar reconocimiento inicial de CSVs del INE"""
    
    def __init__(self):
        self.csv_dir = ROOT_DIR / "data" / "raw" / "csv"
        self.results_dir = ROOT_DIR / "scripts" / "analysis" / "results" / "reconocimiento"
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.resumen = []
        self.columnas_comunes = {}
        self.problemas = []
        
    def verificar_directorios(self) -> bool:
        """Verifica que existan los directorios necesarios"""
        if not self.csv_dir.exists():
            print(f"❌ No existe el directorio de CSVs: {self.csv_dir}")
            return False
            
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)
            
        return True
        
    def listar_archivos_csv(self) -> List[Path]:
        """Lista todos los archivos CSV disponibles"""
        return sorted(list(self.csv_dir.glob("*.csv")))
        
    def analizar_archivo(self, filepath: Path) -> Dict:
        """Analiza un archivo CSV individual"""
        info = {
            'archivo': filepath.name,
            'tamaño_mb': round(filepath.stat().st_size / 1024 / 1024, 2),
            'encoding': 'desconocido',
            'status': 'error',
            'filas': 0,
            'columnas': 0,
            'columnas_lista': [],
            'error': None
        }
        
        try:
            # Detectar encoding
            info['encoding'] = detectar_encoding(str(filepath))
            
            # Leer primeras filas para obtener estructura
            df = pd.read_csv(filepath, encoding=info['encoding'], nrows=5)
            
            # Obtener información básica
            info['columnas'] = len(df.columns)
            info['columnas_lista'] = df.columns.tolist()
            
            # Contar filas sin cargar todo el archivo
            with open(filepath, 'r', encoding=info['encoding']) as f:
                info['filas'] = sum(1 for line in f) - 1  # -1 por el header
                
            info['status'] = 'ok'
            
        except Exception as e:
            info['error'] = str(e)
            self.problemas.append({
                'archivo': filepath.name,
                'error': str(e)
            })
            
        return info
        
    def detectar_columnas_comunes(self):
        """Detecta columnas que aparecen en múltiples archivos"""
        todas_columnas = {}
        
        for archivo_info in self.resumen:
            if archivo_info['status'] == 'ok':
                for col in archivo_info['columnas_lista']:
                    if col not in todas_columnas:
                        todas_columnas[col] = []
                    todas_columnas[col].append(archivo_info['archivo'])
                    
        # Filtrar solo columnas que aparecen en más de un archivo
        self.columnas_comunes = {
            col: {
                'archivos': archivos,
                'frecuencia': len(archivos),
                'porcentaje': round(len(archivos) / len(self.resumen) * 100, 1)
            }
            for col, archivos in todas_columnas.items()
            if len(archivos) > 1
        }
        
    def generar_reporte(self):
        """Genera el reporte de reconocimiento"""
        # Ordenar resumen por nombre de archivo
        self.resumen.sort(key=lambda x: x['archivo'])
        
        # Crear reporte completo
        reporte = {
            'metadata': {
                'timestamp': self.timestamp,
                'total_archivos': len(self.resumen),
                'archivos_ok': sum(1 for x in self.resumen if x['status'] == 'ok'),
                'archivos_error': sum(1 for x in self.resumen if x['status'] == 'error'),
                'tamaño_total_mb': sum(x['tamaño_mb'] for x in self.resumen),
                'fecha_analisis': datetime.now().isoformat()
            },
            'archivos': self.resumen,
            'columnas_comunes': self.columnas_comunes,
            'problemas': self.problemas
        }
        
        # Guardar JSON
        json_path = self.results_dir / f"reconocimiento_{self.timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
            
        # Guardar versión Markdown para lectura fácil
        self.generar_markdown(reporte)
        
        return reporte
        
    def generar_markdown(self, reporte: Dict):
        """Genera versión Markdown del reporte"""
        md_path = self.results_dir / f"reconocimiento_{self.timestamp}.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Reconocimiento Inicial - Archivos ETCL\n")
            f.write(f"**Fecha**: {reporte['metadata']['fecha_analisis']}\n\n")
            
            # Resumen
            f.write("## Resumen\n")
            f.write(f"- Total archivos: {reporte['metadata']['total_archivos']}\n")
            f.write(f"- Archivos OK: {reporte['metadata']['archivos_ok']}\n")
            f.write(f"- Archivos con error: {reporte['metadata']['archivos_error']}\n")
            f.write(f"- Tamaño total: {reporte['metadata']['tamaño_total_mb']:.1f} MB\n\n")
            
            # Tabla de archivos
            f.write("## Detalle de Archivos\n\n")
            f.write("| Archivo | Tamaño (MB) | Filas | Columnas | Encoding | Status |\n")
            f.write("|---------|-------------|--------|----------|----------|--------|\n")
            
            for info in reporte['archivos']:
                f.write(f"| {info['archivo']} | {info['tamaño_mb']} | ")
                f.write(f"{info['filas']:,} | {info['columnas']} | ")
                f.write(f"{info['encoding']} | {info['status']} |\n")
                
            # Columnas más comunes
            f.write("\n## Top 10 Columnas Más Comunes\n\n")
            columnas_ordenadas = sorted(
                reporte['columnas_comunes'].items(),
                key=lambda x: x[1]['frecuencia'],
                reverse=True
            )[:10]
            
            f.write("| Columna | Aparece en | Porcentaje |\n")
            f.write("|---------|------------|------------|\n")
            
            for col, info in columnas_ordenadas:
                f.write(f"| {col} | {info['frecuencia']} archivos | {info['porcentaje']}% |\n")
                
            # Problemas encontrados
            if reporte['problemas']:
                f.write("\n## Problemas Encontrados\n\n")
                for problema in reporte['problemas']:
                    f.write(f"- **{problema['archivo']}**: {problema['error']}\n")
                    
    def ejecutar(self):
        """Ejecuta el reconocimiento completo"""
        print("🔍 Iniciando reconocimiento inicial de archivos CSV del INE...")
        
        # Verificar directorios
        if not self.verificar_directorios():
            return None
            
        # Listar archivos
        archivos = self.listar_archivos_csv()
        print(f"\n📁 Encontrados {len(archivos)} archivos CSV")
        
        # Analizar cada archivo
        print("\n📊 Analizando archivos...")
        for i, archivo in enumerate(archivos, 1):
            print(f"  [{i}/{len(archivos)}] {archivo.name}...", end='')
            info = self.analizar_archivo(archivo)
            self.resumen.append(info)
            print(f" {'✓' if info['status'] == 'ok' else '✗'}")
            
        # Detectar columnas comunes
        print("\n🔗 Detectando columnas comunes...")
        self.detectar_columnas_comunes()
        
        # Generar reporte
        print("\n📝 Generando reporte...")
        reporte = self.generar_reporte()
        
        print(f"\n✅ Reconocimiento completado!")
        print(f"   - Resultados guardados en: {self.results_dir}")
        
        # Mostrar resumen
        print("\n" + "="*50)
        print("RESUMEN DEL RECONOCIMIENTO")
        print("="*50)
        print(f"Total archivos analizados: {reporte['metadata']['total_archivos']}")
        print(f"Archivos procesados OK: {reporte['metadata']['archivos_ok']}")
        print(f"Archivos con errores: {reporte['metadata']['archivos_error']}")
        print(f"Tamaño total: {reporte['metadata']['tamaño_total_mb']:.1f} MB")
        
        # Top 5 columnas comunes
        print("\nTop 5 columnas más comunes:")
        columnas_top = sorted(
            self.columnas_comunes.items(),
            key=lambda x: x[1]['frecuencia'],
            reverse=True
        )[:5]
        
        for col, info in columnas_top:
            print(f"  - '{col}': aparece en {info['frecuencia']} archivos ({info['porcentaje']}%)")
            
        return reporte


if __name__ == "__main__":
    reconocimiento = ReconocimientoInicial()
    reconocimiento.ejecutar()
