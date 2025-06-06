import os
import argparse
import logging
import json
import sys
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Base directory del proyecto (nivel superior a scripts)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# URL(s) por defecto si no se especifican via CLI
default_urls = [
    "https://servicios.ine.es/wstempus/jsCache/es/DATOS_TABLA/59391?tip=AM&"
]

def setup_logger(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), "INFO"),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def create_session(retries: int = 3, backoff_factor: float = 0.3, status_forcelist=None, timeout: int = 10):
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist or [429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.timeout = timeout
    return session


def fetch_and_save(url: str, output_dir: str, session: requests.Session) -> bool:
    try:
        logging.info(f"Requesting data from {url}")
        response = session.get(url, timeout=session.timeout)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            logging.error(f"Unexpected Content-Type: {content_type}")
            return False

        data = response.json()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"ine_data_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logging.info(f"Data saved to {filepath}")
        return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {e}")
        return False
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return False


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extrae datos JSON de la API del INE y los guarda en un directorio local."
    )
    parser.add_argument(
        "--urls", 
        nargs='+', 
        default=default_urls,
        help="URL(s) de la API a consultar (default en el script)"
    )
    parser.add_argument(
        "--output-dir", 
        default=os.path.join(BASE_DIR, "data", "raw"),
        help="Directorio donde guardar los JSON (default: data/raw)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Nivel de logging"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logger(args.log_level)

    os.makedirs(args.output_dir, exist_ok=True)

    session = create_session()
    success = True

    for url in args.urls:
        if not fetch_and_save(url, args.output_dir, session):
            success = False

    if not success:
        logging.error("One or more requests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
