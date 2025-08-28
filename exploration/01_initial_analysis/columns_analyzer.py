"""
Analizador masivo de columnas para todos los CSVs
Genera un Excel con análisis completo de dimensiones y métricas
"""

import csv
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))

class ColumnsAnalyzer:
    """Analiza todas las tablas y genera Excel consolidado"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / 'data' / 'raw' / 'csv'
        self.reports_path = self.base_path / 'data' / 'exploration_reports'
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        # Cargar configuración
        config_path = self.base_path / 'config' / 'tables.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def analyze_all_tables(self):
        """Analiza todas las tablas de forma masiva"""
        
        print("Analizando todas las tablas...")
        print("-" * 60)
        
        all_analyses = {}
        
        # Obtener lista de archivos CSV
        csv_files = sorted(self.data_path.glob("*.csv"))
        
        for csv_file in csv_files:
            # Extraer código de tabla
            codigo = csv_file.name.split('_')[0]
            print(f"Analizando tabla {codigo}: {csv_file.name[:50]}...")
            
            try:
                # Analizar el CSV
                analysis = self.analyze_single_csv(csv_file, codigo)
                all_analyses[codigo] = analysis
                
            except Exception as e:
                print(f"  [ERROR] {e}")
                all_analyses[codigo] = {"error": str(e)}
        
        return all_analyses
    
    def analyze_single_csv(self, csv_path, codigo):
        """Analiza un CSV individual"""
        
        # Leer primeras líneas para detectar estructura
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Detectar separador
            first_line = f.readline()
            if ';' in first_line:
                delimiter = ';'
            elif ',' in first_line:
                delimiter = ','
            else:
                delimiter = '\t'
        
        # Leer con pandas para análisis rápido (solo muestra)
        try:
            # Leer solo primeras 1000 filas para análisis rápido
            df_sample = pd.read_csv(csv_path, sep=delimiter, nrows=1000, encoding='utf-8')
        except:
            # Intentar con otro encoding
            df_sample = pd.read_csv(csv_path, sep=delimiter, nrows=1000, encoding='latin-1')
        
        # Leer todo para contar filas
        with open(csv_path, 'r', encoding='utf-8') as f:
            total_rows = sum(1 for line in f) - 1  # Menos header
        
        # Analizar cada columna
        columns_info = {}
        
        for col in df_sample.columns:
            col_clean = col.replace('\ufeff', '').strip()
            
            # Obtener valores únicos en la muestra
            unique_values = df_sample[col].dropna().unique()
            n_unique = len(unique_values)
            
            # Determinar tipo
            tipo_detectado = self.detect_column_type(col_clean, unique_values, n_unique)
            
            # Información de la columna
            columns_info[col_clean] = {
                'posicion': list(df_sample.columns).index(col),
                'tipo_detectado': tipo_detectado,
                'valores_unicos_muestra': n_unique,
                'ejemplos': list(unique_values[:5]) if n_unique <= 10 else list(unique_values[:3]),
                'tiene_nulos': df_sample[col].isna().any()
            }
        
        return {
            'codigo': codigo,
            'archivo': csv_path.name,
            'num_filas': total_rows,
            'num_columnas': len(df_sample.columns),
            'columnas': list(columns_info.keys()),
            'columnas_detalle': columns_info,
            'separador': delimiter
        }
    
    def detect_column_type(self, col_name, unique_values, n_unique):
        """Detecta si una columna es dimensión, métrica o temporal"""
        
        col_lower = col_name.lower()
        
        # Reglas de detección
        if 'periodo' in col_lower or 'period' in col_lower:
            return 'TEMPORAL'
        elif any(word in col_lower for word in ['total', 'valor', 'coste', 'importe', 'cantidad']):
            return 'METRICA'
        elif n_unique <= 100:  # Pocas categorías = dimensión
            return 'DIMENSION'
        else:
            # Ver si son números
            try:
                # Intentar convertir a float los primeros valores
                for val in unique_values[:10]:
                    if pd.notna(val):
                        str(val).replace(',', '.').replace(' ', '')
                        float(str(val).replace(',', '.').replace(' ', ''))
                return 'METRICA'
            except:
                return 'DIMENSION' if n_unique < 500 else 'METRICA'
    
    def generate_excel_report(self, analyses):
        """Genera un Excel con toda la información"""
        
        output_file = self.reports_path / f"analisis_columnas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # HOJA 1: Resumen general
            summary_data = []
            for codigo in sorted(analyses.keys()):
                if 'error' not in analyses[codigo]:
                    info = analyses[codigo]
                    
                    # Contar tipos
                    dims = sum(1 for c in info['columnas_detalle'].values() 
                              if c['tipo_detectado'] == 'DIMENSION')
                    mets = sum(1 for c in info['columnas_detalle'].values() 
                              if c['tipo_detectado'] == 'METRICA')
                    temps = sum(1 for c in info['columnas_detalle'].values() 
                               if c['tipo_detectado'] == 'TEMPORAL')
                    
                    summary_data.append({
                        'Tabla': codigo,
                        'Filas': info['num_filas'],
                        'Columnas': info['num_columnas'],
                        'Dimensiones': dims,
                        'Métricas': mets,
                        'Temporales': temps,
                        'Archivo': info['archivo'][:50]
                    })
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Resumen', index=False)
            
            # HOJA 2: Matriz de columnas
            all_columns = set()
            table_columns = {}
            
            for codigo, info in analyses.items():
                if 'error' not in info:
                    table_columns[codigo] = info['columnas']
                    all_columns.update(info['columnas'])
            
            # Crear matriz
            matrix_data = []
            for col in sorted(all_columns):
                row = {'Columna': col}
                for codigo in sorted(table_columns.keys()):
                    if col in table_columns[codigo]:
                        # Obtener tipo
                        tipo = analyses[codigo]['columnas_detalle'][col]['tipo_detectado']
                        row[codigo] = tipo[0]  # D, M o T
                    else:
                        row[codigo] = ''
                matrix_data.append(row)
            
            df_matrix = pd.DataFrame(matrix_data)
            df_matrix.to_excel(writer, sheet_name='Matriz_Columnas', index=False)
            
            # HOJA 3: Detalle de cada tabla
            details_data = []
            for codigo in sorted(analyses.keys()):
                if 'error' not in analyses[codigo]:
                    info = analyses[codigo]
                    for col, col_info in info['columnas_detalle'].items():
                        details_data.append({
                            'Tabla': codigo,
                            'Columna': col,
                            'Tipo': col_info['tipo_detectado'],
                            'Valores_Unicos': col_info['valores_unicos_muestra'],
                            'Tiene_Nulos': col_info['tiene_nulos'],
                            'Ejemplos': str(col_info['ejemplos'][:3])
                        })
            
            df_details = pd.DataFrame(details_data)
            df_details.to_excel(writer, sheet_name='Detalle_Columnas', index=False)
            
            # Ajustar anchos de columna
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"\nExcel generado: {output_file}")
        return output_file
    
    def run_complete_analysis(self):
        """Ejecuta el análisis completo y genera Excel"""
        
        print("\n" + "="*60)
        print("ANÁLISIS MASIVO DE COLUMNAS - TODAS LAS TABLAS")
        print("="*60)
        
        # Analizar todas las tablas
        analyses = self.analyze_all_tables()
        
        # Generar Excel
        excel_file = self.generate_excel_report(analyses)
        
        # Guardar también en JSON
        json_file = self.reports_path / f"analisis_columnas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"JSON generado: {json_file}")
        
        # Resumen
        print("\n" + "="*60)
        print("RESUMEN DEL ANÁLISIS")
        print("="*60)
        
        total_tablas = len(analyses)
        total_columnas = len(set(col for info in analyses.values() 
                                if 'columnas' in info 
                                for col in info['columnas']))
        
        print(f"Tablas analizadas: {total_tablas}")
        print(f"Columnas únicas totales: {total_columnas}")
        print(f"\nArchivos generados:")
        print(f"  - Excel: {excel_file.name}")
        print(f"  - JSON: {json_file.name}")
        
        return excel_file


def main():
    """Función principal"""
    analyzer = ColumnsAnalyzer()
    
    # Verificar que pandas está instalado
    try:
        import pandas
        import openpyxl
    except ImportError:
        print("ERROR: Necesitas instalar pandas y openpyxl")
        print("Ejecuta: pip install pandas openpyxl")
        return
    
    # Ejecutar análisis
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()