import re
import json
from docx import Document
import os

# Directorio base donde están todos los archivos
base_dir = r"C:\Users\slunagda\AbsentismoEspana"

# Cargar el archivo JSON generado para diagnóstico
json_file = os.path.join(base_dir, "urls_etcl_completo.json")

print("=== DIAGNÓSTICO DE URLs ===")

# Leer el JSON existente
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Analizar las URLs "unknown"
unknown_urls = [url for url in data['urls_individuales'] if url['tipo'] == 'unknown']

print(f"URLs marcadas como 'unknown': {len(unknown_urls)}")
print("\nEjemplos de URLs 'unknown':")
for i, url in enumerate(unknown_urls[:5]):  # Mostrar primeras 5
    print(f"{i+1}. {url['url']}")

print("\n" + "="*50)

def determine_url_type_improved(url):
    """Función mejorada para determinar el tipo de URL"""
    url_lower = url.lower()
    
    # Detectar CSV con múltiples patrones
    if any(pattern in url_lower for pattern in ['.csv', 'csv_bdsc', 'files/t/es/csv']):
        return 'csv'
    
    # Detectar JSON/API
    elif '/datos_tabla/' in url_lower and any(param in url_lower for param in ['tip=', '?']):
        return 'json'
    
    # Detectar otros formatos de API del INE
    elif 'wstempus' in url_lower and 'datos_tabla' in url_lower:
        return 'json'
    
    else:
        return 'unknown'

# Reclasificar todas las URLs
print("Reclasificando URLs...")
urls_corregidas = []
cambios = 0

for url_entry in data['urls_individuales']:
    url_original = url_entry.copy()
    nuevo_tipo = determine_url_type_improved(url_entry['url'])
    
    if nuevo_tipo != url_entry['tipo']:
        cambios += 1
        print(f"Cambio detectado: {url_entry['url'][:60]}... | {url_entry['tipo']} → {nuevo_tipo}")
    
    # Actualizar el tipo
    url_entry['tipo'] = nuevo_tipo
    
    # Regenerar ID con el nuevo tipo
    code = url_entry['codigo_tabla']
    tip = url_entry['parametro_tip']
    
    if code and tip:
        nuevo_id = f"{code}_{tip}_{nuevo_tipo}"
    elif code:
        nuevo_id = f"{code}_{nuevo_tipo}"
    else:
        clean_url = re.sub(r'[^0-9A-Za-z]+', '_', url_entry['url'])[:50]
        nuevo_id = f"{clean_url}_{nuevo_tipo}"
    
    url_entry['id'] = nuevo_id
    urls_corregidas.append(url_entry)

print(f"\nCambios realizados: {cambios}")

# Reagrupar URLs corregidas por código de tabla
urls_agrupadas_corregidas = {}
for url_entry in urls_corregidas:
    codigo = url_entry['codigo_tabla']
    if codigo:
        if codigo not in urls_agrupadas_corregidas:
            urls_agrupadas_corregidas[codigo] = {
                'codigo_tabla': codigo,
                'nombre': url_entry['nombre'],
                'urls': {}
            }
        
        tipo = url_entry['tipo']
        urls_agrupadas_corregidas[codigo]['urls'][tipo] = {
            'id': url_entry['id'],
            'url': url_entry['url'],
            'parametro_tip': url_entry['parametro_tip']
        }

# Calcular nuevas estadísticas
tipos_count_corregido = {}
for url in urls_corregidas:
    tipo = url['tipo']
    tipos_count_corregido[tipo] = tipos_count_corregido.get(tipo, 0) + 1

# Crear estructura corregida
resultado_corregido = {
    'metadata': {
        'total_urls': len(urls_corregidas),
        'total_tablas': len(urls_agrupadas_corregidas),
        'tipos_url': list(tipos_count_corregido.keys()),
        'descripcion': 'URLs extraídas de documentos ETCL del INE, organizadas por tabla (CORREGIDO)',
        'distribucion_tipos': tipos_count_corregido
    },
    'tablas': list(urls_agrupadas_corregidas.values()),
    'urls_individuales': urls_corregidas
}

# Guardar archivo corregido
archivo_corregido = os.path.join(base_dir, "urls_etcl_completo_corregido.json")
with open(archivo_corregido, 'w', encoding='utf-8') as f:
    json.dump(resultado_corregido, f, ensure_ascii=False, indent=2)

print(f"\n=== RESULTADO FINAL ===")
print(f"URLs totales: {len(urls_corregidas)}")
print(f"Tablas identificadas: {len(urls_agrupadas_corregidas)}")
print(f"Distribución por tipo (CORREGIDA):")
for tipo, count in tipos_count_corregido.items():
    print(f"  {tipo}: {count} URLs")

print(f"\nArchivo corregido guardado en: {archivo_corregido}")

# Mostrar ejemplos de tablas con ambos tipos de URL
print(f"\n=== EJEMPLOS DE TABLAS CON JSON Y CSV ===")
tablas_completas = [tabla for tabla in urls_agrupadas_corregidas.values() 
                   if 'json' in tabla['urls'] and 'csv' in tabla['urls']]

print(f"Tablas con ambos formatos disponibles: {len(tablas_completas)}")
for i, tabla in enumerate(tablas_completas[:3]):  # Mostrar primeras 3
    print(f"\n{i+1}. {tabla['nombre']} (Tabla {tabla['codigo_tabla']}):")
    print(f"   JSON: {tabla['urls']['json']['url'][:70]}...")
    print(f"   CSV:  {tabla['urls']['csv']['url'][:70]}...")