# streamlit_app/pages/99_Demo_CRM.py
# --- Demo CRM-like con fix de overflow para que se vea la sombra ---

from __future__ import annotations
from pathlib import Path
import sys

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from contextlib import contextmanager

# --------------------------------- CONFIG ---------------------------------
st.set_page_config(page_title="Demo CRM", page_icon="📊", layout="wide")

# --------------------------------- CSS SKIN --------------------------------
# Notas importantes:
# 1) Forzamos overflow visible en wrappers de Streamlit para que la sombra no se recorte.
# 2) Selector robusto para distintas versiones (testid y style inline).
# 3) Sombra triple + ring interno + borde sutil + fondo gris suave.

st.markdown("""
<style>
:root{
  --crm-bg: #EEF1F6;                     /* un poco más oscuro para mayor contraste */
  --crm-surface: #FFFFFF;
  --crm-border: rgba(15, 23, 42, 0.05);  /* borde muy sutil */
  --crm-radius: 14px;                    /* 14–16 para look CRM */
  --crm-text: #111827;
  --crm-text-muted: #6B7280;
  --crm-primary: #1B59F8;
  --crm-gap: 16px;

  /* capas de sombra */
  --crm-shadow-1: 0 1px 2px rgba(16,24,40,0.06);
  --crm-shadow-2: 0 10px 24px rgba(16,24,40,0.10);
  --crm-shadow-3: 0 18px 50px rgba(16,24,40,0.08);
}

.stApp { background-color: var(--crm-bg) !important; }

/* Contenedor principal centrado (~1180px) */
.main .block-container{
  max-width: 1180px;
  padding-top: 24px;
  padding-bottom: 48px;
  overflow: visible !important; /* <-- que no recorte sombras */
}

/* Varios wrappers internos de Streamlit a veces ponen overflow hidden */
.block-container, [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"]{
  overflow: visible !important; /* <-- clave para ver la sombra fuera del borde */
}

/* ================== PIEL DE CARD (robusta a cambios) ==================
   Cubre:
   1) st.container(border=True) con testid
   2) wrappers con border inline
   3) wrappers dentro de columnas
*/
.stContainer > div[data-testid="stVerticalBlockBorderWrapper"],
div[style*="border: 1px solid"][style*="border-radius"],
[data-testid="column"] div[style*="border: 1px solid"]{
  background: var(--crm-surface) !important;
  border: 1px solid var(--crm-border) !important;
  border-radius: var(--crm-radius) !important;

  /* Ring interior + sombras (3 capas) */
  box-shadow:
    inset 0 0 0 1px rgba(255,255,255,0.85),
    var(--crm-shadow-1),
    var(--crm-shadow-2),
    var(--crm-shadow-3) !important;

  padding: 20px !important;
  margin-bottom: 18px !important;
  transition: box-shadow .18s ease, transform .18s ease, filter .18s ease;
  /* permitir que la sombra se vea sin recortes del propio card */
  overflow: visible !important;
}

.stContainer > div[data-testid="stVerticalBlockBorderWrapper"]:hover,
div[style*="border: 1px solid"][style*="border-radius"]:hover,
[data-testid="column"] div[style*="border: 1px solid"]:hover{
  box-shadow:
    inset 0 0 0 1px rgba(255,255,255,0.92),
    0 2px 4px rgba(16,24,40,0.10),
    0 14px 30px rgba(16,24,40,0.12),
    0 22px 60px rgba(16,24,40,0.10) !important;
  transform: translate3d(0,-1px,0);
}

/* Tipografía base */
.stMarkdown, .stText, .stCaption, .stDataFrame, .stPlotlyChart { color: var(--crm-text); }
.stCaption{ color: var(--crm-text-muted) !important; }

/* Título dentro de card */
.stContainer h3 { font-size: 18px; font-weight: 700; margin: 0 0 6px 0; color: var(--crm-text); }

/* Gutters entre columnas */
[data-testid="column"] > div { padding-right: var(--crm-gap); }
[data-testid="stHorizontalBlock"] > div:last-child > div { padding-right: 0; }

/* Quick Action */
.crm-qa{
  border: 1px dashed rgba(16,24,40,0.14);
  border-radius: 12px;
  text-align: center;
  padding: 18px;
  color: var(--crm-text-muted);
  background: rgba(16,24,40,0.03);
}

/* Pastilla de icono en KPI */
.kpi-pill{
  width:36px;height:36px;border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  background: rgba(27,89,248,0.12); color: var(--crm-primary);
  font-size:18px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------ HELPERS UI --------------------------------
@contextmanager
def card(title: str | None = None, subtitle: str | None = None, icon: str | None = None):
    """Card estándar basado en contenedor nativo (sin HTML envolvente)."""
    c = st.container(border=True)
    with c:
        if title or subtitle or icon:
            cols = st.columns([1, 12]) if icon else None
            if icon:
                with cols[0]:
                    st.markdown('<div class="kpi-pill">{}</div>'.format(icon), unsafe_allow_html=True)
                with cols[1]:
                    if title: st.markdown(f"**{title}**")
                    if subtitle: st.caption(subtitle)
            else:
                if title: st.markdown(f"**{title}**")
                if subtitle: st.caption(subtitle)
        yield

def figure_plotly(fig, *, modebar: bool = False):
    cfg = {'displayModeBar': modebar}
    st.plotly_chart(fig, use_container_width=True, config=cfg)

def kpi_card(title:str, icon:str, delta:str, value:str):
    cols = st.columns([1, 7, 4])
    with cols[0]:
        st.markdown('<div class="kpi-pill">{}</div>'.format(icon), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div style='font-weight:600'>{title}</div>", unsafe_allow_html=True)
        st.caption(delta)
    with cols[2]:
        pass
    st.markdown(f"<div style='font-size:28px;font-weight:700;margin-top:8px'>{value}</div>",
                unsafe_allow_html=True)

def quick_action(label: str):
    st.markdown(f"<div class='crm-qa'>{label}</div>", unsafe_allow_html=True)

# ------------------------------ LAYOUT DEMO -------------------------------
st.markdown("## Dashboard")

# KPIs (4)
k1,k2,k3,k4 = st.columns(4)
with k1:
    with card(): kpi_card("Total Contacts","👤","+12% vs last month","0")
with k2:
    with card(): kpi_card("Active Leads","🟢","+8% vs last month","0")
with k3:
    with card(): kpi_card("Pipeline Value","💲","+23% vs last month","$0")
with k4:
    with card(): kpi_card("Qualified Leads","🏷️","-5% vs last month","0")

# Paneles
c1, c2 = st.columns([2,2])
with c1:
    with card("Recent Contacts"):
        st.info("No contacts available")
with c2:
    with card("Lead Pipeline"):
        st.info("No leads available")

# Quick Actions
with card("Quick Actions"):
    a,b,c = st.columns(3)
    with a: quick_action("Add Contact")
    with b: quick_action("Add Lead")
    with c: quick_action("Add Opportunity")

# Chart en card
with card("📊 Evolución temporal", "Tasa de absentismo trimestral"):
    periodos = pd.date_range('2020-01', '2024-01', freq='Q')
    df = pd.DataFrame({
        "periodo": periodos,
        "tasa": np.random.uniform(10, 15, len(periodos)) + np.sin(np.arange(len(periodos)) * 0.5) * 2
    })
    fig = go.Figure()
    fig.add_scatter(x=df["periodo"], y=df["tasa"], mode="lines")
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0))
    figure_plotly(fig)


