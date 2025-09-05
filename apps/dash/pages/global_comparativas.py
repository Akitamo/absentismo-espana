from dash import html, register_page

register_page(__name__, path="/global/comparativas", name="Comparativas (Global)", title="Comparativas - Global")

def layout():
    return html.Div([
        html.Div([
            html.H3("Comparativas (Global)"),
            html.P("Espacio para comparativas globales (por sectores, geografía, etc.)."),
        ], className="page")
    ])

