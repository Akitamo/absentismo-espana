from dash import html, register_page

register_page(__name__, path="/it/comparativas", name="Comparativas (IT)", title="Comparativas - IT")

def layout():
    return html.Div([
        html.Div([
            html.H3("Comparativas (IT)"),
            html.P("Espacio para comparativas IT (por sectores, geografía, etc.)."),
        ], className="page")
    ])

