"""
Generador de Informe de Factibilidad - Sistema de Absentismo España
Crea informes visuales HTML interactivos sobre la factibilidad del análisis de absentismo
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

class GeneradorInformeFactibilidad:
    """
    Generador de informes HTML interactivos para análisis de factibilidad
    """
    
    def __init__(self):
        """Inicializa el generador"""
        self.logger = self._configurar_logging()
        self.template_html = self._cargar_template_html()
        
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
    
    def _cargar_template_html(self) -> str:
        """Carga la plantilla HTML completa"""
        return '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de Factibilidad - Absentismo España</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
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
        
        .stat-card:hover { transform: translateY(-5px); }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .stat-label { color: #7f8c8d; font-size: 1.1em; }
        
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
        
        .tabs {
            display: flex;
            border-bottom: 2px solid #ecf0f1;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .tab {
            padding: 15px 25px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.1em;
            color: #7f8c8d;
            transition: all 0.3s ease;
        }
        
        .tab.active, .tab:hover {
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; animation: fadeIn 0.3s ease; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
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
        
        tr:hover { background: #f8f9fa; }
        
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
        
        .metric-item h4 { color: #2c3e50; margin-bottom: 5px; }
        .metric-item p { color: #7f8c8d; font-size: 0.9em; }
        
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
            .tabs { flex-direction: column; }
            .tab { text-align: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Análisis de Factibilidad</h1>
            <p class="subtitle">Sistema de Análisis de Absentismo España</p>
            <p style="color: #7f8c8d; margin-top: 10px;">Generado el {timestamp}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_tablas}</div>
                <div class="stat-label">Tablas Analizadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_registros}</div>
                <div class="stat-label">Registros Totales</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{tamano_total_mb} MB</div>
                <div class="stat-label">Datos Totales</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{calidad_promedio}%</div>
                <div class="stat-label">Calidad Promedio</div>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Resumen Ejecutivo</h2>
            <div class="recommendation-box">
                <h3>Recomendación General</h3>
                <p>{recomendacion_general}</p>
            </div>
            
            <div class="metric-list">
                <div class="metric-item">
                    <h4>Tablas Prioritarias</h4>
                    <p>{tablas_prioritarias} tablas con datos críticos para absentismo</p>
                </div>
                <div class="metric-item">
                    <h4>Métricas Calculables</h4>
                    <p>{metricas_calculables} tipos de análisis posibles</p>
                </div>
                <div class="metric-item">
                    <h4>Cobertura Temporal</h4>
                    <p>{periodo_inicio} - {periodo_fin}</p>
                </div>
                <div class="metric-item">
                    <h4>Dimensiones Disponibles</h4>
                    <p>Geográfica, Sectorial, Temporal</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📈 Análisis por Relevancia</h2>
            <div class="tabs">
                <button class="tab active" onclick="showTab('relevancia-overview')">Resumen</button>
                <button class="tab" onclick="showTab('relevancia-detalle')">Detalle por Tabla</button>
                <button class="tab" onclick="showTab('relevancia-metricas')">Métricas Disponibles</button>
            </div>
            
            <div id="relevancia-overview" class="tab-content active">
                <div class="chart-container">
                    <canvas id="relevanciaPieChart"></canvas>
                </div>
                {relevancia_resumen_html}
            </div>
            
            <div id="relevancia-detalle" class="tab-content">
                {tablas_detalle_html}
            </div>
            
            <div id="relevancia-metricas" class="tab-content">
                {metricas_detalle_html}
            </div>
        </div>

        <div class="section">
            <h2>🛠️ Plan de Implementación</h2>
            {plan_implementacion_html}
        </div>

        <div class="section">
            <h2>💡 Casos de Uso Identificados</h2>
            {casos_uso_html}
        </div>

        <div class="footer">
            <p>Sistema de Análisis de Absentismo España • Generado automáticamente • INE ETCL Data</p>
        </div>
    </div>

    <script>
        function showTab(tabId) {
            // Ocultar todas las tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remover clase active de todos los botones
            document.querySelectorAll('.tab').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Mostrar tab seleccionada
            document.getElementById(tabId).classList.add('active');
            
            // Activar botón correspondiente
            event.target.classList.add('active');
        }

        // Gráfico de relevancia
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('relevanciaPieChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Muy Alta', 'Alta', 'Media', 'Baja'],
                    datasets: [{
                        data: {relevancia_datos},
                        backgroundColor: [
                            '#e74c3c',
                            '#f39c12', 
                            '#f1c40f',
                            '#95a5a6'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        title: {
                            display: true,
                            text: 'Distribución de Tablas por Relevancia'
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>
        '''
    
    def cargar_datos_analisis(self, archivo_estructura: str, archivo_deteccion: str) -> Dict[str, Any]:
        """
        Carga los datos de los análisis de estructura y detección
        
        Args:
            archivo_estructura: Archivo JSON del análisis de estructura
            archivo_deteccion: Archivo JSON de la detección de absentismo
            
        Returns:
            Diccionario con datos combinados
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
            'total_registros': 0,
            'tamano_total_mb': 0,
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
                    'tamano_total_mb': resumen_est.get('tamaño_total_mb', 0),
                    'calidad_promedio': resumen_est.get('calidad_promedio', 0)
                })
                
                # Periodo de cobertura
                periodo = resumen_est.get('periodo_cobertura', {})
                if periodo.get('inicio'):
                    metricas['periodo_inicio'] = periodo['inicio']
                    metricas['periodo_fin'] = periodo['fin']
                
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
    
    def generar_html_relevancia(self, datos: Dict[str, Any]) -> Dict[str, str]:
        """Genera HTML para la sección de relevancia"""
        html_sections = {
            'relevancia_resumen_html': '',
            'tablas_detalle_html': '',
            'metricas_detalle_html': '',
            'relevancia_datos': '[0, 0, 0, 0]'
        }
        
        try:
            if 'estructura' in datos and 'resumen_ejecutivo' in datos['estructura']:
                relevancia = datos['estructura']['resumen_ejecutivo'].get('tablas_por_relevancia', {})
                
                # Datos para el gráfico
                datos_grafico = [
                    len(relevancia.get('muy_alta', [])),
                    len(relevancia.get('alta', [])),
                    len(relevancia.get('media', [])),
                    len(relevancia.get('baja', []))
                ]
                html_sections['relevancia_datos'] = str(datos_grafico)
                
                # Resumen de relevancia
                html_sections['relevancia_resumen_html'] = f'''
                <div class="metric-list">
                    <div class="metric-item">
                        <h4>🔴 Muy Alta Relevancia</h4>
                        <p>{len(relevancia.get('muy_alta', []))} tablas - Datos críticos para absentismo</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, len(relevancia.get('muy_alta', []))*10)}%"></div>
                        </div>
                    </div>
                    <div class="metric-item">
                        <h4>🟠 Alta Relevancia</h4>
                        <p>{len(relevancia.get('alta', []))} tablas - Datos complementarios importantes</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, len(relevancia.get('alta', []))*10)}%"></div>
                        </div>
                    </div>
                    <div class="metric-item">
                        <h4>🟡 Media Relevancia</h4>
                        <p>{len(relevancia.get('media', []))} tablas - Datos de apoyo</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, len(relevancia.get('media', []))*5)}%"></div>
                        </div>
                    </div>
                    <div class="metric-item">
                        <h4>⚪ Baja Relevancia</h4>
                        <p>{len(relevancia.get('baja', []))} tablas - Datos no relevantes</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, len(relevancia.get('baja', []))*2)}%"></div>
                        </div>
                    </div>
                </div>
                '''
            
            # Tabla detalle
            if 'deteccion' in datos and 'informe_detallado' in datos['deteccion']:
                detalle_tablas = datos['deteccion']['informe_detallado'].get('detalle_por_tabla', {})
                
                filas_tabla = []
                for tabla_id, info in detalle_tablas.items():
                    utilidad = info.get('utilidad', 'baja')
                    score = info.get('score_absentismo', 0)
                    calculos = ', '.join(info.get('calculos_posibles', [])[:3])  # Primeros 3
                    
                    badge_class = f"badge-{utilidad.replace('_', '-')}"
                    
                    filas_tabla.append(f'''
                    <tr>
                        <td><strong>{tabla_id}</strong></td>
                        <td><span class="badge {badge_class}">{utilidad.replace('_', ' ')}</span></td>
                        <td>{score}</td>
                        <td>{info.get('columnas_relevantes', 0)}</td>
                        <td>{calculos or 'Ninguno'}</td>
                    </tr>
                    ''')
                
                html_sections['tablas_detalle_html'] = f'''
                <table>
                    <thead>
                        <tr>
                            <th>Tabla ID</th>
                            <th>Utilidad</th>
                            <th>Score Absentismo</th>
                            <th>Columnas Relevantes</th>
                            <th>Cálculos Posibles</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(filas_tabla)}
                    </tbody>
                </table>
                '''
            
            # Métricas disponibles
            if 'deteccion' in datos and 'deteccion_raw' in datos['deteccion']:
                metricas_disp = datos['deteccion']['deteccion_raw'].get('metricas_calculables', {}).get('disponibles', {})
                
                items_metricas = []
                for metrica, tablas in metricas_disp.items():
                    if tablas:
                        nombre_metrica = metrica.replace('_', ' ').title()
                        items_metricas.append(f'''
                        <div class="metric-item">
                            <h4>{nombre_metrica}</h4>
                            <p>Disponible en {len(tablas)} tablas: {', '.join(tablas[:5])}</p>
                        </div>
                        ''')
                
                html_sections['metricas_detalle_html'] = f'''
                <div class="metric-list">
                    {''.join(items_metricas)}
                </div>
                '''
                
        except Exception as e:
            self.logger.error(f"Error generando HTML relevancia: {e}")
        
        return html_sections
    
    def generar_html_implementacion(self, datos: Dict[str, Any]) -> str:
        """Genera HTML para el plan de implementación"""
        try:
            if ('deteccion' in datos and 
                'deteccion_raw' in datos['deteccion'] and 
                'recomendaciones' in datos['deteccion']['deteccion_raw']):
                
                recom = datos['deteccion']['deteccion_raw']['recomendaciones']
                orden = recom.get('orden_implementacion', [])
                
                fases_html = []
                for fase in orden:
                    tablas_str = ', '.join(fase.get('tablas', []))
                    
                    fases_html.append(f'''
                    <div class="metric-item">
                        <h4>Fase {fase.get('fase', 'N/A')} - {fase.get('prioridad', 'Normal')}</h4>
                        <p><strong>Objetivo:</strong> {fase.get('objetivo', 'Sin objetivo definido')}</p>
                        <p><strong>Tiempo estimado:</strong> {fase.get('tiempo_estimado', 'Por determinar')}</p>
                        <p><strong>Tablas:</strong> {tablas_str}</p>
                    </div>
                    ''')
                
                return f'''
                <div class="metric-list">
                    {''.join(fases_html)}
                </div>
                '''
            
        except Exception as e:
            self.logger.error(f"Error generando HTML implementación: {e}")
        
        return '<p>Plan de implementación no disponible</p>'
    
    def generar_html_casos_uso(self, datos: Dict[str, Any]) -> str:
        """Genera HTML para casos de uso"""
        try:
            if ('deteccion' in datos and 
                'informe_detallado' in datos['deteccion'] and 
                'casos_uso_identificados' in datos['deteccion']['informe_detallado']):
                
                casos = datos['deteccion']['informe_detallado']['casos_uso_identificados']
                
                casos_html = []
                for caso in casos:
                    valor_color = {
                        'Alto': '#e74c3c',
                        'Medio': '#f39c12', 
                        'Bajo': '#95a5a6'
                    }.get(caso.get('valor_negocio', 'Medio'), '#95a5a6')
                    
                    casos_html.append(f'''
                    <div class="metric-item" style="border-left-color: {valor_color}">
                        <h4>{caso.get('titulo', 'Caso de uso')}</h4>
                        <p>{caso.get('descripcion', 'Sin descripción')}</p>
                        <p><strong>Complejidad:</strong> {caso.get('complejidad', 'Media')} | 
                           <strong>Valor:</strong> {caso.get('valor_negocio', 'Medio')}</p>
                    </div>
                    ''')
                
                return f'''
                <div class="metric-list">
                    {''.join(casos_html)}
                </div>
                '''
                
        except Exception as e:
            self.logger.error(f"Error generando HTML casos uso: {e}")
        
        return '<p>Casos de uso no disponibles</p>'
    
    def generar_informe_completo(self, datos: Dict[str, Any], archivo_salida: str) -> bool:
        """
        Genera el informe HTML completo
        
        Args:
            datos: Datos combinados de análisis
            archivo_salida: Ruta del archivo HTML de salida
            
        Returns:
            True si se generó correctamente
        """
        try:
            self.logger.info("🎨 Generando informe HTML completo")
            
            # Extraer métricas principales
            metricas = self.extraer_metricas_resumen(datos)
            
            # Generar secciones HTML
            html_relevancia = self.generar_html_relevancia(datos)
            html_implementacion = self.generar_html_implementacion(datos)
            html_casos_uso = self.generar_html_casos_uso(datos)
            
            # Preparar variables para la plantilla
            variables = {
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M"),
                **metricas,
                **html_relevancia,
                'plan_implementacion_html': html_implementacion,
                'casos_uso_html': html_casos_uso
            }
            
            # Generar HTML final
            html_final = self.template_html.format(**variables)
            
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
    print("🎨 GENERANDO INFORME DE FACTIBILIDAD")
    print("="*50)
    
    generador = GeneradorInformeFactibilidad()
    
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
