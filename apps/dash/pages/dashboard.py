from dash import html, dcc, dash_table, register_page, Input, Output, State, callback
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import base64

from src.core.data_service import DataService
from apps.dash.components.ui import card

register_page(__name__, path="/")

ds = DataService()

# Cargar imagen de referencia de diseño (baseline) como data URI (si existe)
_root = Path(__file__).resolve().parents[3]
_overlay_path = _root / "design" / "Diseño dashboardFIN.jpg"
try:
    _overlay_bytes = _overlay_path.read_bytes()
    _overlay_b64 = base64.b64encode(_overlay_bytes).decode("ascii")
    OVERLAY_SRC = f"data:image/jpeg;base64,{_overlay_b64}"
except Exception:
    OVERLAY_SRC = None

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
            html.Div([
                html.Label("Overlay diseño"),
                dcc.Checklist(
                    id="overlay-toggle",
                    options=[{"label": "Mostrar", "value": "on"}],
                    value=[],
                    inline=True,
                ),
                html.Div([
                    html.Span("Opacidad", style={"marginRight": 6}),
                    dcc.Slider(id="overlay-opacity", min=0, max=1, step=0.05, value=0.35,
                               tooltip={"placement": "bottom", "always_visible": False})
                ], style={"marginTop": 6}),
                html.Div([
                    html.Span("Zoom", style={"marginRight": 6}),
                    dcc.Slider(id="overlay-zoom", min=0.8, max=1.3, step=0.01, value=1.0)
                ], style={"marginTop": 6}),
                html.Div([
                    html.Span("Offset X", style={"marginRight": 6}),
                    dcc.Slider(id="overlay-offset-x", min=-300, max=300, step=1, value=0)
                ], style={"marginTop": 6}),
                html.Div([
                    html.Span("Offset Y", style={"marginRight": 6}),
                    dcc.Slider(id="overlay-offset-y", min=-300, max=300, step=1, value=0)
                ], style={"marginTop": 6}),
            ], className="filter"),
        ], className="filters"),

        html.Div(id="kpis", className="kpis"),

        html.Div([
            card(
                title="Evolución",
                body=dcc.Graph(id="evolucion"),
                className="card-evolucion",
                loading=True,
            ),
            card(
                title="Ranking CCAA",
                body=dash_table.DataTable(id="ranking-table", page_size=10, style_table={"overflowX": "auto"}),
                className="card-ranking",
            ),
        ], className="main")
        ,
        # Imagen superpuesta del diseño (si existe)
        (html.Img(id="design-overlay", src=OVERLAY_SRC, style={
            "display": "none",
            "position": "fixed",
            "left": 0,
            "top": 0,
            "width": "1440px",
            "height": "auto",
            "opacity": 0.35,
            "transformOrigin": "top left",
            "transform": "translate(0px, 0px) scale(1)",
            "pointerEvents": "none",
            "zIndex": 9999,
            # "mixBlendMode": "multiply",
        }) if OVERLAY_SRC else html.Div(id="design-overlay", style={"display": "none"}))
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


@callback(
    Output("design-overlay", "style"),
    Input("overlay-toggle", "value"),
    Input("overlay-opacity", "value"),
    Input("overlay-zoom", "value"),
    Input("overlay-offset-x", "value"),
    Input("overlay-offset-y", "value"),
    State("design-overlay", "style"),
    prevent_initial_call=False,
)
def _toggle_overlay(toggle_vals, opacity, zoom, offx, offy, style):
    style = dict(style or {})
    show = toggle_vals and ("on" in toggle_vals)
    style["display"] = "block" if show else "none"
    if opacity is not None:
        style["opacity"] = float(opacity)
    if zoom is not None or offx is not None or offy is not None:
        z = float(zoom or 1)
        x = int(offx or 0)
        y = int(offy or 0)
        style["transform"] = f"translate({x}px, {y}px) scale({z})"
    return style
