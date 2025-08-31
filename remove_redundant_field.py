import duckdb
from pathlib import Path
import sys

# Conectar a la base de datos
db_path = Path(r"C:\dev\projects\absentismo-espana\data\analysis.db")

if not db_path.exists():
    print(f"ERROR: No se encuentra la base de datos en {db_path}")
    sys.exit(1)

print("=" * 80)
print("ELIMINACION DE CAMPO REDUNDANTE: jerarquia_sector_cod")
print("=" * 80)

conn = duckdb.connect(str(db_path))

try:
    # 1. Verificar estructura actual
    print("\n1. Verificando estructura actual de la tabla...")
    columns_before = conn.execute("DESCRIBE observaciones_tiempo_trabajo").fetchdf()
    print(f"   Columnas actuales: {len(columns_before)}")
    
    # Verificar que el campo existe
    if 'jerarquia_sector_cod' not in columns_before['column_name'].values:
        print("   ADVERTENCIA: El campo jerarquia_sector_cod no existe en la tabla")
        sys.exit(0)
    
    # 2. Crear tabla temporal sin el campo jerarquia_sector_cod
    print("\n2. Creando tabla temporal sin jerarquia_sector_cod...")
    
    # Obtener lista de columnas sin jerarquia_sector_cod
    columns_to_keep = [col for col in columns_before['column_name'].values 
                      if col != 'jerarquia_sector_cod']
    
    columns_str = ', '.join(columns_to_keep)
    
    # Crear tabla temporal con los datos
    query_create_temp = f"""
    CREATE TABLE observaciones_tiempo_trabajo_new AS 
    SELECT {columns_str}
    FROM observaciones_tiempo_trabajo
    """
    
    conn.execute(query_create_temp)
    
    # Verificar cantidad de registros
    count_original = conn.execute("SELECT COUNT(*) FROM observaciones_tiempo_trabajo").fetchone()[0]
    count_new = conn.execute("SELECT COUNT(*) FROM observaciones_tiempo_trabajo_new").fetchone()[0]
    
    print(f"   Registros en tabla original: {count_original:,}")
    print(f"   Registros en tabla nueva: {count_new:,}")
    
    if count_original != count_new:
        print("   ERROR: La cantidad de registros no coincide!")
        conn.execute("DROP TABLE observaciones_tiempo_trabajo_new")
        sys.exit(1)
    
    # 3. Reemplazar tabla original
    print("\n3. Reemplazando tabla original...")
    conn.execute("DROP TABLE observaciones_tiempo_trabajo")
    conn.execute("ALTER TABLE observaciones_tiempo_trabajo_new RENAME TO observaciones_tiempo_trabajo")
    
    # 4. Verificar resultado final
    print("\n4. Verificando resultado final...")
    columns_after = conn.execute("DESCRIBE observaciones_tiempo_trabajo").fetchdf()
    print(f"   Columnas finales: {len(columns_after)}")
    
    if 'jerarquia_sector_cod' in columns_after['column_name'].values:
        print("   ERROR: El campo jerarquia_sector_cod aun existe!")
        sys.exit(1)
    
    if 'jerarquia_sector_lbl' not in columns_after['column_name'].values:
        print("   ERROR: El campo jerarquia_sector_lbl fue eliminado por error!")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("EXITO: Campo jerarquia_sector_cod eliminado correctamente")
    print("=" * 80)
    print(f"\nResumen:")
    print(f"  - Columnas antes: {len(columns_before)}")
    print(f"  - Columnas despues: {len(columns_after)}")
    print(f"  - Registros preservados: {count_new:,}")
    print(f"  - Campo jerarquia_sector_lbl: MANTENIDO")
    print(f"  - Campo version_datos: MANTENIDO")
    
    # Mostrar estructura final
    print("\nEstructura final de la tabla:")
    print("-" * 40)
    for idx, row in columns_after.iterrows():
        print(f"  {row['column_name']:30} {row['column_type']}")

except Exception as e:
    print(f"\nERROR durante la eliminacion: {str(e)}")
    # Intentar hacer rollback si es posible
    try:
        if 'observaciones_tiempo_trabajo_new' in [t[0] for t in conn.execute("SHOW TABLES").fetchall()]:
            conn.execute("DROP TABLE IF EXISTS observaciones_tiempo_trabajo_new")
            print("Tabla temporal eliminada")
    except:
        pass
    sys.exit(1)
finally:
    conn.close()

print("\nProceso completado exitosamente.")