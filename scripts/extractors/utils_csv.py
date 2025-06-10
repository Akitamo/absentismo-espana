"""
Utilidades para extracción y manejo de archivos CSV del INE
"""

import os
import csv
import time
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def configurar_logging(config: Dict[str, Any]) -> logging.Logger:
    """Configura el sistema de logging"""
    # Crear directorio de logs si no existe
    log_dir = Path(config['rutas']['logs'])
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar logger
    logger = logging.getLogger('ExtractorCSV')
    logger.setLevel(getattr(logging, config['logging']['nivel']))
    
    # Evitar duplicar handlers
    if not logger.handlers:
        # Handler para archivo
        file_handler = logging.FileHandler(
            config['logging']['archivo'], 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(config['logging']['formato'])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def crear_directorios(config: Dict[str, Any]) -> None:
    """Crea todos los directorios necesarios"""
    for ruta in config['rutas'].values():
        Path(ruta).mkdir(parents=True, exist_ok=True)

def crear_sesion_robusta(timeout: int = 30, reintentos: int = 3) -> requests.Session:
    """Crea una sesión de requests con reintentos automáticos"""
    session = requests.Session()
    
    # Configuración de reintentos
    retry_strategy = Retry(
        total=reintentos,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.timeout = timeout
    
    return session

def calcular_hash_archivo(filepath: Path) -> Optional[str]:
    """Calcula el hash MD5 de un archivo"""
    if not filepath.exists():
        return None
    
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def validar_archivo_csv(filepath: Path, min_filas: int = 2) -> Dict[str, Any]:
    """
    Valida que un archivo CSV sea válido
    
    Returns:
        Dict con información de validación:
        - valido: bool
        - filas: int
        - columnas: int
        - error: str (si hay error)
    """
    resultado = {
        'valido': False,
        'filas': 0,
        'columnas': 0,
        'error': None,
        'encoding_detectado': None
    }
    
    if not filepath.exists():
        resultado['error'] = "Archivo no existe"
        return resultado
    
    if filepath.stat().st_size == 0:
        resultado['error'] = "Archivo vacío"
        return resultado
    
    # Intentar diferentes encodings
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                # Detectar delimitador
                sample = f.read(1024)
                f.seek(0)
                
                # Intentar detectar dialecto
                try:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample, delimiters=',;\t|')
                except:
                    dialect = csv.excel  # fallback
                
                reader = csv.reader(f, dialect)
                filas = 0
                columnas = 0
                
                for i, row in enumerate(reader):
                    filas += 1
                    if i == 0:
                        columnas = len(row)
                    
                    # Verificar consistencia de columnas
                    if len(row) != columnas and i > 0:
                        # Permitir algunas inconsistencias menores
                        pass
                    
                    # Limitar verificación para archivos grandes
                    if i > 100:
                        break
                
                if filas >= min_filas and columnas > 0:
                    resultado.update({
                        'valido': True,
                        'filas': filas,
                        'columnas': columnas,
                        'encoding_detectado': encoding
                    })
                    return resultado
                else:
                    resultado['error'] = f"Insuficientes filas ({filas}) o columnas ({columnas})"
                    
        except Exception as e:
            continue  # Probar siguiente encoding
    
    if not resultado['valido'] and not resultado['error']:
        resultado['error'] = "No se pudo leer con ningún encoding"
    
    return resultado

def crear_backup_archivo(filepath: Path, backup_dir: Path) -> Optional[Path]:
    """Crea backup de un archivo existente"""
    if not filepath.exists():
        return None
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
    backup_path = backup_dir / backup_name
    
    try:
        import shutil
        shutil.copy2(filepath, backup_path)
        return backup_path
    except Exception:
        return None

def necesita_descarga(url: str, filepath: Path, config: Dict[str, Any], 
                     urls_data: Dict[str, Any]) -> bool:
    """
    Determina si necesita descargar un archivo
    
    Args:
        url: URL del archivo
        filepath: Ruta local del archivo
        config: Configuración
        urls_data: Datos de URLs con información de fechas
    """
    # Si no existe, descargar
    if not filepath.exists():
        return True
    
    # Si configurado para sobrescribir, descargar
    if config['configuracion_descarga']['sobrescribir_existentes']:
        return True
    
    # Si no se debe verificar existencia, no descargar
    if not config['configuracion_descarga']['verificar_existencia']:
        return False
    
    # Verificar si el archivo local es válido
    validacion = validar_archivo_csv(filepath)
    if not validacion['valido']:
        return True
    
    # TODO: Aquí se podría agregar verificación de fecha de modificación
    # comparando con metadatos del INE si estuvieran disponibles
    
    return False

def generar_informe_descarga(resultados: List[Dict[str, Any]], 
                           archivo_informe: Path) -> Dict[str, Any]:
    """Genera informe completo de resultados de descarga"""
    total = len(resultados)
    exitosos = sum(1 for r in resultados if r.get('exito', False))
    errores = total - exitosos
    
    # Calcular métricas adicionales
    tamaño_total_bytes = sum(r.get('tamaño_bytes', 0) for r in resultados if r.get('exito', False))
    tamaño_total_mb = round(tamaño_total_bytes / (1024 * 1024), 2)
    
    tiempo_total_seg = sum(r.get('tiempo_descarga', 0) for r in resultados)
    tiempo_total_min = round(tiempo_total_seg / 60, 2)
    
    reintentos_totales = sum(r.get('reintentos_usados', 0) for r in resultados)
    
    # Agrupar errores
    errores_por_tipo = {}
    archivos_fallidos = []
    
    for r in resultados:
        if not r.get('exito', False) and r.get('error') not in ['omitido_existe']:
            error_tipo = str(r.get('error', 'desconocido'))
            errores_por_tipo[error_tipo] = errores_por_tipo.get(error_tipo, 0) + 1
            archivos_fallidos.append({
                'tabla_id': r.get('tabla_id'),
                'error': error_tipo,
                'url': r.get('url')
            })
    
    informe = {
        'timestamp': datetime.now().isoformat(),
        'resumen': {
            'total_intentos': total,
            'exitosos': exitosos,
            'errores': errores,
            'tasa_exito': exitosos / total if total > 0 else 0,
            'tamaño_total_mb': tamaño_total_mb,
            'tiempo_total_min': tiempo_total_min,
            'reintentos_totales': reintentos_totales,
            'promedio_mb_por_archivo': round(tamaño_total_mb / exitosos, 2) if exitosos > 0 else 0,
            'promedio_seg_por_archivo': round(tiempo_total_seg / total, 2) if total > 0 else 0
        },
        'errores_detallados': {
            'por_tipo': errores_por_tipo,
            'archivos_fallidos': archivos_fallidos
        },
        'estadisticas_descarga': {
            'archivos_omitidos': sum(1 for r in resultados if r.get('error') == 'omitido_existe'),
            'archivos_nuevos': sum(1 for r in resultados if r.get('exito') and r.get('error') != 'omitido_existe'),
            'tamaño_promedio_mb': round(tamaño_total_mb / exitosos, 2) if exitosos > 0 else 0
        },
        'resultados_detallados': resultados
    }
    
    # Guardar informe como JSON
    import json
    try:
        with open(archivo_informe, 'w', encoding='utf-8') as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error guardando informe: {e}")
    
    return informe

def limpiar_nombre_archivo(nombre: str) -> str:
    """Limpia nombre de archivo de caracteres no válidos"""
    import re
    # Remover caracteres no válidos para nombres de archivo incluyendo comas y espacios
    nombre_limpio = re.sub(r'[<>:"/\\|?*,\s]+', '_', nombre)
    # Remover múltiples guiones bajos consecutivos
    nombre_limpio = re.sub(r'_+', '_', nombre_limpio)
    # Remover guiones bajos al inicio y final
    nombre_limpio = nombre_limpio.strip('_')
    # Limitar longitud
    if len(nombre_limpio) > 80:
        nombre_limpio = nombre_limpio[:80]
    return nombre_limpio

def obtener_info_tabla(tabla_id: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Obtiene información de una tabla desde la configuración"""
    for categoria, data in config['categorias'].items():
        if tabla_id in data.get('tablas', []):
            return {
                'categoria': categoria,
                'nombre': data.get('nombres', {}).get(tabla_id, f"Tabla {tabla_id}"),
                'descripcion': data.get('descripcion', '')
            }
    return {
        'categoria': 'desconocida',
        'nombre': f"Tabla {tabla_id}",
        'descripcion': ''
    }