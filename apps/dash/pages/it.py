from dash import html, dcc, dash_table, register_page, Input, Output, State, callback
import plotly.graph_objects as go
import pandas as pd

from src.core.data_service import DataService
from apps.dash.components.ui import card
from apps.dash.components.kpi import build_absentismo_kpi
from apps.dash.plotly_theme import plotly_template

register_page(__name__, path="/it", name="Absentismo IT", title="Absentismo IT")

ds = DataService()

def layout():
    return html.Div([
        # Sección KPIs + Insight
        html.Div([
            card(body=html.Div(id="kpis-it", className="left-grid kpi-grid--compact"), className="card-kpi-shell"),
            html.Div([html.H4("Análisis"), html.P("Texto generado por IA sobre KPIs (IT).")], id="insight-kpis-it", className="insight-panel"),
        ], className="section"),

        # Sección Evolución + Ranking + Insight
        html.Div([
            html.Div([
                card(title="Evolución (IT)", body=dcc.Graph(id="evolucion-it"), className="card-evolucion", loading=True),
                card(title="Ranking CCAA (IT)", body=dash_table.DataTable(id="ranking-it", page_size=10), className="card-ranking"),
            ], className="left-grid"),
            html.Div([html.H4("Análisis"), html.P("Texto IA para evolución y ranking (IT).")], id="insight-main-it", className="insight-panel"),
        ], className="section"),
    ], className="page")


@callback(
    Output("kpis-it", "children"),
    Output("evolucion-it", "figure"),
    Output("ranking-it", "data"),
    Output("ranking-it", "columns"),
    Input("url", "pathname"),
)
def update_it(_):
    periods = ds.get_available_periods()
    cur_period = (periods[0] if periods else "2024T4")
    prev = _prev_period(cur_period)

    k_cur = ds.get_kpis(cur_period, "Total Nacional", "Todos")
    k_prev = ds.get_kpis(prev, "Total Nacional", "Todos")

    df_evo_it = ds.get_evolution_it_data("Total Nacional", "Todos")
    df_evo_abs = ds.get_evolution_data("Total Nacional", "Todos")

    t_it = k_cur.get("tasa_it", 0.0)
    t_it_prev = k_prev.get("tasa_it", t_it)
    t_abs = k_cur.get("tasa_absentismo", 0.0)
    t_abs_prev = k_prev.get("tasa_absentismo", t_abs)

    prev_label = prev or "trimestre anterior"
    kpi_children = html.Div([
        card(title="Tasa IT (Total)", icon_src="/assets/icons/it.svg",
             body=build_absentismo_kpi(t_it, t_it_prev, df_evo_it, prev_label=prev_label, value_col="tasa_it"), variant="kpi", className="card-kpi"),
        card(title="Tasa de absentismo (Total)", icon_src="/assets/icons/absentismo.svg",
             body=build_absentismo_kpi(t_abs, t_abs_prev, df_evo_abs, prev_label=prev_label), variant="kpi", className="card-kpi"),
    ], className="kpi-grid")

    fig = go.Figure()
    if isinstance(df_evo_it, pd.DataFrame) and not df_evo_it.empty:
        df_plot = df_evo_it.tail(36)
        fig.add_trace(go.Scatter(x=df_plot["periodo"], y=df_plot["tasa_it"], mode="lines",
                                 line=dict(color="#1B59F8", width=2), fill="tozeroy",
                                 fillcolor="rgba(27, 89, 248, 0.1)", name="Tasa IT"))
    fig.update_layout(template=plotly_template(), margin=dict(l=0, r=0, t=10, b=0), height=350, showlegend=False)

    df_rank = ds.get_ranking_ccaa_it(cur_period)
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

