from dash import html, dcc, dash_table, register_page, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

from src.core.data_service import DataService

register_page(__name__, path="/")

ds = DataService()

def kpi_card(title: str, value: str, subtitle: str | None = None):
    return html.Div([
        html.Div(title, className="kpi-title"),
        html.Div(value, className="kpi-value"),
        html.Div(subtitle or "", className="kpi-subtitle"),
    ], className="kpi-card")


def layout():
    try:
        periods = ds.get_available_periods()
    except Exception:
        periods = ["2024T4", "2024T3", "2024T2", "2024T1"]

    try:
        ccaa_list = ["Total Nacional"] + ds.get_ccaa_list()
    except Exception:
        ccaa_list = ["Total Nacional"]

    try:
        sectors = ["Todos"] + ds.get_sectors_list()
    except Exception:
        sectors = ["Todos"]

    return html.Div([
        html.Div([
            html.Div([
                html.Label("Periodo"),
                dcc.Dropdown(id="f-periodo", options=periods, value=periods[0] if periods else None, clearable=False),
            ], className="filter"),
            html.Div([
                html.Label("Comunidad Autónoma"),
                dcc.Dropdown(id="f-ccaa", options=ccaa_list, value=ccaa_list[0] if ccaa_list else None, clearable=False),
            ], className="filter"),
            html.Div([
                html.Label("Sector"),
                dcc.Dropdown(id="f-sector", options=sectors, value=sectors[0] if sectors else None, clearable=False),
            ], className="filter"),
        ], className="filters"),

        html.Div(id="kpis", className="kpis"),

        html.Div([
            dcc.Graph(id="evolucion"),
            dash_table.DataTable(id="ranking-table", page_size=10, style_table={"overflowX": "auto"})
        ], className="main")
    ], className="page")


@callback(
    Output("kpis", "children"),
    Output("evolucion", "figure"),
    Output("ranking-table", "data"),
    Output("ranking-table", "columns"),
    Input("f-periodo", "value"),
    Input("f-ccaa", "value"),
    Input("f-sector", "value"),
)
def update_dashboard(periodo, ccaa, sector):
    # KPIs
    kpis = ds.get_kpis(periodo or "2024T4", ccaa or "Total Nacional", sector or "Todos")
    kpi_children = html.Div([
        kpi_card("Tasa Absentismo", f"{kpis.get('tasa_absentismo', 0):.1f}%"),
        kpi_card("Tasa IT", f"{kpis.get('tasa_it', 0):.1f}%"),
        kpi_card("HPE", f"{kpis.get('hpe', 0):.1f}h"),
        kpi_card("HNT Ocasionales", f"{kpis.get('hntmo', 0):.1f}h"),
    ], className="kpi-grid")

    # Evolución (plotly)
    df_evo = ds.get_evolution_data(ccaa or "Total Nacional", sector or "Todos")
    fig = go.Figure()
    if not df_evo.empty:
        fig.add_trace(go.Scatter(
            x=df_evo["periodo"],
            y=df_evo["tasa_absentismo"],
            mode="lines",
            line=dict(color="#1B59F8", width=2),
            fill="tozeroy",
            fillcolor="rgba(27, 89, 248, 0.1)",
            name="Tasa de Absentismo"
        ))
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350, showlegend=False)

    # Ranking
    df_rank = ds.get_ranking_ccaa(periodo or "2024T4")
    data = df_rank.to_dict("records") if isinstance(df_rank, pd.DataFrame) else []
    columns = ([{"name": c, "id": c} for c in df_rank.columns]
               if isinstance(df_rank, pd.DataFrame) and len(df_rank.columns) > 0 else [])

    return kpi_children, fig, data, columns
