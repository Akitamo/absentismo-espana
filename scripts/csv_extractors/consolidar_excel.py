import pandas as pd

# Leer las tablas CSV creadas
OUTPUT_DIR = r"C:\Users\slunagda\AbsentismoEspana\data\processed"

df_periodo = pd.read_csv(f"{OUTPUT_DIR}/tabla_periodo.csv")
df_ccaa = pd.read_csv(f"{OUTPUT_DIR}/tabla_ccaa.csv")
df_jornada = pd.read_csv(f"{OUTPUT_DIR}/tabla_tipo_jornada.csv")

# Crear Excel consolidado
EXCEL_FILE = r"C:\Users\slunagda\AbsentismoEspana\informes\tablas_maestras_unificadas.xlsx"

with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
    # Escribir cada tabla en su hoja
    df_periodo.to_excel(writer, sheet_name='Periodo', index=False)
    df_ccaa.to_excel(writer, sheet_name='CCAA', index=False)
    df_jornada.to_excel(writer, sheet_name='TipoJornada', index=False)
    
    # Crear hoja de resumen
    resumen_data = [
        ['Periodo', len(df_periodo), f"Periodos trimestrales 2008T1-2024T4"],
        ['CCAA', len(df_ccaa), f"17 CCAA + 2 Ciudades + Nacional"],
        ['TipoJornada', len(df_jornada), f"Ambas jornadas, Completa, Parcial"]
    ]
    
    df_resumen = pd.DataFrame(resumen_data, columns=['Tabla', 'Registros', 'Descripcion'])
    df_resumen.to_excel(writer, sheet_name='Resumen', index=False)

print("✅ Excel consolidado creado exitosamente")
print(f"📊 Archivo: {EXCEL_FILE}")
print(f"📋 Contiene {len(df_periodo)} periodos, {len(df_ccaa)} CCAA, {len(df_jornada)} tipos jornada")
