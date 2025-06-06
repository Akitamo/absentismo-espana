#!/usr/bin/env python3
# scripts/normalizar_ine_total.py

import json
import sys
from pathlib import Path
import pandas as pd

# Definición de BASE_DIR y rutas
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROC_DIR = BASE_DIR / 'data' / 'processed'
PROC_DIR.mkdir(parents=True, exist_ok=True)

# Ajustar sys.path para importar inferencia de columnas
sys.path.insert(0, str(BASE_DIR / 'scripts'))
from inferir_columnas_etcl import inferir_columnas  # función que infiere columnas dinámicas


def normalizar_serie_dynamic(json_data, out_path: Path):
    """
    Normaliza una lista de series JSON y guarda CSV con columnas dinámicas.
    """
    # 1) Inferir columnas para toda la colección usando el mismo método que la prueba
    cols = inferir_columnas(json_data)

    rows = []
    # 2) Recorrer cada serie en el JSON
    # Inferir una lista de diccionarios meta_map por serie para eficiencia
    meta_maps = []
    for serie in json_data:
        meta = {}
        for md in serie.get('MetaData', []):
            # Columnas dinámicas definidas por el campo 'nombre' en la inferencia
            col_name = md.get('nombre') or md.get('Nombre')
            if col_name in cols:
                meta[col_name] = md.get('Nombre')
        meta_maps.append(meta)

    # 3) Desanidar Data y crear filas
    for serie, meta in zip(json_data, meta_maps):
        for punto in serie.get('Data', []):
            row = {}
            for col in cols:
                if col in meta:
                    row[col] = meta[col]
                else:
                    # las demás columnas vienen de los campos transformados de Data
                    # utilizar la lógica exacta de la prueba:
                    if col.lower() == 'tipo de dato':
                        row[col] = punto.get('T3_TipoDato')
                    elif col.lower() == 'periodo':
                        anyo = punto.get('Anyo')
                        per = punto.get('T3_Periodo', '').strip()
                        row[col] = f"{anyo}{per}"
                    elif col.lower() == 'año' or col.lower() == 'ano':
                        row[col] = punto.get('Anyo')
                    elif col.lower() == 'trimestre':
                        row[col] = punto.get('T3_Periodo', '').strip()
                    elif col.lower() in ('total', 'valor'):
                        row[col] = punto.get('Valor')
                    else:
                        # fallback a cualquier clave directa
                        row[col] = punto.get(col)
            rows.append(row)

    # 4) Crear DataFrame con columnas en orden
    df = pd.DataFrame(rows, columns=cols)


    df = pd.DataFrame(rows, columns=cols)

    # 5) Guardar CSV con especificaciones
    df.to_csv(out_path, index=False, sep=';', decimal=',', encoding='cp1252')
    print(f"✅ Generado: {out_path.name}")


def main():
    json_files = sorted(RAW_DIR.glob('*.json'))
    if not json_files:
        print(f"ERROR: No JSONs en {RAW_DIR}")
        sys.exit(1)

    for path in json_files:
        id_ = path.stem
        print(f"Procesando {id_}…")
        j = json.loads(path.read_text(encoding='utf-8'))
        out_csv = PROC_DIR / f"{id_}.csv"
        normalizar_serie_dynamic(j, out_csv)

    print("🏁 Todos los CSV han sido generados en data/processed/")

if __name__ == '__main__':
    main()
