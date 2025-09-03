from dash import html, dcc, dash_table, register_page, Input, Output, State, callback
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

from src.core.data_service import DataService
from apps.dash.components.ui import card

register_page(__name__, path="/", name="Dashboard", title="Dashboard · Absentismo")

ds = DataService()

# Cargar imagen de referencia de diseño (baseline) como data URI (si existe)
_root = Path(__file__).resolve().parents[3]

def kpi_card(title: str, value: str, *, icon: str = "", trend: str | None = None):
    return html.Div([
        html.Div([
            html.Span(icon, className="kpi-icon") if icon else None,
            html.Div(title, className="kpi-title"),
        ], className="kpi-head"),
        html.Div(value, className="kpi-value"),
        (html.Div(trend, className=f"kpi-trend {'up' if trend and trend.startswith('↑') else 'down' if trend and trend.startswith('↓') else ''}") if trend else None),
    ], className="kpi-card")


def _prev_period(periodo: str) -> str:
    try:
        y = int(periodo[:4])
        q = int(periodo[-1])
        if q == 1:
            return f"{y-1}T4"
        return f"{y}T{q-1}"
    except Exception:
        return periodo


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
        # KPIs al inicio
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
                body=dash_table.DataTable(
                    id="ranking-table",
                    page_size=10,
                    fixed_rows={"headers": True},
                    style_table={
                        "overflowX": "auto",
                        "maxHeight": "420px",
                        "overflowY": "auto",
                    },
                    style_header={
                        "position": "sticky",
                        "top": 0,
                        "zIndex": 1,
                        "backgroundColor": "#FAFBFF",
                        "fontWeight": 600,
                    },
                    style_cell={
                        "padding": "12px 10px",
                        "whiteSpace": "nowrap",
                        "minWidth": "120px",
                    },
                ),
                className="card-ranking",
            ),
        ], className="main")
    ], className="page")


@callback(
    Output("kpis", "children"),
    Output("evolucion", "figure"),
    Output("ranking-table", "data"),
    Output("ranking-table", "columns"),
    Input("url", "pathname"),
)
def update_dashboard(_pathname):
    # KPIs (solo dos: Tasa Absentismo y Tasa IT) con comparación vs periodo anterior
    try:
        periods = ds.get_available_periods()
    except Exception:
        periods = ["2024T4", "2024T3"]
    cur_period = (periods[0] if periods else "2024T4")
    ccaa = "Total Nacional"
    sector = "Todos"
    k_cur = ds.get_kpis(cur_period, ccaa, sector)
    prev = _prev_period(cur_period)
    k_prev = ds.get_kpis(prev, ccaa, sector)

    # Calcular deltas
    def _trend(val_cur, val_prev, label):
        try:
            d = float(val_cur) - float(val_prev)
            arrow = "↑" if d > 0.0001 else ("↓" if d < -0.0001 else "→")
            return f"{arrow} {abs(d):.1f}% vs {prev}"
        except Exception:
            return None

    t_abs = k_cur.get('tasa_absentismo', 0)
    t_abs_prev = k_prev.get('tasa_absentismo', 0)
    t_it = k_cur.get('tasa_it', 0)
    t_it_prev = k_prev.get('tasa_it', 0)

    kpi_children = html.Div([
        kpi_card(
            "Tasa Absentismo",
            f"{t_abs:.1f}%",
            icon="📊",
            trend=_trend(t_abs, t_abs_prev, 'absentismo'),
        ),
        kpi_card(
            "Tasa IT",
            f"{t_it:.1f}%",
            icon="🏥",
            trend=_trend(t_it, t_it_prev, 'it'),
        ),
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
    df_rank = ds.get_ranking_ccaa(cur_period)
    data = df_rank.to_dict("records") if isinstance(df_rank, pd.DataFrame) else []
    columns = ([{"name": c, "id": c} for c in df_rank.columns]
               if isinstance(df_rank, pd.DataFrame) and len(df_rank.columns) > 0 else [])

    return kpi_children, fig, data, columns


# Overlay retirado
