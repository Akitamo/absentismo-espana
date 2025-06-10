import pandas as pd
import os
from pathlib import Path

# Crear directorio processed
OUTPUT_DIR = r"Path(__file__).resolve().parent\data\processed"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("🚀 CREANDO TABLAS MAESTRAS UNIFICADAS")
print("=" * 50)

# 1. TABLA PERIODO
print("\n📅 TABLA PERIODO")
periodos_data = []
for año in range(2008, 2025):
    for trimestre in range(1, 5):
        periodo_id = f"{año}T{trimestre}"
        mes_inicio = (trimestre - 1) * 3 + 1
        fecha_inicio = f"{año}-{mes_inicio:02d}-01"
        
        periodos_data.append({
            'PeriodoID': periodo_id,
            'Año': año,
            'Trimestre': trimestre,
            'FechaInicio': fecha_inicio,
            'Descripcion': f"{trimestre}º Trimestre {año}",
            'OrdenCronologico': año * 10 + trimestre
        })

df_periodo = pd.DataFrame(periodos_data)
print(f"✅ {len(df_periodo)} periodos creados ({df_periodo['PeriodoID'].min()} - {df_periodo['PeriodoID'].max()})")

# 2. TABLA CCAA
print("\n🗺️ TABLA CCAA")
ccaa_data = [
    {'CCAA_ID': 'Nacional', 'CodigoINE': '00', 'NombreOficial': 'Nacional', 'NombreCorto': 'Nacional', 'Tipo': 'Nacional', 'EsNacional': True},
    {'CCAA_ID': 'Andalucía', 'CodigoINE': '01', 'NombreOficial': 'Andalucía', 'NombreCorto': 'Andalucía', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Aragón', 'CodigoINE': '02', 'NombreOficial': 'Aragón', 'NombreCorto': 'Aragón', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Asturias (Principado de)', 'CodigoINE': '03', 'NombreOficial': 'Asturias (Principado de)', 'NombreCorto': 'Asturias', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Balears (Illes)', 'CodigoINE': '04', 'NombreOficial': 'Balears (Illes)', 'NombreCorto': 'Baleares', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Canarias', 'CodigoINE': '05', 'NombreOficial': 'Canarias', 'NombreCorto': 'Canarias', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Cantabria', 'CodigoINE': '06', 'NombreOficial': 'Cantabria', 'NombreCorto': 'Cantabria', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Castilla y León', 'CodigoINE': '07', 'NombreOficial': 'Castilla y León', 'NombreCorto': 'Castilla y León', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Castilla-La Mancha', 'CodigoINE': '08', 'NombreOficial': 'Castilla-La Mancha', 'NombreCorto': 'Castilla-La Mancha', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Cataluña', 'CodigoINE': '09', 'NombreOficial': 'Cataluña', 'NombreCorto': 'Cataluña', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Comunitat Valenciana', 'CodigoINE': '10', 'NombreOficial': 'Comunitat Valenciana', 'NombreCorto': 'Valencia', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Extremadura', 'CodigoINE': '11', 'NombreOficial': 'Extremadura', 'NombreCorto': 'Extremadura', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Galicia', 'CodigoINE': '12', 'NombreOficial': 'Galicia', 'NombreCorto': 'Galicia', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Madrid (Comunidad de)', 'CodigoINE': '13', 'NombreOficial': 'Madrid (Comunidad de)', 'NombreCorto': 'Madrid', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Murcia (Región de)', 'CodigoINE': '14', 'NombreOficial': 'Murcia (Región de)', 'NombreCorto': 'Murcia', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Navarra (Comunidad Foral de)', 'CodigoINE': '15', 'NombreOficial': 'Navarra (Comunidad Foral de)', 'NombreCorto': 'Navarra', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'País Vasco', 'CodigoINE': '16', 'NombreOficial': 'País Vasco', 'NombreCorto': 'País Vasco', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Rioja (La)', 'CodigoINE': '17', 'NombreOficial': 'Rioja (La)', 'NombreCorto': 'La Rioja', 'Tipo': 'Comunidad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Ceuta', 'CodigoINE': '18', 'NombreOficial': 'Ceuta', 'NombreCorto': 'Ceuta', 'Tipo': 'Ciudad Autónoma', 'EsNacional': False},
    {'CCAA_ID': 'Melilla', 'CodigoINE': '19', 'NombreOficial': 'Melilla', 'NombreCorto': 'Melilla', 'Tipo': 'Ciudad Autónoma', 'EsNacional': False}
]

df_ccaa = pd.DataFrame(ccaa_data)
print(f"✅ {len(df_ccaa)} CCAA creadas (17 CCAA + 2 Ciudades Autónomas + Nacional)")

# 3. TABLA TIPO JORNADA
print("\n⏰ TABLA TIPO JORNADA")
jornada_data = [
    {'TipoJornada_ID': 'Ambas jornadas', 'Codigo': 'AMBAS_JORNADAS', 'Descripcion': 'Ambas jornadas', 'EsAgregado': True, 'OrdenVisualizacion': 1},
    {'TipoJornada_ID': 'Jornada completa', 'Codigo': 'JORNADA_COMPLETA', 'Descripcion': 'Jornada completa', 'EsAgregado': False, 'OrdenVisualizacion': 2},
    {'TipoJornada_ID': 'Jornada parcial', 'Codigo': 'JORNADA_PARCIAL', 'Descripcion': 'Jornada parcial', 'EsAgregado': False, 'OrdenVisualizacion': 3}
]

df_jornada = pd.DataFrame(jornada_data)
print(f"✅ {len(df_jornada)} tipos de jornada creados")

# 4. GUARDAR ARCHIVOS
print("\n💾 GUARDANDO ARCHIVOS...")

# CSV individuales
df_periodo.to_csv(os.path.join(OUTPUT_DIR, 'tabla_periodo.csv'), index=False, encoding='utf-8')
df_ccaa.to_csv(os.path.join(OUTPUT_DIR, 'tabla_ccaa.csv'), index=False, encoding='utf-8')
df_jornada.to_csv(os.path.join(OUTPUT_DIR, 'tabla_tipo_jornada.csv'), index=False, encoding='utf-8')

print("✅ Archivos CSV individuales guardados")

# Excel consolidado
EXCEL_FILE = r"Path(__file__).resolve().parent\informes\tablas_maestras_unificadas.xlsx"

with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
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

print("✅ Excel consolidado guardado")

print(f"\n🎉 ¡UNIFICACIÓN COMPLETADA!")
print("=" * 50)
print(f"📊 RESULTADOS:")
print(f"   • {len(df_periodo)} periodos únicos (2008T1 - 2024T4)")
print(f"   • {len(df_ccaa)} comunidades autónomas + nacional")
print(f"   • {len(df_jornada)} tipos de jornada")
print(f"\n📁 ARCHIVOS GENERADOS:")
print(f"   • CSV individuales: {OUTPUT_DIR}")
print(f"   • Excel consolidado: {EXCEL_FILE}")
print(f"\n🎯 LISTO PARA POWER BI:")
print(f"   Las tablas están preparadas como dimensiones")
print(f"   para crear relaciones con las tablas de hechos.")
