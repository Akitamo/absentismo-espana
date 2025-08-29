"""
Dashboard de Absentismo Laboral España
Versión moderna con diseño actualizado
Datos: INE-ETCL (2008-2025)
"""

import streamlit as st
import sys
from pathlib import Path

# Añadir path para imports
sys.path.append(str(Path(__file__).parent))

# Imports locales
from pages import dashboard
from design.theme import apply_theme

# ===============================
# CONFIGURACIÓN INICIAL
# ===============================

st.set_page_config(
    page_title="Absentismo Laboral España",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Dashboard de análisis de absentismo laboral basado en datos INE-ETCL"
    }
)

# ===============================
# APLICACIÓN PRINCIPAL
# ===============================

def main():
    """Función principal de la aplicación"""
    
    # Aplicar tema personalizado
    apply_theme()
    
    # Sidebar para navegación
    with st.sidebar:
        # Logo y título
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0 2rem 0;'>
                <h1 style='color: white; font-size: 1.8rem; margin: 0; font-weight: 700;'>
                    ABSENTISMO
                </h1>
                <p style='color: rgba(255,255,255,0.6); font-size: 0.875rem; margin: 0.5rem 0 0 0;'>
                    Panel de Control
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Navegación principal con iconos mejorados
        st.markdown("<p style='color: rgba(255,255,255,0.5); font-size: 0.75rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px;'>MENÚ PRINCIPAL</p>", unsafe_allow_html=True)
        
        page = st.radio(
            "nav",
            [
                "📊 Dashboard",
                "📈 Análisis",
                "👥 Comparativas", 
                "📥 Exportar"
            ],
            label_visibility="collapsed",
            key="navigation"
        )
        
        # Separador
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # Sección de información
        st.markdown("<p style='color: rgba(255,255,255,0.5); font-size: 0.75rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px;'>INFORMACIÓN</p>", unsafe_allow_html=True)
        
        # Info boxes
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div style='background: rgba(255,255,255,0.05); padding: 0.75rem; border-radius: 8px;'>
                    <p style='color: rgba(255,255,255,0.5); font-size: 0.7rem; margin: 0;'>FUENTE</p>
                    <p style='color: white; font-size: 0.875rem; margin: 0; font-weight: 600;'>INE-ETCL</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div style='background: rgba(255,255,255,0.05); padding: 0.75rem; border-radius: 8px;'>
                    <p style='color: rgba(255,255,255,0.5); font-size: 0.7rem; margin: 0;'>ACTUALIZADO</p>
                    <p style='color: white; font-size: 0.875rem; margin: 0; font-weight: 600;'>Q1 2025</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Espacio al final
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Router de páginas
    if "Dashboard" in page:
        dashboard.show()
    elif "Análisis" in page:
        st.info("📈 Página de análisis detallado en desarrollo...")
        st.markdown("Esta sección incluirá:")
        st.markdown("- Análisis por CCAA")
        st.markdown("- Análisis por sectores CNAE")
        st.markdown("- Comparativas temporales")
        st.markdown("- Tendencias y proyecciones")
    elif "Comparativas" in page:
        st.info("👥 Página de comparativas en desarrollo...")
        st.markdown("Esta sección permitirá:")
        st.markdown("- Comparar entre CCAA")
        st.markdown("- Comparar entre sectores")
        st.markdown("- Comparar periodos")
        st.markdown("- Benchmarking")
    elif "Exportar" in page:
        st.info("📥 Página de exportación en desarrollo...")
        st.markdown("Esta sección permitirá:")
        st.markdown("- Exportar a Excel")
        st.markdown("- Exportar a CSV")
        st.markdown("- Generar informes PDF")
        st.markdown("- Descargar gráficos")

if __name__ == "__main__":
    main()