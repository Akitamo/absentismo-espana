"""
Script para validar datos cargados en DuckDB contra valores del INE
Compara valores específicos para verificar que la carga es correcta
"""

import sys
import pandas as pd
from pathlib import Path
import duckdb

# Añadir el directorio al path
sys.path.append(str(Path(__file__).parent))

def validate_against_ine():
    """
    Valida datos cargados contra valores conocidos del INE
    """
    print("\n" + "="*80)
    print("VALIDACIÓN DE DATOS CONTRA INE")
    print("="*80 + "\n")
    
    # Conectar a DuckDB
    db_path = Path(__file__).parent / "data" / "analysis.db"
    conn = duckdb.connect(str(db_path))
    
    # VALIDACIÓN 1: Tabla 6042 - Valores específicos
    print("1. VALIDACIÓN TABLA 6042 - Tiempo de trabajo por sectores y jornada")
    print("-" * 60)
    
    # Valores de referencia del INE (tabla 6042)
    # URL: https://www.ine.es/jaxiT3/Datos.htm?t=6042
    valores_ine = [
        # 2025T1, Total B-S, Ambas jornadas
        {"periodo": "2025T1", "sector": "TOTAL", "jornada": "TOTAL", "metrica": "horas_pactadas", "valor_ine": 151.0},
        {"periodo": "2025T1", "sector": "TOTAL", "jornada": "TOTAL", "metrica": "horas_efectivas", "valor_ine": 151.4},
        {"periodo": "2025T1", "sector": "TOTAL", "jornada": "TOTAL", "metrica": "horas_no_trabajadas", "causa": "it_total", "valor_ine": 8.3},
        
        # 2024T4, Total B-S, Ambas jornadas
        {"periodo": "2024T4", "sector": "TOTAL", "jornada": "TOTAL", "metrica": "horas_pactadas", "valor_ine": 151.4},
        {"periodo": "2024T4", "sector": "TOTAL", "jornada": "TOTAL", "metrica": "horas_efectivas", "valor_ine": 151.9},
        {"periodo": "2024T4", "sector": "TOTAL", "jornada": "TOTAL", "metrica": "horas_no_trabajadas", "causa": "it_total", "valor_ine": 7.9},
        
        # 2025T1, Industria, Ambas jornadas
        {"periodo": "2025T1", "sector": "B-E", "jornada": "TOTAL", "metrica": "horas_pactadas", "valor_ine": 152.4},
        {"periodo": "2025T1", "sector": "B-E", "jornada": "TOTAL", "metrica": "horas_efectivas", "valor_ine": 153.5},
        
        # 2025T1, Total B-S, Tiempo completo (valores validados en exploración)
        {"periodo": "2025T1", "sector": "TOTAL", "jornada": "COMPLETA", "metrica": "horas_pactadas", "valor_ine": 168.4},
        {"periodo": "2025T1", "sector": "TOTAL", "jornada": "COMPLETA", "metrica": "horas_efectivas", "valor_ine": 168.7},
        
        # 2025T1, Total B-S, Tiempo parcial (valores validados en exploración)
        {"periodo": "2025T1", "sector": "TOTAL", "jornada": "PARCIAL", "metrica": "horas_pactadas", "valor_ine": 89.3},
        {"periodo": "2025T1", "sector": "TOTAL", "jornada": "PARCIAL", "metrica": "horas_efectivas", "valor_ine": 89.9},
    ]
    
    print("\nComparando valores específicos:\n")
    print(f"{'Periodo':<8} {'Sector':<10} {'Jornada':<10} {'Métrica':<25} {'Causa':<15} {'INE':<8} {'BD':<8} {'Diff':<8} {'Status':<10}")
    print("-" * 120)
    
    validaciones_ok = 0
    validaciones_total = 0
    
    for val in valores_ine:
        validaciones_total += 1
        
        # Construir query
        if val.get("causa"):
            query = f"""
            SELECT valor 
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '{val['periodo']}'
              AND cnae_nivel = '{('TOTAL' if val['sector'] == 'TOTAL' else 'SECTOR_BS')}'
              AND {'cnae_codigo IS NULL' if val['sector'] == 'TOTAL' else f"cnae_codigo = '{val['sector']}'"}
              AND tipo_jornada = '{val['jornada']}'
              AND metrica = '{val['metrica']}'
              AND causa = '{val['causa']}'
              AND fuente_tabla = '6042'
            """
        else:
            query = f"""
            SELECT valor 
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '{val['periodo']}'
              AND cnae_nivel = '{('TOTAL' if val['sector'] == 'TOTAL' else 'SECTOR_BS')}'
              AND {'cnae_codigo IS NULL' if val['sector'] == 'TOTAL' else f"cnae_codigo = '{val['sector']}'"}
              AND tipo_jornada = '{val['jornada']}'
              AND metrica = '{val['metrica']}'
              AND causa IS NULL
              AND fuente_tabla = '6042'
            """
        
        try:
            result = conn.execute(query).fetchone()
            
            if result:
                valor_bd = float(result[0])
                valor_bd = round(valor_bd, 1)
                valor_ine = val['valor_ine']  # Los valores ya están correctos, no dividir
                diff = abs(valor_bd - valor_ine)
                
                status = "[OK]" if diff < 0.1 else "[ERROR]"
                if diff < 0.1:
                    validaciones_ok += 1
                
                print(f"{val['periodo']:<8} {val['sector']:<10} {val['jornada']:<10} "
                      f"{val['metrica']:<25} {val.get('causa', '-'):<15} "
                      f"{valor_ine:<8.1f} {valor_bd:<8.1f} {diff:<8.2f} {status:<10}")
            else:
                print(f"{val['periodo']:<8} {val['sector']:<10} {val['jornada']:<10} "
                      f"{val['metrica']:<25} {val.get('causa', '-'):<15} "
                      f"{val['valor_ine']:<8.1f} {'N/A':<8} {'N/A':<8} {'[NO DATA]':<10}")
        except Exception as e:
            print(f"Error ejecutando query: {e}")
    
    print("-" * 120)
    print(f"\nResultado: {validaciones_ok}/{validaciones_total} validaciones correctas")
    
    # VALIDACIÓN 2: Cálculo de tasa de absentismo
    print("\n2. VALIDACIÓN DE CÁLCULO DE TASA DE ABSENTISMO")
    print("-" * 60)
    
    query_absentismo = """
    SELECT 
        periodo,
        SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as horas_pactadas,
        SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) as horas_it,
        ROUND(
            SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) * 100.0 / 
            NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0),
            2
        ) as tasa_absentismo_it
    FROM observaciones_tiempo_trabajo
    WHERE cnae_nivel = 'TOTAL'
      AND tipo_jornada = 'TOTAL'
      AND fuente_tabla = '6042'
    GROUP BY periodo
    ORDER BY periodo DESC
    """
    
    df_absentismo = conn.execute(query_absentismo).fetchdf()
    
    print("\nTasas de absentismo IT calculadas (Total Nacional B-S):")
    print(df_absentismo.to_string(index=False))
    
    # Verificación manual
    print("\nVerificación manual del cálculo:")
    for _, row in df_absentismo.iterrows():
        tasa_manual = (row['horas_it'] / row['horas_pactadas']) * 100
        print(f"{row['periodo']}: {row['horas_it']:.1f} / {row['horas_pactadas']:.1f} * 100 = {tasa_manual:.2f}%")
    
    # VALIDACIÓN 3: Consistencia de datos
    print("\n3. VALIDACIÓN DE CONSISTENCIA")
    print("-" * 60)
    
    # Verificar que no hay duplicados
    query_duplicados = """
    SELECT COUNT(*) as total, COUNT(DISTINCT 
        periodo || '|' || COALESCE(ambito_territorial, '') || '|' || 
        COALESCE(ccaa_codigo, '') || '|' || cnae_nivel || '|' || 
        COALESCE(cnae_codigo, '') || '|' || COALESCE(tipo_jornada, '') || '|' || 
        metrica || '|' || COALESCE(causa, '')
    ) as unicos
    FROM observaciones_tiempo_trabajo
    """
    
    result = conn.execute(query_duplicados).fetchone()
    print(f"\nRegistros totales: {result[0]}")
    print(f"Combinaciones únicas: {result[1]}")
    if result[0] == result[1]:
        print("[OK] No hay duplicados en la clave primaria")
    else:
        print(f"[ADVERTENCIA] Posibles duplicados ({result[0] - result[1]} registros)")
    
    # Verificar rangos de valores
    query_rangos = """
    SELECT 
        MIN(valor) as min_valor,
        MAX(valor) as max_valor,
        AVG(valor) as avg_valor
    FROM observaciones_tiempo_trabajo
    WHERE metrica = 'horas_pactadas'
    """
    
    result = conn.execute(query_rangos).fetchone()
    print(f"\nRango de horas pactadas:")
    print(f"  Mínimo: {result[0]:.1f} horas")
    print(f"  Máximo: {result[1]:.1f} horas")
    print(f"  Promedio: {result[2]:.1f} horas")
    
    if result[0] > 0 and result[1] < 200:
        print("[OK] Valores en rango esperado (0-200 horas/mes)")
    else:
        print("[ADVERTENCIA] Valores fuera de rango esperado")
    
    # RESUMEN FINAL
    print("\n" + "="*80)
    print("RESUMEN DE VALIDACIÓN")
    print("="*80)
    
    if validaciones_ok == validaciones_total:
        print("\n[OK] VALIDACION EXITOSA: Los datos cargados coinciden con el INE")
        print("  Puedes proceder con la carga completa de todos los periodos")
    else:
        print(f"\n[ERROR] VALIDACION CON ERRORES: {validaciones_total - validaciones_ok} valores no coinciden")
        print("  Revisa los mapeos y transformaciones antes de la carga completa")
    
    conn.close()
    
    return validaciones_ok == validaciones_total

if __name__ == "__main__":
    success = validate_against_ine()
    sys.exit(0 if success else 1)