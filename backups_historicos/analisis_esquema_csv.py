import pandas as pd
import os
import json
from datetime import datetime 

def analizar_esquemas_csv(processed_data_dir):
    """
    Analiza los esquemas de todos los archivos CSV en una carpeta,
    identificando columnas comunes y únicas, y sus tipos de datos.
    Genera un archivo de resumen de esquema.
    """
    print(f"Analizando esquemas de los CSVs en: {processed_data_dir}")

    csv_files = [f for f in os.listdir(processed_data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No se encontraron archivos CSV en '{processed_data_dir}'.")
        return None

    all_columns_info = {} 
    common_columns_tracker = {}   
    
    schema_report = {
        "timestamp": datetime.now().isoformat(), 
        "files_analyzed": len(csv_files),
        "individual_schemas": [],
        "common_columns_analysis": {} 
    }

    for csv_file in csv_files:
        filepath = os.path.join(processed_data_dir, csv_file)
        print(f"  Procesando {csv_file}...")
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8', low_memory=False) 
            
            file_schema = {
                "file_name": csv_file,
                "num_rows": len(df),
                "num_columns": len(df.columns),
                "columns": []
            }

            for col in df.columns:
                col_type = str(df[col].dtype)
                num_unique = df[col].nunique()
                
                # --- RE-RE-CORRECCIÓN CLAVE AQUÍ: Simplificación y robustez para top_values ---
                top_values_raw = df[col].value_counts().nlargest(5).to_dict()
                top_values_serializable = {}
                for k, v in top_values_raw.items():
                    serializable_k = k
                    if pd.isna(k): # Manejar NaN/NaT
                        serializable_k = "NaN/NaT"
                    elif isinstance(k, pd.Timestamp): # Convertir Timestamp de Pandas a string
                        serializable_k = k.isoformat()
                    elif isinstance(k, datetime): # Convertir objeto datetime a string
                        serializable_k = k.isoformat()
                    elif not isinstance(k, (str, int, float, bool)): # Si no es un tipo serializable básico, forzar a string
                        # print(f"DEBUG: Found non-serializable key type: {type(k)} for value: {k} in file: {csv_file}, column: {col}") 
                        serializable_k = str(k) # Forzar a string cualquier cosa que no sea ya string, int, float, bool

                    # Asegurar que el valor 'v' (el conteo) sea un tipo numérico básico o string
                    serializable_v = v if isinstance(v, (int, float, bool)) else str(v)

                    top_values_serializable[serializable_k] = serializable_v
                # --- FIN RE-RE-CORRECCIÓN CLAVE ---


                file_schema["columns"].append({
                    "name": col,
                    "type": col_type,
                    "num_unique_values": num_unique,
                    "top_5_values": top_values_serializable, 
                    "is_null_percentage": df[col].isnull().sum() / len(df) if len(df) > 0 else 0
                })

                if col not in common_columns_tracker:
                    common_columns_tracker[col] = {'count': 0, 'files': set(), 'type_samples': {}}
                
                common_columns_tracker[col]['count'] += 1
                common_columns_tracker[col]['files'].add(csv_file)
                common_columns_tracker[col]['type_samples'][col_type] = common_columns_tracker[col]['type_samples'].get(col_type, 0) + 1
                
                if col not in all_columns_info:
                    all_columns_info[col] = {'types': {}, 'files': set()}
                all_columns_info[col]['types'][col_type] = all_columns_info[col]['types'].get(col_type, 0) + 1
                all_columns_info[col]['files'].add(csv_file)
            
            schema_report["individual_schemas"].append(file_schema)

        except Exception as e:
            print(f"  Error al procesar {csv_file}: {e}")
            schema_report["individual_schemas"].append({
                "file_name": csv_file,
                "error": str(e)
            })

    # Consolidar información de columnas comunes y tipos de datos globales
    for col, info in common_columns_tracker.items():
        schema_report["common_columns_analysis"][col] = {
            "appears_in_files": info['count'], 
            "file_names": sorted(list(info['files'])), 
            "common_types_across_files": all_columns_info.get(col, {}).get('types', {})
        }
    
    # Guardar el reporte de esquema
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..')) 
    output_report_path = os.path.join(project_root, 'data', 'schema_report_ine.json')

    with open(output_report_path, 'w', encoding='utf-8') as f:
        json.dump(schema_report, f, ensure_ascii=False, indent=4)
    
    print(f"\nReporte de esquema generado en: {output_report_path}")
    return schema_report

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..')) 
    
    processed_data_dir = os.path.join(project_root, 'data', 'processed')
    
    schema_analysis_results = analizar_esquemas_csv(processed_data_dir)
    
    if schema_analysis_results:
        print("\nAnálisis de esquemas completado. Revisa 'data/schema_report_ine.json' para detalles.")
        print("\nResumen de columnas comunes (aparecen en más de un archivo):")
        for col, info in schema_analysis_results["common_columns_analysis"].items():
            if info["appears_in_files"] > 1: 
                print(f"- '{col}' aparece en {info['appears_in_files']} archivos. Tipos: {info['common_types_across_files']}")