#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapeo de métricas del informe Adecco Q4 2024 a campos de nuestra BD.
Identifica qué datos podemos replicar y cómo calcularlos.
"""

# MÉTRICAS CLAVE DEL INFORME ADECCO Q4 2024
ADECCO_METRICS = {
    "tasa_absentismo_general": {
        "valor_adecco": 7.4,
        "periodo": "2024T4",
        "descripcion": "Tasa general de absentismo laboral",
        "formula": "(horas_no_trabajadas / horas_pactadas_efectivas) * 100",
        "campos_bd": ["horas_no_trabajadas", "horas_pactadas"],
        "query_base": """
            SELECT 
                periodo,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_total,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100 as tasa_absentismo
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '2024T4'
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND (tipo_jornada = 'TOTAL' OR tipo_jornada IS NULL)
            GROUP BY periodo
        """
    },
    
    "tasa_absentismo_IT": {
        "valor_adecco": 5.8,
        "periodo": "2024T4",
        "descripcion": "Tasa de absentismo por Incapacidad Temporal",
        "formula": "(horas_IT / horas_pactadas_efectivas) * 100",
        "campos_bd": ["horas_no_trabajadas con causa='it_total'", "horas_pactadas"],
        "query_base": """
            SELECT 
                periodo,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) as hnt_it,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100 as tasa_it
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '2024T4'
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND (tipo_jornada = 'TOTAL' OR tipo_jornada IS NULL)
            GROUP BY periodo
        """
    },
    
    "absentismo_por_sector": {
        "valores_adecco": {
            "Industria": 8.1,
            "Servicios": 7.3,
            "Construcción": 6.3
        },
        "periodo": "2024T4",
        "descripcion": "Tasa de absentismo por sector económico",
        "query_base": """
            SELECT 
                periodo,
                cnae_codigo as sector,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_total,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100 as tasa_absentismo
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '2024T4'
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'SECTOR_BS'
                AND cnae_codigo IN ('Industria', 'Construcción', 'Servicios')
                AND (tipo_jornada = 'TOTAL' OR tipo_jornada IS NULL)
            GROUP BY periodo, cnae_codigo
            ORDER BY cnae_codigo
        """
    },
    
    "absentismo_por_ccaa": {
        "valores_adecco_top5": {
            "País Vasco": 9.1,
            "Asturias": 8.6,
            "Navarra": 8.3,
            "Castilla y León": 8.1,
            "Cantabria": 8.0
        },
        "valores_adecco_bottom5": {
            "La Rioja": 5.5,
            "Baleares": 5.9,
            "Madrid": 6.3,
            "Extremadura": 6.5,
            "Andalucía": 6.6
        },
        "periodo": "2024T4",
        "descripcion": "Tasa de absentismo por Comunidad Autónoma",
        "nota": "Solo tabla 6063 tiene datos por CCAA",
        "query_base": """
            SELECT 
                periodo,
                ccaa_codigo,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_total,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100 as tasa_absentismo
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '2024T4'
                AND ambito_territorial = 'CCAA'
                AND cnae_nivel = 'TOTAL'
                AND (tipo_jornada = 'TOTAL' OR tipo_jornada IS NULL)
            GROUP BY periodo, ccaa_codigo
            ORDER BY tasa_absentismo DESC
        """
    },
    
    "IT_por_ccaa": {
        "valores_adecco_top3": {
            "Asturias": 6.9,
            "País Vasco": 6.8,
            "Navarra": 6.6
        },
        "periodo": "2024T4",
        "descripcion": "Tasa de IT por CCAA",
        "query_base": """
            SELECT 
                periodo,
                ccaa_codigo,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) as hnt_it,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100 as tasa_it
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '2024T4'
                AND ambito_territorial = 'CCAA'
                AND cnae_nivel = 'TOTAL'
                AND (tipo_jornada = 'TOTAL' OR tipo_jornada IS NULL)
            GROUP BY periodo, ccaa_codigo
            ORDER BY tasa_it DESC
        """
    },
    
    "horas_perdidas_total": {
        "valor_adecco": 111.0,
        "periodo": "2024T4",
        "descripcion": "Horas de trabajo perdidas por trabajador al año",
        "formula": "horas_no_trabajadas * 4 (trimestres)",
        "query_base": """
            SELECT 
                periodo,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_trimestre,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) * 4 as hnt_anual_proyectado
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '2024T4'
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND (tipo_jornada = 'TOTAL' OR tipo_jornada IS NULL)
            GROUP BY periodo
        """
    },
    
    "evolucion_temporal": {
        "valores_adecco": {
            "2024T1": 7.2,
            "2024T2": 6.7,
            "2024T3": 6.9,
            "2024T4": 7.4
        },
        "descripcion": "Evolución trimestral de la tasa de absentismo",
        "query_base": """
            SELECT 
                periodo,
                SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) as hnt_total,
                SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END) as hp_total,
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100 as tasa_absentismo
            FROM observaciones_tiempo_trabajo
            WHERE periodo IN ('2024T1', '2024T2', '2024T3', '2024T4')
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND (tipo_jornada = 'TOTAL' OR tipo_jornada IS NULL)
            GROUP BY periodo
            ORDER BY periodo
        """
    },
    
    "causas_absentismo": {
        "valores_adecco": {
            "IT": 5.8,
            "Otras causas": 1.6
        },
        "periodo": "2024T4",
        "descripcion": "Desglose por causas principales",
        "query_base": """
            SELECT 
                periodo,
                CASE 
                    WHEN causa = 'it_total' THEN 'IT'
                    WHEN causa IS NOT NULL THEN 'Otras causas'
                    ELSE 'Sin especificar'
                END as tipo_causa,
                SUM(valor) as horas_causa,
                SUM(valor) / NULLIF(
                    (SELECT SUM(valor) 
                     FROM observaciones_tiempo_trabajo 
                     WHERE periodo = '2024T4' 
                       AND metrica = 'horas_pactadas'
                       AND ambito_territorial = 'NAC'
                       AND cnae_nivel = 'TOTAL'), 0) * 100 as tasa_causa
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '2024T4'
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND metrica = 'horas_no_trabajadas'
                AND (tipo_jornada = 'TOTAL' OR tipo_jornada IS NULL)
            GROUP BY periodo, tipo_causa
        """
    }
}

# MAPEO DE CÓDIGOS CCAA
CCAA_MAPPING = {
    "01": "Andalucía",
    "02": "Aragón", 
    "03": "Asturias",
    "04": "Baleares",
    "05": "Canarias",
    "06": "Cantabria",
    "07": "Castilla y León",
    "08": "Castilla-La Mancha",
    "09": "Cataluña",
    "10": "C. Valenciana",
    "11": "Extremadura",
    "12": "Galicia",
    "13": "Madrid",
    "14": "Murcia",
    "15": "Navarra",
    "16": "País Vasco",
    "17": "La Rioja",
    "00": "Total Nacional"
}

# VERIFICACIONES NECESARIAS
VALIDATIONS_REQUIRED = [
    {
        "check": "Verificar que tenemos datos 2024T4",
        "query": "SELECT DISTINCT periodo FROM observaciones_tiempo_trabajo WHERE periodo LIKE '2024%' ORDER BY periodo"
    },
    {
        "check": "Verificar estructura de causas de HNT",
        "query": "SELECT DISTINCT causa FROM observaciones_tiempo_trabajo WHERE metrica = 'horas_no_trabajadas' AND periodo = '2024T4'"
    },
    {
        "check": "Verificar disponibilidad de datos por CCAA",
        "query": "SELECT COUNT(*) as registros FROM observaciones_tiempo_trabajo WHERE ambito_territorial = 'CCAA' AND periodo = '2024T4'"
    },
    {
        "check": "Verificar sectores disponibles",
        "query": "SELECT DISTINCT cnae_codigo FROM observaciones_tiempo_trabajo WHERE cnae_nivel = 'SECTOR_BS' AND periodo = '2024T4'"
    }
]

# MÉTRICAS NO REPLICABLES (limitaciones de datos)
LIMITACIONES = {
    "divisiones_cnae_especificas": {
        "descripcion": "El informe Adecco muestra 88 divisiones CNAE con detalle que requieren tabla 6046",
        "solucion": "Usar datos agregados por sector o sección CNAE"
    },
    "datos_empresa_tamaño": {
        "descripcion": "Adecco segmenta por tamaño de empresa (menos de 50, 50-249, 250+)",
        "solucion": "No disponible en nuestras tablas de tiempo de trabajo"
    },
    "comparativa_europea": {
        "descripcion": "Adecco compara con datos de Eurostat",
        "solucion": "Solo tenemos datos nacionales de INE"
    }
}

if __name__ == "__main__":
    print("=" * 80)
    print("MAPEO DE MÉTRICAS ADECCO Q4 2024 -> BD INE")
    print("=" * 80)
    
    print("\n📊 MÉTRICAS PRINCIPALES REPLICABLES:")
    print("-" * 40)
    for key, metric in ADECCO_METRICS.items():
        if "valor_adecco" in metric:
            print(f"✓ {key}: {metric['valor_adecco']}% ({metric['descripcion']})")
        elif "valores_adecco" in metric:
            print(f"✓ {key}: {metric['descripcion']}")
            for subkey, value in metric.get("valores_adecco", {}).items():
                print(f"  - {subkey}: {value}%")
    
    print("\n⚠️ LIMITACIONES IDENTIFICADAS:")
    print("-" * 40)
    for key, limit in LIMITACIONES.items():
        print(f"✗ {key}: {limit['descripcion']}")
        print(f"  → Solución: {limit['solucion']}")
    
    print("\n✅ VALIDACIONES NECESARIAS:")
    print("-" * 40)
    for val in VALIDATIONS_REQUIRED:
        print(f"• {val['check']}")
    
    print("\n" + "=" * 80)
    print("SIGUIENTE PASO: Ejecutar queries de validación en DuckDB")
    print("=" * 80)