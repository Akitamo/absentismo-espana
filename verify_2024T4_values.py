#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar valores exactos de 2024T4 y calcular tasas según Adecco.
"""

import duckdb
import pandas as pd
from pathlib import Path

def main():
    # Conectar a BD con encoding específico
    db_path = Path(__file__).parent / 'data' / 'analysis.db'
    # Usar conexión read-only para evitar problemas
    conn = duckdb.connect(str(db_path), read_only=True)
    
    print("=" * 80)
    print("VERIFICACIÓN DE VALORES 2024T4 - METODOLOGÍA ADECCO")
    print("=" * 80)
    
    # Obtener todas las métricas para 2024T4
    query = """
        SELECT 
            metrica,
            causa,
            ROUND(SUM(valor), 2) as total_valor
        FROM observaciones_tiempo_trabajo
        WHERE periodo = '2024T4'
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY metrica, causa
        ORDER BY metrica, causa
    """
    
    df = conn.execute(query).df()
    
    print("\n1. VALORES BASE DISPONIBLES EN BD:")
    print("-" * 40)
    for _, row in df.iterrows():
        causa_str = f" ({row['causa']})" if pd.notna(row['causa']) else " (TOTAL)"
        print(f"   {row['metrica']}{causa_str}: {row['total_valor']}")
    
    # Calcular métricas según metodología Adecco
    print("\n2. ANÁLISIS DE COMPONENTES Y AGREGADOS:")
    print("-" * 40)
    
    # Extraer valores específicos
    hp = df[(df['metrica'] == 'horas_pactadas')]['total_valor'].sum()
    hext = df[(df['metrica'] == 'horas_extraordinarias')]['total_valor'].sum()
    hnt_total = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'].isna())]['total_valor'].sum()
    
    # Componentes individuales
    hnt_vacaciones = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'vacaciones')]['total_valor'].sum()
    hnt_festivos = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'festivos')]['total_valor'].sum()
    hnt_vac_fest = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'vacaciones_y_fiestas')]['total_valor'].sum()
    hnt_razones_tec = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'razones_tecnicas_economicas')]['total_valor'].sum()
    hnt_it = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'it_total')]['total_valor'].sum()
    
    # Agregados
    hnt_pagadas_agregado = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'pagadas_agregado')]['total_valor'].sum()
    hnt_no_pagadas_agregado = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'no_pagadas_agregado')]['total_valor'].sum()
    
    # Otras causas detalladas
    hnt_maternidad = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'maternidad_paternidad')]['total_valor'].sum()
    hnt_permisos = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'permisos_retribuidos')]['total_valor'].sum()
    hnt_compensacion = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'compensacion_extras')]['total_valor'].sum()
    hnt_otras_rem = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'otras_remuneradas')]['total_valor'].sum()
    hnt_conflictividad = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'conflictividad')]['total_valor'].sum()
    hnt_otras_no_rem = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'otras_no_remuneradas')]['total_valor'].sum()
    
    print(f"   ANÁLISIS DE AGREGADOS:")
    print(f"   - pagadas_agregado: {hnt_pagadas_agregado}")
    print(f"   - no_pagadas_agregado: {hnt_no_pagadas_agregado}")
    print(f"   - vacaciones_y_fiestas: {hnt_vac_fest}")
    print(f"   ")
    print(f"   COMPONENTES DETALLADOS:")
    print(f"   - IT: {hnt_it}")
    print(f"   - vacaciones (individual): {hnt_vacaciones}")
    print(f"   - festivos (individual): {hnt_festivos}")
    print(f"   - maternidad: {hnt_maternidad}")
    print(f"   - permisos: {hnt_permisos}")
    print(f"   - razones técnicas: {hnt_razones_tec}")
    print(f"   ")
    print(f"   SUMA COMPONENTES: {hnt_it + hnt_vacaciones + hnt_festivos + hnt_maternidad + hnt_permisos + hnt_razones_tec + hnt_compensacion + hnt_otras_rem + hnt_conflictividad + hnt_otras_no_rem}")
    print(f"   HNT TOTAL: {hnt_total}")
    
    print("\n3. CÁLCULO SEGÚN METODOLOGÍA ADECCO:")
    
    print(f"   HP (Horas Pactadas): {hp}")
    print(f"   HEXT (Horas Extraordinarias): {hext}")
    print(f"   HNT Total: {hnt_total}")
    print(f"   HNT Vacaciones: {hnt_vacaciones}")
    print(f"   HNT Festivos: {hnt_festivos}")
    print(f"   HNT Vacaciones y Fiestas: {hnt_vac_fest}")
    print(f"   HNT Razones Técnicas: {hnt_razones_tec}")
    print(f"   HNT IT: {hnt_it}")
    
    # HIPÓTESIS 1: vacaciones_y_fiestas ya incluye vacaciones y festivos por separado
    # Entonces NO debemos restar las individuales si ya tenemos el agregado
    print("\n   ANÁLISIS: vacaciones_y_fiestas parece ser el agregado")
    print(f"   - vacaciones: {hnt_vacaciones}")
    print(f"   - festivos: {hnt_festivos}")
    print(f"   - vacaciones_y_fiestas: {hnt_vac_fest}")
    print(f"   - Suma vac+fest: {hnt_vacaciones + hnt_festivos} vs agregado: {hnt_vac_fest}")
    
    # Si vacaciones_y_fiestas es el agregado, usar solo ese
    if hnt_vac_fest > 0 and (hnt_vacaciones + hnt_festivos) < hnt_vac_fest:
        # Usar el agregado
        vacaciones_festivos_total = hnt_vac_fest
        print(f"   -> Usando agregado vacaciones_y_fiestas: {vacaciones_festivos_total}")
    else:
        # Usar la suma de individuales
        vacaciones_festivos_total = hnt_vacaciones + hnt_festivos
        print(f"   -> Usando suma de individuales: {vacaciones_festivos_total}")
    
    # Cálculo HPE según documento (corregido)
    # HPE = HP + HEXT - vacaciones - festivos - razones técnicas
    hpe = hp + hext - vacaciones_festivos_total - hnt_razones_tec
    
    print(f"\n   HPE = HP + HEXT - (vacaciones+festivos) - razones_tec")
    print(f"   HPE = {hp} + {hext} - {vacaciones_festivos_total} - {hnt_razones_tec}")
    print(f"   HPE = {hpe}")
    
    # Cálculo HNTmo según documento (corregido)
    # HNTmo = HNT total - vacaciones - festivos - razones técnicas
    hntmo = hnt_total - vacaciones_festivos_total - hnt_razones_tec
    
    print(f"\n   HNTmo = HNT total - (vacaciones+festivos) - razones_tec")
    print(f"   HNTmo = {hnt_total} - {vacaciones_festivos_total} - {hnt_razones_tec}")
    print(f"   HNTmo = {hntmo}")
    
    # Tasas finales
    tasa_absentismo = (hntmo / hpe) * 100 if hpe > 0 else 0
    tasa_it = (hnt_it / hpe) * 100 if hpe > 0 else 0
    
    print("\n3. TASAS CALCULADAS:")
    print("-" * 40)
    print(f"   Tasa Absentismo General = HNTmo / HPE * 100")
    print(f"   Tasa Absentismo General = {hntmo} / {hpe} * 100 = {tasa_absentismo:.2f}%")
    print(f"   ")
    print(f"   Tasa Absentismo IT = HNT_IT / HPE * 100")
    print(f"   Tasa Absentismo IT = {hnt_it} / {hpe} * 100 = {tasa_it:.2f}%")
    
    print("\n4. COMPARACIÓN CON VALORES ESPERADOS:")
    print("-" * 40)
    print(f"   Tasa Absentismo General:")
    print(f"      - Esperado (Adecco): 7.4%")
    print(f"      - Calculado: {tasa_absentismo:.2f}%")
    print(f"      - Diferencia: {tasa_absentismo - 7.4:+.2f}%")
    print(f"   ")
    print(f"   Tasa Absentismo IT:")
    print(f"      - Esperado (Adecco): 5.8%")
    print(f"      - Calculado: {tasa_it:.2f}%")
    print(f"      - Diferencia: {tasa_it - 5.8:+.2f}%")
    
    # Verificar si los valores están divididos por 10 (problema conocido del INE)
    print("\n5. HIPÓTESIS: Valores podrían estar en décimas")
    print("-" * 40)
    hp_ajustado = hp / 10
    hpe_ajustado = hpe / 10
    hntmo_ajustado = hntmo / 10
    hnt_it_ajustado = hnt_it / 10
    
    tasa_abs_ajustada = (hntmo_ajustado / hpe_ajustado) * 100 if hpe_ajustado > 0 else 0
    tasa_it_ajustada = (hnt_it_ajustado / hpe_ajustado) * 100 if hpe_ajustado > 0 else 0
    
    print(f"   Si dividimos valores por 10:")
    print(f"   Tasa Absentismo General = {hntmo_ajustado:.2f} / {hpe_ajustado:.2f} * 100 = {tasa_abs_ajustada:.2f}%")
    print(f"   Tasa Absentismo IT = {hnt_it_ajustado:.2f} / {hpe_ajustado:.2f} * 100 = {tasa_it_ajustada:.2f}%")
    
    conn.close()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()