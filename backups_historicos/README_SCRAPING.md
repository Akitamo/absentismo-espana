# Proyecto Absentismo España - Web Scraping

## Estructura del Proyecto (Actualizada: 2025-05-26 11:22)

### 📁 Directorios:
- `scripts/scrapers/` - Scripts de web scraping específicos
- `data/raw/` - Datos extraídos sin procesar
- `data/processed/` - Datos procesados y limpios  
- `logs/` - Logs de ejecución de scrapers
- `config/` - Archivos de configuración

### 📄 Archivos Esenciales Mantenidos:
- `scripts/create_database_structure.py` - Creación de tablas PostgreSQL
- `config/database.env` - Configuración de base de datos
- `scripts/test_connection.py` - Test de conexión BD (opcional)

### 🗑️ Archivos Eliminados (Obsoletos por API):
- `scripts/test_simple_connection.py`
- `scripts/find_correct_url.py`
- `scripts/analyze_successful_data.py`
- `scripts/search_etcl_tables.py`
- `scripts/analyze_government_api.py`

### 🎯 Próximos Pasos:
1. Explorar estructura web del INE
2. Instalar librerías de scraping (BeautifulSoup, requests)
3. Crear scraper básico de prueba
4. Implementar extracción de datos ETCL
5. Automatizar carga en PostgreSQL

### 🔧 Configuración Actual:
- Python 3.11
- PostgreSQL (localhost:5432)
- Base de datos: absentismo_db
- Entorno virtual: venv/
