import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

# Configuración
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'absentismo_db'
DB_USER = 'postgres'
DB_PASSWORD = 'Luna1969'

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

print("=== CREANDO ESTRUCTURA DE BASE DE DATOS ===")

# SQL para crear tablas principales
sql_queries = [
    """
    -- Tabla principal de absentismo (datos del INE)
    CREATE TABLE IF NOT EXISTS absentismo_laboral (
        id SERIAL PRIMARY KEY,
        fecha_referencia DATE NOT NULL,
        ccaa VARCHAR(50),
        sector VARCHAR(50),
        horas_pactadas_efectivas DECIMAL(10,2),
        horas_no_trabajadas_total DECIMAL(10,2),
        horas_no_trabajadas_it DECIMAL(10,2),
        tasa_absentismo DECIMAL(5,2),
        tasa_absentismo_it DECIMAL(5,2),
        num_trabajadores INTEGER,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(fecha_referencia, ccaa, sector)
    );
    """,
    
    """
    -- Tabla de accidentes laborales (Ministerio de Trabajo)
    CREATE TABLE IF NOT EXISTS accidentes_laborales (
        id SERIAL PRIMARY KEY,
        fecha_referencia DATE NOT NULL,
        ccaa VARCHAR(50),
        sector VARCHAR(50),
        tipo_accidente VARCHAR(20), -- 'jornada' o 'itinere'
        sexo VARCHAR(10),
        grupo_edad VARCHAR(20),
        gravedad VARCHAR(20), -- 'leve', 'grave', 'mortal'
        num_accidentes INTEGER,
        incidencia DECIMAL(8,2), -- por cada 100.000 trabajadores
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    """
    -- Tabla de enfermedades profesionales (CEPROSS)
    CREATE TABLE IF NOT EXISTS enfermedades_profesionales (
        id SERIAL PRIMARY KEY,
        fecha_referencia DATE NOT NULL,
        ccaa VARCHAR(50),
        sector VARCHAR(50),
        tipo_enfermedad VARCHAR(100),
        sexo VARCHAR(10),
        grupo_edad VARCHAR(20),
        num_casos INTEGER,
        incidencia DECIMAL(8,2),
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    """
    -- Tabla de afiliaciones (Seguridad Social)
    CREATE TABLE IF NOT EXISTS afiliaciones_ss (
        id SERIAL PRIMARY KEY,
        fecha_referencia DATE NOT NULL,
        ccaa VARCHAR(50),
        sector VARCHAR(50),
        num_afiliados INTEGER,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(fecha_referencia, ccaa, sector)
    );
    """,
    
    """
    -- Tabla de metadatos y control de actualizaciones
    CREATE TABLE IF NOT EXISTS control_actualizaciones (
        id SERIAL PRIMARY KEY,
        fuente_datos VARCHAR(50) NOT NULL,
        ultima_actualizacion TIMESTAMP,
        estado VARCHAR(20), -- 'exitoso', 'error', 'en_proceso'
        registros_procesados INTEGER,
        observaciones TEXT
    );
    """
]

try:
    with engine.connect() as conn:
        for i, query in enumerate(sql_queries, 1):
            print(f"Ejecutando consulta {i}/5...")
            conn.execute(text(query))
        
        conn.commit()
        print("✅ Todas las tablas creadas correctamente")
        
        # Insertar registro inicial de control
        control_query = """
        INSERT INTO control_actualizaciones (fuente_datos, estado, observaciones)
        VALUES 
            ('INE_ETCL', 'pendiente', 'Encuesta Trimestral Coste Laboral'),
            ('MITES_ATR', 'pendiente', 'Accidentes de Trabajo'),
            ('SS_AFILIACIONES', 'pendiente', 'Afiliaciones Seguridad Social'),
            ('SS_CEPROSS', 'pendiente', 'Enfermedades Profesionales')
        ON CONFLICT DO NOTHING;
        """
        conn.execute(text(control_query))
        conn.commit()
        
        # Mostrar resumen de tablas
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        result = conn.execute(text(tables_query))
        tables = result.fetchall()
        
        print("\n📋 TABLAS CREADAS:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n🎯 BASE DE DATOS LISTA PARA RECIBIR DATOS REALES")
        
except Exception as e:
    print(f"❌ Error creando estructura: {e}")