#!/usr/bin/env python3
# scripts/inferir_columnas_etcl.py

import os
import json
import requests
import csv
from pathlib import Path

# Rutas
BASE = Path(__file__).resolve().parent.parent
RAW_DIR = BASE / 'data' / 'raw'
URLS_CONFIG = BASE / 'urls_etcl.json'
OUTPUT_CSV = BASE / 'data' / 'columnas_por_serie.csv'

def ensure_raw_dir():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

def fetch_json(id_, url):
    """Descarga el JSON si no existe y lo devuelve ya parseado."""
    path = RAW_DIR / f'{id_}.json'
    if not path.exists():
        print(f'  → Descargando {id_} …')
        r = requests.get(url)
        r.raise_for_status()
        path.write_text(r.text, encoding='utf-8')
    else:
        print(f'  → Usando cache {id_}.json')
    return json.loads(path.read_text(encoding='utf-8'))

def inferir_columnas(json_data):
    """
    Simula la creación de una única fila en el normalizador para inferir
    dinámicamente sus columnas:
      1) Dimensiones que aparecen en MetaData: tomamos T3_Variable como título.
      2) Campos extraídos de cada punto de datos:
         - 'Tipo de dato' (T3_TipoDato)
         - 'Periodo'     (f"{Anyo}{T3_Periodo}")
         - 'Año'         (Anyo)
         - 'Trimestre'   (T3_Periodo)
         - 'Total'       (Valor)
    """
    cols = []

    # Si el JSON es una lista de series, nos quedamos con la primera serie
    # (basta para inferir nombres de columna)
    series_list = json_data if isinstance(json_data, list) else []
    if not series_list:
        return cols

    primera = series_list[0]

    # 1) Metadatos / dimensiones dinámicas
    for md in primera.get('MetaData', []):
        var = md.get('T3_Variable', '').strip()
        if not var:
            continue
        # Normaliza a minúsculas + capital inicial
        title = var.title()
        if title not in cols:
            cols.append(title)

    # 2) Campos fijos del punto de datos
    extras = [
        'Tipo de dato',  # de punto['T3_TipoDato']
        'Periodo',       # f"{Anyo}{T3_Periodo}"
        'Año',           # punto['Anyo']
        'Trimestre',     # punto['T3_Periodo']
        'Total'          # punto['Valor']
    ]
    for e in extras:
        if e not in cols:
            cols.append(e)

    return cols

def main():
    ensure_raw_dir()

    with URLS_CONFIG.open(encoding='utf-8') as f:
        series_cfg = json.load(f)

    with OUTPUT_CSV.open('w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'nombre', 'columnas'])
        for s in series_cfg:
            id_     = s['id']
            nombre  = s.get('nombre', '')
            url     = s['url']
            print(f'Procesando {id_}: {nombre}')
            j = fetch_json(id_, url)
            columnas = inferir_columnas(j)
            writer.writerow([id_, nombre, ';'.join(columnas)])

    print(f'\n✅ Informe generado: {OUTPUT_CSV}')

if __name__ == '__main__':
    main()
