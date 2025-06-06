import re
import json
from docx import Document
import os

# Directorio base donde están todos los archivos
base_dir = r"C:\Users\slunagda\AbsentismoEspana"

# Rutas a los documentos Word con las URLs
docx_paths = [
    os.path.join(base_dir, "Análisis urls INE ETCL.docx"),
    os.path.join(base_dir, "Análisis urls INE ETCL CSVs.docx")
]

# Salida: fichero JSON con la lista completa de URLs y metadatos
output_json = os.path.join(base_dir, "urls_etcl_completo.json")

def extract_table_code(url):
    """Extrae el código de tabla de la URL"""
    m_code = re.search(r'/DATOS_TABLA/(\d+)', url)
    return m_code.group(1) if m_code else None

def extract_tip_parameter(url):
    """Extrae el parámetro tip de la URL"""
    m_tip = re.search(r'tip=([A-Z]+)', url)
    return m_tip.group(1).lower() if m_tip else None

def determine_url_type(url):
    """Determina si la URL es de tipo JSON (API) o CSV (descarga)"""
    if '/csv_bdsc/' in url and url.endswith('.csv'):
        return 'csv'
    elif '/DATOS_TABLA/' in url:
        return 'json'
    else:
        return 'unknown'

def generate_id(url, url_type):
    """Genera un ID único para la URL basado en el código de tabla y tipo"""
    code = extract_table_code(url)
    tip = extract_tip_parameter(url)
    
    if code and tip:
        return f"{code}_{tip}_{url_type}"
    elif code:
        return f"{code}_{url_type}"
    else:
        # Fallback: usar parte de la URL
        clean_url = re.sub(r'[^0-9A-Za-z]+', '_', url)[:50]
        return f"{clean_url}_{url_type}"

def process_document(docx_path):
    """Procesa un documento Word y extrae las URLs con sus metadatos"""
    doc = Document(docx_path)
    urls = []
    last_title = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Detectar si el párrafo es un título (sin URL)
        if not re.search(r'https?://\S+', text):
            # Limpiar el título de caracteres especiales del markdown
            clean_title = re.sub(r'[*#>\s]+', ' ', text).strip()
            if clean_title:
                last_title = clean_title
            continue
            
        # Buscar todas las URLs en el párrafo
        url_matches = re.findall(r'https?://\S+', text)
        
        for url in url_matches:
            # Limpiar la URL de caracteres finales no deseados
            url = url.rstrip('.,;:')
            
            url_type = determine_url_type(url)
            code = extract_table_code(url)
            tip = extract_tip_parameter(url)
            id_ = generate_id(url, url_type)
            
            # Determinar el nombre descriptivo
            if last_title:
                nombre = last_title
            else:
                # Usar el texto antes de la URL como nombre
                texto_antes_url = text.split(url)[0].strip()
                # Limpiar caracteres de markdown y formateo
                nombre = re.sub(r'[*#>\[\]]+', '', texto_antes_url).strip().rstrip(':').strip()
                if not nombre:
                    nombre = f"Tabla {code}" if code else "URL sin título"
            
            url_entry = {
                "id": id_,
                "nombre": nombre,
                "url": url,
                "tipo": url_type,
                "codigo_tabla": code,
                "parametro_tip": tip
            }
            
            urls.append(url_entry)
    
    return urls

# Procesar todos los documentos
all_urls = []
for docx_path in docx_paths:
    if os.path.exists(docx_path):
        print(f"Procesando: {docx_path}")
        urls_from_doc = process_document(docx_path)
        all_urls.extend(urls_from_doc)
        print(f"  - Extraídas {len(urls_from_doc)} URLs")
    else:
        print(f"Advertencia: No se encontró el archivo {docx_path}")

# Agrupar URLs por código de tabla para mejor organización
urls_agrupadas = {}
for url_entry in all_urls:
    codigo = url_entry['codigo_tabla']
    if codigo:
        if codigo not in urls_agrupadas:
            urls_agrupadas[codigo] = {
                'codigo_tabla': codigo,
                'nombre': url_entry['nombre'],
                'urls': {}
            }
        
        tipo = url_entry['tipo']
        urls_agrupadas[codigo]['urls'][tipo] = {
            'id': url_entry['id'],
            'url': url_entry['url'],
            'parametro_tip': url_entry['parametro_tip']
        }

# Convertir a lista para el JSON final
resultado_final = {
    'metadata': {
        'total_urls': len(all_urls),
        'total_tablas': len(urls_agrupadas),
        'tipos_url': list(set(url['tipo'] for url in all_urls)),
        'descripcion': 'URLs extraídas de documentos ETCL del INE, organizadas por tabla'
    },
    'tablas': list(urls_agrupadas.values()),
    'urls_individuales': all_urls
}

# Escribir JSON de salida con formato legible
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(resultado_final, f, ensure_ascii=False, indent=2)

print(f"\n=== RESUMEN ===")
print(f"URLs totales extraídas: {len(all_urls)}")
print(f"Tablas identificadas: {len(urls_agrupadas)}")
print(f"Tipos de URL encontrados: {list(set(url['tipo'] for url in all_urls))}")
print(f"Archivo generado: {output_json}")

# Mostrar algunas estadísticas adicionales
tipos_count = {}
for url in all_urls:
    tipo = url['tipo']
    tipos_count[tipo] = tipos_count.get(tipo, 0) + 1

print(f"\nDistribución por tipo:")
for tipo, count in tipos_count.items():
    print(f"  {tipo}: {count} URLs")