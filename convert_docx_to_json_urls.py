import re
import json
from docx import Document
import os
from pathlib import Path

# Ajusta la ruta al documento Word con las URLs (usa raw string o escapa \)
docx_path = r"Path(__file__).resolve().parent\Análisis urls INE ETCL.docx"
# Salida: fichero JSON con la lista de URLs y metadatos
output_json = os.path.join(os.path.dirname(__file__), "urls_etcl.json")

# Cargar el documento
doc = Document(docx_path)

urls = []
last_title = None

for para in doc.paragraphs:
    text = para.text.strip()
    if not text:
        continue
    # Detectar si el párrafo es un título (sin URL) y lo guardamos como posible título
    if not re.search(r'https?://\S+', text):
        last_title = text
        continue
    # Si llegamos aquí, el párrafo contiene al menos una URL
    matches = re.findall(r'https?://\S+', text)
    for url in matches:
        # Extraer código de tabla (número tras DATOS_TABLA/)
        m_code = re.search(r'/DATOS_TABLA/(\d+)', url)
        code = m_code.group(1) if m_code else None
        # Extraer parámetro tip (AM, TM, etc.)
        m_tip = re.search(r'tip=([A-Z]+)', url)
        tip = m_tip.group(1).lower() if m_tip else None
        # Construir ID
        if code and tip:
            id_ = f"{code}_{tip}"
        elif code:
            id_ = code
        else:
            # Fallback: nombre de dominio + path
            id_ = re.sub(r'[^0-9A-Za-z]+', '_', url)[:50]
        # Nombre descriptivo: usar el título anterior si existe, sino texto antes de la URL
        nombre = last_title or text.split(url)[0].strip().rstrip(':').strip()
        urls.append({
            "id": id_,
            "nombre": nombre,
            "url": url
        })

# Escribir JSON de salida
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(urls, f, ensure_ascii=False, indent=2)

print(f"Generado {output_json} con {len(urls)} URLs extraídas.")
