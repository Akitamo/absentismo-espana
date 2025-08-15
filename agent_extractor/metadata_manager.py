"""
Gestor de Metadata para el Agent Extractor
Gestiona el tracking de versiones y actualizaciones de las tablas INE
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
import logging

class MetadataManager:
    """Gestiona metadata de las tablas descargadas"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.metadata_dir = self.base_path / 'data' / 'metadata'
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def calculate_file_hash(self, file_path):
        """Calcula el hash SHA256 de un archivo"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculando hash: {e}")
            return None
    
    def extract_last_period(self, csv_path):
        """Extrae el último período disponible del CSV"""
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    # Buscar columna de periodo en la primera línea de datos
                    header = lines[0].strip().split(';')
                    if 'Periodo' in header:
                        periodo_idx = header.index('Periodo')
                        # Segunda línea tiene los datos más recientes
                        data_line = lines[1].strip().split(';')
                        if len(data_line) > periodo_idx:
                            return data_line[periodo_idx]
        except Exception as e:
            self.logger.error(f"Error extrayendo período: {e}")
        return None
    
    def get_table_metadata(self, codigo_tabla):
        """Obtiene metadata de una tabla específica"""
        metadata_file = self.metadata_dir / f"{codigo_tabla}_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error leyendo metadata de {codigo_tabla}: {e}")
        return None
    
    def save_table_metadata(self, codigo_tabla, csv_path, url_origen=None):
        """Guarda metadata de una tabla"""
        metadata = {
            'codigo_tabla': codigo_tabla,
            'fecha_descarga': datetime.now().isoformat(),
            'archivo': str(csv_path),
            'ultimo_periodo': self.extract_last_period(csv_path),
            'hash_archivo': self.calculate_file_hash(csv_path),
            'tamaño_bytes': csv_path.stat().st_size if csv_path.exists() else 0,
            'url_origen': url_origen,
            'version': 1  # Para futuro control de versiones
        }
        
        # Si existe metadata anterior, incrementar versión
        old_metadata = self.get_table_metadata(codigo_tabla)
        if old_metadata:
            metadata['version'] = old_metadata.get('version', 0) + 1
            metadata['version_anterior'] = {
                'fecha': old_metadata.get('fecha_descarga'),
                'periodo': old_metadata.get('ultimo_periodo'),
                'hash': old_metadata.get('hash_archivo')
            }
        
        metadata_file = self.metadata_dir / f"{codigo_tabla}_metadata.json"
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Metadata guardada para tabla {codigo_tabla}")
            return metadata
        except Exception as e:
            self.logger.error(f"Error guardando metadata: {e}")
            return None
    
    def check_table_needs_update(self, codigo_tabla, remote_periodo):
        """Verifica si una tabla necesita actualización"""
        metadata = self.get_table_metadata(codigo_tabla)
        
        if not metadata:
            # No hay metadata, necesita descarga
            return True, "No existe metadata local"
        
        local_periodo = metadata.get('ultimo_periodo')
        
        if not local_periodo:
            return True, "No se pudo determinar período local"
        
        # Comparar períodos (formato: 2024T4, 2024T3, etc.)
        if self._compare_periods(local_periodo, remote_periodo) < 0:
            return True, f"Nuevo período disponible: {remote_periodo} (local: {local_periodo})"
        
        return False, f"Tabla actualizada (período: {local_periodo})"
    
    def _compare_periods(self, period1, period2):
        """Compara dos períodos en formato YYYYTQ"""
        try:
            # Extraer año y trimestre
            year1, quarter1 = period1.replace('T', ' ').split()
            year2, quarter2 = period2.replace('T', ' ').split()
            
            year1, year2 = int(year1), int(year2)
            quarter1, quarter2 = int(quarter1), int(quarter2)
            
            if year1 != year2:
                return year1 - year2
            return quarter1 - quarter2
        except:
            return 0
    
    def create_backup(self, csv_path):
        """Crea backup del archivo anterior antes de actualizar"""
        if csv_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.base_path / 'data' / 'backups'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_name = f"{csv_path.stem}_{timestamp}{csv_path.suffix}"
            backup_path = backup_dir / backup_name
            
            try:
                import shutil
                shutil.copy2(csv_path, backup_path)
                self.logger.info(f"Backup creado: {backup_path}")
                return backup_path
            except Exception as e:
                self.logger.error(f"Error creando backup: {e}")
                return None
    
    def get_all_metadata_summary(self):
        """Obtiene resumen de metadata de todas las tablas"""
        summary = {
            'fecha_resumen': datetime.now().isoformat(),
            'tablas': []
        }
        
        for metadata_file in self.metadata_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    summary['tablas'].append({
                        'codigo': metadata.get('codigo_tabla'),
                        'ultimo_periodo': metadata.get('ultimo_periodo'),
                        'fecha_descarga': metadata.get('fecha_descarga'),
                        'version': metadata.get('version', 1)
                    })
            except Exception as e:
                self.logger.error(f"Error leyendo {metadata_file}: {e}")
        
        return summary