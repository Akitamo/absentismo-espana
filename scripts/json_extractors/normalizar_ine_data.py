import json
import pandas as pd
from pathlib import Path

# Columnas finales en orden
FINAL_COLS = [
    'Sectores de actividad CNAE 2009',
    'Componentes del coste',
    'Tipo de dato',
    'Clase de indicador',
    'Periodo',
    'Año',
    'Trimestre',
    'Total'
]

def normalizar_formato_long():
    """
    Lee el JSON más reciente en data/raw y genera un CSV long con las columnas EXACTAS.
    - Sector = prefijo de serie['Nombre'] antes del primer punto.
    - Componentes y Clase de indicador desde MetaData.
    - Tipo de dato por punto.
    - Formato español: sep=';', decimal=',', encoding='cp1252'.
    """
    base_dir = Path(__file__).resolve().parent.parent
    raw_dir = base_dir / 'data' / 'raw'
    proc_dir = base_dir / 'data' / 'processed'
    proc_dir.mkdir(parents=True, exist_ok=True)

    # Seleccionar el JSON más reciente
    json_files = sorted(raw_dir.glob('*.json'),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True)
    if not json_files:
        print(f"ERROR: No hay archivos JSON en {raw_dir}")
        return
    raw_path = json_files[0]
    print(f"Usando JSON de entrada: {raw_path.name}")

    # Cargar el JSON
    with raw_path.open('r', encoding='utf-8') as f:
        series_list = json.load(f)

    rows = []
    for serie in series_list:
        # Determinar sector por prefijo de Nombre
        nombre_serie = serie.get('Nombre', '')
        sector = nombre_serie.split('.', 1)[0].strip()

        # Extraer Componentes del coste y Clase de indicador
        componentes = None
        clase_ind = None
        for md in serie.get('MetaData', []):
            var = md.get('T3_Variable', '').strip().upper()
            val = md.get('Nombre', '').strip()
            if var == 'COMPONENTES DEL COSTE':
                componentes = val
            elif var == 'CONCEPTOS SALARIALES/LABORALES':
                clase_ind = val

        # Desanidar cada punto de datos
        for punto in serie.get('Data', []):
            año = punto.get('Anyo')
            periodo = punto.get('T3_Periodo', '').strip()
            row = {
                'Sectores de actividad CNAE 2009': sector,
                'Componentes del coste': componentes,
                'Tipo de dato': punto.get('T3_TipoDato'),
                'Clase de indicador': clase_ind,
                'Periodo': f"{año}{periodo}",
                'Año': año,
                'Trimestre': periodo,
                'Total': punto.get('Valor')
            }
            rows.append(row)

    # Crear DataFrame y asegurar columnas
    df = pd.DataFrame(rows)
    for col in FINAL_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[FINAL_COLS]

    # Guardar CSV en formato español
    out_file = proc_dir / 'tiempo_trabajo_sectores_componentes_coste_long.csv'
    df.to_csv(
        out_file,
        index=False,
        sep=';',
        decimal=',',
        encoding='cp1252'
    )
    print(f"✅ CSV final (long) generado en: {out_file}")

if __name__ == '__main__':
    normalizar_formato_long()
