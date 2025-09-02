from dash import Dash, html, dcc, page_container
from dash import page_registry

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Absentismo Laboral España"
)

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Header([
        html.H2("Absentismo Laboral España"),
        html.Nav([
            dcc.Link(
                p.get("name", p["module"]).replace("apps.dash.pages.", ""),
                href=p.get("path", "/"),
                className="active" if p.get("path", "/") == "/" else ""
            ) for p in sorted(page_registry.values(), key=lambda x: x.get("path", "/"))
        ], className="nav")
    ], style={"padding": "12px 16px"}),
    html.Main([
        dcc.Loading(page_container, type="dot")
    ], style={"padding": "8px 16px"})
])


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
