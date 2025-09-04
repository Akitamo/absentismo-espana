"""
Script para cargar todas las tablas ETCL requeridas a DuckDB
Procesa las 6 tablas necesarias: 6042, 6043, 6044, 6045, 6046, 6063
"""

import sys
import pandas as pd
from pathlib import Path
import logging
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio al path
sys.path.append(str(Path(__file__).parent))
# Añadir también la raíz del repo para importar correctamente el paquete
sys.path.append(str(Path(__file__).resolve().parents[2]))

from agent_processor.etl.extractor import Extractor
from agent_processor.etl.transformer import Transformer
from agent_processor.etl.loader import Loader

# Tablas requeridas según diseño validado
REQUIRED_TABLES = ['6042', '6043', '6044', '6045', '6046', '6063']

def load_all_tables(test_mode=False):
    """
    Carga todas las tablas ETCL requeridas a DuckDB
    
    Args:
        test_mode: Si True, procesa solo datos recientes para pruebas
    """
    print("\n" + "="*80)
    print("CARGA COMPLETA DE TABLAS ETCL A DUCKDB")
    print("="*80 + "\n")
    
    # Estadísticas generales
    stats_general = {
        'inicio': datetime.now(),
        'tablas_procesadas': [],
        'total_registros': 0,
        'errores': [],
        'detalles_por_tabla': {}
    }
    
    try:
        # Configuración: usar rutas desde la raíz del repo (CSV locales existentes)
        repo_root = Path(__file__).resolve().parents[2]
        raw_dir = repo_root / "data" / "raw" / "csv"
        db_path = repo_root / "data" / "analysis.db"
        
        # Cargar configuración
        config_path = repo_root / "agent_processor" / "config" / "mappings.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = {'mappings': json.load(f)}
        
        # Inicializar componentes
        extractor = Extractor(raw_dir, config)
        transformer = Transformer(config)
        loader = Loader(db_path)
        
        # Conectar a la base de datos
        loader.connect()
        
        # Limpiar tabla si es primera carga
        print("Preparando base de datos...")
        loader.create_schema()
        
        # Limpiar datos existentes (soporta --yes para auto-confirmar)
        if not test_mode:
            if any(arg in ("--yes", "-y") for arg in sys.argv[1:]):
                loader.conn.execute(f"DELETE FROM {loader.table_name}")
                print("Tabla limpiada (auto).")
            else:
                respuesta = input("\n¿Desea limpiar los datos existentes antes de cargar? (s/n): ")
                if respuesta.lower() == 's':
                    loader.conn.execute(f"DELETE FROM {loader.table_name}")
                    print("Tabla limpiada.")
        
        print("\nIniciando carga de tablas...")
        print("-" * 40)
        
        # Procesar cada tabla
        all_transformed_data = []
        
        for table_id in REQUIRED_TABLES:
            print(f"\nProcesando tabla {table_id}...")
            
            try:
                # Extraer datos
                print(f"  Extrayendo datos...")
                df_raw = extractor.extract_table(table_id, test_mode=test_mode)
                registros_extraidos = len(df_raw)
                print(f"  [OK] {registros_extraidos} registros extraídos")
                
                # Transformar datos
                print(f"  Transformando datos...")
                df_transformed = transformer.transform_table(table_id, df_raw)
                registros_transformados = len(df_transformed)
                print(f"  [OK] {registros_transformados} registros transformados")
                
                # Guardar para carga conjunta
                all_transformed_data.append(df_transformed)
                
                # Estadísticas por tabla
                stats_general['detalles_por_tabla'][table_id] = {
                    'registros_extraidos': registros_extraidos,
                    'registros_transformados': registros_transformados,
                    'metricas': df_transformed['metrica'].value_counts().to_dict() if 'metrica' in df_transformed.columns else {},
                    'periodos': df_transformed['periodo'].nunique() if 'periodo' in df_transformed.columns else 0,
                    'exitoso': True
                }
                
                stats_general['tablas_procesadas'].append(table_id)
                stats_general['total_registros'] += registros_transformados
                
            except Exception as e:
                error_msg = f"Error procesando tabla {table_id}: {str(e)}"
                logger.error(error_msg)
                stats_general['errores'].append(error_msg)
                stats_general['detalles_por_tabla'][table_id] = {
                    'exitoso': False,
                    'error': str(e)
                }
                continue
        
        # Combinar todos los datos transformados
        if all_transformed_data:
            print("\n" + "-" * 40)
            print("Combinando todos los datos...")
            df_combined = pd.concat(all_transformed_data, ignore_index=True)
            print(f"[OK] Total de registros a cargar: {len(df_combined)}")
            
            # Cargar a DuckDB
            print("\nCargando a DuckDB...")
            load_stats = loader.load(df_combined, replace=True)  # Replace para limpiar y cargar todo
            print(f"[OK] {load_stats['registros_cargados']} registros cargados exitosamente")
            
            # Obtener estadísticas finales de la BD
            print("\nObteniendo estadísticas de la base de datos...")
            db_stats = loader.get_stats()
            
            # Crear vistas de análisis
            print("\nCreando vistas de análisis...")
            loader.create_analysis_views()
            print("[OK] Vistas de análisis creadas")
            
        else:
            print("\n[ERROR] No se pudo procesar ninguna tabla")
            db_stats = {}
        
        # Desconectar
        loader.disconnect()
        
        # Calcular duración
        stats_general['fin'] = datetime.now()
        stats_general['duracion'] = str(stats_general['fin'] - stats_general['inicio'])
        
        # REPORTE FINAL
        print("\n" + "="*80)
        print("REPORTE DE CARGA COMPLETA")
        print("="*80)
        
        print(f"\nResumen General:")
        print(f"  Duración total: {stats_general['duracion']}")
        print(f"  Tablas procesadas: {len(stats_general['tablas_procesadas'])}/{len(REQUIRED_TABLES)}")
        print(f"  Total registros cargados: {stats_general['total_registros']}")
        
        if stats_general['errores']:
            print(f"\n  ⚠ Errores encontrados: {len(stats_general['errores'])}")
            for error in stats_general['errores']:
                print(f"    - {error}")
        
        print(f"\nDetalle por tabla:")
        print("-" * 60)
        print(f"{'Tabla':<10} {'Extraídos':<12} {'Transformados':<15} {'Estado':<10}")
        print("-" * 60)
        
        for table_id in REQUIRED_TABLES:
            if table_id in stats_general['detalles_por_tabla']:
                detalle = stats_general['detalles_por_tabla'][table_id]
                if detalle['exitoso']:
                    print(f"{table_id:<10} {detalle['registros_extraidos']:<12} "
                          f"{detalle['registros_transformados']:<15} {'OK':<10}")
                else:
                    print(f"{table_id:<10} {'ERROR':<12} {'ERROR':<15} {'FALLO':<10}")
            else:
                print(f"{table_id:<10} {'N/A':<12} {'N/A':<15} {'NO PROC':<10}")
        
        print("-" * 60)
        
        if db_stats:
            print(f"\nEstadísticas de la base de datos:")
            print(f"  Total registros en BD: {db_stats.get('total_registros', 0)}")
            
            if 'por_tabla' in db_stats:
                print(f"\n  Registros por tabla fuente:")
                for tabla, count in db_stats['por_tabla'].items():
                    print(f"    - {tabla}: {count:,} registros")
            
            if 'por_metrica' in db_stats:
                print(f"\n  Registros por métrica:")
                for metrica, count in db_stats['por_metrica'].items():
                    print(f"    - {metrica}: {count:,} registros")
            
            if 'ultimos_periodos' in db_stats:
                print(f"\n  Últimos periodos cargados:")
                for periodo, count in list(db_stats['ultimos_periodos'].items())[:3]:
                    print(f"    - {periodo}: {count:,} registros")
        
        # Ejecutar query de verificación
        if db_stats.get('total_registros', 0) > 0:
            print("\n" + "="*80)
            print("VERIFICACIÓN DE DATOS CARGADOS")
            print("="*80)
            
            loader.connect()
            
            # Query de resumen
            query_resumen = """
            SELECT 
                fuente_tabla,
                COUNT(DISTINCT periodo) as num_periodos,
                COUNT(DISTINCT metrica) as num_metricas,
                COUNT(*) as total_registros,
                MIN(periodo) as periodo_min,
                MAX(periodo) as periodo_max
            FROM observaciones_tiempo_trabajo
            GROUP BY fuente_tabla
            ORDER BY fuente_tabla
            """
            
            df_resumen = loader.execute_query(query_resumen)
            print("\nResumen por tabla fuente:")
            print(df_resumen.to_string(index=False))
            
            # Query de tasa de absentismo nacional
            query_absentismo = """
            SELECT 
                periodo,
                ROUND(AVG(tasa_absentismo), 2) as tasa_absentismo_promedio
            FROM v_tasa_absentismo
            WHERE ambito_territorial = 'NAC'
              AND cnae_nivel = 'TOTAL'
            GROUP BY periodo
            ORDER BY periodo DESC
            LIMIT 5
            """
            
            df_absentismo = loader.execute_query(query_absentismo)
            print("\nTasa de absentismo nacional (últimos periodos):")
            print(df_absentismo.to_string(index=False))
            
            loader.disconnect()
        
        print("\n" + "="*80)
        print("CARGA COMPLETADA EXITOSAMENTE")
        print("="*80)
        print(f"""
        Base de datos lista en: {db_path}
        Total de registros: {stats_general['total_registros']:,}
        Tablas procesadas: {', '.join(stats_general['tablas_procesadas'])}
        
        Próximos pasos:
        1. Validar los datos cargados
        2. Crear dashboard con Streamlit
        3. Implementar consultas en lenguaje natural
        """)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO]: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Modo no interactivo si se pasa --yes/-y
    if any(arg in ("--yes", "-y") for arg in sys.argv[1:]):
        test_mode = False
        print("\nModo completo (auto) - se cargarán todos los datos históricos")
    else:
        # Preguntar modo de ejecución
        print("\nOpciones de carga:")
        print("1. Carga completa (todos los datos)")
        print("2. Modo test (solo últimos 4 trimestres)")
        
        opcion = input("\nSeleccione opción (1 o 2): ")
        
        test_mode = (opcion == '2')
        
        if test_mode:
            print("\nModo test activado - se cargarán solo los últimos 4 trimestres")
        else:
            print("\nModo completo - se cargarán todos los datos históricos")
    
    success = load_all_tables(test_mode=test_mode)
    sys.exit(0 if success else 1)


