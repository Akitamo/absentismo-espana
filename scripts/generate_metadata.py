"""
Script para generar metadata retroactivo de archivos CSV ya descargados
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from agent_extractor.metadata_manager import MetadataManager
import json

def generate_retroactive_metadata():
    """Genera metadata para archivos CSV existentes"""
    
    metadata_manager = MetadataManager()
    base_path = Path(__file__).parent.parent
    csv_dir = base_path / 'data' / 'raw' / 'csv'
    config_path = base_path / 'config' / 'tables.json'
    
    # Cargar configuración de tablas
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Mapear nombres de archivo a códigos de tabla
    archivo_a_codigo = {}
    for categoria, info in config['categorias'].items():
        for codigo, tabla_info in info['tablas'].items():
            nombre_archivo = f"{codigo}_{tabla_info['nombre'].replace(' ', '_').replace('/', '-')}.csv"
            archivo_a_codigo[nombre_archivo] = (codigo, tabla_info['url_csv'])
    
    # Procesar cada archivo CSV existente
    archivos_procesados = 0
    for csv_file in csv_dir.glob("*.csv"):
        # Buscar código correspondiente
        codigo_tabla = None
        url_origen = None
        
        for nombre_esperado, (codigo, url) in archivo_a_codigo.items():
            if csv_file.name == nombre_esperado:
                codigo_tabla = codigo
                url_origen = url
                break
        
        if not codigo_tabla:
            # Intentar extraer código del nombre del archivo
            codigo_tabla = csv_file.name.split('_')[0]
            print(f"[AVISO] Código extraído del nombre para {csv_file.name}: {codigo_tabla}")
        
        # Generar metadata
        metadata = metadata_manager.save_table_metadata(
            codigo_tabla=codigo_tabla,
            csv_path=csv_file,
            url_origen=url_origen
        )
        
        if metadata:
            print(f"[OK] Metadata generado para tabla {codigo_tabla}")
            print(f"     - Período: {metadata.get('ultimo_periodo', 'N/A')}")
            print(f"     - Tamaño: {metadata.get('tamaño_bytes', 0) / 1024:.1f} KB")
            archivos_procesados += 1
        else:
            print(f"[ERROR] No se pudo generar metadata para {csv_file.name}")
    
    print(f"\n=== RESUMEN ===")
    print(f"Archivos procesados: {archivos_procesados}")
    print(f"Metadata guardada en: {metadata_manager.metadata_dir}")
    
    # Mostrar resumen general
    summary = metadata_manager.get_all_metadata_summary()
    print(f"\nTablas con metadata: {len(summary['tablas'])}")
    
    # Mostrar últimos períodos disponibles
    periodos = set()
    for tabla in summary['tablas']:
        if tabla.get('ultimo_periodo'):
            periodos.add(tabla['ultimo_periodo'])
    
    if periodos:
        print(f"Períodos encontrados: {', '.join(sorted(periodos, reverse=True)[:5])}")

if __name__ == "__main__":
    generate_retroactive_metadata()