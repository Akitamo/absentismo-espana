from dash import html, register_page

register_page(__name__, path="/comparativas", name="Comparativas")

def layout():
    return html.Div([
        html.H3("Comparativas"),
        html.P("Sección en construcción: comparativas CCAA, sectores y periodos."),
    ], className="page")

