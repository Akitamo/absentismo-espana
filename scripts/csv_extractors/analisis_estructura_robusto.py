"""
Analizador Estructura Robusto - Sistema de Absentismo España
Analiza archivos CSV problemáticos usando el parser robusto
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
from parser_robusto_csv import ParserRobustoCSV

# Suprimir warnings de pandas
warnings.filterwarnings('ignore')

class AnalizadorEstructuraRobusto:
    """
    Analizador que puede manejar archivos CSV problemáticos del INE
    """
    
    def __init__(self, data_dir: str = "../../data/raw/csv/"):
        """
        Inicializa el analizador robusto
        
        Args:
            data_dir: Directorio con los archivos CSV
        """
        self.data_dir = Path(data_dir)
        self.logger = self._configurar_logging()
        self.parser_robusto = ParserRobustoCSV()
        
        self.resultados = {
            'metadatos_generales': {},
            'analisis_por_tabla': {},
            'resumen_ejecutivo': {},
            'parsing_info': {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info("AnalizadorEstructuraRobusto inicializado")
    
    def _configurar_logging(self) -> logging.Logger:
        """Configura el logging"""
        logger = logging.getLogger('AnalizadorRobusto')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def analizar_archivo_csv_robusto(self, archivo: Path) -> Dict[str, Any]:
        """
        Analiza un archivo CSV usando el parser robusto
        
        Args:
            archivo: Path del archivo CSV
            
        Returns:
            Diccionario con análisis completo del archivo
        """
        id_tabla = archivo.stem.split('_')[0]
        self.logger.info(f"Analizando tabla {id_tabla}: {archivo.name}")
        
        analisis = {
            'id_tabla': id_tabla,
            'nombre_archivo': archivo.name,
            'ruta_completa': str(archivo),
            'tamaño_bytes': archivo.stat().st_size,
            'tamaño_mb': round(archivo.stat().st_size / (1024*1024), 2),
            'fecha_modificacion': datetime.fromtimestamp(archivo.stat().st_mtime).isoformat(),
            'parsing_exitoso': False,
            'info_parsing': {},
            'estructura': {},
            'contenido': {},
            'calidad_datos': {},
            'relevancia_absentismo': {},
            'errores': []
        }
        
        try:
            # Intentar cargar con parser robusto
            df, info_parsing = self.parser_robusto.reparar_y_cargar_csv(archivo)
            
            analisis['info_parsing'] = info_parsing
            
            if df is not None:
                analisis['parsing_exitoso'] = True
                
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
                
                # Si se reparó el archivo, agregar información adicional
                if info_parsing.get('reparacion_aplicada', False):
                    self.logger.info(f"🔧 Archivo {id_tabla} fue reparado automáticamente")
                
            else:
                analisis['parsing_exitoso'] = False
                error_msg = f"No se pudo cargar {archivo.name} con ninguna estrategia"
                analisis['errores'].append(error_msg)
                self.logger.warning(f"❌ {error_msg}")
                
        except Exception as e:
            error_msg = f"Error inesperado analizando {archivo.name}: {str(e)}"
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
            
            # Valores únicos por columna
            for col in df.columns:
                valores_unicos = df[col].nunique()
                contenido['valores_unicos_por_columna'][col] = valores_unicos
            
            # Detectar rango temporal
            contenido['rango_temporal'] = self._detectar_rango_temporal(df)
            
            # Muestras de datos (primeras 3 filas)
            try:
                contenido['muestras_datos'] = df.head(3).to_dict('records')
            except:
                contenido['muestras_datos'] = []
            
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
            if total_celdas > 0:
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
                if calidad['duplicados'] > 0 and len(df) > 0:
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
            
            # Bonus por ID de tabla específicos
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
        Ejecuta análisis completo de todas las tablas CSV usando parsing robusto
        
        Returns:
            Diccionario con resultados completos del análisis
        """
        archivos = list(self.data_dir.glob("*.csv"))
        
        if not archivos:
            self.logger.error("No se encontraron archivos CSV para analizar")
            return {'error': 'No hay archivos CSV disponibles'}
        
        self.logger.info(f"🚀 Iniciando análisis robusto de {len(archivos)} archivos CSV")
        
        # Analizar cada archivo
        exitosos = 0
        fallidos = 0
        
        for archivo in archivos:
            id_tabla = archivo.stem.split('_')[0]
            analisis = self.analizar_archivo_csv_robusto(archivo)
            self.resultados['analisis_por_tabla'][id_tabla] = analisis
            
            if analisis['parsing_exitoso']:
                exitosos += 1
            else:
                fallidos += 1
        
        # Información del parsing
        self.resultados['parsing_info'] = {
            'total_archivos': len(archivos),
            'exitosos': exitosos,
            'fallidos': fallidos,
            'tasa_exito': round(exitosos / len(archivos) * 100, 1)
        }
        
        # Generar resumen ejecutivo
        self.resultados['resumen_ejecutivo'] = self._generar_resumen_ejecutivo()
        
        # Generar metadatos generales
        self.resultados['metadatos_generales'] = self._generar_metadatos_generales()
        
        self.logger.info(f"✅ Análisis robusto completado: {exitosos}/{len(archivos)} archivos procesados exitosamente")
        
        return self.resultados
    
    def _generar_resumen_ejecutivo(self) -> Dict[str, Any]:
        """Genera resumen ejecutivo del análisis"""
        resumen = {
            'total_tablas': len(self.resultados['analisis_por_tabla']),
            'tablas_procesadas_exitosamente': 0,
            'total_registros': 0,
            'total_columnas': 0,
            'tamaño_total_mb': 0,
            'periodo_cobertura': {'inicio': None, 'fin': None},
            'calidad_promedio': 0,
            'tablas_por_relevancia': {'muy_alta': [], 'alta': [], 'media': [], 'baja': []},
            'tipos_datos_absentismo': {},
            'estadisticas_parsing': self.resultados.get('parsing_info', {})
        }
        
        scores_calidad = []
        años_todos = []
        
        for id_tabla, analisis in self.resultados['analisis_por_tabla'].items():
            if not analisis.get('parsing_exitoso', False):
                continue
                
            resumen['tablas_procesadas_exitosamente'] += 1
            
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
                                       if not a.get('parsing_exitoso', False)]),
            'parsing_robusto_usado': True,
            'estrategias_parsing_disponibles': len(self.parser_robusto.estrategias_parsing)
        }
    
    def guardar_resultados(self, archivo_salida: str = "../../informes/analisis_estructura_robusto.json") -> bool:
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
        parsing_info = self.resultados.get('parsing_info', {})
        
        print("\n" + "="*80)
        print("📊 RESUMEN EJECUTIVO - ANÁLISIS ESTRUCTURA ROBUSTO")
        print("="*80)
        
        print(f"📁 Total archivos encontrados: {resumen['total_tablas']}")
        print(f"✅ Archivos procesados exitosamente: {resumen['tablas_procesadas_exitosamente']}")
        print(f"📊 Tasa de éxito parsing: {parsing_info.get('tasa_exito', 0)}%")
        print(f"📈 Total registros procesados: {resumen['total_registros']:,}")
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
    """Función principal para ejecutar el análisis robusto"""
    print("🔧 INICIANDO ANÁLISIS ESTRUCTURA ROBUSTO")
    print("="*60)
    
    # Crear analizador robusto
    analizador = AnalizadorEstructuraRobusto()
    
    # Ejecutar análisis
    resultados = analizador.analizar_todas_las_tablas()
    
    if 'error' in resultados:
        print(f"❌ Error: {resultados['error']}")
        return
    
    # Mostrar resumen en consola
    analizador.mostrar_resumen_consola()
    
    # Guardar resultados
    if analizador.guardar_resultados():
        print(f"✅ Análisis robusto completado y guardado en informes/")
    else:
        print(f"⚠️  Análisis completado pero error guardando archivo")

if __name__ == "__main__":
    main()
