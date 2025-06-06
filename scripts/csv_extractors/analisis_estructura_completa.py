"""
Analizador de Estructura Completa - Sistema de Absentismo España
Examina la estructura y contenido de todas las tablas CSV descargadas del INE
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional
import numpy as np
import warnings

# Suprimir warnings de pandas
warnings.filterwarnings('ignore')

class AnalizadorEstructura:
    """
    Analizador completo de estructura de archivos CSV del INE
    """
    
    def __init__(self, data_dir: str = "../../data/raw/csv/"):
        """
        Inicializa el analizador
        
        Args:
            data_dir: Directorio con los archivos CSV
        """
        self.data_dir = Path(data_dir)
        self.logger = self._configurar_logging()
        self.resultados = {
            'metadatos_generales': {},
            'analisis_por_tabla': {},
            'resumen_ejecutivo': {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info("AnalizadorEstructura inicializado")
    
    def _configurar_logging(self) -> logging.Logger:
        """Configura el logging"""
        logger = logging.getLogger('AnalizadorEstructura')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def obtener_archivos_csv(self) -> List[Path]:
        """Obtiene lista de todos los archivos CSV disponibles"""
        if not self.data_dir.exists():
            self.logger.error(f"Directorio no encontrado: {self.data_dir}")
            return []
        
        archivos = list(self.data_dir.glob("*.csv"))
        self.logger.info(f"Encontrados {len(archivos)} archivos CSV")
        
        return sorted(archivos)
    
    def extraer_id_tabla(self, archivo: Path) -> str:
        """Extrae el ID de tabla del nombre del archivo"""
        nombre = archivo.stem
        # El ID está al inicio del nombre del archivo
        id_tabla = nombre.split('_')[0]
        return id_tabla
    
    def analizar_archivo_csv(self, archivo: Path) -> Dict[str, Any]:
        """
        Analiza un archivo CSV individual
        
        Args:
            archivo: Path del archivo CSV
            
        Returns:
            Diccionario con análisis completo del archivo
        """
        id_tabla = self.extraer_id_tabla(archivo)
        self.logger.info(f"Analizando tabla {id_tabla}: {archivo.name}")
        
        analisis = {
            'id_tabla': id_tabla,
            'nombre_archivo': archivo.name,
            'ruta_completa': str(archivo),
            'tamaño_bytes': archivo.stat().st_size,
            'tamaño_mb': round(archivo.stat().st_size / (1024*1024), 2),
            'fecha_modificacion': datetime.fromtimestamp(archivo.stat().st_mtime).isoformat(),
            'estructura': {},
            'contenido': {},
            'calidad_datos': {},
            'relevancia_absentismo': {},
            'errores': []
        }
        
        try:
            # Leer archivo CSV
            df = pd.read_csv(archivo, encoding='utf-8', low_memory=False)
            
            # Análisis de estructura
            analisis['estructura'] = {
                'total_filas': len(df),
                'total_columnas': len(df.columns),
                'columnas': list(df.columns),
                'tipos_datos': df.dtypes.astype(str).to_dict(),
                'memoria_usage_mb': round(df.memory_usage(deep=True).sum() / (1024*1024), 2)
            }
            
            # Análisis de contenido
            analisis['contenido'] = self._analizar_contenido(df)
            
            # Análisis de calidad de datos
            analisis['calidad_datos'] = self._analizar_calidad_datos(df)
            
            # Análisis específico para absentismo
            analisis['relevancia_absentismo'] = self._analizar_relevancia_absentismo(df, id_tabla)
            
            self.logger.info(f"✅ Tabla {id_tabla} analizada: {len(df):,} filas, {len(df.columns)} columnas")
            
        except Exception as e:
            error_msg = f"Error analizando {archivo.name}: {str(e)}"
            self.logger.error(error_msg)
            analisis['errores'].append(error_msg)
        
        return analisis
    
    def _analizar_contenido(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza el contenido del DataFrame"""
        contenido = {
            'filas_unicas': 0,
            'columnas_numericas': [],
            'columnas_texto': [],
            'columnas_fecha': [],
            'valores_unicos_por_columna': {},
            'rango_temporal': {},
            'muestras_datos': {}
        }
        
        try:
            # Filas únicas
            contenido['filas_unicas'] = len(df.drop_duplicates())
            
            # Clasificar columnas por tipo
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    contenido['columnas_numericas'].append(col)
                elif df[col].dtype == 'object':
                    # Intentar detectar fechas
                    if self._es_columna_fecha(df[col]):
                        contenido['columnas_fecha'].append(col)
                    else:
                        contenido['columnas_texto'].append(col)
            
            # Valores únicos por columna (máximo 100 para evitar sobrecarga)
            for col in df.columns:
                valores_unicos = df[col].nunique()
                contenido['valores_unicos_por_columna'][col] = valores_unicos
            
            # Detectar rango temporal
            contenido['rango_temporal'] = self._detectar_rango_temporal(df)
            
            # Muestras de datos (primeras 3 filas)
            contenido['muestras_datos'] = df.head(3).to_dict('records')
            
        except Exception as e:
            self.logger.warning(f"Error en análisis de contenido: {e}")
        
        return contenido
    
    def _analizar_calidad_datos(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza la calidad de los datos"""
        calidad = {
            'completitud': {},
            'consistencia': {},
            'valores_atipicos': {},
            'duplicados': 0,
            'score_calidad': 0
        }
        
        try:
            # Completitud (valores faltantes)
            total_celdas = len(df) * len(df.columns)
            valores_faltantes = df.isnull().sum().sum()
            
            calidad['completitud'] = {
                'total_celdas': total_celdas,
                'valores_faltantes': int(valores_faltantes),
                'porcentaje_completo': round((1 - valores_faltantes/total_celdas) * 100, 2),
                'faltantes_por_columna': df.isnull().sum().to_dict()
            }
            
            # Duplicados
            calidad['duplicados'] = len(df) - len(df.drop_duplicates())
            
            # Score de calidad (0-100)
            score = calidad['completitud']['porcentaje_completo']
            if calidad['duplicados'] > 0:
                score -= min(10, calidad['duplicados'] / len(df) * 100)
            
            calidad['score_calidad'] = max(0, round(score, 1))
            
        except Exception as e:
            self.logger.warning(f"Error en análisis de calidad: {e}")
        
        return calidad
    
    def _analizar_relevancia_absentismo(self, df: pd.DataFrame, id_tabla: str) -> Dict[str, Any]:
        """Analiza la relevancia específica para absentismo"""
        relevancia = {
            'score_relevancia': 0,
            'columnas_clave_encontradas': [],
            'palabras_clave_detectadas': [],
            'tipo_datos_absentismo': 'ninguno',
            'utilidad_estimada': 'baja'
        }
        
        # Palabras clave para absentismo
        palabras_clave_tiempo = ['horas', 'tiempo', 'trabajo', 'jornada', 'efectiva', 'pactada']
        palabras_clave_ausencia = ['ausencia', 'baja', 'IT', 'incapacidad', 'permiso', 'vacaciones']
        palabras_clave_coste = ['coste', 'laboral', 'salario', 'retribucion']
        
        try:
            columnas_str = ' '.join(df.columns).lower()
            score = 0
            
            # Buscar palabras clave en nombres de columnas
            for palabra in palabras_clave_tiempo:
                if palabra in columnas_str:
                    relevancia['palabras_clave_detectadas'].append(palabra)
                    score += 3
            
            for palabra in palabras_clave_ausencia:
                if palabra in columnas_str:
                    relevancia['palabras_clave_detectadas'].append(palabra)
                    score += 5  # Mayor peso para ausencias
            
            for palabra in palabras_clave_coste:
                if palabra in columnas_str:
                    relevancia['palabras_clave_detectadas'].append(palabra)
                    score += 2
            
            # Bonus por ID de tabla específicos (basado en conocimiento previo)
            tablas_muy_relevantes = ['6042', '6043', '6044', '6045', '6046', '6063']  # Tiempo trabajo
            tablas_relevantes = ['6038', '6039', '6040', '6041', '6056']  # Costes salariales y IT
            
            if id_tabla in tablas_muy_relevantes:
                score += 10
                relevancia['tipo_datos_absentismo'] = 'tiempo_trabajo'
            elif id_tabla in tablas_relevantes:
                score += 5
                relevancia['tipo_datos_absentismo'] = 'costes_relacionados'
            
            # Buscar columnas específicamente útiles
            for col in df.columns:
                col_lower = col.lower()
                if any(kw in col_lower for kw in ['horas_no_trabajadas', 'horas_efectivas', 'absentismo']):
                    relevancia['columnas_clave_encontradas'].append(col)
                    score += 8
            
            # Determinar utilidad
            if score >= 15:
                relevancia['utilidad_estimada'] = 'muy_alta'
            elif score >= 10:
                relevancia['utilidad_estimada'] = 'alta'
            elif score >= 5:
                relevancia['utilidad_estimada'] = 'media'
            else:
                relevancia['utilidad_estimada'] = 'baja'
            
            relevancia['score_relevancia'] = min(100, score)
            
        except Exception as e:
            self.logger.warning(f"Error en análisis de relevancia: {e}")
        
        return relevancia
    
    def _es_columna_fecha(self, serie: pd.Series) -> bool:
        """Detecta si una columna contiene fechas"""
        try:
            # Intentar convertir una muestra a fecha
            muestra = serie.dropna().head(10)
            if len(muestra) == 0:
                return False
            
            for valor in muestra:
                if isinstance(valor, str) and any(sep in valor for sep in ['-', '/', '.']):
                    try:
                        pd.to_datetime(valor)
                        return True
                    except:
                        continue
            return False
        except:
            return False
    
    def _detectar_rango_temporal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta el rango temporal de los datos"""
        rango = {
            'tiene_datos_temporales': False,
            'columnas_temporales': [],
            'periodo_inicio': None,
            'periodo_fin': None,
            'años_cobertura': []
        }
        
        try:
            # Buscar columnas que podrían ser fechas o períodos
            for col in df.columns:
                col_lower = col.lower()
                if any(kw in col_lower for kw in ['fecha', 'periodo', 'trimestre', 'año', 'mes']):
                    rango['columnas_temporales'].append(col)
                    rango['tiene_datos_temporales'] = True
                    
                    # Intentar extraer años
                    valores_unicos = df[col].dropna().unique()
                    for valor in valores_unicos[:20]:  # Limitar a 20 valores
                        if isinstance(valor, (int, float)) and 2000 <= valor <= 2030:
                            rango['años_cobertura'].append(int(valor))
                        elif isinstance(valor, str):
                            # Buscar años en strings
                            import re
                            años_encontrados = re.findall(r'\b(20[0-3][0-9])\b', str(valor))
                            rango['años_cobertura'].extend([int(año) for año in años_encontrados])
            
            # Limpiar años duplicados y ordenar
            if rango['años_cobertura']:
                rango['años_cobertura'] = sorted(list(set(rango['años_cobertura'])))
                rango['periodo_inicio'] = min(rango['años_cobertura'])
                rango['periodo_fin'] = max(rango['años_cobertura'])
            
        except Exception as e:
            self.logger.warning(f"Error detectando rango temporal: {e}")
        
        return rango
    
    def analizar_todas_las_tablas(self) -> Dict[str, Any]:
        """
        Ejecuta análisis completo de todas las tablas CSV
        
        Returns:
            Diccionario con resultados completos del análisis
        """
        archivos = self.obtener_archivos_csv()
        
        if not archivos:
            self.logger.error("No se encontraron archivos CSV para analizar")
            return {'error': 'No hay archivos CSV disponibles'}
        
        self.logger.info(f"🚀 Iniciando análisis de {len(archivos)} archivos CSV")
        
        # Analizar cada archivo
        for archivo in archivos:
            id_tabla = self.extraer_id_tabla(archivo)
            analisis = self.analizar_archivo_csv(archivo)
            self.resultados['analisis_por_tabla'][id_tabla] = analisis
        
        # Generar resumen ejecutivo
        self.resultados['resumen_ejecutivo'] = self._generar_resumen_ejecutivo()
        
        # Generar metadatos generales
        self.resultados['metadatos_generales'] = self._generar_metadatos_generales()
        
        self.logger.info("✅ Análisis completo finalizado")
        
        return self.resultados
    
    def _generar_resumen_ejecutivo(self) -> Dict[str, Any]:
        """Genera resumen ejecutivo del análisis"""
        resumen = {
            'total_tablas': len(self.resultados['analisis_por_tabla']),
            'total_registros': 0,
            'total_columnas': 0,
            'tamaño_total_mb': 0,
            'periodo_cobertura': {'inicio': None, 'fin': None},
            'calidad_promedio': 0,
            'tablas_por_relevancia': {'muy_alta': [], 'alta': [], 'media': [], 'baja': []},
            'tipos_datos_absentismo': {},
            'estadisticas_globales': {}
        }
        
        scores_calidad = []
        años_todos = []
        
        for id_tabla, analisis in self.resultados['analisis_por_tabla'].items():
            if 'errores' in analisis and analisis['errores']:
                continue
                
            # Acumular estadísticas
            if 'estructura' in analisis:
                resumen['total_registros'] += analisis['estructura'].get('total_filas', 0)
                resumen['total_columnas'] += analisis['estructura'].get('total_columnas', 0)
            
            resumen['tamaño_total_mb'] += analisis.get('tamaño_mb', 0)
            
            # Calidad
            if 'calidad_datos' in analisis and 'score_calidad' in analisis['calidad_datos']:
                scores_calidad.append(analisis['calidad_datos']['score_calidad'])
            
            # Relevancia
            if 'relevancia_absentismo' in analisis:
                utilidad = analisis['relevancia_absentismo'].get('utilidad_estimada', 'baja')
                resumen['tablas_por_relevancia'][utilidad].append(id_tabla)
                
                tipo_datos = analisis['relevancia_absentismo'].get('tipo_datos_absentismo', 'ninguno')
                if tipo_datos not in resumen['tipos_datos_absentismo']:
                    resumen['tipos_datos_absentismo'][tipo_datos] = []
                resumen['tipos_datos_absentismo'][tipo_datos].append(id_tabla)
            
            # Años de cobertura
            if ('contenido' in analisis and 
                'rango_temporal' in analisis['contenido'] and 
                analisis['contenido']['rango_temporal'].get('años_cobertura')):
                años_todos.extend(analisis['contenido']['rango_temporal']['años_cobertura'])
        
        # Calcular promedios
        if scores_calidad:
            resumen['calidad_promedio'] = round(sum(scores_calidad) / len(scores_calidad), 1)
        
        if años_todos:
            años_unicos = sorted(list(set(años_todos)))
            resumen['periodo_cobertura'] = {
                'inicio': min(años_unicos),
                'fin': max(años_unicos),
                'años_disponibles': años_unicos
            }
        
        # Redondear tamaño total
        resumen['tamaño_total_mb'] = round(resumen['tamaño_total_mb'], 1)
        
        return resumen
    
    def _generar_metadatos_generales(self) -> Dict[str, Any]:
        """Genera metadatos generales del análisis"""
        return {
            'directorio_analizado': str(self.data_dir),
            'fecha_analisis': datetime.now().isoformat(),
            'version_pandas': pd.__version__,
            'total_archivos_procesados': len(self.resultados['analisis_por_tabla']),
            'archivos_con_errores': len([a for a in self.resultados['analisis_por_tabla'].values() 
                                       if a.get('errores', [])]),
            'columnas_mas_comunes': self._obtener_columnas_mas_comunes(),
            'estadisticas_tamaños': self._obtener_estadisticas_tamaños()
        }
    
    def _obtener_columnas_mas_comunes(self) -> List[Dict[str, Any]]:
        """Obtiene las columnas más comunes entre todas las tablas"""
        contador_columnas = {}
        
        for analisis in self.resultados['analisis_por_tabla'].values():
            if 'estructura' in analisis and 'columnas' in analisis['estructura']:
                for col in analisis['estructura']['columnas']:
                    col_lower = col.lower()
                    if col_lower not in contador_columnas:
                        contador_columnas[col_lower] = {'nombre': col, 'frecuencia': 0, 'tablas': []}
                    contador_columnas[col_lower]['frecuencia'] += 1
                    contador_columnas[col_lower]['tablas'].append(analisis['id_tabla'])
        
        # Ordenar por frecuencia
        columnas_ordenadas = sorted(contador_columnas.values(), 
                                  key=lambda x: x['frecuencia'], reverse=True)
        
        return columnas_ordenadas[:20]  # Top 20
    
    def _obtener_estadisticas_tamaños(self) -> Dict[str, Any]:
        """Obtiene estadísticas de tamaños de archivos"""
        tamaños = [a.get('tamaño_mb', 0) for a in self.resultados['analisis_por_tabla'].values()]
        
        if not tamaños:
            return {}
        
        return {
            'tamaño_minimo_mb': round(min(tamaños), 2),
            'tamaño_maximo_mb': round(max(tamaños), 2),
            'tamaño_promedio_mb': round(sum(tamaños) / len(tamaños), 2),
            'tamaño_mediana_mb': round(np.median(tamaños), 2)
        }
    
    def guardar_resultados(self, archivo_salida: str = "../../informes/analisis_estructura_35_tablas.json") -> bool:
        """
        Guarda los resultados del análisis en archivo JSON
        
        Args:
            archivo_salida: Ruta del archivo de salida
            
        Returns:
            True si se guardó correctamente
        """
        try:
            ruta_salida = Path(archivo_salida)
            ruta_salida.parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"✅ Resultados guardados en: {ruta_salida}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando resultados: {e}")
            return False
    
    def mostrar_resumen_consola(self) -> None:
        """Muestra un resumen del análisis en la consola"""
        if not self.resultados.get('resumen_ejecutivo'):
            self.logger.warning("No hay resultados para mostrar")
            return
        
        resumen = self.resultados['resumen_ejecutivo']
        
        print("\n" + "="*80)
        print("📊 RESUMEN EJECUTIVO - ANÁLISIS ESTRUCTURA COMPLETA")
        print("="*80)
        
        print(f"📁 Total tablas analizadas: {resumen['total_tablas']}")
        print(f"📈 Total registros: {resumen['total_registros']:,}")
        print(f"🔢 Total columnas: {resumen['total_columnas']:,}")
        print(f"💾 Tamaño total: {resumen['tamaño_total_mb']} MB")
        print(f"⭐ Calidad promedio: {resumen['calidad_promedio']}%")
        
        if resumen['periodo_cobertura']['inicio']:
            print(f"📅 Periodo cobertura: {resumen['periodo_cobertura']['inicio']}-{resumen['periodo_cobertura']['fin']}")
        
        print(f"\n🎯 RELEVANCIA PARA ABSENTISMO:")
        for nivel, tablas in resumen['tablas_por_relevancia'].items():
            if tablas:
                print(f"   {nivel.upper()}: {len(tablas)} tablas - {tablas}")
        
        print(f"\n📋 TIPOS DE DATOS:")
        for tipo, tablas in resumen['tipos_datos_absentismo'].items():
            if tablas and tipo != 'ninguno':
                print(f"   {tipo}: {tablas}")
        
        print("\n" + "="*80)

def main():
    """Función principal para ejecutar el análisis"""
    print("🚀 INICIANDO ANÁLISIS ESTRUCTURA COMPLETA")
    print("="*60)
    
    # Crear analizador
    analizador = AnalizadorEstructura()
    
    # Ejecutar análisis
    resultados = analizador.analizar_todas_las_tablas()
    
    if 'error' in resultados:
        print(f"❌ Error: {resultados['error']}")
        return
    
    # Mostrar resumen en consola
    analizador.mostrar_resumen_consola()
    
    # Guardar resultados
    if analizador.guardar_resultados():
        print(f"✅ Análisis completado y guardado en informes/")
    else:
        print(f"⚠️  Análisis completado pero error guardando archivo")

if __name__ == "__main__":
    main()
