from dash import Dash, html, dcc

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Absentismo Laboral España"
)

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Header(html.H2("Absentismo Laboral España"), style={"padding": "12px 16px"}),
    html.Main([
        dcc.Loading(dcc.PageContainer(), type="dot")
    ], style={"padding": "8px 16px"})
])


if __name__ == "__main__":
    app.run_server(debug=True)

