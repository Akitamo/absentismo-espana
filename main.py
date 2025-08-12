"""
Sistema de Extracción de Datos INE - Absentismo España v2
Punto de entrada principal para el agente extractor
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Añadir el directorio al path
sys.path.append(str(Path(__file__).parent))

from agent_extractor import INEExtractor

def main():
    parser = argparse.ArgumentParser(
        description='Agente Extractor INE - Sistema de descarga de datos de absentismo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --check              # Verificar actualizaciones
  python main.py --download-all       # Descargar todas las tablas
  python main.py --download 6042      # Descargar tabla específica
  python main.py --info 6042          # Ver información de una tabla
        """
    )
    
    parser.add_argument('--check', action='store_true',
                      help='Verificar actualizaciones en las tablas del INE')
    
    parser.add_argument('--download-all', action='store_true',
                      help='Descargar todas las tablas configuradas')
    
    parser.add_argument('--download', type=str, metavar='CODIGO',
                      help='Descargar una tabla específica por su código')
    
    parser.add_argument('--info', type=str, metavar='CODIGO',
                      help='Obtener información de una tabla específica')
    
    parser.add_argument('--quiet', action='store_true',
                      help='Modo silencioso, menos output')
    
    args = parser.parse_args()
    
    # Si no se proporciona ningún argumento, mostrar ayuda
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Inicializar el extractor
    print(f"\n{'='*60}")
    print(f"SISTEMA DE EXTRACCIÓN INE - ABSENTISMO ESPAÑA v2")
    print(f"{'='*60}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    extractor = INEExtractor()
    
    # Verificar actualizaciones
    if args.check:
        print("Verificando actualizaciones en el INE...")
        print("-" * 50)
        resultado = extractor.check_for_updates()
        
        print(f"\nTablas verificadas: {resultado['tablas_verificadas']}")
        
        if resultado['actualizaciones_detectadas']:
            print(f"\n¡Se detectaron {len(resultado['actualizaciones_detectadas'])} actualizaciones!")
            for tabla in resultado['actualizaciones_detectadas']:
                print(f"  • {tabla['codigo']}: {tabla['nombre'][:50]}")
                print(f"    Último periodo: {tabla.get('ultimo_periodo', 'N/A')}")
        else:
            print("No se detectaron actualizaciones nuevas.")
        
        if resultado['errores']:
            print(f"\n⚠ Se encontraron {len(resultado['errores'])} errores:")
            for error in resultado['errores'][:5]:  # Mostrar solo los primeros 5
                print(f"  • {error['codigo']}: {error['error']}")
    
    # Descargar todas las tablas
    elif args.download_all:
        print("Iniciando descarga de todas las tablas...")
        resultado = extractor.download_all(verbose=not args.quiet)
        
        if not args.quiet:
            print(f"\n✅ Descarga completada:")
            print(f"  • Exitosas: {len(resultado['exitosas'])}/{resultado['total_tablas']}")
            print(f"  • Tiempo: {resultado['tiempo_total']:.1f} segundos")
    
    # Descargar tabla específica
    elif args.download:
        codigo = args.download
        print(f"Descargando tabla {codigo}...")
        resultado = extractor.download_table(codigo)
        
        if resultado['exitoso']:
            print(f"✅ Tabla {codigo} descargada exitosamente")
            print(f"  • Tamaño: {resultado['tamaño_kb']:.1f} KB")
            print(f"  • Encoding: {resultado['encoding_usado']}")
        else:
            print(f"❌ Error descargando tabla {codigo}: {resultado['error']}")
    
    # Información de tabla
    elif args.info:
        codigo = args.info
        print(f"Obteniendo información de tabla {codigo}...")
        info = extractor.get_table_info(codigo)
        
        if info:
            print(f"\n📊 Información de tabla {codigo}:")
            print(f"  • Nombre: {info['nombre']}")
            print(f"  • Categoría: {info['categoria']}")
            print(f"  • Datos disponibles: {info['datos_disponibles']}")
            
            if info['periodo_info']['ultimo_periodo']:
                print(f"  • Último periodo: {info['periodo_info']['ultimo_periodo']}")
                print(f"  • Total periodos: {info['periodo_info']['total_periodos']}")
            
            print(f"\nURLs:")
            print(f"  • CSV: {info['url_csv']}")
            print(f"  • JSON: {info['url_json']}")
        else:
            print(f"❌ No se encontró información para la tabla {codigo}")
    
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)