#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test de conexión a base de datos desde streamlit_app."""

from pathlib import Path
import os
import sys
import duckdb

print("=" * 60)
print("TEST DE CONEXIÓN A BASE DE DATOS")
print("=" * 60)

# Información del entorno
print("\n1. INFORMACIÓN DEL ENTORNO:")
print("-" * 40)
print(f"Sistema operativo: {os.name}")
print(f"Python: {sys.version}")
print(f"Directorio actual: {os.getcwd()}")
print(f"Script actual: {__file__}")
print(f"Script resuelto: {Path(__file__).resolve()}")

# Probar diferentes rutas
print("\n2. PRUEBA DE RUTAS:")
print("-" * 40)

# Opción 1: Ruta relativa desde streamlit_app
path1 = Path(__file__).parent.parent / 'data' / 'analysis.db'
print(f"\nOpción 1 - Ruta relativa desde script:")
print(f"  Path: {path1}")
print(f"  Path resuelto: {path1.resolve()}")
print(f"  Existe: {path1.exists()}")

# Opción 2: Ruta absoluta directa Windows
path2 = Path("C:/dev/projects/absentismo-espana/data/analysis.db")
print(f"\nOpción 2 - Ruta absoluta con /:")
print(f"  Path: {path2}")
print(f"  Existe: {path2.exists()}")

# Opción 3: Ruta absoluta con backslash
path3 = Path(r"C:\dev\projects\absentismo-espana\data\analysis.db")
print(f"\nOpción 3 - Ruta absoluta con \\:")
print(f"  Path: {path3}")
print(f"  Existe: {path3.exists()}")

# Listar archivos en el directorio data
data_dir = Path(__file__).parent.parent / 'data'
print(f"\n3. CONTENIDO DEL DIRECTORIO DATA:")
print("-" * 40)
print(f"Directorio data: {data_dir}")
print(f"Directorio data resuelto: {data_dir.resolve()}")
print(f"Existe directorio: {data_dir.exists()}")

if data_dir.exists():
    print("\nArchivos .db en data/:")
    for f in data_dir.glob("*.db"):
        print(f"  - {f.name} ({f.stat().st_size / 1024 / 1024:.2f} MB)")
        
# Test de conexión
print("\n4. TEST DE CONEXIÓN DUCKDB:")
print("-" * 40)

for i, path in enumerate([path1, path2, path3], 1):
    if path.exists():
        print(f"\nIntentando conectar con opción {i}: {path}")
        try:
            conn = duckdb.connect(str(path), read_only=True)
            # Test query
            result = conn.execute("SELECT COUNT(*) FROM observaciones_tiempo_trabajo").fetchone()
            print(f"  ✓ Conexión exitosa! Registros: {result[0]}")
            conn.close()
            break
        except Exception as e:
            print(f"  ✗ Error: {e}")
    else:
        print(f"\nOpción {i} no existe: {path}")

print("\n" + "=" * 60)