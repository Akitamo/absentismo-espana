#!/usr/bin/env python
"""
Módulo para analizar los periodos temporales en los archivos CSV del INE
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnalizadorPeriodos:
    """Analiza y extrae información sobre periodos temporales de los CSVs del INE"""
    
    def __init__(self, ruta_csv_dir=None):
        """
        Inicializa el analizador
        
        Args:
            ruta_csv_dir: Directorio donde están los CSVs (por defecto data/raw/csv)
        """
        if ruta_csv_dir is None:
            self.ruta_csv_dir = Path(__file__).parent / "data" / "raw" / "csv"
        else:
            self.ruta_csv_dir = Path(ruta_csv_dir)
            
        # Patrones para detectar periodos
        self.patrones_periodo = [
            r'(\d{4})T(\d)',           # 2024T3
            r'(\d{4}) T(\d)',          # 2024 T3
            r'(\d{4})\s*[Tt]rimestre\s*(\d)',  # 2024 Trimestre 3
            r'T(\d)\s+(\d{4})',        # T3 2024
            r'(\d{4})-T(\d)',          # 2024-T3
            r'(\d{4})Q(\d)',           # 2024Q3
            r'Q(\d)\s+(\d{4})',        # Q3 2024
            r'(\d{4})\s*-\s*(\d{2})',  # 2024-03 (mensual)
            r'(\d{2})/(\d{4})',        # 03/2024 (mensual)
        ]
        
        # Posibles columnas que contienen periodos
        self.columnas_periodo = [
            'periodo', 'Periodo', 'PERIODO',
            'fecha', 'Fecha', 'FECHA',
            'trimestre', 'Trimestre', 'TRIMESTRE',
            'año', 'Año', 'AÑO',
            'quarter', 'Quarter', 'QUARTER',
            'time', 'Time', 'TIME',
            'periodo temporal', 'Periodo temporal',
            'fecha_referencia', 'Fecha referencia'
        ]
    
    def detectar_columna_periodo(self, df):
        """
        Detecta qué columna contiene la información de periodo
        
        Args:
            df: DataFrame de pandas
            
        Returns:
            str: Nombre de la columna o None
        """
        # Primero buscar por nombre
        for col in df.columns:
            for nombre_periodo in self.columnas_periodo:
                if nombre_periodo.lower() in col.lower():
                    return col
        
        # Si no encuentra por nombre, buscar por contenido
        for col in df.columns:
            if df[col].dtype == 'object':  # Solo columnas de texto
                muestra = df[col].dropna().astype(str).head(10)
                for valor in muestra:
                    for patron in self.patrones_periodo:
                        if re.search(patron, valor):
                            return col
        
        return None
    
    def extraer_periodo_de_texto(self, texto):
        """
        Extrae información de periodo de un texto
        
        Args:
            texto: String con información de periodo
            
        Returns:
            dict: {'año': int, 'trimestre': int, 'formato': str} o None
        """
        texto = str(texto).strip()
        
        # Probar cada patrón
        for i, patron in enumerate(self.patrones_periodo):
            match = re.search(patron, texto)
            if match:
                grupos = match.groups()
                
                # Formatear según el patrón
                if i <= 5:  # Patrones trimestrales
                    if i in [0, 1, 2, 4, 5]:  # Año primero
                        año = int(grupos[0])
                        trimestre = int(grupos[1])
                    else:  # Trimestre primero
                        trimestre = int(grupos[0])
                        año = int(grupos[1])
                    
                    return {
                        'año': año,
                        'trimestre': trimestre,
                        'formato': 'trimestral',
                        'texto_original': texto
                    }
                else:  # Patrones mensuales
                    if i == 7:  # YYYY-MM
                        año = int(grupos[0])
                        mes = int(grupos[1])
                    else:  # MM/YYYY
                        mes = int(grupos[0])
                        año = int(grupos[1])
                    
                    # Convertir mes a trimestre
                    trimestre = ((mes - 1) // 3) + 1
                    
                    return {
                        'año': año,
                        'mes': mes,
                        'trimestre': trimestre,
                        'formato': 'mensual',
                        'texto_original': texto
                    }
        
        return None
    
    def analizar_archivo_csv(self, ruta_csv):
        """
        Analiza un archivo CSV para extraer información de periodos
        
        Args:
            ruta_csv: Path al archivo CSV
            
        Returns:
            dict: Información sobre periodos encontrados
        """
        try:
            # Intentar diferentes encodings
            for encoding in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
                try:
                    df = pd.read_csv(ruta_csv, encoding=encoding, sep=None, engine='python')
                    break
                except:
                    continue
            else:
                logger.error(f"No se pudo leer {ruta_csv} con ningún encoding")
                return None
            
            # Detectar columna de periodo
            col_periodo = self.detectar_columna_periodo(df)
            if not col_periodo:
                logger.warning(f"No se encontró columna de periodo en {ruta_csv.name}")
                return {
                    'archivo': ruta_csv.name,
                    'error': 'No se encontró columna de periodo',
                    'total_filas': len(df)
                }
            
            # Extraer todos los periodos únicos
            periodos_unicos = df[col_periodo].dropna().unique()
            periodos_procesados = []
            
            for periodo_texto in periodos_unicos:
                periodo_info = self.extraer_periodo_de_texto(periodo_texto)
                if periodo_info:
                    # Contar filas para este periodo
                    periodo_info['filas'] = len(df[df[col_periodo] == periodo_texto])
                    periodos_procesados.append(periodo_info)
            
            if not periodos_procesados:
                return {
                    'archivo': ruta_csv.name,
                    'error': 'No se pudieron procesar los periodos',
                    'columna_periodo': col_periodo,
                    'total_filas': len(df)
                }
            
            # Ordenar por año y trimestre/mes
            periodos_procesados.sort(key=lambda x: (x['año'], x.get('trimestre', 0), x.get('mes', 0)))
            
            # Extraer información resumida
            primer_periodo = periodos_procesados[0]
            ultimo_periodo = periodos_procesados[-1]
            
            resultado = {
                'archivo': ruta_csv.name,
                'columna_periodo': col_periodo,
                'formato_temporal': periodos_procesados[0]['formato'],
                'total_filas': len(df),
                'total_periodos': len(periodos_procesados),
                'primer_periodo': {
                    'año': primer_periodo['año'],
                    'trimestre': primer_periodo.get('trimestre'),
                    'mes': primer_periodo.get('mes'),
                    'texto': primer_periodo['texto_original'],
                    'filas': primer_periodo['filas']
                },
                'ultimo_periodo': {
                    'año': ultimo_periodo['año'],
                    'trimestre': ultimo_periodo.get('trimestre'),
                    'mes': ultimo_periodo.get('mes'),
                    'texto': ultimo_periodo['texto_original'],
                    'filas': ultimo_periodo['filas']
                },
                'filas_por_periodo': {
                    p['texto_original']: p['filas'] 
                    for p in periodos_procesados[-5:]  # Últimos 5 periodos
                }
            }
            
            # Añadir rango temporal legible
            if resultado['formato_temporal'] == 'trimestral':
                resultado['rango_temporal'] = {
                    'desde': f"{primer_periodo['año']}T{primer_periodo['trimestre']}",
                    'hasta': f"{ultimo_periodo['año']}T{ultimo_periodo['trimestre']}"
                }
            else:
                resultado['rango_temporal'] = {
                    'desde': f"{primer_periodo['año']}-{primer_periodo['mes']:02d}",
                    'hasta': f"{ultimo_periodo['año']}-{ultimo_periodo['mes']:02d}"
                }
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error analizando {ruta_csv}: {str(e)}")
            return {
                'archivo': ruta_csv.name,
                'error': str(e)
            }
    
    def analizar_todos_los_csv(self):
        """
        Analiza todos los archivos CSV en el directorio
        
        Returns:
            dict: Análisis de periodos para todos los archivos
        """
        if not self.ruta_csv_dir.exists():
            logger.error(f"No existe el directorio {self.ruta_csv_dir}")
            return {}
        
        archivos_csv = list(self.ruta_csv_dir.glob("*.csv"))
        if not archivos_csv:
            logger.warning(f"No se encontraron archivos CSV en {self.ruta_csv_dir}")
            return {}
        
        logger.info(f"Analizando {len(archivos_csv)} archivos CSV...")
        
        resultados = {}
        for csv_file in archivos_csv:
            logger.info(f"Analizando {csv_file.name}...")
            analisis = self.analizar_archivo_csv(csv_file)
            if analisis:
                resultados[csv_file.name] = analisis
        
        return resultados
    
    def generar_resumen(self, analisis):
        """
        Genera un resumen del análisis de periodos
        
        Args:
            analisis: dict con los resultados del análisis
            
        Returns:
            dict: Resumen consolidado
        """
        archivos_ok = [a for a in analisis.values() if 'error' not in a]
        archivos_error = [a for a in analisis.values() if 'error' in a]
        
        # Encontrar el periodo más reciente
        ultimo_periodo_global = None
        if archivos_ok:
            # Comparar últimos periodos
            for archivo in archivos_ok:
                ultimo = archivo['ultimo_periodo']
                if not ultimo_periodo_global or \
                   (ultimo['año'], ultimo.get('trimestre', 0)) > \
                   (ultimo_periodo_global['año'], ultimo_periodo_global.get('trimestre', 0)):
                    ultimo_periodo_global = ultimo
        
        resumen = {
            'timestamp': datetime.now().isoformat(),
            'total_archivos': len(analisis),
            'archivos_procesados': len(archivos_ok),
            'archivos_con_error': len(archivos_error),
            'ultimo_periodo_disponible': ultimo_periodo_global,
            'formatos_encontrados': list(set(a['formato_temporal'] for a in archivos_ok if 'formato_temporal' in a)),
            'errores': {a['archivo']: a['error'] for a in archivos_error}
        }
        
        return resumen
    
    def guardar_analisis(self, analisis, ruta_salida):
        """
        Guarda el análisis en un archivo JSON
        
        Args:
            analisis: dict con los resultados
            ruta_salida: Path donde guardar el archivo
        """
        ruta_salida = Path(ruta_salida)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        
        # Añadir resumen al análisis
        analisis_completo = {
            'resumen': self.generar_resumen(analisis),
            'archivos': analisis
        }
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(analisis_completo, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Análisis guardado en {ruta_salida}")


def main():
    """Función principal para testing"""
    analizador = AnalizadorPeriodos()
    resultados = analizador.analizar_todos_los_csv()
    
    if resultados:
        # Mostrar resumen
        resumen = analizador.generar_resumen(resultados)
        print(f"\n📊 RESUMEN DEL ANÁLISIS")
        print(f"Archivos procesados: {resumen['archivos_procesados']}/{resumen['total_archivos']}")
        if resumen['ultimo_periodo_disponible']:
            ultimo = resumen['ultimo_periodo_disponible']
            print(f"Último periodo: {ultimo['texto']} ({ultimo['año']})")
        
        # Guardar resultados
        ruta_salida = Path(__file__).parent / "analisis_periodos_test.json"
        analizador.guardar_analisis(resultados, ruta_salida)
        print(f"\n💾 Resultados guardados en: {ruta_salida}")
    else:
        print("❌ No se pudieron analizar los archivos")


if __name__ == "__main__":
    main()
