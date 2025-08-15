"""
Módulo de actualización inteligente para el Agent Extractor
Verifica y descarga solo las tablas con nuevos datos disponibles
"""

import json
import requests
from pathlib import Path
from datetime import datetime
import logging
from .metadata_manager import MetadataManager
from .downloader import Downloader

class UpdateManager:
    """Gestiona actualizaciones inteligentes de tablas INE"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.config_path = self.base_path / 'config' / 'tables.json'
        self.metadata_manager = MetadataManager()
        self.downloader = Downloader()
        self.logger = logging.getLogger(__name__)
        
        # Cargar configuración
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_remote_period(self, tabla_info):
        """Obtiene el último período disponible en el INE para una tabla"""
        try:
            # Usar la API JSON del INE para obtener metadata
            response = self.session.get(tabla_info['url_json'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Buscar el período más reciente en los datos
                # La estructura exacta puede variar, intentamos varios caminos
                periodo = None
                
                # Intento 1: Buscar en estructura de datos
                if isinstance(data, list) and len(data) > 0:
                    # Buscar campo que contenga período
                    for item in data[:5]:  # Revisar primeros elementos
                        for key, value in item.items():
                            if 'periodo' in key.lower() or 'period' in key.lower():
                                periodo = value
                                break
                        if periodo:
                            break
                
                # Intento 2: Si es estructura diferente
                if not periodo and isinstance(data, dict):
                    # Buscar en valores del diccionario
                    for key, value in data.items():
                        if 'data' in key.lower() and isinstance(value, list):
                            if len(value) > 0 and isinstance(value[0], dict):
                                for k, v in value[0].items():
                                    if 'periodo' in k.lower():
                                        periodo = v
                                        break
                
                # Si no encontramos período, intentar descargar CSV y extraerlo
                if not periodo:
                    periodo = self._extract_period_from_csv(tabla_info['url_csv'])
                
                return periodo
                
        except Exception as e:
            self.logger.error(f"Error obteniendo período remoto: {e}")
            return None
    
    def _extract_period_from_csv(self, url_csv):
        """Extrae el período del CSV descargando solo las primeras líneas"""
        try:
            # Descargar solo parte del archivo
            response = self.session.get(url_csv, stream=True, timeout=10)
            
            if response.status_code == 200:
                # Leer solo las primeras líneas
                lines = []
                for line in response.iter_lines(decode_unicode=True):
                    lines.append(line)
                    if len(lines) > 5:  # Solo necesitamos las primeras líneas
                        break
                
                # Buscar columna de período
                if len(lines) > 1:
                    header = lines[0].split(';')
                    if 'Periodo' in header:
                        periodo_idx = header.index('Periodo')
                        data_line = lines[1].split(';')
                        if len(data_line) > periodo_idx:
                            return data_line[periodo_idx]
        except Exception as e:
            self.logger.error(f"Error extrayendo período del CSV: {e}")
        
        return None
    
    def check_table_updates(self, codigo_tabla):
        """Verifica si una tabla específica tiene actualizaciones"""
        # Buscar información de la tabla en la configuración
        tabla_info = None
        for categoria, info in self.config['categorias'].items():
            if codigo_tabla in info['tablas']:
                tabla_info = info['tablas'][codigo_tabla]
                break
        
        if not tabla_info:
            return {
                'codigo': codigo_tabla,
                'error': 'Tabla no encontrada en configuración',
                'necesita_actualizacion': False
            }
        
        # Obtener metadata local
        metadata_local = self.metadata_manager.get_table_metadata(codigo_tabla)
        periodo_local = metadata_local.get('ultimo_periodo') if metadata_local else None
        
        # Obtener período remoto
        periodo_remoto = self.check_remote_period(tabla_info)
        
        # Comparar períodos
        necesita_actualizacion = False
        mensaje = ""
        
        if not periodo_local:
            necesita_actualizacion = True
            mensaje = "No hay datos locales"
        elif not periodo_remoto:
            mensaje = "No se pudo verificar período remoto"
        elif periodo_local != periodo_remoto:
            # Comparar períodos
            comparacion = self.metadata_manager._compare_periods(periodo_local, periodo_remoto)
            if comparacion < 0:
                necesita_actualizacion = True
                mensaje = f"Nuevo período disponible: {periodo_remoto} (local: {periodo_local})"
            else:
                mensaje = f"Tabla actualizada (período: {periodo_local})"
        else:
            mensaje = f"Tabla actualizada (período: {periodo_local})"
        
        return {
            'codigo': codigo_tabla,
            'nombre': tabla_info.get('nombre', ''),
            'periodo_local': periodo_local,
            'periodo_remoto': periodo_remoto,
            'necesita_actualizacion': necesita_actualizacion,
            'mensaje': mensaje
        }
    
    def check_all_updates(self, verbose=True):
        """Verifica actualizaciones para todas las tablas"""
        resultados = {
            'fecha_verificacion': datetime.now().isoformat(),
            'total_tablas': 0,
            'actualizaciones_disponibles': 0,
            'tablas': []
        }
        
        for categoria, info in self.config['categorias'].items():
            if verbose:
                print(f"\n[INFO] Verificando categoría: {categoria}")
            
            for codigo_tabla in info['tablas'].keys():
                if verbose:
                    print(f"  Verificando tabla {codigo_tabla}...", end=" ")
                
                resultado = self.check_table_updates(codigo_tabla)
                resultados['tablas'].append(resultado)
                resultados['total_tablas'] += 1
                
                if resultado['necesita_actualizacion']:
                    resultados['actualizaciones_disponibles'] += 1
                    if verbose:
                        print(f"[ACTUALIZACIÓN DISPONIBLE]")
                else:
                    if verbose:
                        print("[OK]")
        
        return resultados
    
    def update_table(self, codigo_tabla):
        """Actualiza una tabla específica si hay nuevos datos"""
        # Verificar si necesita actualización
        check_result = self.check_table_updates(codigo_tabla)
        
        if not check_result['necesita_actualizacion']:
            return {
                'codigo': codigo_tabla,
                'actualizado': False,
                'mensaje': check_result['mensaje']
            }
        
        # Proceder con la actualización
        print(f"[INFO] Actualizando tabla {codigo_tabla}...")
        
        # Buscar TODOS los archivos existentes para esta tabla (por patrón)
        csv_dir = self.base_path / 'data' / 'raw' / 'csv'
        archivos_existentes = list(csv_dir.glob(f"{codigo_tabla}_*.csv"))
        
        # Crear backup y eliminar archivos antiguos
        for archivo_actual in archivos_existentes:
            if archivo_actual.exists():
                backup_path = self.metadata_manager.create_backup(archivo_actual)
                print(f"  Backup creado: {backup_path.name}")
                
                # IMPORTANTE: Eliminar el archivo original después del backup
                try:
                    archivo_actual.unlink()
                    print(f"  Archivo antiguo eliminado: {archivo_actual.name}")
                except Exception as e:
                    self.logger.warning(f"No se pudo eliminar {archivo_actual.name}: {e}")
        
        # Descargar nueva versión
        resultado_descarga = self.downloader.download_single_table(codigo_tabla)
        
        if resultado_descarga['exitoso']:
            # Verificar que solo quede UN archivo para esta tabla
            archivos_finales = list(csv_dir.glob(f"{codigo_tabla}_*.csv"))
            if len(archivos_finales) > 1:
                self.logger.warning(f"ADVERTENCIA: Múltiples archivos para tabla {codigo_tabla}: {[f.name for f in archivos_finales]}")
                # Intentar limpieza automática manteniendo el más reciente
                archivos_finales.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for archivo_extra in archivos_finales[1:]:
                    try:
                        archivo_extra.unlink()
                        print(f"  Limpieza: Eliminado duplicado {archivo_extra.name}")
                    except Exception as e:
                        self.logger.error(f"No se pudo eliminar duplicado {archivo_extra.name}: {e}")
            elif len(archivos_finales) == 0:
                self.logger.error(f"ERROR: No se encontró archivo para tabla {codigo_tabla} después de la descarga")
            
            return {
                'codigo': codigo_tabla,
                'actualizado': True,
                'periodo_anterior': check_result['periodo_local'],
                'periodo_nuevo': check_result['periodo_remoto'],
                'mensaje': 'Actualización exitosa'
            }
        else:
            return {
                'codigo': codigo_tabla,
                'actualizado': False,
                'mensaje': f"Error en descarga: {resultado_descarga.get('error', 'Desconocido')}"
            }
    
    def update_all(self, verbose=True):
        """Actualiza todas las tablas que tengan nuevos datos disponibles"""
        print("\n" + "="*60)
        print("INICIANDO ACTUALIZACIÓN MASIVA")
        print("="*60)
        
        # Primero verificar qué tablas necesitan actualización
        verificacion = self.check_all_updates(verbose=False)
        
        if verificacion['actualizaciones_disponibles'] == 0:
            print("\n[INFO] No hay actualizaciones disponibles. Todas las tablas están al día.")
            return {
                'fecha_actualizacion': datetime.now().isoformat(),
                'tablas_actualizadas': 0,
                'errores': 0
            }
        
        print(f"\n[INFO] Se encontraron {verificacion['actualizaciones_disponibles']} tablas con actualizaciones disponibles")
        
        # Actualizar solo las que lo necesitan
        resultados = {
            'fecha_actualizacion': datetime.now().isoformat(),
            'tablas_actualizadas': 0,
            'errores': 0,
            'detalles': []
        }
        
        for tabla in verificacion['tablas']:
            if tabla['necesita_actualizacion']:
                print(f"\nActualizando {tabla['codigo']}: {tabla['nombre'][:50]}...")
                resultado = self.update_table(tabla['codigo'])
                
                if resultado['actualizado']:
                    resultados['tablas_actualizadas'] += 1
                    print(f"  [OK] Actualizado de {resultado.get('periodo_anterior', 'N/A')} a {resultado.get('periodo_nuevo', 'N/A')}")
                else:
                    resultados['errores'] += 1
                    print(f"  [ERROR] {resultado['mensaje']}")
                
                resultados['detalles'].append(resultado)
        
        # Guardar resumen de actualización
        resumen_path = self.base_path / 'data' / 'metadata' / 'ultima_actualizacion.json'
        with open(resumen_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        # Validación final de duplicados
        print("\n[VALIDACIÓN DE DUPLICADOS]")
        csv_dir = self.base_path / 'data' / 'raw' / 'csv'
        duplicados = []
        
        # Verificar todas las tablas procesadas
        for detalle in resultados['detalles']:
            if detalle['actualizado']:
                codigo = detalle['codigo']
                archivos = list(csv_dir.glob(f"{codigo}_*.csv"))
                if len(archivos) > 1:
                    duplicados.append(f"{codigo} ({len(archivos)} archivos)")
        
        if duplicados:
            print(f"  [ADVERTENCIA] Duplicados detectados: {', '.join(duplicados)}")
            resultados['advertencias'] = f"Duplicados en: {duplicados}"
        else:
            print(f"  [OK] Sin duplicados detectados")
        
        print("\n" + "="*60)
        print("RESUMEN DE ACTUALIZACIÓN")
        print("="*60)
        print(f"Tablas actualizadas: {resultados['tablas_actualizadas']}")
        print(f"Errores: {resultados['errores']}")
        if duplicados:
            print(f"Advertencias: {len(duplicados)} tablas con duplicados")
        print(f"Resumen guardado en: {resumen_path}")
        
        return resultados