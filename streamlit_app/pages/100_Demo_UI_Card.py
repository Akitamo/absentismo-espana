from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from components.ui_card import metric_card, plotly_card, table_card

st.set_page_config(page_title="Demo UI Card", layout="wide")

st.markdown("## Demo UI Card (component)")

# KPIs
c1,c2,c3,c4 = st.columns(4)
with c1: metric_card("Total Contacts", "0", "+12% vs last month", "👤", height=140, key="m1")
with c2: metric_card("Active Leads", "0", "+8% vs last month", "🟢", height=140, key="m2")
with c3: metric_card("Pipeline Value", "$0", "+23% vs last month", "💲", height=140, key="m3")
with c4: metric_card("Qualified Leads", "0", "-5% vs last month", "🏷️", height=140, key="m4")

# Tabla simple (HTML)
html = """
<table style="width:100%;border-collapse:collapse">
  <thead><tr><th style="text-align:left;padding:6px">CCAA</th><th style="text-align:right;padding:6px">Tasa</th></tr></thead>
  <tbody>
    <tr><td style="padding:6px">Madrid</td><td style="text-align:right;padding:6px">7.1%</td></tr>
    <tr><td style="padding:6px">Cataluña</td><td style="text-align:right;padding:6px">7.6%</td></tr>
  </tbody>
</table>
"""
t1, t2 = st.columns([2,2])
with t1:
    table_card("Recent Contacts", html, height=160, key="t1")
with t2:
    table_card("Lead Pipeline", "<div style='padding:6px;color:#6b7280'>No leads available</div>", height=160, key="t2")

# Gráfico Plotly
periodos = pd.date_range('2020-01', '2024-01', freq='Q')
df = pd.DataFrame({
    "periodo": periodos,
    "tasa": np.random.uniform(10, 15, len(periodos)) + np.sin(np.arange(len(periodos)) * 0.5) * 2
})
fig = go.Figure()
fig.add_scatter(x=df["periodo"], y=df["tasa"], mode="lines")  # el componente aplica color/fill
fig.update_layout(showlegend=False)
plotly_card("📊 Evolución temporal", "Tasa de absentismo trimestral", fig_json=fig.to_json(), height=420, key="plot1")