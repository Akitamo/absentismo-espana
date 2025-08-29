#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación de cálculo exacto según metodología Adecco del documento.
"""

import duckdb
import pandas as pd
from pathlib import Path

def main():
    # Conectar a BD
    db_path = Path(__file__).parent / 'data' / 'analysis.db'
    conn = duckdb.connect(str(db_path), read_only=True)
    
    print("=" * 80)
    print("CÁLCULO EXACTO SEGÚN METODOLOGÍA ADECCO")
    print("=" * 80)
    
    # Query para obtener los datos necesarios
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
    
    # Extraer valores base
    hp = df[(df['metrica'] == 'horas_pactadas')]['total_valor'].sum()
    hext = df[(df['metrica'] == 'horas_extraordinarias')]['total_valor'].sum()
    
    print("\n1. VALORES BASE:")
    print("-" * 40)
    print(f"   HP (Horas Pactadas): {hp}")
    print(f"   HEXT (Horas Extraordinarias): {hext}")
    
    # Identificar qué valores usar para vacaciones y festivos
    hnt_vac_individual = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'vacaciones')]['total_valor'].sum()
    hnt_fest_individual = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'festivos')]['total_valor'].sum()
    hnt_vac_fest_agregado = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'vacaciones_y_fiestas')]['total_valor'].sum()
    
    print(f"\n2. ANÁLISIS VACACIONES Y FESTIVOS:")
    print("-" * 40)
    print(f"   Vacaciones (individual): {hnt_vac_individual}")
    print(f"   Festivos (individual): {hnt_fest_individual}")
    print(f"   Vacaciones_y_fiestas (agregado): {hnt_vac_fest_agregado}")
    
    # Decidir qué usar
    if hnt_vac_fest_agregado > 0:
        vacaciones_festivos = hnt_vac_fest_agregado
        print(f"   -> Usando agregado: {vacaciones_festivos}")
    else:
        vacaciones_festivos = hnt_vac_individual + hnt_fest_individual
        print(f"   -> Usando suma individuales: {vacaciones_festivos}")
    
    # Razones técnicas/económicas (ERTEs)
    hnt_razones_tec = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'razones_tecnicas_economicas')]['total_valor'].sum()
    print(f"\n   Razones técnicas/económicas (ERTEs): {hnt_razones_tec}")
    
    # CÁLCULO DE HPE (Horas Pactadas Efectivas)
    print(f"\n3. CÁLCULO HPE (Horas Pactadas Efectivas):")
    print("-" * 40)
    print(f"   HPE = HP + HEXT - vacaciones - festivos - ERTEs")
    hpe = hp + hext - vacaciones_festivos - hnt_razones_tec
    print(f"   HPE = {hp} + {hext} - {vacaciones_festivos} - {hnt_razones_tec}")
    print(f"   HPE = {hpe:.2f}")
    
    # COMPONENTES DE HNTmo (motivos ocasionales)
    print(f"\n4. COMPONENTES DE HNTmo (según documento página 98-106):")
    print("-" * 40)
    
    # Según el documento, HNTmo incluye:
    hnt_it = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'it_total')]['total_valor'].sum()
    hnt_maternidad = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'maternidad_paternidad')]['total_valor'].sum()
    hnt_permisos = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'permisos_retribuidos')]['total_valor'].sum()
    hnt_compensacion = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'compensacion_extras')]['total_valor'].sum()
    hnt_otras_rem = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'otras_remuneradas')]['total_valor'].sum()
    hnt_perdidas = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'perdidas_lugar_trabajo')]['total_valor'].sum()
    hnt_conflictividad = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'conflictividad')]['total_valor'].sum()
    hnt_otras_no_rem = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'otras_no_remuneradas')]['total_valor'].sum()
    
    print(f"   IT (HNTRc): {hnt_it}")
    print(f"   Maternidad/Paternidad (HNTRd): {hnt_maternidad}")
    print(f"   Permisos remunerados (HNTRe): {hnt_permisos}")
    print(f"   Compensación extras (HNTRg): {hnt_compensacion}")
    print(f"   Otras remuneradas (HNTRi): {hnt_otras_rem}")
    print(f"   Pérdidas lugar trabajo (HNTRh): {hnt_perdidas}")
    print(f"   Conflictividad (HNTnR1): {hnt_conflictividad}")
    print(f"   Otras no remuneradas (HNTnR2): {hnt_otras_no_rem}")
    
    # Suma de HNTmo
    hntmo = (hnt_it + hnt_maternidad + hnt_permisos + hnt_compensacion + 
             hnt_otras_rem + hnt_perdidas + hnt_conflictividad + hnt_otras_no_rem)
    
    print(f"\n   HNTmo = Suma de componentes ocasionales")
    print(f"   HNTmo = {hntmo:.2f}")
    
    # CÁLCULO DE TASAS
    print(f"\n5. CÁLCULO DE TASAS:")
    print("-" * 40)
    
    tasa_absentismo = (hntmo / hpe) * 100 if hpe > 0 else 0
    tasa_it = (hnt_it / hpe) * 100 if hpe > 0 else 0
    
    print(f"   Tasa Absentismo General = HNTmo / HPE × 100")
    print(f"   Tasa Absentismo General = {hntmo:.2f} / {hpe:.2f} × 100 = {tasa_absentismo:.2f}%")
    print(f"")
    print(f"   Tasa IT = HNT_IT / HPE × 100")
    print(f"   Tasa IT = {hnt_it:.2f} / {hpe:.2f} × 100 = {tasa_it:.2f}%")
    
    print(f"\n6. COMPARACIÓN CON ADECCO:")
    print("-" * 40)
    print(f"   Tasa Absentismo General:")
    print(f"      Adecco: 7.4%")
    print(f"      Calculado: {tasa_absentismo:.2f}%")
    print(f"      Diferencia: {tasa_absentismo - 7.4:+.2f}%")
    print(f"")
    print(f"   Tasa IT:")
    print(f"      Adecco: 5.8%")
    print(f"      Calculado: {tasa_it:.2f}%")
    print(f"      Diferencia: {tasa_it - 5.8:+.2f}%")
    
    # Análisis adicional con agregados
    print(f"\n7. ANÁLISIS DE AGREGADOS (posible problema):")
    print("-" * 40)
    hnt_pagadas_agregado = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'pagadas_agregado')]['total_valor'].sum()
    hnt_no_pagadas_agregado = df[(df['metrica'] == 'horas_no_trabajadas') & (df['causa'] == 'no_pagadas_agregado')]['total_valor'].sum()
    
    print(f"   pagadas_agregado: {hnt_pagadas_agregado}")
    print(f"   no_pagadas_agregado: {hnt_no_pagadas_agregado}")
    print(f"   ")
    print(f"   Si 'pagadas_agregado' ya incluye múltiples componentes,")
    print(f"   podríamos estar duplicando valores.")
    
    # Hipótesis alternativa: usar solo agregados
    print(f"\n8. CÁLCULO ALTERNATIVO (usando agregados):")
    print("-" * 40)
    
    # Si pagadas_agregado incluye todo excepto vacaciones/festivos/ERTEs
    hntmo_alt = hnt_pagadas_agregado + hnt_no_pagadas_agregado
    tasa_abs_alt = (hntmo_alt / hpe) * 100 if hpe > 0 else 0
    
    print(f"   HNTmo alternativo = pagadas_agregado + no_pagadas_agregado")
    print(f"   HNTmo alternativo = {hnt_pagadas_agregado} + {hnt_no_pagadas_agregado} = {hntmo_alt:.2f}")
    print(f"   Tasa Absentismo = {hntmo_alt:.2f} / {hpe:.2f} × 100 = {tasa_abs_alt:.2f}%")
    
    conn.close()
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()