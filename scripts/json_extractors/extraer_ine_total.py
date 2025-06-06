#!/usr/bin/env python3
# scripts/extraer_ine_total.py

import os
import json
import logging
import sys
from pathlib import Path
import requests

# Importamos create_session de tu script de prueba
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'scripts'))
from extraer_ine_data import create_session  # fileciteturn6file0

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Directorios y archivos
RAW_DIR = BASE_DIR / 'data' / 'raw'
URLS_CONFIG = BASE_DIR / 'urls_etcl.json'


def ensure_raw_dir():
    """Crear carpeta RAW_DIR si no existe."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_and_save_id(id_: str, url: str, session: requests.Session) -> bool:
    """
    Descarga el JSON de la URL con retries y lo guarda como data/raw/{id_}.json.
    """
    try:
        logging.info(f"Requesting data for series {id_} from {url}")
        resp = session.get(url, timeout=session.timeout)
        resp.raise_for_status()

        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            logging.error(f"Unexpected Content-Type for {id_}: {content_type}")
            return False

        data = resp.json()
        out_path = RAW_DIR / f"{id_}.json"
        with out_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved JSON to {out_path}")
        return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {id_}: {e}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error for {id_}: {e}")
        return False
    except Exception as e:
        logging.exception(f"Unexpected error for {id_}: {e}")
        return False


def main():
    # Prepara directorios
    ensure_raw_dir()

    # Cargamos configuracion de series
    with URLS_CONFIG.open(encoding='utf-8') as f:
        series = json.load(f)

    session = create_session()
    success = True

    for s in series:
        id_  = s.get('id')
        url  = s.get('url')
        if not id_ or not url:
            logging.warning(f"Skipping invalid entry: {s}")
            continue
        if not fetch_and_save_id(id_, url, session):
            success = False

    if not success:
        logging.error("One or more series failed to download.")
        sys.exit(1)
    logging.info("All series processed successfully.")


if __name__ == '__main__':
    main()
