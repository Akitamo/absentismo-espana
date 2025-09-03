from dash import html, register_page

register_page(__name__, path="/analisis", name="Análisis", title="Análisis · Absentismo")

def layout():
    return html.Div([
        html.H3("Análisis"),
        html.P("Sección en construcción: análisis nacional, territorial y sectorial."),
    ], className="page")
