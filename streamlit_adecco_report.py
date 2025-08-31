#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Streamlit para comparar datos de absentismo con informe Adecco Q4 2024.
Muestra tablas comparativas entre valores publicados por Adecco y calculados desde BD.
"""

import streamlit as st
import pandas as pd
import duckdb
from pathlib import Path
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Comparación Absentismo - Adecco Q4 2024",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones de conexión y consultas
@st.cache_resource
def connect_db():
    """Conecta a la base de datos DuckDB."""
    db_path = Path(__file__).parent / 'data' / 'analysis.db'
    return duckdb.connect(str(db_path))

@st.cache_data
def calcular_tasa_absentismo_nacional(_conn, periodo='2024T4'):
    """Calcula la tasa de absentismo nacional."""
    query = """
        SELECT 
            periodo,
            ROUND(SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END), 2) as hnt_total,
            ROUND(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 2) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100, 
                2
            ) as tasa_absentismo
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY periodo
    """
    return _conn.execute(query, [periodo]).df()

@st.cache_data
def calcular_tasa_IT_nacional(_conn, periodo='2024T4'):
    """Calcula la tasa de absentismo por IT."""
    query = """
        SELECT 
            periodo,
            ROUND(SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END), 2) as hnt_it,
            ROUND(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 2) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' AND causa = 'it_total' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_it
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY periodo
    """
    return _conn.execute(query, [periodo]).df()

@st.cache_data
def calcular_absentismo_por_sector(_conn, periodo='2024T4'):
    """Calcula la tasa de absentismo por sector."""
    sector_mapping = {
        'B-E': 'Industria',
        'F': 'Construcción',
        'G-S': 'Servicios'
    }
    
    query = """
        SELECT 
            cnae_codigo as sector_codigo,
            ROUND(SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END), 2) as hnt_total,
            ROUND(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 2) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_absentismo
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'SECTOR_BS'
            AND es_total_jornada = true
        GROUP BY cnae_codigo
        ORDER BY cnae_codigo
    """
    df = _conn.execute(query, [periodo]).df()
    df['sector'] = df['sector_codigo'].map(sector_mapping)
    return df

@st.cache_data
def calcular_absentismo_por_ccaa(_conn, periodo='2024T4'):
    """Calcula la tasa de absentismo por CCAA."""
    ccaa_names = {
        "01": "Andalucía", "02": "Aragón", "03": "Asturias", "04": "Baleares",
        "05": "Canarias", "06": "Cantabria", "07": "Castilla y León", 
        "08": "Castilla-La Mancha", "09": "Cataluña", "10": "C. Valenciana",
        "11": "Extremadura", "12": "Galicia", "13": "Madrid", "14": "Murcia",
        "15": "Navarra", "16": "País Vasco", "17": "La Rioja"
    }
    
    query = """
        SELECT 
            ccaa_codigo,
            ROUND(SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END), 2) as hnt_total,
            ROUND(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 2) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_absentismo
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'CCAA'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY ccaa_codigo
        ORDER BY tasa_absentismo DESC
    """
    df = _conn.execute(query, [periodo]).df()
    df['ccaa_nombre'] = df['ccaa_codigo'].map(ccaa_names)
    return df

@st.cache_data
def calcular_evolucion_trimestral(_conn, año='2024'):
    """Calcula la evolución trimestral del absentismo."""
    query = f"""
        SELECT 
            periodo,
            ROUND(SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END), 2) as hnt_total,
            ROUND(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 2) as hp_total,
            ROUND(
                (SUM(CASE WHEN metrica = 'horas_no_trabajadas' THEN valor ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN metrica = 'horas_pactadas' THEN valor ELSE 0 END), 0)) * 100,
                2
            ) as tasa_absentismo
        FROM observaciones_tiempo_trabajo
        WHERE periodo LIKE '{año}%'
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND es_total_jornada = true
        GROUP BY periodo
        ORDER BY periodo
    """
    return _conn.execute(query).df()

@st.cache_data
def calcular_causas_absentismo(_conn, periodo='2024T4'):
    """Calcula el desglose por causas de absentismo."""
    query = """
        WITH horas_pactadas_total AS (
            SELECT SUM(valor) as hp_total
            FROM observaciones_tiempo_trabajo
            WHERE periodo = ?
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND metrica = 'horas_pactadas'
                AND es_total_jornada = true
        )
        SELECT 
            CASE 
                WHEN causa = 'it_total' THEN 'Incapacidad Temporal (IT)'
                WHEN causa IN ('vacaciones', 'festivos', 'vacaciones_y_fiestas') THEN 'Vacaciones y festivos'
                WHEN causa IN ('maternidad_paternidad') THEN 'Maternidad/Paternidad'
                WHEN causa IN ('permisos_retribuidos') THEN 'Permisos retribuidos'
                WHEN causa IN ('conflictividad') THEN 'Conflictividad laboral'
                WHEN causa IS NULL THEN 'TOTAL GENERAL'
                ELSE 'Otras causas'
            END as tipo_causa,
            ROUND(SUM(valor), 2) as horas_causa,
            ROUND(
                (SUM(valor) / (SELECT hp_total FROM horas_pactadas_total)) * 100,
                2
            ) as tasa_causa
        FROM observaciones_tiempo_trabajo
        WHERE periodo = ?
            AND ambito_territorial = 'NAC'
            AND cnae_nivel = 'TOTAL'
            AND metrica = 'horas_no_trabajadas'
            AND es_total_jornada = true
        GROUP BY tipo_causa
        ORDER BY 
            CASE WHEN tipo_causa = 'TOTAL GENERAL' THEN 0 ELSE 1 END,
            tasa_causa DESC
    """
    return _conn.execute(query, [periodo, periodo]).df()

# Valores de referencia del informe Adecco
ADECCO_Q4_2024 = {
    "tasa_general": 7.4,
    "tasa_it": 5.8,
    "horas_perdidas": 111.0,
    "sectores": {
        "Industria": 8.1,
        "Servicios": 7.3,
        "Construcción": 6.3
    },
    "evolucion_2024": {
        "2024T1": 7.2,
        "2024T2": 6.7,
        "2024T3": 6.9,
        "2024T4": 7.4
    },
    "ccaa_ranking": [
        ("País Vasco", 9.1),
        ("Asturias", 8.6),
        ("Navarra", 8.3),
        ("Castilla y León", 8.1),
        ("Cantabria", 8.0),
        ("Aragón", 7.9),
        ("Galicia", 7.6),
        ("Cataluña", 7.5),
        ("Murcia", 7.4),
        ("C. Valenciana", 7.2),
        ("Canarias", 6.8),
        ("Castilla-La Mancha", 6.7),
        ("Andalucía", 6.6),
        ("Extremadura", 6.5),
        ("Madrid", 6.3),
        ("Baleares", 5.9),
        ("La Rioja", 5.5)
    ],
    "it_ccaa_top": [
        ("Asturias", 6.9),
        ("País Vasco", 6.8),
        ("Navarra", 6.6)
    ]
}

def main():
    """Función principal de la aplicación Streamlit."""
    
    # Header
    st.title("📊 Comparación de Absentismo Laboral")
    st.markdown("### Informe Adecco Q4 2024 vs Base de Datos INE")
    st.markdown(f"*Fecha de análisis: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")
    
    # Conectar a BD
    conn = connect_db()
    
    # Sidebar para selección
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        periodo_seleccionado = st.selectbox(
            "Seleccionar periodo",
            ["2024T4", "2024T3", "2024T2", "2024T1"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 📌 Notas importantes")
        st.info("""
        - Los valores de Adecco están fijos para Q4 2024
        - Los datos de BD provienen del INE (ETCL)
        - Las diferencias pueden deberse a:
          - Metodología de cálculo
          - Agregación de datos
          - Definición de métricas
        """)
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Indicadores Principales",
        "🏭 Por Sectores", 
        "🗺️ Por CCAA",
        "📅 Evolución Temporal",
        "📋 Desglose Causas",
        "🔍 Análisis Detallado"
    ])
    
    # TAB 1: INDICADORES PRINCIPALES
    with tab1:
        st.header("Indicadores Principales de Absentismo")
        
        col1, col2, col3 = st.columns(3)
        
        # Tasa general
        with col1:
            st.metric("**TASA GENERAL ABSENTISMO**", "", "")
            df_nacional = calcular_tasa_absentismo_nacional(conn, periodo_seleccionado)
            
            if not df_nacional.empty:
                tasa_bd = df_nacional.iloc[0]['tasa_absentismo']
                tasa_adecco = ADECCO_Q4_2024['tasa_general']
                
                comparison_df = pd.DataFrame({
                    'Fuente': ['Adecco Q4 2024', 'BD INE', 'Diferencia'],
                    'Tasa (%)': [tasa_adecco, tasa_bd, round(tasa_bd - tasa_adecco, 2)]
                })
                st.dataframe(comparison_df, hide_index=True, use_container_width=True)
        
        # Tasa IT
        with col2:
            st.metric("**TASA INCAPACIDAD TEMPORAL**", "", "")
            df_it = calcular_tasa_IT_nacional(conn, periodo_seleccionado)
            
            if not df_it.empty:
                tasa_it_bd = df_it.iloc[0]['tasa_it']
                tasa_it_adecco = ADECCO_Q4_2024['tasa_it']
                
                comparison_it_df = pd.DataFrame({
                    'Fuente': ['Adecco Q4 2024', 'BD INE', 'Diferencia'],
                    'Tasa IT (%)': [tasa_it_adecco, tasa_it_bd, round(tasa_it_bd - tasa_it_adecco, 2)]
                })
                st.dataframe(comparison_it_df, hide_index=True, use_container_width=True)
        
        # Horas perdidas
        with col3:
            st.metric("**HORAS PERDIDAS/TRABAJADOR**", "", "")
            horas_adecco = ADECCO_Q4_2024['horas_perdidas']
            
            if not df_nacional.empty:
                horas_bd = df_nacional.iloc[0]['hnt_total']
                horas_anualizadas = horas_bd * 4  # Proyección anual
                
                comparison_horas_df = pd.DataFrame({
                    'Fuente': ['Adecco (anual)', 'BD (trimestre)', 'BD (anualizado)'],
                    'Horas': [horas_adecco, round(horas_bd, 2), round(horas_anualizadas, 2)]
                })
                st.dataframe(comparison_horas_df, hide_index=True, use_container_width=True)
        
        # Nota sobre diferencias
        with st.expander("ℹ️ Explicación de las diferencias"):
            st.warning("""
            **Las diferencias significativas observadas pueden deberse a:**
            
            1. **Metodología de cálculo diferente**: 
               - Adecco puede usar horas efectivas mientras nosotros usamos horas pactadas
               - Diferente tratamiento de vacaciones y festivos
            
            2. **Agregación de datos**:
               - Posible diferencia en qué componentes se incluyen en "horas no trabajadas"
               - Tratamiento distinto de jornadas parciales
            
            3. **Cobertura de datos**:
               - Adecco podría usar una muestra diferente de empresas
               - Posibles ajustes estacionales aplicados por Adecco
            
            **Siguiente paso**: Revisar la metodología exacta de Adecco y ajustar cálculos.
            """)
    
    # TAB 2: POR SECTORES
    with tab2:
        st.header("Absentismo por Sector Económico")
        
        df_sectores = calcular_absentismo_por_sector(conn, periodo_seleccionado)
        
        if not df_sectores.empty:
            # Preparar comparación
            sectores_comparison = []
            for _, row in df_sectores.iterrows():
                sector = row['sector']
                if sector in ADECCO_Q4_2024['sectores']:
                    sectores_comparison.append({
                        'Sector': sector,
                        'Tasa Adecco (%)': ADECCO_Q4_2024['sectores'][sector],
                        'Tasa BD (%)': row['tasa_absentismo'],
                        'Diferencia (%)': round(row['tasa_absentismo'] - ADECCO_Q4_2024['sectores'][sector], 2),
                        'Horas No Trabajadas': round(row['hnt_total'], 2),
                        'Horas Pactadas': round(row['hp_total'], 2)
                    })
            
            df_comp_sectores = pd.DataFrame(sectores_comparison)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Comparación de Tasas")
                st.dataframe(
                    df_comp_sectores[['Sector', 'Tasa Adecco (%)', 'Tasa BD (%)', 'Diferencia (%)']],
                    hide_index=True,
                    use_container_width=True
                )
            
            with col2:
                st.subheader("Datos Base (BD)")
                st.dataframe(
                    df_comp_sectores[['Sector', 'Horas No Trabajadas', 'Horas Pactadas']],
                    hide_index=True,
                    use_container_width=True
                )
            
            st.info("💡 Los códigos de sector en BD (B-E, F, G-S) se mapean a Industria, Construcción y Servicios respectivamente.")
    
    # TAB 3: POR CCAA
    with tab3:
        st.header("Absentismo por Comunidad Autónoma")
        
        df_ccaa = calcular_absentismo_por_ccaa(conn, periodo_seleccionado)
        
        if not df_ccaa.empty:
            # Crear diccionario de tasas Adecco
            adecco_ccaa_dict = dict(ADECCO_Q4_2024['ccaa_ranking'])
            
            # Preparar comparación
            ccaa_comparison = []
            for _, row in df_ccaa.iterrows():
                ccaa = row['ccaa_nombre']
                ccaa_comparison.append({
                    'CCAA': ccaa,
                    'Tasa BD (%)': row['tasa_absentismo'],
                    'Tasa Adecco (%)': adecco_ccaa_dict.get(ccaa, '-'),
                    'Diferencia (%)': round(row['tasa_absentismo'] - adecco_ccaa_dict.get(ccaa, row['tasa_absentismo']), 2) if ccaa in adecco_ccaa_dict else '-',
                    'Ranking BD': len(ccaa_comparison) + 1,
                    'Horas No Trabajadas': round(row['hnt_total'], 2)
                })
            
            df_comp_ccaa = pd.DataFrame(ccaa_comparison)
            
            # Mostrar top 5 y bottom 5
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔴 TOP 5 - Mayor Absentismo (BD)")
                st.dataframe(
                    df_comp_ccaa.head(5)[['CCAA', 'Tasa BD (%)', 'Tasa Adecco (%)']],
                    hide_index=True,
                    use_container_width=True
                )
            
            with col2:
                st.subheader("🟢 TOP 5 - Menor Absentismo (BD)")
                st.dataframe(
                    df_comp_ccaa.tail(5)[['CCAA', 'Tasa BD (%)', 'Tasa Adecco (%)']],
                    hide_index=True,
                    use_container_width=True
                )
            
            # Tabla completa
            with st.expander("Ver tabla completa de CCAA"):
                st.dataframe(
                    df_comp_ccaa,
                    hide_index=True,
                    use_container_width=True
                )
    
    # TAB 4: EVOLUCIÓN TEMPORAL
    with tab4:
        st.header("Evolución Trimestral 2024")
        
        df_evol = calcular_evolucion_trimestral(conn, '2024')
        
        if not df_evol.empty:
            # Preparar comparación
            evol_comparison = []
            for _, row in df_evol.iterrows():
                periodo = row['periodo']
                if periodo in ADECCO_Q4_2024['evolucion_2024']:
                    evol_comparison.append({
                        'Periodo': periodo,
                        'Tasa Adecco (%)': ADECCO_Q4_2024['evolucion_2024'][periodo],
                        'Tasa BD (%)': row['tasa_absentismo'],
                        'Diferencia (%)': round(row['tasa_absentismo'] - ADECCO_Q4_2024['evolucion_2024'][periodo], 2),
                        'Horas No Trabajadas': round(row['hnt_total'], 2),
                        'Horas Pactadas': round(row['hp_total'], 2)
                    })
            
            df_comp_evol = pd.DataFrame(evol_comparison)
            
            st.dataframe(
                df_comp_evol,
                hide_index=True,
                use_container_width=True
            )
            
            # Mostrar tendencia
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Tendencia Adecco")
                st.dataframe(
                    pd.DataFrame({
                        'Trimestre': ['T1', 'T2', 'T3', 'T4'],
                        'Tasa (%)': [7.2, 6.7, 6.9, 7.4],
                        'Variación': ['-', '-0.5', '+0.2', '+0.5']
                    }),
                    hide_index=True
                )
            
            with col2:
                st.subheader("📊 Tendencia BD")
                if len(df_comp_evol) > 1:
                    variaciones = ['-']
                    for i in range(1, len(df_comp_evol)):
                        var = round(df_comp_evol.iloc[i]['Tasa BD (%)'] - df_comp_evol.iloc[i-1]['Tasa BD (%)'], 2)
                        variaciones.append(f"{var:+.2f}" if var != 0 else "0.00")
                    
                    st.dataframe(
                        pd.DataFrame({
                            'Trimestre': ['T1', 'T2', 'T3', 'T4'][:len(df_comp_evol)],
                            'Tasa (%)': df_comp_evol['Tasa BD (%)'].tolist(),
                            'Variación': variaciones
                        }),
                        hide_index=True
                    )
    
    # TAB 5: DESGLOSE CAUSAS
    with tab5:
        st.header("Desglose por Causas de Absentismo")
        
        df_causas = calcular_causas_absentismo(conn, periodo_seleccionado)
        
        if not df_causas.empty:
            # Separar total del resto
            df_total = df_causas[df_causas['tipo_causa'] == 'TOTAL GENERAL']
            df_detalle = df_causas[df_causas['tipo_causa'] != 'TOTAL GENERAL']
            
            # Mostrar total
            if not df_total.empty:
                st.subheader("📊 Total General")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tasa Total (%)", f"{df_total.iloc[0]['tasa_causa']:.2f}%")
                with col2:
                    st.metric("Horas Totales", f"{df_total.iloc[0]['horas_causa']:.2f}")
                with col3:
                    st.metric("Referencia Adecco", "7.4%")
            
            # Mostrar desglose
            st.subheader("📋 Desglose por Tipo de Causa")
            
            # Agregar referencia Adecco donde existe
            df_detalle_display = df_detalle.copy()
            df_detalle_display['Tasa Adecco (%)'] = df_detalle_display['tipo_causa'].apply(
                lambda x: 5.8 if x == 'Incapacidad Temporal (IT)' else '-'
            )
            
            st.dataframe(
                df_detalle_display[['tipo_causa', 'tasa_causa', 'Tasa Adecco (%)', 'horas_causa']].rename(columns={
                    'tipo_causa': 'Causa',
                    'tasa_causa': 'Tasa BD (%)',
                    'horas_causa': 'Horas'
                }),
                hide_index=True,
                use_container_width=True
            )
            
            # Comparación específica IT
            it_row = df_detalle[df_detalle['tipo_causa'] == 'Incapacidad Temporal (IT)']
            if not it_row.empty:
                st.info(f"""
                **Comparación Incapacidad Temporal:**
                - Adecco: 5.8% (referencia Q4 2024)
                - BD: {it_row.iloc[0]['tasa_causa']:.2f}%
                - Diferencia: {(it_row.iloc[0]['tasa_causa'] - 5.8):.2f}%
                """)
    
    # TAB 6: ANÁLISIS DETALLADO
    with tab6:
        st.header("Análisis Detallado y Metodología")
        
        st.subheader("🔍 Análisis de Discrepancias")
        
        st.markdown("""
        ### Principales diferencias encontradas:
        
        1. **Tasa General de Absentismo**
           - Las tasas calculadas desde BD son consistentemente más altas
           - Posible causa: Diferente definición de "horas pactadas efectivas"
        
        2. **Incapacidad Temporal**
           - La tasa IT en BD es menor que la reportada por Adecco
           - Puede indicar diferente categorización de ausencias médicas
        
        3. **Variabilidad por CCAA**
           - Rankings diferentes entre BD y Adecco
           - Sugiere diferencias en muestras o metodología de agregación
        
        ### Posibles explicaciones técnicas:
        
        - **Fórmula de cálculo**: BD usa `(HNT / HP) * 100`
        - **Adecco podría usar**: `(HNT / (HP - Vacaciones - Festivos)) * 100`
        - **Ajustes estacionales**: Adecco puede aplicar correcciones que no aplicamos
        - **Cobertura muestral**: Diferencias en empresas incluidas
        """)
        
        st.subheader("📊 Datos de Validación")
        
        # Query para mostrar datos raw de validación
        query_validation = """
            SELECT 
                metrica,
                COUNT(*) as registros,
                COUNT(DISTINCT causa) as num_causas,
                ROUND(SUM(valor), 2) as suma_valores
            FROM observaciones_tiempo_trabajo
            WHERE periodo = '2024T4'
                AND ambito_territorial = 'NAC'
                AND cnae_nivel = 'TOTAL'
                AND es_total_jornada = true
            GROUP BY metrica
            ORDER BY metrica
        """
        
        df_validation = conn.execute(query_validation).df()
        
        st.dataframe(
            df_validation,
            hide_index=True,
            use_container_width=True
        )
        
        st.subheader("💡 Recomendaciones")
        
        st.success("""
        **Para mejorar la comparabilidad con Adecco:**
        
        1. ✅ Obtener documento metodológico completo de Adecco
        2. ✅ Revisar definición exacta de "horas pactadas efectivas"
        3. ✅ Verificar si excluyen vacaciones/festivos del denominador
        4. ✅ Analizar posibles ajustes estacionales aplicados
        5. ✅ Considerar implementar filtros adicionales por tipo de empresa
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>
        Datos BD: INE - Encuesta Trimestral de Coste Laboral (ETCL) | 
        Referencia: Informe Adecco Q4 2024 | 
        Procesamiento: Agent Processor v1.0
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()