"""
CSV Explorer - Análisis básico de estructura de archivos CSV del INE
Fase 1: Exploración básica de estructura
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Añadir el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

class CSVExplorer:
    """Explorador básico de estructura de CSVs"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / 'data' / 'raw' / 'csv'
        self.reports_path = self.base_path / 'data' / 'exploration_reports' / 'structure'
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        # Cargar configuración de tablas
        config_path = self.base_path / 'config' / 'tables.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def explore_csv(self, codigo_tabla):
        """Analiza la estructura básica de un CSV"""
        
        # Buscar el archivo CSV
        csv_files = list(self.data_path.glob(f"{codigo_tabla}_*.csv"))
        if not csv_files:
            return {"error": f"No se encontró archivo CSV para tabla {codigo_tabla}"}
        
        csv_file = csv_files[0]
        print(f"Analizando: {csv_file.name}")
        
        # Resultados del análisis
        analysis = {
            "codigo_tabla": codigo_tabla,
            "archivo": csv_file.name,
            "fecha_analisis": datetime.now().isoformat(),
            "tamaño_bytes": csv_file.stat().st_size,
            "tamaño_mb": round(csv_file.stat().st_size / (1024*1024), 2)
        }
        
        # Intentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        content = None
        
        for encoding in encodings:
            try:
                with open(csv_file, 'r', encoding=encoding) as f:
                    content = f.read()
                    analysis['encoding'] = encoding
                    break
            except UnicodeDecodeError:
                continue
        
        if not content:
            return {"error": f"No se pudo leer el archivo con ningún encoding"}
        
        # Analizar estructura
        lines = content.strip().split('\n')
        
        # Detectar separador
        if ';' in lines[0]:
            delimiter = ';'
        elif ',' in lines[0]:
            delimiter = ','
        elif '\t' in lines[0]:
            delimiter = '\t'
        else:
            delimiter = ','
        
        analysis['separador'] = delimiter
        
        # Leer como CSV
        csv_reader = csv.reader(lines, delimiter=delimiter)
        rows = list(csv_reader)
        
        # Información básica
        analysis['num_filas'] = len(rows) - 1  # Sin contar header
        analysis['num_columnas'] = len(rows[0]) if rows else 0
        
        # Columnas
        if rows:
            # Limpiar BOM y caracteres especiales de las columnas
            columnas = [col.replace('\ufeff', '').strip() for col in rows[0]]
            analysis['columnas'] = columnas
            
            # Analizar cada columna
            columnas_info = {}
            for i, col in enumerate(columnas):
                col_values = [row[i] if i < len(row) else '' for row in rows[1:]]
                
                # Valores únicos (muestra)
                unique_values = list(set(col_values[:1000]))  # Muestra de primeros 1000
                
                columnas_info[col] = {
                    "posicion": i,
                    "valores_unicos_muestra": len(unique_values),
                    "tiene_vacios": '' in unique_values,
                    "primeros_valores": unique_values[:5] if len(unique_values) <= 10 else unique_values[:3]
                }
                
                # Detectar tipo probable
                if col.lower() in ['periodo', 'period']:
                    columnas_info[col]['tipo_probable'] = 'temporal'
                elif col.lower() in ['total', 'valor', 'coste', 'horas']:
                    columnas_info[col]['tipo_probable'] = 'metrica'
                elif len(unique_values) < 100:
                    columnas_info[col]['tipo_probable'] = 'dimension'
                else:
                    columnas_info[col]['tipo_probable'] = 'metrica'
            
            analysis['columnas_detalle'] = columnas_info
            
            # Primeras y últimas filas (sin header)
            analysis['primeras_filas'] = [dict(zip(columnas, row)) for row in rows[1:4]]
            analysis['ultimas_filas'] = [dict(zip(columnas, row)) for row in rows[-3:]]
            
            # Detectar período temporal
            if 'Periodo' in columnas:
                periodo_idx = columnas.index('Periodo')
                periodos = [row[periodo_idx] for row in rows[1:] if periodo_idx < len(row)]
                periodos_unicos = sorted(list(set(periodos)))
                
                if periodos_unicos:
                    analysis['rango_temporal'] = {
                        "primer_periodo": periodos_unicos[0],
                        "ultimo_periodo": periodos_unicos[-1],
                        "total_periodos": len(periodos_unicos)
                    }
        
        return analysis
    
    def explore_all(self):
        """Explora todas las tablas configuradas"""
        resultados = {
            "fecha_exploracion": datetime.now().isoformat(),
            "tablas_analizadas": 0,
            "tablas": {}
        }
        
        # Recorrer todas las categorías y tablas
        for categoria, info in self.config['categorias'].items():
            print(f"\nExplorando categoría: {categoria}")
            
            for codigo_tabla, tabla_info in info['tablas'].items():
                print(f"  Tabla {codigo_tabla}: {tabla_info['nombre'][:50]}...")
                
                analysis = self.explore_csv(codigo_tabla)
                
                if 'error' not in analysis:
                    resultados['tablas'][codigo_tabla] = analysis
                    resultados['tablas_analizadas'] += 1
                    
                    # Guardar reporte individual
                    output_file = self.reports_path / f"structure_{codigo_tabla}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(analysis, f, indent=2, ensure_ascii=False)
                    
                    print(f"    [OK] {analysis['num_filas']} filas, {analysis['num_columnas']} columnas")
                else:
                    print(f"    [ERROR] {analysis['error']}")
        
        # Guardar resumen general
        summary_file = self.reports_path / "exploration_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\nExploración completada: {resultados['tablas_analizadas']} tablas analizadas")
        print(f"Reportes guardados en: {self.reports_path}")
        
        return resultados
    
    def explore_tables(self, codigos_tablas):
        """Explora tablas específicas"""
        resultados = {}
        
        for codigo in codigos_tablas:
            print(f"\nExplorando tabla {codigo}...")
            analysis = self.explore_csv(codigo)
            
            if 'error' not in analysis:
                resultados[codigo] = analysis
                
                # Guardar reporte
                output_file = self.reports_path / f"structure_{codigo}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                
                # Mostrar resumen
                print(f"  Filas: {analysis['num_filas']}")
                print(f"  Columnas: {analysis['num_columnas']}")
                print(f"  Encoding: {analysis['encoding']}")
                print(f"  Columnas: {', '.join(analysis['columnas'])}")
                
                if 'rango_temporal' in analysis:
                    print(f"  Período: {analysis['rango_temporal']['primer_periodo']} - {analysis['rango_temporal']['ultimo_periodo']}")
            else:
                print(f"  Error: {analysis['error']}")
        
        return resultados


def main():
    parser = argparse.ArgumentParser(
        description='Explorador de estructura de CSVs del INE'
    )
    
    parser.add_argument('--table', type=str, help='Código de tabla específica')
    parser.add_argument('--tables', type=str, nargs='+', help='Lista de códigos de tabla')
    parser.add_argument('--all', action='store_true', help='Explorar todas las tablas')
    parser.add_argument('--pilot', action='store_true', help='Explorar tablas piloto (6042, 6043, 6044)')
    
    args = parser.parse_args()
    
    explorer = CSVExplorer()
    
    if args.all:
        explorer.explore_all()
    elif args.pilot:
        # Tablas piloto para pruebas
        print("Explorando tablas piloto...")
        explorer.explore_tables(['6042', '6043', '6044'])
    elif args.tables:
        explorer.explore_tables(args.tables)
    elif args.table:
        explorer.explore_tables([args.table])
    else:
        print("Uso: python csv_explorer.py --pilot")
        print("     python csv_explorer.py --table 6042")
        print("     python csv_explorer.py --tables 6042 6043 6044")
        print("     python csv_explorer.py --all")


if __name__ == "__main__":
    main()