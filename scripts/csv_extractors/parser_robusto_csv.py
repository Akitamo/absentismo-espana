"""
Parser Robusto CSV - Sistema de Absentismo España
Maneja archivos CSV problemáticos del INE con diferentes formatos y errores
"""

import pandas as pd
import csv
import chardet
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import warnings

warnings.filterwarnings('ignore')

class ParserRobustoCSV:
    """
    Parser especializado en manejar archivos CSV problemáticos del INE
    """
    
    def __init__(self):
        """Inicializa el parser robusto"""
        self.logger = self._configurar_logging()
        
        # Estrategias de parsing para probar
        self.estrategias_parsing = [
            {'sep': ',', 'quotechar': '"', 'on_bad_lines': 'skip'},
            {'sep': ';', 'quotechar': '"', 'on_bad_lines': 'skip'}, 
            {'sep': '\t', 'quotechar': '"', 'on_bad_lines': 'skip'},
            {'sep': ',', 'quotechar': "'", 'on_bad_lines': 'skip'},
            {'sep': ',', 'quoting': csv.QUOTE_NONE, 'on_bad_lines': 'skip'},
            {'sep': ',', 'skipinitialspace': True, 'on_bad_lines': 'skip'},
            {'sep': ',', 'engine': 'python', 'on_bad_lines': 'skip'},
            {'sep': ';', 'engine': 'python', 'on_bad_lines': 'skip'}
        ]
        
        self.encodings_probar = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
    def _configurar_logging(self) -> logging.Logger:
        """Configura el logging"""
        logger = logging.getLogger('ParserRobusto')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def detectar_encoding(self, archivo: Path) -> str:
        """Detecta el encoding del archivo"""
        try:
            with open(archivo, 'rb') as f:
                muestra = f.read(10000)  # Leer muestra
                resultado = chardet.detect(muestra)
                encoding = resultado.get('encoding', 'utf-8')
                confidence = resultado.get('confidence', 0)
                
                if confidence > 0.7:
                    self.logger.debug(f"Encoding detectado para {archivo.name}: {encoding} (confianza: {confidence:.2f})")
                    return encoding
                else:
                    self.logger.debug(f"Encoding incierto para {archivo.name}, usando utf-8")
                    return 'utf-8'
        except:
            return 'utf-8'
    
    def inspeccionar_estructura_archivo(self, archivo: Path, num_lineas: int = 10) -> Dict[str, Any]:
        """Inspecciona las primeras líneas para entender la estructura"""
        inspeccion = {
            'primeras_lineas': [],
            'separadores_detectados': [],
            'num_columnas_por_linea': [],
            'encoding_detectado': None
        }
        
        try:
            encoding = self.detectar_encoding(archivo)
            inspeccion['encoding_detectado'] = encoding
            
            with open(archivo, 'r', encoding=encoding) as f:
                for i, linea in enumerate(f):
                    if i >= num_lineas:
                        break
                    
                    linea_limpia = linea.strip()
                    inspeccion['primeras_lineas'].append(linea_limpia)
                    
                    # Contar separadores comunes
                    for sep in [',', ';', '\t', '|']:
                        if sep in linea_limpia:
                            if sep not in inspeccion['separadores_detectados']:
                                inspeccion['separadores_detectados'].append(sep)
                    
                    # Contar columnas aproximadas
                    num_comas = linea_limpia.count(',')
                    num_puntos_coma = linea_limpia.count(';')
                    num_tabs = linea_limpia.count('\t')
                    
                    inspeccion['num_columnas_por_linea'].append({
                        'linea': i,
                        'comas': num_comas,
                        'puntos_coma': num_puntos_coma,
                        'tabs': num_tabs
                    })
                    
        except Exception as e:
            self.logger.warning(f"Error inspeccionando {archivo.name}: {e}")
        
        return inspeccion
    
    def cargar_csv_robusto(self, archivo: Path, max_intentos: int = None) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
        """
        Intenta cargar un CSV problemático usando múltiples estrategias
        
        Args:
            archivo: Path del archivo CSV
            max_intentos: Máximo número de estrategias a probar
            
        Returns:
            Tupla (DataFrame o None, info del proceso)
        """
        info_proceso = {
            'archivo': str(archivo),
            'exito': False,
            'estrategia_exitosa': None,
            'encoding_usado': None,
            'errores_encontrados': [],
            'filas_leidas': 0,
            'columnas_detectadas': 0,
            'inspeccion_previa': None
        }
        
        self.logger.info(f"🔍 Intentando cargar CSV problemático: {archivo.name}")
        
        # Inspeccionar archivo primero
        info_proceso['inspeccion_previa'] = self.inspeccionar_estructura_archivo(archivo)
        
        # Determinar encodings a probar
        encoding_detectado = info_proceso['inspeccion_previa']['encoding_detectado']
        encodings = [encoding_detectado] + [e for e in self.encodings_probar if e != encoding_detectado]
        
        # Limitar intentos si se especifica
        estrategias = self.estrategias_parsing
        if max_intentos:
            estrategias = estrategias[:max_intentos]
        
        # Probar cada combinación de encoding + estrategia
        for encoding in encodings:
            for i, estrategia in enumerate(estrategias):
                try:
                    self.logger.debug(f"Intento {i+1}: {estrategia} con encoding {encoding}")
                    
                    # Intentar cargar
                    df = pd.read_csv(archivo, encoding=encoding, **estrategia)
                    
                    if len(df) > 0 and len(df.columns) > 0:
                        info_proceso.update({
                            'exito': True,
                            'estrategia_exitosa': estrategia,
                            'encoding_usado': encoding,
                            'filas_leidas': len(df),
                            'columnas_detectadas': len(df.columns)
                        })
                        
                        self.logger.info(f"✅ {archivo.name} cargado exitosamente: {len(df)} filas, {len(df.columns)} columnas")
                        return df, info_proceso
                    
                except Exception as e:
                    error_msg = str(e)
                    info_proceso['errores_encontrados'].append({
                        'estrategia': estrategia,
                        'encoding': encoding,
                        'error': error_msg
                    })
                    self.logger.debug(f"Error con estrategia {i+1}: {error_msg}")
        
        # Si llegamos aquí, ninguna estrategia funcionó
        self.logger.warning(f"❌ No se pudo cargar {archivo.name} con ninguna estrategia")
        return None, info_proceso
    
    def reparar_y_cargar_csv(self, archivo: Path) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
        """
        Intenta reparar un CSV problemático antes de cargarlo
        
        Args:
            archivo: Path del archivo CSV
            
        Returns:
            Tupla (DataFrame o None, info del proceso)
        """
        info_reparacion = {
            'archivo': str(archivo),
            'reparacion_aplicada': False,
            'lineas_problematicas': [],
            'archivo_reparado': None
        }
        
        try:
            # Leer archivo línea por línea
            encoding = self.detectar_encoding(archivo)
            lineas_reparadas = []
            lineas_problematicas = 0
            
            with open(archivo, 'r', encoding=encoding) as f:
                header = f.readline().strip()
                num_columnas_esperadas = header.count(',') + 1
                lineas_reparadas.append(header)
                
                for num_linea, linea in enumerate(f, 2):
                    linea_limpia = linea.strip()
                    num_columnas_actual = linea_limpia.count(',') + 1
                    
                    if num_columnas_actual != num_columnas_esperadas:
                        # Intentar reparar
                        if num_columnas_actual > num_columnas_esperadas:
                            # Demasiadas comas, mantener solo las primeras N-1 como separadores
                            partes = linea_limpia.split(',')
                            linea_reparada = ','.join(partes[:num_columnas_esperadas])
                        else:
                            # Pocas comas, rellenar con valores vacíos
                            faltantes = num_columnas_esperadas - num_columnas_actual
                            linea_reparada = linea_limpia + ',' * faltantes
                        
                        lineas_reparadas.append(linea_reparada)
                        lineas_problematicas += 1
                        
                        if lineas_problematicas <= 5:  # Registrar solo primeras 5
                            info_reparacion['lineas_problematicas'].append({
                                'numero': num_linea,
                                'original': linea_limpia,
                                'reparada': linea_reparada
                            })
                    else:
                        lineas_reparadas.append(linea_limpia)
            
            if lineas_problematicas > 0:
                # Crear archivo temporal reparado
                archivo_temp = archivo.parent / f"temp_reparado_{archivo.name}"
                
                with open(archivo_temp, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lineas_reparadas))
                
                info_reparacion.update({
                    'reparacion_aplicada': True,
                    'archivo_reparado': str(archivo_temp),
                    'lineas_reparadas': lineas_problematicas
                })
                
                self.logger.info(f"🔧 Archivo reparado: {lineas_problematicas} líneas corregidas")
                
                # Intentar cargar archivo reparado
                df, info_carga = self.cargar_csv_robusto(archivo_temp)
                
                # Limpiar archivo temporal
                try:
                    archivo_temp.unlink()
                except:
                    pass
                
                # Combinar información
                info_completa = {**info_reparacion, **info_carga}
                return df, info_completa
            
        except Exception as e:
            self.logger.error(f"Error reparando {archivo.name}: {e}")
        
        # Si no se necesitó reparación o falló, intentar carga normal
        df, info_carga = self.cargar_csv_robusto(archivo)
        info_completa = {**info_reparacion, **info_carga}
        return df, info_completa
    
    def procesar_directorio_csv(self, directorio: str) -> Dict[str, Any]:
        """
        Procesa todos los archivos CSV de un directorio con parsing robusto
        
        Args:
            directorio: Path del directorio con archivos CSV
            
        Returns:
            Diccionario con resultados del procesamiento
        """
        directorio_path = Path(directorio)
        archivos_csv = list(directorio_path.glob("*.csv"))
        
        resultados = {
            'directorio': str(directorio_path),
            'total_archivos': len(archivos_csv),
            'exitosos': 0,
            'fallidos': 0,
            'archivos_procesados': {},
            'resumen_errores': {},
            'estadisticas_globales': {}
        }
        
        self.logger.info(f"🚀 Procesando {len(archivos_csv)} archivos CSV con parsing robusto")
        
        for archivo in archivos_csv:
            df, info = self.reparar_y_cargar_csv(archivo)
            
            id_tabla = archivo.stem.split('_')[0]
            
            if df is not None:
                resultados['exitosos'] += 1
                resultados['archivos_procesados'][id_tabla] = {
                    'exito': True,
                    'archivo': archivo.name,
                    'filas': len(df),
                    'columnas': len(df.columns),
                    'info_proceso': info
                }
                
                # Guardar muestra del DataFrame para análisis posterior
                resultados['archivos_procesados'][id_tabla]['muestra_datos'] = df.head(3).to_dict('records')
                resultados['archivos_procesados'][id_tabla]['columnas_nombres'] = list(df.columns)
                
            else:
                resultados['fallidos'] += 1
                resultados['archivos_procesados'][id_tabla] = {
                    'exito': False,
                    'archivo': archivo.name,
                    'errores': info.get('errores_encontrados', []),
                    'info_proceso': info
                }
        
        # Generar estadísticas globales
        total_filas = sum(a.get('filas', 0) for a in resultados['archivos_procesados'].values() if a.get('exito'))
        total_columnas = sum(a.get('columnas', 0) for a in resultados['archivos_procesados'].values() if a.get('exito'))
        
        resultados['estadisticas_globales'] = {
            'tasa_exito': round(resultados['exitosos'] / resultados['total_archivos'] * 100, 1),
            'total_filas_procesadas': total_filas,
            'total_columnas_procesadas': total_columnas,
            'archivos_reparados': len([a for a in resultados['archivos_procesados'].values() 
                                     if a.get('info_proceso', {}).get('reparacion_aplicada', False)])
        }
        
        self.logger.info(f"✅ Procesamiento completado: {resultados['exitosos']}/{resultados['total_archivos']} archivos exitosos")
        
        return resultados

def main():
    """Función principal para probar el parser robusto"""
    print("🔧 PARSER ROBUSTO CSV - REPARACIÓN DE ARCHIVOS PROBLEMÁTICOS")
    print("="*70)
    
    parser = ParserRobustoCSV()
    
    # Procesar directorio de datos
    directorio_datos = "../../data/raw/csv/"
    resultados = parser.procesar_directorio_csv(directorio_datos)
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DEL PROCESAMIENTO:")
    print(f"   Total archivos: {resultados['total_archivos']}")
    print(f"   Exitosos: {resultados['exitosos']}")
    print(f"   Fallidos: {resultados['fallidos']}")
    print(f"   Tasa de éxito: {resultados['estadisticas_globales']['tasa_exito']}%")
    print(f"   Archivos reparados: {resultados['estadisticas_globales']['archivos_reparados']}")
    print(f"   Total filas procesadas: {resultados['estadisticas_globales']['total_filas_procesadas']:,}")
    
    # Guardar resultados
    import json
    output_file = "../../informes/diagnostico_parsing_csv.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Diagnóstico guardado en: {output_file}")

if __name__ == "__main__":
    main()
