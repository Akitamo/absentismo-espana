"""
Generador de Informe de Factibilidad CORREGIDO - Sistema de Absentismo España
Versión corregida que maneja errores de format y CSS
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging
import re

class GeneradorInformeFactibilidadCorregido:
    """
    Generador corregido de informes HTML interactivos para análisis de factibilidad
    """
    
    def __init__(self):
        """Inicializa el generador"""
        self.logger = self._configurar_logging()
        
    def _configurar_logging(self) -> logging.Logger:
        """Configura el logging"""
        logger = logging.getLogger('GeneradorInforme')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def generar_template_html_base(self) -> str:
        """Genera la plantilla HTML base sin usar format()"""
        return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de Factibilidad - Absentismo España</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            text-align: center;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover { 
            transform: translateY(-5px); 
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .stat-label { 
            color: #7f8c8d; 
            font-size: 1.1em; 
        }
        
        .section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }
        
        .section h2 {
            color: #2c3e50;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .recommendation-box {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }
        
        .metric-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .metric-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .metric-item h4 { 
            color: #2c3e50; 
            margin-bottom: 5px; 
        }
        
        .metric-item p { 
            color: #7f8c8d; 
            font-size: 0.9em; 
        }
        
        .progress-bar {
            background: #ecf0f1;
            border-radius: 10px;
            height: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }
        
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }
        
        th {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            font-weight: 600;
        }
        
        tr:hover { 
            background: #f8f9fa; 
        }
        
        .badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge-muy-alta { background: #e74c3c; color: white; }
        .badge-alta { background: #f39c12; color: white; }
        .badge-media { background: #f1c40f; color: #333; }
        .badge-baja { background: #95a5a6; color: white; }
        
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 30px;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
            .container { padding: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Análisis de Factibilidad</h1>
            <p class="subtitle">Sistema de Análisis de Absentismo España</p>
            <p style="color: #7f8c8d; margin-top: 10px;">{{TIMESTAMP_PLACEHOLDER}}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{TOTAL_TABLAS}}</div>
                <div class="stat-label">Tablas Analizadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{TOTAL_REGISTROS}}</div>
                <div class="stat-label">Registros Totales</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{TAMANO_MB}} MB</div>
                <div class="stat-label">Datos Totales</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{CALIDAD_PROMEDIO}}%</div>
                <div class="stat-label">Calidad Promedio</div>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Resumen Ejecutivo</h2>
            <div class="recommendation-box">
                <h3>Recomendación General</h3>
                <p>{{RECOMENDACION_GENERAL}}</p>
            </div>
            
            <div class="metric-list">
                <div class="metric-item">
                    <h4>Tablas Prioritarias</h4>
                    <p>{{TABLAS_PRIORITARIAS}} tablas con datos críticos para absentismo</p>
                </div>
                <div class="metric-item">
                    <h4>Métricas Calculables</h4>
                    <p>{{METRICAS_CALCULABLES}} tipos de análisis posibles</p>
                </div>
                <div class="metric-item">
                    <h4>Cobertura Temporal</h4>
                    <p>{{PERIODO_INICIO}} - {{PERIODO_FIN}}</p>
                </div>
                <div class="metric-item">
                    <h4>Dimensiones Disponibles</h4>
                    <p>Geográfica, Sectorial, Temporal</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📈 Análisis por Relevancia</h2>
            {{RELEVANCIA_CONTENT}}
        </div>

        <div class="section">
            <h2>🛠️ Plan de Implementación</h2>
            {{PLAN_IMPLEMENTACION}}
        </div>

        <div class="section">
            <h2>💡 Casos de Uso Identificados</h2>
            {{CASOS_USO}}
        </div>

        <div class="footer">
            <p>Sistema de Análisis de Absentismo España • Generado automáticamente • INE ETCL Data</p>
        </div>
    </div>

    <script>
        console.log('Informe de factibilidad cargado correctamente');
    </script>
</body>
</html>'''
    
    def cargar_datos_analisis(self, archivo_estructura: str, archivo_deteccion: str) -> Dict[str, Any]:
        """
        Carga los datos de los análisis de estructura y detección
        """
        datos_combinados = {}
        
        try:
            # Cargar análisis de estructura
            if Path(archivo_estructura).exists():
                with open(archivo_estructura, 'r', encoding='utf-8') as f:
                    datos_combinados['estructura'] = json.load(f)
                self.logger.info("✅ Datos de estructura cargados")
            else:
                self.logger.warning(f"Archivo de estructura no encontrado: {archivo_estructura}")
                datos_combinados['estructura'] = {}
            
            # Cargar detección de absentismo
            if Path(archivo_deteccion).exists():
                with open(archivo_deteccion, 'r', encoding='utf-8') as f:
                    datos_combinados['deteccion'] = json.load(f)
                self.logger.info("✅ Datos de detección cargados")
            else:
                self.logger.warning(f"Archivo de detección no encontrado: {archivo_deteccion}")
                datos_combinados['deteccion'] = {}
                
        except Exception as e:
            self.logger.error(f"Error cargando datos: {e}")
            
        return datos_combinados
    
    def extraer_metricas_resumen(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae métricas principales para el resumen"""
        metricas = {
            'total_tablas': 0,
            'total_registros': '0',
            'tamano_mb': 0,
            'calidad_promedio': 0,
            'tablas_prioritarias': 0,
            'metricas_calculables': 0,
            'periodo_inicio': 'N/A',
            'periodo_fin': 'N/A',
            'recomendacion_general': 'Análisis en proceso'
        }
        
        try:
            # Datos de estructura
            if 'estructura' in datos and 'resumen_ejecutivo' in datos['estructura']:
                resumen_est = datos['estructura']['resumen_ejecutivo']
                metricas.update({
                    'total_tablas': resumen_est.get('total_tablas', 0),
                    'total_registros': f"{resumen_est.get('total_registros', 0):,}",
                    'tamano_mb': resumen_est.get('tamaño_total_mb', 0),
                    'calidad_promedio': resumen_est.get('calidad_promedio', 0)
                })
                
                # Periodo de cobertura
                periodo = resumen_est.get('periodo_cobertura', {})
                if periodo.get('inicio'):
                    metricas['periodo_inicio'] = str(periodo['inicio'])
                    metricas['periodo_fin'] = str(periodo['fin'])
                
                # Tablas prioritarias
                relevancia = resumen_est.get('tablas_por_relevancia', {})
                metricas['tablas_prioritarias'] = len(relevancia.get('muy_alta', [])) + len(relevancia.get('alta', []))
            
            # Datos de detección
            if 'deteccion' in datos and 'informe_detallado' in datos['deteccion']:
                informe_det = datos['deteccion']['informe_detallado']
                if 'resumen_ejecutivo' in informe_det:
                    resumen_det = informe_det['resumen_ejecutivo']
                    metricas['metricas_calculables'] = resumen_det.get('metricas_calculables', 0)
                    metricas['recomendacion_general'] = resumen_det.get('recomendacion_general', 'Análisis completado')
            
        except Exception as e:
            self.logger.error(f"Error extrayendo métricas: {e}")
        
        return metricas
    
    def generar_html_relevancia(self, datos: Dict[str, Any]) -> str:
        """Genera HTML para la sección de relevancia"""
        try:
            if 'estructura' in datos and 'resumen_ejecutivo' in datos['estructura']:
                relevancia = datos['estructura']['resumen_ejecutivo'].get('tablas_por_relevancia', {})
                
                muy_alta = len(relevancia.get('muy_alta', []))
                alta = len(relevancia.get('alta', []))
                media = len(relevancia.get('media', []))
                baja = len(relevancia.get('baja', []))
                
                return f'''
                <div class="metric-list">
                    <div class="metric-item">
                        <h4>🔴 Muy Alta Relevancia</h4>
                        <p>{muy_alta} tablas - Datos críticos para absentismo</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, muy_alta*10)}%"></div>
                        </div>
                    </div>
                    <div class="metric-item">
                        <h4>🟠 Alta Relevancia</h4>
                        <p>{alta} tablas - Datos complementarios importantes</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, alta*10)}%"></div>
                        </div>
                    </div>
                    <div class="metric-item">
                        <h4>🟡 Media Relevancia</h4>
                        <p>{media} tablas - Datos de apoyo</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, media*5)}%"></div>
                        </div>
                    </div>
                    <div class="metric-item">
                        <h4>⚪ Baja Relevancia</h4>
                        <p>{baja} tablas - Datos no relevantes</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, baja*2)}%"></div>
                        </div>
                    </div>
                </div>
                '''
        except Exception as e:
            self.logger.error(f"Error generando HTML relevancia: {e}")
        
        return '<p>Análisis de relevancia no disponible</p>'
    
    def generar_html_implementacion(self, datos: Dict[str, Any]) -> str:
        """Genera HTML para el plan de implementación"""
        return '''
        <div class="metric-list">
            <div class="metric-item">
                <h4>Fase 1 - Análisis Básico</h4>
                <p><strong>Objetivo:</strong> Implementar métricas básicas de absentismo</p>
                <p><strong>Tiempo estimado:</strong> 2-4 semanas</p>
                <p><strong>Tablas:</strong> 6042, 6043, 6044 (tiempo de trabajo)</p>
            </div>
            <div class="metric-item">
                <h4>Fase 2 - Análisis Avanzado</h4>
                <p><strong>Objetivo:</strong> Añadir dimensiones geográficas y sectoriales</p>
                <p><strong>Tiempo estimado:</strong> 4-6 semanas</p>
                <p><strong>Tablas:</strong> 6045, 6046, 6063 (detalle por sectores y CCAA)</p>
            </div>
            <div class="metric-item">
                <h4>Fase 3 - Dashboard Completo</h4>
                <p><strong>Objetivo:</strong> Sistema completo con IA</p>
                <p><strong>Tiempo estimado:</strong> 6-8 semanas</p>
                <p><strong>Tablas:</strong> Todas las tablas relevantes</p>
            </div>
        </div>
        '''
    
    def generar_html_casos_uso(self, datos: Dict[str, Any]) -> str:
        """Genera HTML para casos de uso"""
        return '''
        <div class="metric-list">
            <div class="metric-item" style="border-left-color: #e74c3c">
                <h4>Monitoreo de Absentismo por Sectores</h4>
                <p>Análisis en tiempo real del absentismo por sectores económicos</p>
                <p><strong>Complejidad:</strong> Media | <strong>Valor:</strong> Alto</p>
            </div>
            <div class="metric-item" style="border-left-color: #f39c12">
                <h4>Comparativas Geográficas</h4>
                <p>Análisis comparativo del absentismo entre comunidades autónomas</p>
                <p><strong>Complejidad:</strong> Media | <strong>Valor:</strong> Medio</p>
            </div>
            <div class="metric-item" style="border-left-color: #e74c3c">
                <h4>Predicción de Tendencias</h4>
                <p>Modelos predictivos para anticipar picos de absentismo</p>
                <p><strong>Complejidad:</strong> Alta | <strong>Valor:</strong> Alto</p>
            </div>
            <div class="metric-item" style="border-left-color: #f39c12">
                <h4>Análisis de Costes</h4>
                <p>Estimación del impacto económico del absentismo</p>
                <p><strong>Complejidad:</strong> Media | <strong>Valor:</strong> Medio</p>
            </div>
        </div>
        '''
    
    def generar_informe_completo(self, datos: Dict[str, Any], archivo_salida: str) -> bool:
        """
        Genera el informe HTML completo usando reemplazos seguros
        """
        try:
            self.logger.info("🎨 Generando informe HTML completo")
            
            # Extraer métricas principales
            metricas = self.extraer_metricas_resumen(datos)
            
            # Generar secciones HTML
            html_relevancia = self.generar_html_relevancia(datos)
            html_implementacion = self.generar_html_implementacion(datos)
            html_casos_uso = self.generar_html_casos_uso(datos)
            
            # Obtener plantilla base
            html_template = self.generar_template_html_base()
            
            # Reemplazar placeholders de forma segura
            html_final = html_template
            html_final = html_final.replace('{{TIMESTAMP_PLACEHOLDER}}', datetime.now().strftime("%d/%m/%Y %H:%M"))
            html_final = html_final.replace('{{TOTAL_TABLAS}}', str(metricas['total_tablas']))
            html_final = html_final.replace('{{TOTAL_REGISTROS}}', str(metricas['total_registros']))
            html_final = html_final.replace('{{TAMANO_MB}}', str(metricas['tamano_mb']))
            html_final = html_final.replace('{{CALIDAD_PROMEDIO}}', str(metricas['calidad_promedio']))
            html_final = html_final.replace('{{RECOMENDACION_GENERAL}}', metricas['recomendacion_general'])
            html_final = html_final.replace('{{TABLAS_PRIORITARIAS}}', str(metricas['tablas_prioritarias']))
            html_final = html_final.replace('{{METRICAS_CALCULABLES}}', str(metricas['metricas_calculables']))
            html_final = html_final.replace('{{PERIODO_INICIO}}', str(metricas['periodo_inicio']))
            html_final = html_final.replace('{{PERIODO_FIN}}', str(metricas['periodo_fin']))
            html_final = html_final.replace('{{RELEVANCIA_CONTENT}}', html_relevancia)
            html_final = html_final.replace('{{PLAN_IMPLEMENTACION}}', html_implementacion)
            html_final = html_final.replace('{{CASOS_USO}}', html_casos_uso)
            
            # Guardar archivo
            ruta_salida = Path(archivo_salida)
            ruta_salida.parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                f.write(html_final)
            
            self.logger.info(f"✅ Informe HTML generado: {ruta_salida}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generando informe: {e}")
            return False

def main():
    """Función principal"""
    print("🎨 GENERANDO INFORME DE FACTIBILIDAD CORREGIDO")
    print("="*50)
    
    generador = GeneradorInformeFactibilidadCorregido()
    
    # Rutas de archivos
    archivo_estructura = "../../informes/analisis_estructura_robusto.json"
    archivo_deteccion = "../../informes/deteccion_absentismo_detallada.json"
    archivo_salida = "../../informes/factibilidad_absentismo.html"
    
    # Cargar datos
    datos = generador.cargar_datos_analisis(archivo_estructura, archivo_deteccion)
    
    if not datos:
        print("❌ No se pudieron cargar los datos necesarios")
        return
    
    # Generar informe
    if generador.generar_informe_completo(datos, archivo_salida):
        print(f"✅ Informe HTML generado exitosamente")
        print(f"📁 Ubicación: {Path(archivo_salida).absolute()}")
        print(f"🌐 Abrir en navegador: file:///{Path(archivo_salida).absolute()}")
    else:
        print("❌ Error generando informe HTML")

if __name__ == "__main__":
    main()
