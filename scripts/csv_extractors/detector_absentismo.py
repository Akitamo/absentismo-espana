"""
Detector de Absentismo - Sistema de Absentismo España
Identifica y analiza específicamente los datos relacionados con absentismo laboral
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

class DetectorAbsentismo:
    """
    Detector especializado en identificar datos de absentismo laboral
    """
    
    def __init__(self, data_dir: str = "../../data/raw/csv/"):
        """
        Inicializa el detector
        
        Args:
            data_dir: Directorio con los archivos CSV
        """
        self.data_dir = Path(data_dir)
        self.logger = self._configurar_logging()
        
        # Diccionarios de mapeo para identificar datos de absentismo
        self.patrones_absentismo = {
            'horas_trabajo': [
                'horas.*trabajo', 'horas.*efectiva', 'horas.*pactada', 
                'tiempo.*trabajo', 'jornada.*efectiva'
            ],
            'ausencias': [
                'horas.*no.*trabajada', 'ausencia', 'baja', 'incapacidad.*temporal',
                'IT', 'permiso', 'licencia', 'maternidad', 'paternidad'
            ],
            'absentismo_directo': [
                'absentismo', 'absenteeism', 'ausentismo'
            ],
            'causas_ausencia': [
                'enfermedad', 'accidente', 'conflicto', 'huelga', 'vacaciones',
                'festivo', 'ERTE', 'suspension'
            ]
        }
        
        # Tablas prioritarias según conocimiento del INE ETCL
        self.tablas_prioritarias = {
            'tiempo_trabajo_principal': ['6042', '6043', '6044', '6045', '6046', '6063'],
            'costes_con_ausencias': ['6038', '6039', '6040', '6041', '6056'],
            'series_temporales': ['59391', '59392'],
            'costes_detallados': ['6030', '6031', '6032', '6033', '6034', '6035', '6036', '6037']
        }
        
        self.resultados = {
            'detectados': {},
            'recomendaciones': {},
            'metricas_calculables': {},
            'estructura_optima_bd': {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info("DetectorAbsentismo inicializado")
    
    def _configurar_logging(self) -> logging.Logger:
        """Configura el logging"""
        logger = logging.getLogger('DetectorAbsentismo')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def detectar_columnas_absentismo(self, df: pd.DataFrame, id_tabla: str) -> Dict[str, Any]:
        """
        Detecta columnas relacionadas con absentismo en un DataFrame
        
        Args:
            df: DataFrame a analizar
            id_tabla: ID de la tabla
            
        Returns:
            Diccionario con detección de columnas de absentismo
        """
        deteccion = {
            'id_tabla': id_tabla,
            'total_columnas': len(df.columns),
            'columnas_detectadas': {
                'horas_trabajo': [],
                'ausencias': [],
                'absentismo_directo': [],
                'causas_ausencia': [],
                'temporal': [],
                'geografica': [],
                'sectorial': []
            },
            'score_absentismo': 0,
            'utilidad_primaria': 'ninguna',
            'datos_muestra': {},
            'calculo_posible': {}
        }
        
        # Analizar cada columna
        for col in df.columns:
            col_lower = col.lower()
            
            # Detectar patrones de absentismo
            for categoria, patrones in self.patrones_absentismo.items():
                for patron in patrones:
                    if re.search(patron, col_lower):
                        deteccion['columnas_detectadas'][categoria].append({
                            'columna': col,
                            'patron_detectado': patron,
                            'valores_unicos': df[col].nunique(),
                            'tipo_datos': str(df[col].dtype)
                        })
                        deteccion['score_absentismo'] += 5
            
            # Detectar dimensiones (temporal, geográfica, sectorial)
            if any(kw in col_lower for kw in ['año', 'mes', 'trimestre', 'periodo', 'fecha']):
                deteccion['columnas_detectadas']['temporal'].append(col)
                deteccion['score_absentismo'] += 2
            
            if any(kw in col_lower for kw in ['ccaa', 'comunidad', 'provincia', 'region']):
                deteccion['columnas_detectadas']['geografica'].append(col)
                deteccion['score_absentismo'] += 2
            
            if any(kw in col_lower for kw in ['sector', 'actividad', 'cnae', 'industria', 'servicio']):
                deteccion['columnas_detectadas']['sectorial'].append(col)
                deteccion['score_absentismo'] += 2
        
        # Bonus por tabla prioritaria
        for categoria, tablas in self.tablas_prioritarias.items():
            if id_tabla in tablas:
                deteccion['score_absentismo'] += 10
                deteccion['utilidad_primaria'] = categoria
                break
        
        # Determinar utilidad
        if deteccion['score_absentismo'] >= 20:
            deteccion['utilidad_primaria'] = 'muy_alta'
        elif deteccion['score_absentismo'] >= 15:
            deteccion['utilidad_primaria'] = 'alta'
        elif deteccion['score_absentismo'] >= 8:
            deteccion['utilidad_primaria'] = 'media'
        else:
            deteccion['utilidad_primaria'] = 'baja'
        
        # Analizar posibilidades de cálculo
        deteccion['calculo_posible'] = self._analizar_calculos_posibles(df, deteccion)
        
        # Obtener muestras de datos relevantes
        deteccion['datos_muestra'] = self._extraer_muestras_relevantes(df, deteccion)
        
        return deteccion
    
    def _analizar_calculos_posibles(self, df: pd.DataFrame, deteccion: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza qué cálculos de absentismo son posibles con los datos"""
        calculos = {
            'tasa_absentismo_total': False,
            'absentismo_por_IT': False,
            'absentismo_por_sector': False,
            'absentismo_por_ccaa': False,
            'tendencias_temporales': False,
            'comparativa_sectorial': False,
            'detalle_causas': False,
            'formulas_detectadas': []
        }
        
        # Verificar si hay columnas de horas trabajo y ausencias
        tiene_horas_trabajo = len(deteccion['columnas_detectadas']['horas_trabajo']) > 0
        tiene_ausencias = len(deteccion['columnas_detectadas']['ausencias']) > 0
        tiene_temporal = len(deteccion['columnas_detectadas']['temporal']) > 0
        tiene_geografica = len(deteccion['columnas_detectadas']['geografica']) > 0
        tiene_sectorial = len(deteccion['columnas_detectadas']['sectorial']) > 0
        
        # Tasa de absentismo total
        if tiene_horas_trabajo or tiene_ausencias:
            calculos['tasa_absentismo_total'] = True
            calculos['formulas_detectadas'].append(
                "Tasa Absentismo = (Horas no trabajadas / Horas pactadas efectivas) * 100"
            )
        
        # Absentismo por IT
        if any('IT' in str(col).upper() or 'incapacidad' in str(col).lower() 
               for cols in deteccion['columnas_detectadas']['ausencias'] 
               for col in [cols.get('columna', '')]):
            calculos['absentismo_por_IT'] = True
            calculos['formulas_detectadas'].append(
                "Absentismo IT = (Horas no trabajadas por IT / Horas pactadas efectivas) * 100"
            )
        
        # Análisis dimensional
        if tiene_sectorial:
            calculos['absentismo_por_sector'] = True
            calculos['comparativa_sectorial'] = True
        
        if tiene_geografica:
            calculos['absentismo_por_ccaa'] = True
        
        if tiene_temporal:
            calculos['tendencias_temporales'] = True
        
        if len(deteccion['columnas_detectadas']['causas_ausencia']) > 0:
            calculos['detalle_causas'] = True
        
        return calculos
    
    def _extraer_muestras_relevantes(self, df: pd.DataFrame, deteccion: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae muestras de datos relevantes para absentismo"""
        muestras = {
            'columnas_numericas_relevantes': {},
            'valores_ejemplo': {},
            'estadisticas_basicas': {}
        }
        
        try:
            # Encontrar columnas numéricas que podrían ser de horas/tiempo
            columnas_numericas = df.select_dtypes(include=['number']).columns
            
            for col in columnas_numericas:
                col_lower = col.lower()
                if any(kw in col_lower for kw in ['hora', 'tiempo', 'jornada']):
                    # Estadísticas básicas
                    stats = {
                        'min': float(df[col].min()) if not df[col].empty else 0,
                        'max': float(df[col].max()) if not df[col].empty else 0,
                        'media': float(df[col].mean()) if not df[col].empty else 0,
                        'mediana': float(df[col].median()) if not df[col].empty else 0
                    }
                    muestras['estadisticas_basicas'][col] = stats
                    
                    # Valores ejemplo (primeros 5 no nulos)
                    valores_ejemplo = df[col].dropna().head(5).tolist()
                    muestras['valores_ejemplo'][col] = valores_ejemplo
            
            # Muestra general de las primeras 3 filas
            muestras['muestra_general'] = df.head(3).to_dict('records')
            
        except Exception as e:
            self.logger.warning(f"Error extrayendo muestras: {e}")
        
        return muestras
    
    def analizar_todas_las_tablas(self) -> Dict[str, Any]:
        """
        Analiza todas las tablas CSV para detectar datos de absentismo
        
        Returns:
            Diccionario completo con detección de absentismo
        """
        archivos = list(self.data_dir.glob("*.csv"))
        
        if not archivos:
            self.logger.error("No se encontraron archivos CSV")
            return {'error': 'No hay archivos CSV disponibles'}
        
        self.logger.info(f"🔍 Analizando {len(archivos)} tablas para detectar absentismo")
        
        # Analizar cada tabla
        for archivo in archivos:
            id_tabla = archivo.stem.split('_')[0]
            
            try:
                self.logger.info(f"Analizando tabla {id_tabla}: {archivo.name}")
                df = pd.read_csv(archivo, encoding='utf-8', nrows=10000)  # Muestra para análisis rápido
                
                deteccion = self.detectar_columnas_absentismo(df, id_tabla)
                self.resultados['detectados'][id_tabla] = deteccion
                
            except Exception as e:
                self.logger.error(f"Error analizando {archivo.name}: {e}")
                self.resultados['detectados'][id_tabla] = {
                    'error': str(e),
                    'archivo': archivo.name
                }
        
        # Generar análisis consolidado
        self._generar_analisis_consolidado()
        
        return self.resultados
    
    def _generar_analisis_consolidado(self) -> None:
        """Genera análisis consolidado y recomendaciones"""
        
        # Clasificar tablas por utilidad
        clasificacion = {
            'muy_alta': [],
            'alta': [],
            'media': [],
            'baja': []
        }
        
        metricas_disponibles = {
            'tasa_absentismo_total': [],
            'absentismo_por_IT': [],
            'absentismo_por_sector': [],
            'absentismo_por_ccaa': [],
            'tendencias_temporales': [],
            'comparativa_sectorial': []
        }
        
        for id_tabla, deteccion in self.resultados['detectados'].items():
            if 'error' in deteccion:
                continue
            
            utilidad = deteccion.get('utilidad_primaria', 'baja')
            if utilidad in clasificacion:
                clasificacion[utilidad].append(id_tabla)
            
            # Recopilar métricas disponibles
            calculos = deteccion.get('calculo_posible', {})
            for metrica, disponible in calculos.items():
                if disponible and metrica in metricas_disponibles:
                    metricas_disponibles[metrica].append(id_tabla)
        
        # Generar recomendaciones
        self.resultados['recomendaciones'] = {
            'tablas_prioritarias': clasificacion['muy_alta'] + clasificacion['alta'],
            'tablas_complementarias': clasificacion['media'],
            'tablas_descartables': clasificacion['baja'],
            'orden_implementacion': self._generar_orden_implementacion(clasificacion),
            'estructura_bd_recomendada': self._recomendar_estructura_bd(clasificacion, metricas_disponibles)
        }
        
        self.resultados['metricas_calculables'] = {
            'disponibles': {k: v for k, v in metricas_disponibles.items() if v},
            'resumen': {
                'total_metricas_posibles': len([k for k, v in metricas_disponibles.items() if v]),
                'tablas_con_absentismo_directo': len(clasificacion['muy_alta']),
                'tablas_con_datos_complementarios': len(clasificacion['alta'] + clasificacion['media'])
            }
        }
    
    def _generar_orden_implementacion(self, clasificacion: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Genera orden recomendado de implementación"""
        orden = [
            {
                'fase': 1,
                'prioridad': 'Crítica',
                'tablas': clasificacion['muy_alta'],
                'objetivo': 'Implementar cálculo básico de tasa de absentismo',
                'tiempo_estimado': '1-2 semanas'
            },
            {
                'fase': 2,
                'prioridad': 'Alta',
                'tablas': clasificacion['alta'],
                'objetivo': 'Añadir análisis sectorial y temporal',
                'tiempo_estimado': '2-3 semanas'
            },
            {
                'fase': 3,
                'prioridad': 'Media',
                'tablas': clasificacion['media'],
                'objetivo': 'Completar análisis con datos complementarios',
                'tiempo_estimado': '1-2 semanas'
            }
        ]
        
        return orden
    
    def _recomendar_estructura_bd(self, clasificacion: Dict[str, List[str]], 
                                 metricas: Dict[str, List[str]]) -> Dict[str, Any]:
        """Recomienda estructura de base de datos optimizada"""
        estructura = {
            'tablas_principales': {
                'absentismo_datos': {
                    'descripcion': 'Tabla principal con datos de absentismo calculados',
                    'fuentes': clasificacion['muy_alta'],
                    'columnas_clave': [
                        'periodo', 'ccaa', 'sector', 'tasa_absentismo', 
                        'horas_efectivas', 'horas_no_trabajadas', 'tipo_ausencia'
                    ]
                },
                'dimensiones_tiempo': {
                    'descripcion': 'Dimensión temporal para análisis',
                    'columnas': ['año', 'trimestre', 'mes', 'fecha']
                },
                'dimensiones_geografia': {
                    'descripcion': 'Dimensión geográfica',
                    'columnas': ['ccaa', 'provincia', 'codigo_ine']
                },
                'dimensiones_sector': {
                    'descripcion': 'Dimensión sectorial',
                    'columnas': ['sector', 'cnae_seccion', 'cnae_division', 'descripcion']
                }
            },
            'tablas_auxiliares': {
                'costes_laborales': {
                    'fuentes': clasificacion['alta'],
                    'proposito': 'Datos complementarios de costes relacionados con absentismo'
                },
                'metadatos_fuentes': {
                    'proposito': 'Metadatos de las fuentes de datos del INE'
                }
            },
            'indices_recomendados': [
                'periodo + ccaa + sector',
                'fecha + sector',
                'ccaa + periodo'
            ]
        }
        
        return estructura
    
    def generar_informe_detallado(self) -> Dict[str, Any]:
        """Genera informe detallado para revisión humana"""
        informe = {
            'resumen_ejecutivo': {
                'total_tablas_analizadas': len(self.resultados['detectados']),
                'tablas_con_datos_absentismo': len([t for t in self.resultados['detectados'].values() 
                                                   if t.get('score_absentismo', 0) > 10]),
                'metricas_calculables': len(self.resultados['metricas_calculables']['disponibles']),
                'recomendacion_general': self._generar_recomendacion_general()
            },
            'detalle_por_tabla': {},
            'plan_implementacion': self.resultados.get('recomendaciones', {}),
            'casos_uso_identificados': self._identificar_casos_uso()
        }
        
        # Detalles por tabla con formato legible
        for id_tabla, deteccion in self.resultados['detectados'].items():
            if 'error' in deteccion:
                continue
                
            informe['detalle_por_tabla'][id_tabla] = {
                'score_absentismo': deteccion.get('score_absentismo', 0),
                'utilidad': deteccion.get('utilidad_primaria', 'baja'),
                'columnas_relevantes': len([col for cols in deteccion.get('columnas_detectadas', {}).values() 
                                          if isinstance(cols, list) for col in cols]),
                'calculos_posibles': [k for k, v in deteccion.get('calculo_posible', {}).items() if v],
                'dimensiones_disponibles': {
                    'temporal': len(deteccion.get('columnas_detectadas', {}).get('temporal', [])),
                    'geografica': len(deteccion.get('columnas_detectadas', {}).get('geografica', [])),
                    'sectorial': len(deteccion.get('columnas_detectadas', {}).get('sectorial', []))
                }
            }
        
        return informe
    
    def _generar_recomendacion_general(self) -> str:
        """Genera recomendación general basada en el análisis"""
        tablas_muy_alta = len(self.resultados.get('recomendaciones', {}).get('tablas_prioritarias', []))
        metricas_disponibles = len(self.resultados.get('metricas_calculables', {}).get('disponibles', {}))
        
        if tablas_muy_alta >= 3 and metricas_disponibles >= 4:
            return "EXCELENTE: Datos suficientes para implementar sistema completo de análisis de absentismo"
        elif tablas_muy_alta >= 2 and metricas_disponibles >= 2:
            return "BUENO: Datos adecuados para implementar análisis básico de absentismo con posibilidad de expansión"
        elif tablas_muy_alta >= 1:
            return "LIMITADO: Datos básicos disponibles, análisis simple posible"
        else:
            return "INSUFICIENTE: Datos limitados para análisis de absentismo, considerar fuentes adicionales"
    
    def _identificar_casos_uso(self) -> List[Dict[str, Any]]:
        """Identifica casos de uso posibles con los datos disponibles"""
        casos_uso = []
        
        metricas = self.resultados.get('metricas_calculables', {}).get('disponibles', {})
        
        if metricas.get('tasa_absentismo_total'):
            casos_uso.append({
                'titulo': 'Dashboard de Absentismo Nacional',
                'descripcion': 'Visualización de tasas de absentismo por CCAA y sectores',
                'complejidad': 'Media',
                'valor_negocio': 'Alto',
                'tablas_necesarias': metricas['tasa_absentismo_total']
            })
        
        if metricas.get('tendencias_temporales'):
            casos_uso.append({
                'titulo': 'Análisis de Tendencias Temporales',
                'descripcion': 'Evolución del absentismo a lo largo del tiempo',
                'complejidad': 'Media',
                'valor_negocio': 'Alto',
                'tablas_necesarias': metricas['tendencias_temporales']
            })
        
        if metricas.get('comparativa_sectorial'):
            casos_uso.append({
                'titulo': 'Benchmarking Sectorial',
                'descripcion': 'Comparación de absentismo entre sectores económicos',
                'complejidad': 'Baja',
                'valor_negocio': 'Medio',
                'tablas_necesarias': metricas['comparativa_sectorial']
            })
        
        return casos_uso
    
    def guardar_resultados(self, archivo_salida: str = "../../informes/deteccion_absentismo_detallada.json") -> bool:
        """Guarda los resultados de la detección"""
        try:
            ruta_salida = Path(archivo_salida)
            ruta_salida.parent.mkdir(parents=True, exist_ok=True)
            
            # Generar informe detallado
            informe_completo = {
                'deteccion_raw': self.resultados,
                'informe_detallado': self.generar_informe_detallado(),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                json.dump(informe_completo, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"✅ Detección guardada en: {ruta_salida}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando detección: {e}")
            return False

def main():
    """Función principal"""
    print("🔍 INICIANDO DETECCIÓN ESPECÍFICA DE ABSENTISMO")
    print("="*60)
    
    detector = DetectorAbsentismo()
    resultados = detector.analizar_todas_las_tablas()
    
    if 'error' in resultados:
        print(f"❌ Error: {resultados['error']}")
        return
    
    # Mostrar resumen
    informe = detector.generar_informe_detallado()
    resumen = informe['resumen_ejecutivo']
    
    print(f"📊 RESULTADOS DE DETECCIÓN:")
    print(f"   Tablas analizadas: {resumen['total_tablas_analizadas']}")
    print(f"   Tablas con datos absentismo: {resumen['tablas_con_datos_absentismo']}")
    print(f"   Métricas calculables: {resumen['metricas_calculables']}")
    print(f"   Recomendación: {resumen['recomendacion_general']}")
    
    # Guardar resultados
    if detector.guardar_resultados():
        print(f"✅ Detección completada y guardada")

if __name__ == "__main__":
    main()
