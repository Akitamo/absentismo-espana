"""
Aplicador de tema basado en design tokens
Usa los valores definidos en tokens.json
"""

import streamlit as st
import json
from pathlib import Path

def load_tokens():
    """Carga los design tokens desde el archivo JSON"""
    tokens_path = Path(__file__).parent / "tokens.json"
    with open(tokens_path, 'r') as f:
        return json.load(f)

def generate_css_from_tokens(tokens):
    """Genera CSS dinámicamente desde los tokens"""
    
    css = f"""
    /* ===== FUENTES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* ===== VARIABLES CSS DESDE TOKENS ===== */
    :root {{
        /* Colores */
        --color-primary: {tokens['colors']['primary']};
        --color-primary-hover: {tokens['colors']['primary_hover']};
        --color-background: {tokens['colors']['background']};
        --color-surface: {tokens['colors']['surface']};
        --color-border: {tokens['colors']['border']};
        --color-border-light: {tokens['colors']['border_light']};
        
        /* Texto */
        --text-primary: {tokens['colors']['text']['primary']};
        --text-secondary: {tokens['colors']['text']['secondary']};
        --text-muted: {tokens['colors']['text']['muted']};
        --text-subtle: {tokens['colors']['text']['subtle']};
        
        /* Status */
        --color-success: {tokens['colors']['status']['success']};
        --color-danger: {tokens['colors']['status']['danger']};
        --color-warning: {tokens['colors']['status']['warning']};
        --color-info: {tokens['colors']['status']['info']};
        
        /* Tipografía */
        --font-family: {tokens['typography']['fontFamily']};
        --font-size-xs: {tokens['typography']['fontSize']['xs']};
        --font-size-sm: {tokens['typography']['fontSize']['sm']};
        --font-size-base: {tokens['typography']['fontSize']['base']};
        --font-size-lg: {tokens['typography']['fontSize']['lg']};
        --font-size-xl: {tokens['typography']['fontSize']['xl']};
        --font-size-2xl: {tokens['typography']['fontSize']['2xl']};
        --font-size-3xl: {tokens['typography']['fontSize']['3xl']};
        
        /* Pesos de fuente */
        --font-weight-regular: {tokens['typography']['fontWeight']['regular']};
        --font-weight-medium: {tokens['typography']['fontWeight']['medium']};
        --font-weight-semibold: {tokens['typography']['fontWeight']['semibold']};
        --font-weight-bold: {tokens['typography']['fontWeight']['bold']};
        
        /* Espaciado */
        --spacing-xs: {tokens['spacing']['xs']};
        --spacing-sm: {tokens['spacing']['sm']};
        --spacing-md: {tokens['spacing']['md']};
        --spacing-lg: {tokens['spacing']['lg']};
        --spacing-xl: {tokens['spacing']['xl']};
        --spacing-2xl: {tokens['spacing']['2xl']};
        
        /* Bordes */
        --radius-sm: {tokens['borders']['radius']['sm']};
        --radius-md: {tokens['borders']['radius']['md']};
        --radius-lg: {tokens['borders']['radius']['lg']};
        --radius-xl: {tokens['borders']['radius']['xl']};
        
        /* Sombras */
        --shadow-sm: {tokens['shadows']['sm']};
        --shadow-md: {tokens['shadows']['md']};
        --shadow-lg: {tokens['shadows']['lg']};
        --shadow-xl: {tokens['shadows']['xl']};
    }}
    
    /* ===== APLICACIÓN DE TOKENS ===== */
    
    /* Base */
    html, body, [class*="css"] {{
        font-family: var(--font-family) !important;
    }}
    
    /* Fondo principal */
    .stApp {{
        background-color: var(--color-background);
    }}
    
    /* Container principal */
    .main .block-container {{
        max-width: {tokens['layout']['contentWidth']};
        padding: var(--spacing-xl) var(--spacing-2xl);
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {tokens['colors']['sidebar_bg']} 0%, #0F1114 100%);
        width: {tokens['layout']['sidebarWidth']} !important;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    }}
    
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 2rem;
    }}
    
    /* Sidebar text color */
    section[data-testid="stSidebar"] .stMarkdown {{
        color: white !important;
    }}
    
    section[data-testid="stSidebar"] h2 {{
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
        margin-bottom: 2rem !important;
    }}
    
    /* Sidebar radio buttons */
    section[data-testid="stSidebar"] .stRadio > label {{
        color: white !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    section[data-testid="stSidebar"] .stRadio > div {{
        gap: 0.5rem;
    }}
    
    section[data-testid="stSidebar"] .stRadio label {{
        color: rgba(255, 255, 255, 0.85) !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }}
    
    section[data-testid="stSidebar"] .stRadio label:hover {{
        background-color: {tokens['colors']['sidebar_hover']} !important;
        color: white !important;
    }}
    
    section[data-testid="stSidebar"] .stRadio label[data-selected="true"] {{
        background-color: {tokens['colors']['primary']} !important;
        color: white !important;
    }}
    
    /* Sidebar captions */
    section[data-testid="stSidebar"] .stCaption {{
        color: rgba(255, 255, 255, 0.5) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Sidebar separator */
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 1.5rem 0 !important;
    }}
    
    /* Headers */
    h1 {{
        color: var(--text-primary);
        font-weight: var(--font-weight-semibold);
        font-size: var(--font-size-2xl);
    }}
    
    h3 {{
        color: var(--text-primary);
        font-weight: var(--font-weight-semibold);
        font-size: var(--font-size-lg);
        margin-top: var(--spacing-xl);
    }}
    
    /* KPI Cards (Metrics) */
    div[data-testid="metric-container"] {{
        background-color: var(--color-surface);
        padding: var(--spacing-lg);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-xl);
        border: 1px solid var(--color-border);
        transition: all 0.3s ease;
    }}
    
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }}
    
    /* Metric labels */
    div[data-testid="metric-container"] label {{
        color: var(--text-secondary);
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-medium);
    }}
    
    /* Metric values */
    div[data-testid="metric-container"] [data-testid="metric-value"] {{
        color: var(--text-primary);
        font-size: var(--font-size-2xl);
        font-weight: var(--font-weight-bold);
    }}
    
    /* Selectboxes */
    .stSelectbox label {{
        color: var(--text-secondary);
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-medium);
    }}
    
    .stSelectbox > div > div {{
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: var(--color-primary);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: var(--spacing-sm) var(--spacing-lg);
        font-weight: var(--font-weight-medium);
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }}
    
    .stButton > button:hover {{
        background-color: var(--color-primary-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }}
    
    /* Dividers */
    hr {{
        border: none;
        border-top: 1px solid var(--color-border-light);
        margin: var(--spacing-xl) 0;
    }}
    
    /* Dataframes */
    .stDataFrame {{
        background-color: var(--color-surface);
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }}
    
    /* Plotly charts container */
    .js-plotly-plot {{
        border-radius: var(--radius-lg);
        overflow: hidden;
    }}
    
    /* Column gaps */
    .row-widget.stHorizontal {{
        gap: var(--spacing-lg);
    }}
    """
    
    return css

def apply_theme():
    """Aplica el tema personalizado a la aplicación"""
    tokens = load_tokens()
    css = generate_css_from_tokens(tokens)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)