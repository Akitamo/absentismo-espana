import os
import sys
from sqlalchemy import create_engine, text
import pandas as pd

# Forzar codificación UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

print("=== PRUEBA POSTGRESQL - VERSION CORREGIDA ===")

# Configuración directa (sin archivo .env para evitar problemas UTF-8)
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'absentismo_db'
DB_USER = 'postgres'
DB_PASSWORD = 'Luna1969'

print("CONFIGURACION:")
print(f"Host: {DB_HOST}")
print(f"Puerto: {DB_PORT}")
print(f"Base de datos: {DB_NAME}")
print(f"Usuario: {DB_USER}")
print("=====================")

# Crear conexión
connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(connection_string, echo=False)
    
    # Probar conexión
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("✅ Conexion exitosa a PostgreSQL")
        print(f"Version: PostgreSQL detectado correctamente")
        
    # Crear tabla de prueba
    test_data = pd.DataFrame({
        'fecha': ['2024-01-01', '2024-02-01', '2024-03-01'],
        'ccaa': ['Madrid', 'Barcelona', 'Valencia'], 
        'tasa_absentismo': [7.2, 8.1, 6.9],
        'sector': ['Servicios', 'Industria', 'Construccion']
    })
    
    # Insertar datos
    test_data.to_sql('prueba_absentismo', engine, if_exists='replace', index=False)
    print("✅ Tabla de prueba creada correctamente")
    
    # Leer datos para confirmar
    result_df = pd.read_sql('SELECT * FROM prueba_absentismo', engine)
    print("✅ Datos insertados correctamente:")
    print(result_df.to_string())
    
    # Probar consulta más compleja
    madrid_df = pd.read_sql(
        "SELECT * FROM prueba_absentismo WHERE ccaa = 'Madrid'", 
        engine
    )
    print("\n✅ Consulta especifica (Madrid):")
    print(madrid_df.to_string())
    
    print("\n🎉 POSTGRESQL CONFIGURADO CORRECTAMENTE")
    print("🚀 Listo para crear extractores de datos reales")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Diagnóstico adicional
    if "authentication failed" in str(e):
        print("💡 Error de autenticacion - verifica la contraseña")
    elif "database" in str(e) and "does not exist" in str(e):
        print("💡 La base de datos 'absentismo_db' no existe")
        print("💡 Creala en pgAdmin o cambia a 'postgres' (base por defecto)")
    elif "could not connect" in str(e):
        print("💡 PostgreSQL no está ejecutándose")
    else:
        print(f"💡 Error detallado: {str(e)}")