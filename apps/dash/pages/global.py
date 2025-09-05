from dash import html, dcc, dash_table, register_page, Input, Output, State, callback
import plotly.graph_objects as go
import pandas as pd

from src.core.data_service import DataService
from apps.dash.components.ui import card
from apps.dash.components.kpi import build_absentismo_kpi
from apps.dash.plotly_theme import plotly_template

register_page(__name__, path="/global", name="Absentismo Global", title="Absentismo Global")

ds = DataService()

def layout():
    return html.Div([
        # Sección KPIs + Insight
        html.Div([
            card(body=html.Div(id="kpis-global", className="left-grid kpi-grid--compact"), className="card-kpi-shell"),
            html.Div([html.H4("Análisis"), html.P("Texto generado por IA sobre KPIs (global).")], id="insight-kpis-global", className="insight-panel"),
        ], className="section"),

        # Sección Evolución + Ranking + Insight
        html.Div([
            html.Div([
                card(title="Evolución (Global)", body=dcc.Graph(id="evolucion-global"), className="card-evolucion", loading=True),
                card(title="Ranking CCAA (Global)", body=dash_table.DataTable(id="ranking-global", page_size=10), className="card-ranking"),
            ], className="left-grid"),
            html.Div([html.H4("Análisis"), html.P("Texto IA para evolución y ranking (global).")], id="insight-main-global", className="insight-panel"),
        ], className="section"),
    ], className="page")


@callback(
    Output("kpis-global", "children"),
    Output("evolucion-global", "figure"),
    Output("ranking-global", "data"),
    Output("ranking-global", "columns"),
    Input("url", "pathname"),
)
def update_global(_):
    periods = ds.get_available_periods()
    cur_period = (periods[0] if periods else "2024T4")
    prev = _prev_period(cur_period)
    
    k_cur = ds.get_kpis(cur_period, "Total Nacional", "Todos")
    k_prev = ds.get_kpis(prev, "Total Nacional", "Todos")
    prev_y = _prev_year_period(cur_period)
    k_prev_y = ds.get_kpis(prev_y, "Total Nacional", "Todos")

    df_evo = ds.get_evolution_data("Total Nacional", "Todos")
    df_it = ds.get_evolution_it_data("Total Nacional", "Todos")

    t_abs = k_cur.get("tasa_absentismo", 0.0)
    t_abs_prev = k_prev.get("tasa_absentismo", t_abs)
    t_it = k_cur.get("tasa_it", 0.0)
    t_it_prev = k_prev.get("tasa_it", t_it)

    prev_label = prev or "trimestre anterior"
    kpi_children = html.Div([
        card(title="Tasa de absentismo (Total)", icon_src="/assets/icons/absentismo.svg",
             body=build_absentismo_kpi(t_abs, t_abs_prev, df_evo, prev_label=prev_label, previous_yoy=k_prev_y.get("tasa_absentismo", t_abs), yoy_label=prev_y), variant="kpi", className="card-kpi"),
        card(title="Tasa IT (Total)", icon_src="/assets/icons/it.svg",
             body=build_absentismo_kpi(t_it, t_it_prev, df_it, prev_label=prev_label, value_col="tasa_it", previous_yoy=k_prev_y.get("tasa_it", t_it), yoy_label=prev_y), variant="kpi", className="card-kpi"),
    ], className="kpi-grid")

    fig = go.Figure()
    if isinstance(df_evo, pd.DataFrame) and not df_evo.empty:
        df_plot = df_evo.tail(36)
        fig.add_trace(go.Scatter(x=df_plot["periodo"], y=df_plot["tasa_absentismo"], mode="lines",
                                 line=dict(color="#1B59F8", width=2), fill="tozeroy",
                                 fillcolor="rgba(27, 89, 248, 0.1)", name="Tasa de Absentismo"))
    fig.update_layout(template=plotly_template(), margin=dict(l=0, r=0, t=10, b=0), height=350, showlegend=False)

    df_rank = ds.get_ranking_ccaa(cur_period)
    data = df_rank.to_dict("records") if isinstance(df_rank, pd.DataFrame) else []
    columns = ([{"name": c, "id": c} for c in df_rank.columns]
               if isinstance(df_rank, pd.DataFrame) and len(df_rank.columns) > 0 else [])

    return kpi_children, fig, data, columns


def _prev_period(periodo: str) -> str:
    try:
        y = int(periodo[:4]); q = int(periodo[-1])
        return f"{y-1}T4" if q == 1 else f"{y}T{q-1}"
    except Exception:
        return periodo

def _prev_year_period(periodo: str) -> str:
    try:
        y = int(periodo[:4]); q = int(periodo[-1])
        return f"{y-1}T{q}"
    except Exception:
        return periodo
