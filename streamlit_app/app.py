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
from views import dashboard
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
    
    # Inicializar estado de la página si no existe
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    
    # Sidebar para navegación
    with st.sidebar:
        # CSS para ocultar elementos nativos y personalizar navegación
        st.markdown("""
            <style>
                /* Ocultar navegación de páginas nativa de Streamlit */
                [data-testid="stSidebarNav"] {display: none;}
                
                /* Ajustar padding superior del sidebar */
                section[data-testid="stSidebar"] > div:first-child {
                    padding-top: 0 !important;
                }
                
                /* Ajustar contenedor del sidebar */
                section[data-testid="stSidebar"] .block-container {
                    padding-top: 0.5rem !important;
                    padding-left: 1.5rem !important;
                    padding-right: 1.5rem !important;
                }
                
                /* Forzar alineación izquierda de TODOS los elementos del sidebar */
                section[data-testid="stSidebar"] [data-testid="column"] {
                    padding: 0 !important;
                }
                
                section[data-testid="stSidebar"] .element-container {
                    width: 100% !important;
                    padding: 0 !important;
                }
                
                /* Eliminar bordes de botones en sidebar y alinear izquierda */
                section[data-testid="stSidebar"] .stButton {
                    width: 100% !important;
                }
                
                section[data-testid="stSidebar"] .stButton > button {
                    border: none !important;
                    background: transparent !important;
                    box-shadow: none !important;
                    padding: 0.625rem 1rem !important;
                    margin: 0 0 0.25rem 0 !important;
                    width: 100% !important;
                    text-align: left !important;
                    justify-content: flex-start !important;
                    border-radius: 8px !important;
                    transition: all 0.2s ease !important;
                    color: #696974 !important;
                    font-size: 0.875rem !important;
                    font-weight: 400 !important;
                    display: flex !important;
                    align-items: center !important;
                    height: 2.5rem !important;
                }
                
                section[data-testid="stSidebar"] .stButton > button:hover {
                    background: rgba(27, 89, 248, 0.05) !important;
                    color: #1B59F8 !important;
                }
                
                /* Eliminar columnas innecesarias y centrado */
                section[data-testid="stSidebar"] .row-widget.stHorizontal {
                    gap: 0 !important;
                }
                
                section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
                    gap: 0 !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Logo Ibermutua al principio
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0 2rem 0; margin-top: -3.5rem;'>
                <div style='font-size: 2.2rem; font-weight: 400; color: #0066CC; font-family: Arial, sans-serif;'>
                    Ibermu<span style='color: #00AAFF;'>tua</span>
                </div>
                <p style='color: #696974; font-size: 0.75rem; margin: 0.5rem 0 0 0; text-transform: uppercase; letter-spacing: 1px;'>
                    Absentismo Laboral
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Crear enlaces de navegación
        menu_items = [
            ('📊 Dashboard', 'Dashboard'),
            ('📈 Análisis', 'Análisis'),
            ('👥 Comparativas', 'Comparativas'),
            ('📥 Exportar', 'Exportar')
        ]
        
        # CSS adicional para radio buttons uniformes
        st.markdown("""
            <style>
                /* Hacer que todos los radio buttons tengan el mismo espaciado */
                section[data-testid="stSidebar"] .stRadio > div {
                    gap: 0.25rem !important;
                }
                
                section[data-testid="stSidebar"] .stRadio label {
                    background: transparent !important;
                    color: var(--text-secondary) !important;
                    padding: 0.625rem 1rem !important;
                    margin: 0 !important;
                    border-radius: var(--radius-md) !important;
                    transition: all 0.2s ease !important;
                    font-size: var(--font-size-sm) !important;
                    font-weight: var(--font-weight-regular) !important;
                    min-height: 2.5rem !important;
                    display: flex !important;
                    align-items: center !important;
                }
                
                section[data-testid="stSidebar"] .stRadio label:hover {
                    background-color: var(--color-sidebar-hover) !important;
                    color: var(--color-primary) !important;
                }
                
                /* Estilo para opción seleccionada */
                section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label,
                section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
                    background-color: rgba(27, 89, 248, 0.05) !important;
                    color: #1B59F8 !important;
                    font-weight: 600 !important;
                }
                
                /* Alternativa para elemento activo */
                section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div[role="radiogroup"] label:has(input:checked) {
                    background-color: rgba(27, 89, 248, 0.05) !important;
                    color: #1B59F8 !important;
                    font-weight: 600 !important;
                }
                
                /* Forzar estilo en el div que contiene el input checked */
                section[data-testid="stSidebar"] .stRadio > div > label:nth-child(1):has(input:checked),
                section[data-testid="stSidebar"] .stRadio > div > label:nth-child(2):has(input:checked),
                section[data-testid="stSidebar"] .stRadio > div > label:nth-child(3):has(input:checked),
                section[data-testid="stSidebar"] .stRadio > div > label:nth-child(4):has(input:checked) {
                    background-color: rgba(27, 89, 248, 0.05) !important;
                    color: #1B59F8 !important;
                    font-weight: 600 !important;
                }
                
                /* Ocultar círculos de radio */
                section[data-testid="stSidebar"] .stRadio input[type="radio"] {
                    display: none !important;
                }
                
                section[data-testid="stSidebar"] .stRadio label > div:first-child {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Radio button para navegación
        selected = st.radio(
            "nav",
            options=[item[1] for item in menu_items],
            format_func=lambda x: next(item[0] for item in menu_items if item[1] == x),
            index=[item[1] for item in menu_items].index(st.session_state.current_page),
            label_visibility="collapsed",
            key="navigation_radio"
        )
        
        # CSS para el elemento seleccionado (solo color y fondo)
        selected_index = [item[1] for item in menu_items].index(st.session_state.current_page) + 1
        st.markdown(f"""
            <style>
                /* Estilo para elemento seleccionado */
                section[data-testid="stSidebar"] .stRadio > div > label:nth-child({selected_index}) {{
                    background-color: var(--color-sidebar-hover) !important;
                    color: var(--color-primary) !important;
                }}
            </style>
        """, unsafe_allow_html=True)
        
        if selected != st.session_state.current_page:
            st.session_state.current_page = selected
            st.rerun()
        
        # Obtener página actual
        page = st.session_state.current_page
        
        # Separador
        st.markdown("<hr style='border: none; border-top: 1px solid #EFF0F6; margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # Sección de información
        st.markdown("<p style='color: #696974; font-size: 0.75rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;'>INFORMACIÓN</p>", unsafe_allow_html=True)
        
        # Info boxes
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div style='background: #F9F9F9; padding: 0.75rem; border-radius: 8px; border: 1px solid #EFF0F6;'>
                    <p style='color: #696974; font-size: 0.7rem; margin: 0;'>FUENTE</p>
                    <p style='color: #000000; font-size: 0.875rem; margin: 0; font-weight: 600;'>INE-ETCL</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div style='background: #F9F9F9; padding: 0.75rem; border-radius: 8px; border: 1px solid #EFF0F6;'>
                    <p style='color: #696974; font-size: 0.7rem; margin: 0;'>ACTUALIZADO</p>
                    <p style='color: #000000; font-size: 0.875rem; margin: 0; font-weight: 600;'>Q1 2025</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Separador para sección Support
        st.markdown("<hr style='border: none; border-top: 1px solid #EFF0F6; margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # Sección Support
        st.markdown("<p style='color: #696974; font-size: 0.75rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;'>SOPORTE</p>", unsafe_allow_html=True)
        
        # Support links
        st.markdown("""
            <div style='padding: 0.5rem 0;'>
                <a href='#' style='display: flex; align-items: center; padding: 0.5rem 1rem; color: #696974; text-decoration: none; border-radius: 8px; transition: all 0.2s; font-size: 0.875rem;' 
                   onmouseover="this.style.backgroundColor='rgba(27,89,248,0.05)'; this.style.color='#1B59F8';" 
                   onmouseout="this.style.backgroundColor='transparent'; this.style.color='#696974';">
                    📚 Empezar
                </a>
                <a href='#' style='display: flex; align-items: center; padding: 0.5rem 1rem; color: #696974; text-decoration: none; border-radius: 8px; transition: all 0.2s; font-size: 0.875rem;' 
                   onmouseover="this.style.backgroundColor='rgba(27,89,248,0.05)'; this.style.color='#1B59F8';" 
                   onmouseout="this.style.backgroundColor='transparent'; this.style.color='#696974';">
                    ⚙️ Configuración
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        # Separador final
        st.markdown("<hr style='border: none; border-top: 1px solid #EFF0F6; margin: 2rem 0 1rem 0;'>", unsafe_allow_html=True)
        
        # Perfil de usuario
        st.markdown("""
            <div style='display: flex; align-items: center; padding: 0.75rem 1rem; background: #F9F9F9; border-radius: 8px; margin-bottom: 1rem;'>
                <div style='width: 36px; height: 36px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; margin-right: 0.75rem;'></div>
                <div>
                    <p style='margin: 0; color: #000000; font-size: 0.875rem; font-weight: 600;'>Analista</p>
                    <p style='margin: 0; color: #696974; font-size: 0.75rem;'>analista@ibermutua.es</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Router de páginas
    if page == "Dashboard":
        dashboard.show()
    elif page == "Análisis":
        st.info("📈 Página de análisis detallado en desarrollo...")
        st.markdown("Esta sección incluirá:")
        st.markdown("- Análisis por CCAA")
        st.markdown("- Análisis por sectores CNAE")
        st.markdown("- Comparativas temporales")
        st.markdown("- Tendencias y proyecciones")
    elif page == "Comparativas":
        st.info("👥 Página de comparativas en desarrollo...")
        st.markdown("Esta sección permitirá:")
        st.markdown("- Comparar entre CCAA")
        st.markdown("- Comparar entre sectores")
        st.markdown("- Comparar periodos")
        st.markdown("- Benchmarking")
    elif page == "Exportar":
        st.info("📥 Página de exportación en desarrollo...")
        st.markdown("Esta sección permitirá:")
        st.markdown("- Exportar a Excel")
        st.markdown("- Exportar a CSV")
        st.markdown("- Generar informes PDF")
        st.markdown("- Descargar gráficos")

if __name__ == "__main__":
    main()