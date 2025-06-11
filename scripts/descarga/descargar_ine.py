"""
Extractor CSV del INE para Sistema de Absentismo España
Descarga archivos CSV de las tablas ETCL del INE de forma robusta y configurable
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import requests
import hashlib
import pandas as pd

# Importar desde la nueva ubicación
import sys
sys.path.append(str(Path(__file__).parent.parent))

from utilidades.helpers import (
    configurar_logging, crear_directorios, crear_sesion_robusta,
    validar_archivo_csv, crear_backup_archivo, necesita_descarga,
    generar_informe_descarga, limpiar_nombre_archivo, obtener_info_tabla
)
from utilidades.config import CONFIG, PROJECT_ROOT, DATA_RAW_PATH, SNAPSHOTS_PATH

class ExtractorCSV_INE:
    """
    Extractor configurable y robusto para archivos CSV del INE
    """
    
    def __init__(self):
        """
        Inicializa el extractor usando la configuración del módulo config
        """
        self.config = CONFIG
        self.logger = configurar_logging(self.config)
        self.session = crear_sesion_robusta(
            timeout=self.config['configuracion_descarga']['timeout_segundos'],
            reintentos=self.config['configuracion_descarga']['reintentos_maximos']
        )
        self.urls_data = {}
        
        # Crear directorios necesarios
        crear_directorios(self.config)
        
        self.logger.info("ExtractorCSV_INE inicializado correctamente")
    
    def cargar_urls_etcl(self, urls_file: str = None) -> bool:
        """
        Carga las URLs desde el archivo de URLs completo
        
        Args:
            urls_file: Archivo con las URLs del ETCL
            
        Returns:
            True si se cargaron correctamente
        """
        if urls_file is None:
            urls_file = str(PROJECT_ROOT / "urls_etcl_completo.json")
            
        urls_path = Path(urls_file)
        if not urls_path.exists():
            self.logger.error(f"Archivo de URLs no encontrado: {urls_file}")
            return False
        
        try:
            with open(urls_path, 'r', encoding='utf-8') as f:
                self.urls_data = json.load(f)
            
            self.logger.info(f"URLs cargadas desde {urls_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cargando URLs: {e}")
            return False
    
    def obtener_tablas_activas(self) -> List[Tuple[str, str, Dict[str, str]]]:
        """
        Obtiene lista de tablas activas según configuración
        
        Returns:
            Lista de tuplas (tabla_id, url_csv, info_tabla)
        """
        tablas_activas = []
        
        for categoria, data in self.config['categorias'].items():
            if not data.get('activa', False):
                continue
                
            for tabla_id in data.get('tablas', []):
                # Buscar URL en los datos cargados
                url_csv = self._obtener_url_csv(tabla_id)
                if url_csv:
                    info_tabla = obtener_info_tabla(tabla_id, self.config)
                    tablas_activas.append((tabla_id, url_csv, info_tabla))
                else:
                    self.logger.warning(f"URL CSV no encontrada para tabla {tabla_id}")
        
        self.logger.info(f"Tablas activas encontradas: {len(tablas_activas)}")
        return tablas_activas
    
    def _obtener_url_csv(self, tabla_id: str) -> Optional[str]:
        """Obtiene la URL CSV para una tabla específica"""
        if not self.urls_data:
            return None
        
        # Buscar en la estructura de URLs (nueva estructura)
        if 'tablas' in self.urls_data:
            for tabla in self.urls_data['tablas']:
                if tabla.get('codigo_tabla') == tabla_id:
                    return tabla.get('urls', {}).get('csv', {}).get('url')
        
        # Buscar en urls_individuales como fallback
        if 'urls_individuales' in self.urls_data:
            for url_data in self.urls_data['urls_individuales']:
                if (url_data.get('codigo_tabla') == tabla_id and 
                    url_data.get('tipo') == 'csv'):
                    return url_data.get('url')
        
        return None
    
    def descargar_archivo(self, url: str, filepath: Path, tabla_id: str, 
                         info_tabla: Dict[str, str]) -> Dict[str, Any]:
        """
        Descarga un archivo CSV con reintentos automáticos
        
        Args:
            url: URL del archivo
            filepath: Ruta de destino
            tabla_id: ID de la tabla
            info_tabla: Información de la tabla
            
        Returns:
            Diccionario con resultado de la descarga
        """
        resultado = {
            'tabla_id': tabla_id,
            'url': url,
            'archivo': str(filepath),
            'exito': False,
            'error': None,
            'tamaño_bytes': 0,
            'tiempo_descarga': 0,
            'reintentos_usados': 0,
            'info_tabla': info_tabla
        }
        
        inicio = time.time()
        
        # Verificar si necesita descarga
        if not necesita_descarga(url, filepath, self.config, self.urls_data):
            self.logger.info(f"Archivo {tabla_id} ya existe y es válido, omitiendo descarga")
            resultado.update({
                'exito': True,
                'error': 'omitido_existe',
                'tamaño_bytes': filepath.stat().st_size if filepath.exists() else 0
            })
            return resultado
        
        # Crear backup si existe archivo previo
        if filepath.exists() and self.config['configuracion_descarga']['crear_backup']:
            backup_dir = PROJECT_ROOT / self.config['rutas']['backups']
            backup_path = crear_backup_archivo(filepath, backup_dir)
            if backup_path:
                self.logger.info(f"Backup creado: {backup_path}")
        
        # Intentar descarga con reintentos
        max_reintentos = self.config['configuracion_descarga']['reintentos_maximos']
        delay = self.config['configuracion_descarga']['delay_entre_reintentos']
        
        for intento in range(max_reintentos + 1):
            try:
                self.logger.info(f"Descargando {tabla_id} (intento {intento + 1}/{max_reintentos + 1})")
                
                response = self.session.get(url, stream=True)
                response.raise_for_status()
                
                # Descargar archivo
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Validar archivo descargado
                if self.config['configuracion_descarga']['validar_csv']:
                    validacion = validar_archivo_csv(filepath)
                    if not validacion['valido']:
                        raise ValueError(f"CSV inválido: {validacion['error']}")
                
                # Éxito
                resultado.update({
                    'exito': True,
                    'tamaño_bytes': filepath.stat().st_size,
                    'reintentos_usados': intento
                })
                
                self.logger.info(f"✅ {tabla_id} descargado exitosamente "
                               f"({resultado['tamaño_bytes']} bytes)")
                break
                
            except Exception as e:
                error_msg = str(e)
                resultado['error'] = error_msg
                resultado['reintentos_usados'] = intento
                
                if intento < max_reintentos:
                    self.logger.warning(f"❌ Error descargando {tabla_id} (intento {intento + 1}): {error_msg}")
                    self.logger.info(f"Reintentando en {delay} segundos...")
                    time.sleep(delay)
                    delay *= 2  # Backoff exponencial
                else:
                    self.logger.error(f"❌ Error final descargando {tabla_id}: {error_msg}")
                    # Limpiar archivo parcial si existe
                    if filepath.exists():
                        try:
                            filepath.unlink()
                        except:
                            pass
        
        resultado['tiempo_descarga'] = time.time() - inicio
        return resultado
    
    def descargar_todas_activas(self) -> Dict[str, Any]:
        """
        Descarga todas las tablas activas según configuración
        
        Returns:
            Diccionario con resultados de todas las descargas
        """
        if not self.urls_data:
            if not self.cargar_urls_etcl():
                return {'error': 'No se pudieron cargar las URLs'}
        
        tablas_activas = self.obtener_tablas_activas()
        if not tablas_activas:
            return {'error': 'No hay tablas activas configuradas'}
        
        self.logger.info(f"🚀 Iniciando descarga de {len(tablas_activas)} tablas")
        
        resultados = []
        data_dir = DATA_RAW_PATH
        
        for tabla_id, url_csv, info_tabla in tablas_activas:
            # Generar nombre de archivo
            nombre_limpio = limpiar_nombre_archivo(info_tabla['nombre'])
            filename = f"{tabla_id}_{nombre_limpio}.csv"
            filepath = data_dir / filename
            
            # Descargar
            resultado = self.descargar_archivo(url_csv, filepath, tabla_id, info_tabla)
            resultados.append(resultado)
            
            # Pausa entre descargas para ser respetuosos con el servidor
            time.sleep(1)
        
        # Generar informe
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        informe_path = PROJECT_ROOT / self.config['rutas']['logs'] / f"informe_descarga_{timestamp}.json"
        informe = generar_informe_descarga(resultados, informe_path)
        
        # Log resumen
        resumen = informe['resumen']
        self.logger.info(f"🏁 Descarga completada: {resumen['exitosos']}/{resumen['total_intentos']} "
                        f"exitosos ({resumen['tasa_exito']:.1%})")
        
        # Generar snapshot automáticamente si hubo descargas exitosas
        if resumen['exitosos'] > 0:
            self.logger.info("📸 Generando snapshot de los archivos descargados...")
            resultado_snapshot = self.generar_snapshot()
            if resultado_snapshot.get('exito'):
                self.logger.info(f"✅ Snapshot guardado en: {resultado_snapshot['directorio']}")
                informe['snapshot'] = resultado_snapshot
            else:
                self.logger.warning(f"⚠️ No se pudo generar snapshot: {resultado_snapshot.get('error')}")
        
        return informe
    
    def listar_tablas_disponibles(self) -> Dict[str, List[Dict[str, str]]]:
        """Lista todas las tablas disponibles por categoría"""
        if not self.urls_data:
            self.cargar_urls_etcl()
        
        disponibles = {}
        
        for categoria, data in self.config['categorias'].items():
            disponibles[categoria] = []
            for tabla_id in data.get('tablas', []):
                url_csv = self._obtener_url_csv(tabla_id)
                disponibles[categoria].append({
                    'id': tabla_id,
                    'nombre': data.get('nombres', {}).get(tabla_id, f"Tabla {tabla_id}"),
                    'activa': data.get('activa', False),
                    'url_disponible': url_csv is not None
                })
        
        return disponibles
    
    def activar_categoria(self, categoria: str) -> bool:
        """Activa una categoría específica"""
        self.logger.warning("Para activar categorías, modifique config.py directamente")
        return False
    
    def desactivar_categoria(self, categoria: str) -> bool:
        """Desactiva una categoría específica"""
        self.logger.warning("Para desactivar categorías, modifique config.py directamente")
        return False
    
    def activar_todas_categorias(self) -> bool:
        """Activa todas las categorías disponibles"""
        self.logger.warning("Para activar todas las categorías, modifique config.py directamente")
        self.logger.info("Establezca 'activa': True en todas las categorías del CONFIG")
        return False
    
    def verificar_sistema(self) -> Dict[str, Any]:
        """Verifica el estado del sistema antes de descarga masiva"""
        verificacion = {
            'espacio_disponible_gb': 0,
            'conexion_ine': False,
            'directorios_ok': False,
            'config_valida': False,
            'urls_cargadas': False,
            'tablas_totales': 0,
            'tablas_activas': 0,
            'estimacion_descarga': {
                'archivos_total': 0,
                'tamaño_estimado_mb': 0,
                'tiempo_estimado_min': 0
            }
        }
        
        try:
            # Verificar espacio en disco
            import shutil
            espacio_libre = shutil.disk_usage(DATA_RAW_PATH)[-1]
            verificacion['espacio_disponible_gb'] = round(espacio_libre / (1024**3), 2)
            
            # Verificar directorios
            verificacion['directorios_ok'] = all([
                DATA_RAW_PATH.exists(),
                (PROJECT_ROOT / self.config['rutas']['logs']).exists()
            ])
            
            # Verificar configuración
            verificacion['config_valida'] = bool(self.config.get('categorias'))
            
            # Verificar URLs cargadas
            verificacion['urls_cargadas'] = bool(self.urls_data)
            
            # Contar tablas
            total_tablas = sum(len(cat.get('tablas', [])) for cat in self.config['categorias'].values())
            tablas_activas = len(self.obtener_tablas_activas())
            verificacion['tablas_totales'] = total_tablas
            verificacion['tablas_activas'] = tablas_activas
            
            # Estimación de descarga (basada en archivos actuales)
            verificacion['estimacion_descarga'] = {
                'archivos_total': total_tablas,
                'tamaño_estimado_mb': round(total_tablas * 2.0, 1),  # 2MB promedio por archivo
                'tiempo_estimado_min': round((total_tablas * 0.5), 1)  # 30 seg promedio por archivo
            }
            
            # Verificar conexión al INE (prueba rápida)
            try:
                response = self.session.get('https://servicios.ine.es/', timeout=10)
                verificacion['conexion_ine'] = response.status_code == 200
            except:
                verificacion['conexion_ine'] = False
                
        except Exception as e:
            self.logger.error(f"Error en verificación del sistema: {e}")
        
        return verificacion
    
    def generar_snapshot(self) -> Dict[str, Any]:
        """
        Genera un snapshot de los CSVs descargados con metadatos completos
        
        Returns:
            Diccionario con resultado del proceso
        """
        try:
            # Crear directorio para snapshots si no existe
            snapshot_base = SNAPSHOTS_PATH
            snapshot_base.mkdir(exist_ok=True)
            
            # Crear directorio con fecha actual
            fecha_snapshot = datetime.now().strftime("%Y-%m-%d")
            snapshot_dir = snapshot_base / fecha_snapshot
            snapshot_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"📸 Generando snapshot en {snapshot_dir}")
            
            # Obtener lista de CSVs descargados
            csv_files = list(DATA_RAW_PATH.glob("*.csv"))
            
            if not csv_files:
                self.logger.warning("No se encontraron archivos CSV para generar snapshot")
                return {'exito': False, 'error': 'No hay CSVs descargados'}
            
            # Preparar estructuras de datos
            metadata = {
                'fecha_descarga': datetime.now().isoformat(),
                'version_ine': f"{datetime.now().year}_T{(datetime.now().month - 1) // 3 + 1}",
                'archivos_totales': len(csv_files),
                'tamaño_total_mb': 0,
                'estado': 'completo',
                'errores': []
            }
            
            checksums = {}
            summary = {}
            
            # Procesar cada archivo CSV
            tamaño_total = 0
            archivos_procesados = 0
            
            for csv_file in csv_files:
                try:
                    self.logger.info(f"Procesando {csv_file.name}...")
                    
                    # Calcular checksums
                    md5_hash = hashlib.md5()
                    sha256_hash = hashlib.sha256()
                    
                    with open(csv_file, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            md5_hash.update(chunk)
                            sha256_hash.update(chunk)
                    
                    # Obtener información del archivo
                    tamaño_bytes = csv_file.stat().st_size
                    tamaño_total += tamaño_bytes
                    
                    # Leer CSV para obtener metadatos
                    try:
                        # Intentar diferentes encodings
                        df = None
                        for encoding in ['utf-8', 'latin1', 'cp1252']:
                            try:
                                df = pd.read_csv(csv_file, encoding=encoding, nrows=5)
                                break
                            except:
                                continue
                        
                        if df is not None:
                            # Contar total de filas (sin cargar todo en memoria)
                            with open(csv_file, 'r', encoding=encoding) as f:
                                num_filas = sum(1 for line in f) - 1  # -1 por el header
                            
                            checksums[csv_file.name] = {
                                'md5': md5_hash.hexdigest(),
                                'sha256': sha256_hash.hexdigest(),
                                'tamaño_bytes': tamaño_bytes,
                                'filas': num_filas,
                                'columnas': len(df.columns)
                            }
                            
                            # Leer primera y última fila para summary
                            df_tail = pd.read_csv(csv_file, encoding=encoding, skiprows=lambda x: x > 0 and x < num_filas)
                            
                            summary[csv_file.name] = {
                                'headers': df.columns.tolist(),
                                'tipos_datos': df.dtypes.astype(str).tolist(),
                                'primera_fila': df.iloc[0].tolist() if len(df) > 0 else [],
                                'ultima_fila': df_tail.iloc[-1].tolist() if len(df_tail) > 0 else []
                            }
                        else:
                            raise ValueError("No se pudo leer el CSV con ningún encoding")
                        
                        archivos_procesados += 1
                        
                    except Exception as e:
                        self.logger.error(f"Error leyendo CSV {csv_file.name}: {e}")
                        metadata['errores'].append(f"{csv_file.name}: {str(e)}")
                        
                        # Agregar información básica aunque no se pueda leer el contenido
                        checksums[csv_file.name] = {
                            'md5': md5_hash.hexdigest(),
                            'sha256': sha256_hash.hexdigest(),
                            'tamaño_bytes': tamaño_bytes,
                            'filas': -1,
                            'columnas': -1,
                            'error': str(e)
                        }
                        
                except Exception as e:
                    self.logger.error(f"Error procesando archivo {csv_file.name}: {e}")
                    metadata['errores'].append(f"{csv_file.name}: {str(e)}")
            
            # Actualizar metadata
            metadata['tamaño_total_mb'] = round(tamaño_total / (1024 * 1024), 2)
            metadata['archivos_procesados'] = archivos_procesados
            
            # Guardar JSONs
            with open(snapshot_dir / 'metadata.json', 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            with open(snapshot_dir / 'checksums.json', 'w', encoding='utf-8') as f:
                json.dump(checksums, f, indent=2, ensure_ascii=False)
            
            with open(snapshot_dir / 'summary.json', 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Snapshot generado exitosamente en {snapshot_dir}")
            self.logger.info(f"   - Archivos procesados: {archivos_procesados}/{len(csv_files)}")
            self.logger.info(f"   - Tamaño total: {metadata['tamaño_total_mb']} MB")
            
            return {
                'exito': True,
                'directorio': str(snapshot_dir),
                'archivos_procesados': archivos_procesados,
                'archivos_totales': len(csv_files),
                'tamaño_mb': metadata['tamaño_total_mb']
            }
            
        except Exception as e:
            self.logger.error(f"Error generando snapshot: {e}")
            return {'exito': False, 'error': str(e)}

def main():
    """Función principal para uso desde línea de comandos"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extractor CSV del INE')
    parser.add_argument('--urls', default=None,
                       help='Archivo de URLs (por defecto busca en raíz del proyecto)')
    parser.add_argument('--listar', action='store_true',
                       help='Listar tablas disponibles')
    parser.add_argument('--verificar-sistema', action='store_true',
                       help='Verificar estado del sistema antes de descarga')
    
    args = parser.parse_args()
    
    # Inicializar extractor
    extractor = ExtractorCSV_INE()
    extractor.cargar_urls_etcl(args.urls)
    
    if args.verificar_sistema:
        verificacion = extractor.verificar_sistema()
        print("\n=== VERIFICACIÓN DEL SISTEMA ===")
        print(f"✅ Espacio disponible: {verificacion['espacio_disponible_gb']} GB")
        print(f"{'✅' if verificacion['conexion_ine'] else '❌'} Conexión al INE")
        print(f"{'✅' if verificacion['directorios_ok'] else '❌'} Directorios")
        print(f"{'✅' if verificacion['config_valida'] else '❌'} Configuración")
        print(f"{'✅' if verificacion['urls_cargadas'] else '❌'} URLs cargadas")
        print(f"\n📊 Tablas: {verificacion['tablas_activas']}/{verificacion['tablas_totales']} activas")
        est = verificacion['estimacion_descarga']
        print(f"📦 Estimación descarga completa: {est['archivos_total']} archivos, ~{est['tamaño_estimado_mb']} MB, ~{est['tiempo_estimado_min']} min")
    
    elif args.listar:
        disponibles = extractor.listar_tablas_disponibles()
        print("\n=== TABLAS DISPONIBLES ===")
        for categoria, tablas in disponibles.items():
            activa = "✅" if any(t['activa'] for t in tablas) else "❌"
            print(f"\n{activa} {categoria.upper()}:")
            for tabla in tablas:
                url_ok = "✅" if tabla['url_disponible'] else "❌"
                estado = "ACTIVA" if tabla['activa'] else "inactiva"
                print(f"  {url_ok} {tabla['id']}: {tabla['nombre']} ({estado})")
        
        # Mostrar resumen
        total_tablas = sum(len(cat) for cat in disponibles.values())
        total_activas = sum(1 for cat in disponibles.values() for t in cat if t['activa'])
        print(f"\n📊 RESUMEN: {total_activas}/{total_tablas} tablas activas")
        print(f"💡 Para activar más tablas, edite config.py")
    
    else:
        # Descarga por defecto (solo tablas activas)
        disponibles = extractor.listar_tablas_disponibles()
        total_activas = sum(1 for cat in disponibles.values() for t in cat if t['activa'])
        
        if total_activas == 0:
            print("⚠️  No hay tablas activas.")
            print("   Edite config.py para activar las categorías que desee descargar.")
        else:
            print(f"🚀 Iniciando descarga de {total_activas} tablas activas...")
            informe = extractor.descargar_todas_activas()
            
            if 'error' in informe:
                print(f"❌ Error: {informe['error']}")
            else:
                resumen = informe['resumen']
                print(f"🏁 Completado: {resumen['exitosos']}/{resumen['total_intentos']} "
                      f"exitosos ({resumen['tasa_exito']:.1%})")

if __name__ == "__main__":
    main()
