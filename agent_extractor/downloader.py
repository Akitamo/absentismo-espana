"""
Módulo de descarga robusta de CSVs del INE
Migrado y simplificado del proyecto original
"""

import requests
import json
import time
import csv
from pathlib import Path
from datetime import datetime
import logging
from .metadata_manager import MetadataManager

class Downloader:
    """Descarga robusta de tablas del INE con reintentos y validación"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / 'config' / 'tables.json'
        self.data_path = Path(__file__).parent.parent / 'data' / 'raw'
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self.session = self._create_session()
        self.logger = self._setup_logger()
        self.metadata_manager = MetadataManager()
    
    def _load_config(self):
        """Carga la configuración"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_session(self):
        """Crea sesión HTTP con configuración robusta"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/csv,application/csv,text/plain,*/*',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
        # Configurar reintentos automáticos
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _setup_logger(self):
        """Configura el logger"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Crear handler para archivo si no existe
        log_file = Path(__file__).parent.parent / 'downloads.log'
        if not logger.handlers:
            handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def download_all_tables(self, verbose=True):
        """Descarga todas las tablas configuradas"""
        resultados = {
            'fecha_inicio': datetime.now().isoformat(),
            'total_tablas': 0,
            'exitosas': [],
            'fallidas': [],
            'tiempo_total': 0
        }
        
        inicio = time.time()
        
        # Contar total de tablas
        for categoria_info in self.config['categorias'].values():
            resultados['total_tablas'] += len(categoria_info['tablas'])
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"DESCARGA DE TABLAS INE - ABSENTISMO")
            print(f"{'='*60}")
            print(f"Total de tablas a descargar: {resultados['total_tablas']}")
            print(f"{'='*60}\n")
        
        contador = 0
        
        for categoria, categoria_info in self.config['categorias'].items():
            if verbose:
                print(f"\n[{categoria.upper()}] - {categoria_info['descripcion']}")
                print(f"{'-'*50}")
            
            for codigo, tabla_info in categoria_info['tablas'].items():
                contador += 1
                
                if verbose:
                    print(f"[{contador}/{resultados['total_tablas']}] Descargando tabla {codigo}: {tabla_info['nombre'][:40]}...", end='')
                
                resultado = self._download_table(codigo, tabla_info)
                
                if resultado['exitoso']:
                    resultados['exitosas'].append(resultado)
                    if verbose:
                        print(f" ✓ ({resultado['tamaño_kb']:.1f} KB)")
                else:
                    resultados['fallidas'].append(resultado)
                    if verbose:
                        print(f" ✗ ({resultado['error']})")
                
                # Pequeña pausa entre descargas
                time.sleep(0.5)
        
        resultados['tiempo_total'] = time.time() - inicio
        resultados['fecha_fin'] = datetime.now().isoformat()
        
        # Guardar resumen
        self._save_download_summary(resultados)
        
        if verbose:
            self._print_summary(resultados)
        
        return resultados
    
    def download_single_table(self, codigo_tabla):
        """Descarga una tabla específica"""
        for categoria_info in self.config['categorias'].values():
            if codigo_tabla in categoria_info['tablas']:
                tabla_info = categoria_info['tablas'][codigo_tabla]
                return self._download_table(codigo_tabla, tabla_info)
        
        return {
            'exitoso': False,
            'codigo': codigo_tabla,
            'error': 'Tabla no encontrada en configuración'
        }
    
    def _download_table(self, codigo, tabla_info):
        """Descarga una tabla con reintentos y validación"""
        resultado = {
            'codigo': codigo,
            'nombre': tabla_info['nombre'],
            'exitoso': False,
            'intentos': 0,
            'tamaño_kb': 0,
            'encoding_usado': None,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        max_reintentos = self.config['configuracion_descarga']['reintentos_maximos']
        timeout = self.config['configuracion_descarga']['timeout_segundos']
        delay = self.config['configuracion_descarga']['delay_entre_reintentos']
        
        for intento in range(max_reintentos):
            resultado['intentos'] = intento + 1
            
            try:
                # Descargar el archivo
                response = self.session.get(
                    tabla_info['url_csv'],
                    timeout=timeout,
                    stream=True
                )
                
                if response.status_code == 200:
                    # Guardar el archivo
                    file_path = self.data_path / f"{codigo}.csv"
                    content = response.content
                    
                    # Intentar decodificar con diferentes encodings
                    texto_decodificado = None
                    for encoding in self.config['configuracion_descarga']['encodings_posibles']:
                        try:
                            texto_decodificado = content.decode(encoding)
                            resultado['encoding_usado'] = encoding
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if texto_decodificado:
                        # Verificar si necesita actualización antes de guardar
                        csv_path = self.data_path / 'csv' / f"{codigo}_{tabla_info['nombre'].replace(' ', '_').replace('/', '-')}.csv"
                        csv_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Crear backup si el archivo existe
                        if csv_path.exists():
                            self.metadata_manager.create_backup(csv_path)
                        
                        # Guardar con encoding UTF-8
                        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                            f.write(texto_decodificado)
                        
                        # Validar el CSV
                        if self._validate_csv(csv_path):
                            # Guardar metadata
                            self.metadata_manager.save_table_metadata(
                                codigo_tabla=codigo,
                                csv_path=csv_path,
                                url_origen=tabla_info['url_csv']
                            )
                            resultado['exitoso'] = True
                            resultado['tamaño_kb'] = len(content) / 1024
                            resultado['archivo'] = str(csv_path)
                            self.logger.info(f"Tabla {codigo} descargada y metadata actualizada")
                            return resultado
                        else:
                            resultado['error'] = 'CSV no válido'
                    else:
                        resultado['error'] = 'No se pudo decodificar el archivo'
                
                else:
                    resultado['error'] = f'HTTP {response.status_code}'
                    
            except requests.exceptions.Timeout:
                resultado['error'] = 'Timeout'
            except requests.exceptions.ConnectionError:
                resultado['error'] = 'Error de conexión'
            except Exception as e:
                resultado['error'] = str(e)
            
            # Si no fue exitoso y no es el último intento, esperar antes de reintentar
            if not resultado['exitoso'] and intento < max_reintentos - 1:
                time.sleep(delay * (intento + 1))  # Backoff exponencial
        
        self.logger.error(f"Error descargando tabla {codigo}: {resultado['error']}")
        return resultado
    
    def _validate_csv(self, file_path):
        """Valida que el archivo CSV sea legible"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                # Intentar leer las primeras líneas
                for i, row in enumerate(reader):
                    if i >= 5:  # Verificar solo las primeras 5 líneas
                        break
                    if not row or len(row) == 0:
                        return False
            return True
        except:
            return False
    
    def _save_download_summary(self, resultados):
        """Guarda el resumen de descargas"""
        summary_file = self.data_path.parent / 'metadata' / f"descarga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_file.parent.mkdir(exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    def _print_summary(self, resultados):
        """Imprime resumen de descargas"""
        print(f"\n{'='*60}")
        print(f"RESUMEN DE DESCARGA")
        print(f"{'='*60}")
        print(f"Total de tablas: {resultados['total_tablas']}")
        print(f"Exitosas: {len(resultados['exitosas'])}")
        print(f"Fallidas: {len(resultados['fallidas'])}")
        print(f"Tiempo total: {resultados['tiempo_total']:.1f} segundos")
        
        if resultados['fallidas']:
            print(f"\nTablas fallidas:")
            for falla in resultados['fallidas']:
                print(f"  - {falla['codigo']}: {falla['error']}")
        
        print(f"{'='*60}\n")