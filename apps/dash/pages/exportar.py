from dash import html, register_page

register_page(__name__, path="/exportar", name="Exportar")

def layout():
    return html.Div([
        html.H3("Exportar"),
        html.P("Sección en construcción: exportación a CSV/Excel/PDF."),
    ], className="page")

