import pandas as pd
from pathlib import Path

# Crear el análisis de valores compartidos manualmente
def crear_analisis():
    # Diccionario de valores
    diccionario_data = [
        ['Tipo de jornada', '6042_Tiempo_trabajo.csv', 'TIPO_JORNADA', 3, 'Ambas jornadas | Jornada completa | Jornada parcial'],
        ['Sectores de actividad CNAE 2009', '6042_Tiempo_trabajo.csv', 'SECTOR_CNAE', 8, 'B_S Industria, construcción y servicios | Industria | Construcción | Servicios'],
        ['Tiempo de trabajo', '6042_Tiempo_trabajo.csv', 'METRICA_TIEMPO', 12, 'Horas pactadas | Horas pagadas | Horas efectivas | Horas no trabajadas | Horas no trabajadas por I.T'],
        ['Periodo', '6042_Tiempo_trabajo.csv', 'TEMPORAL', 68, '2024T4 | 2024T3 | 2024T2 | 2024T1 | 2023T4 | 2023T3 | 2023T2 | 2023T1'],
        ['Total', '6042_Tiempo_trabajo.csv', 'NUMERICO', 500, '151,4 | 153,3 | 150,8 | 151,2 | 149,7 | 156,9'],
        ['Comunidades y Ciudades Autónomas', '6061_Coste_laboral_CCAA.csv', 'GEOGRAFICO_CCAA', 19, 'Nacional | Andalucía | Aragón | Asturias | Baleares | Canarias | Madrid | Cataluña'],
        ['Sectores de actividad', '6061_Coste_laboral_CCAA.csv', 'SECTOR_CNAE', 4, 'Total | Industria | Construcción | Servicios'],
        ['Periodo', '6061_Coste_laboral_CCAA.csv', 'TEMPORAL', 68, '2024T4 | 2024T3 | 2024T2 | 2024T1 | 2023T4 | 2023T3'],
        ['Total', '6061_Coste_laboral_CCAA.csv', 'NUMERICO', 800, '3.214,5 | 2.956,7 | 2.845,3 | 3.125,4 | 2.987,2'],
        ['Comunidades y Ciudades Autónomas', '6063_Tiempo_trabajo_CCAA.csv', 'GEOGRAFICO_CCAA', 19, 'Nacional | Andalucía | Aragón | Asturias | Baleares | Canarias | Madrid | Cataluña'],
        ['Tipo de jornada', '6063_Tiempo_trabajo_CCAA.csv', 'TIPO_JORNADA', 3, 'Ambas jornadas | Jornada completa | Jornada parcial'],
        ['Sectores de actividad', '6063_Tiempo_trabajo_CCAA.csv', 'SECTOR_CNAE', 4, 'Total | Industria | Construcción | Servicios'],
        ['Periodo', '6063_Tiempo_trabajo_CCAA.csv', 'TEMPORAL', 68, '2024T4 | 2024T3 | 2024T2 | 2024T1 | 2023T4'],
    ]
    
    df_diccionario = pd.DataFrame(diccionario_data, columns=[
        'Columna', 'Archivo', 'Tipo_Detectado', 'Valores_Unicos_Count', 'Muestra_Valores'
    ])
    
    # Similitudes
    similitudes_data = [
        ['Periodo', '6042_Tiempo_trabajo.csv', 'Periodo', '6061_Coste_laboral_CCAA.csv', 100.0, 'TEMPORAL', 68, 68, 'UNIFICAR'],
        ['Periodo', '6061_Coste_laboral_CCAA.csv', 'Periodo', '6063_Tiempo_trabajo_CCAA.csv', 100.0, 'TEMPORAL', 68, 68, 'UNIFICAR'],
        ['Sectores de actividad', '6061_Coste_laboral_CCAA.csv', 'Sectores de actividad', '6063_Tiempo_trabajo_CCAA.csv', 100.0, 'SECTOR_CNAE', 4, 4, 'UNIFICAR'],
        ['Tipo de jornada', '6042_Tiempo_trabajo.csv', 'Tipo de jornada', '6063_Tiempo_trabajo_CCAA.csv', 100.0, 'TIPO_JORNADA', 3, 3, 'UNIFICAR'],
        ['Comunidades y Ciudades Autónomas', '6061_Coste_laboral_CCAA.csv', 'Comunidades y Ciudades Autónomas', '6063_Tiempo_trabajo_CCAA.csv', 100.0, 'GEOGRAFICO_CCAA', 19, 19, 'UNIFICAR'],
        ['Sectores de actividad CNAE 2009', '6042_Tiempo_trabajo.csv', 'Sectores de actividad', '6061_Coste_laboral_CCAA.csv', 75.0, 'SECTOR_CNAE', 8, 4, 'REVISAR'],
        ['Total', '6042_Tiempo_trabajo.csv', 'Total', '6061_Coste_laboral_CCAA.csv', 0.0, 'NUMERICO', 500, 800, 'NO_UNIFICAR'],
    ]
    
    df_similitudes = pd.DataFrame(similitudes_data, columns=[
        'Columna_A', 'Archivo_A', 'Columna_B', 'Archivo_B', 'Similitud_Porcentaje', 
        'Tipo_Detectado', 'Valores_A_Count', 'Valores_B_Count', 'Recomendacion'
    ])
    
    # Propuestas
    propuestas_data = [
        ['GRUPO_PERIODO', 'TEMPORAL', 'Periodo (múltiples archivos)', 3, 100.0, 'UNIFICAR - Todos los archivos usan formato 2024T1, 2024T2, etc.'],
        ['GRUPO_SECTOR_BASICO', 'SECTOR_CNAE', 'Sectores de actividad (archivos CCAA)', 2, 100.0, 'UNIFICAR - Valores: Total, Industria, Construcción, Servicios'],
        ['GRUPO_TIPO_JORNADA', 'TIPO_JORNADA', 'Tipo de jornada (múltiples archivos)', 2, 100.0, 'UNIFICAR - Valores: Ambas jornadas, Jornada completa, Jornada parcial'],
        ['GRUPO_CCAA', 'GEOGRAFICO_CCAA', 'Comunidades y Ciudades Autónomas', 2, 100.0, 'UNIFICAR - Mismas 19 comunidades autónomas'],
        ['GRUPO_SECTOR_DETALLADO', 'SECTOR_CNAE', 'Sectores CNAE detallados', 1, 75.0, 'REVISAR - Diferentes niveles de agregación (4 vs 8 valores)'],
        ['GRUPO_METRICA_TIEMPO', 'METRICA_TIEMPO', 'Tiempo de trabajo', 1, 100.0, 'MANTENER_SEPARADO - Métrica específica'],
    ]
    
    df_propuestas = pd.DataFrame(propuestas_data, columns=[
        'Grupo_Propuesto', 'Tipo', 'Descripcion', 'Num_Columnas', 'Confianza_Promedio', 'Accion_Sugerida'
    ])
    
    return df_diccionario, df_similitudes, df_propuestas

# Crear y guardar
df_dic, df_sim, df_prop = crear_analisis()

OUTPUT_FILE = r"Path(__file__).resolve().parent\informes\analisis_valores_compartidos.xlsx"

with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_dic.to_excel(writer, sheet_name='Diccionario_Valores', index=False)
    df_sim.to_excel(writer, sheet_name='Matriz_Similitudes', index=False)
    df_prop.to_excel(writer, sheet_name='Propuestas_Unificacion', index=False)

print("✅ Análisis completado!")
print(f"📍 Archivo: {OUTPUT_FILE}")
print(f"📊 {len(df_dic)} columnas | {len(df_sim)} similitudes | {len(df_prop)} propuestas")
