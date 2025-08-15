"""
Script de validación para detectar y prevenir archivos duplicados
"""

import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent.parent))

def check_duplicates():
    """Verifica que no haya archivos duplicados en data/raw/csv"""
    
    base_path = Path(__file__).parent.parent
    csv_dir = base_path / 'data' / 'raw' / 'csv'
    config_path = base_path / 'config' / 'tables.json'
    
    # Cargar configuración
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Obtener todos los códigos de tabla
    codigos_tablas = set()
    for categoria, info in config['categorias'].items():
        codigos_tablas.update(info['tablas'].keys())
    
    print(f"Verificando duplicados para {len(codigos_tablas)} tablas...")
    print("-" * 60)
    
    duplicados_encontrados = False
    archivos_por_tabla = {}
    
    # Verificar cada tabla
    for codigo in sorted(codigos_tablas):
        archivos = list(csv_dir.glob(f"{codigo}_*.csv"))
        archivos_por_tabla[codigo] = archivos
        
        if len(archivos) > 1:
            duplicados_encontrados = True
            print(f"[DUPLICADO] Tabla {codigo}: {len(archivos)} archivos")
            for archivo in archivos:
                # Obtener fecha de modificación
                mtime = archivo.stat().st_mtime
                from datetime import datetime
                fecha = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"  - {archivo.name} (modificado: {fecha})")
        elif len(archivos) == 1:
            print(f"[OK] Tabla {codigo}: 1 archivo")
        else:
            print(f"[FALTA] Tabla {codigo}: Sin archivos")
    
    print("-" * 60)
    
    # Resumen
    total_archivos = sum(len(archivos) for archivos in archivos_por_tabla.values())
    tablas_con_archivos = sum(1 for archivos in archivos_por_tabla.values() if len(archivos) > 0)
    tablas_con_duplicados = sum(1 for archivos in archivos_por_tabla.values() if len(archivos) > 1)
    tablas_sin_archivos = sum(1 for archivos in archivos_por_tabla.values() if len(archivos) == 0)
    
    print(f"\nRESUMEN:")
    print(f"  Total de archivos CSV: {total_archivos}")
    print(f"  Tablas esperadas: {len(codigos_tablas)}")
    print(f"  Tablas con archivos: {tablas_con_archivos}")
    print(f"  Tablas con duplicados: {tablas_con_duplicados}")
    print(f"  Tablas sin archivos: {tablas_sin_archivos}")
    
    if duplicados_encontrados:
        print("\n[ADVERTENCIA] Se encontraron archivos duplicados!")
        print("Ejecute 'python scripts/clean_duplicates.py' para limpiar")
        return False
    else:
        print("\n[OK] No hay archivos duplicados")
        return True

def clean_duplicates():
    """Limpia archivos duplicados manteniendo el más reciente"""
    
    base_path = Path(__file__).parent.parent
    csv_dir = base_path / 'data' / 'raw' / 'csv'
    config_path = base_path / 'config' / 'tables.json'
    
    # Cargar configuración
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Obtener todos los códigos
    codigos_tablas = set()
    for categoria, info in config['categorias'].items():
        codigos_tablas.update(info['tablas'].keys())
    
    archivos_eliminados = 0
    
    for codigo in sorted(codigos_tablas):
        archivos = list(csv_dir.glob(f"{codigo}_*.csv"))
        
        if len(archivos) > 1:
            # Ordenar por fecha de modificación (más reciente primero)
            archivos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            print(f"Tabla {codigo}: Manteniendo {archivos[0].name}")
            
            # Eliminar los más antiguos
            for archivo in archivos[1:]:
                print(f"  Eliminando: {archivo.name}")
                archivo.unlink()
                archivos_eliminados += 1
    
    if archivos_eliminados > 0:
        print(f"\n[OK] Se eliminaron {archivos_eliminados} archivos duplicados")
    else:
        print("\n[OK] No había duplicados que eliminar")
    
    return archivos_eliminados

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        print("Limpiando duplicados...")
        clean_duplicates()
    else:
        check_duplicates()