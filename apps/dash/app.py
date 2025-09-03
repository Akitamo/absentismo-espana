from pathlib import Path
import sys

# Ensure repository root is on sys.path so 'src.*' imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dash import Dash, html, dcc, page_container
from dash import page_registry
from dash import Input, Output, State, callback

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Absentismo Laboral España"
)

def _sorted_pages():
    # Orden deseado del sidebar
    order = ["/", "/analisis", "/comparativas", "/exportar"]
    pages = list(page_registry.values())
    pages.sort(key=lambda p: order.index(p.get("path", "/")) if p.get("path", "/") in order else 999)
    return pages


def _icon_for(path: str) -> str:
    return {
        "/": "🏠",
        "/analisis": "📊",
        "/comparativas": "📈",
        "/exportar": "⬇️",
    }.get(path, "•")


def _label_for(path: str, default: str) -> str:
    return {
        "/": "Dashboard",
        "/analisis": "Análisis",
        "/comparativas": "Comparativas",
        "/exportar": "Exportar",
    }.get(path, default)


def _build_sidebar_links(current_path: str = "/"):
    links = []
    for p in _sorted_pages():
        path = p.get("path", "/")
        name = _label_for(path, p.get("name", p["module"]).replace("apps.dash.pages.", ""))
        cls = "active" if path == (current_path or "/") else ""
        links.append(
            dcc.Link([
                html.Span(_icon_for(path), className="icon"),
                html.Span(name, className="label"),
            ], href=path, className=cls, title=name)
        )
    return links

# Cargar logo Ibermutua desde design/ como data URI
_root = Path(__file__).resolve().parents[2]
_logo_path = _root / "design" / "Ibermutua.png"
LOGO_SRC = None
try:
    import base64
    _logo_b = _logo_path.read_bytes()
    LOGO_SRC = f"data:image/png;base64,{base64.b64encode(_logo_b).decode('ascii')}"
except Exception:
    LOGO_SRC = None


app.layout = html.Div([
    dcc.Location(id="url"),
    # Asegurar carga de overrides aunque Dash no los inyecte automáticamente
    html.Link(rel="stylesheet", href="/assets/z-overrides.css"),
    dcc.Store(id="ui-store", data={"sidebar_open": False}),
    html.Div([
        (html.Img(src=LOGO_SRC, className="brand-logo", title="Ibermutua") if LOGO_SRC else html.Div("Absentismo España", className="brand")),
        html.Nav(id="sidebar-links", className="nav sidebar-nav"),
        html.Div([
            html.Div("demo", className="user-name"),
            html.Div("demo@example.com", className="user-mail")
        ], className="sidebar-user")
    ], className="sidebar", id="sidebar"),
    html.Div([
        html.Header([
            html.Div([
                html.Button("☰", id="btn-menu", className="icon-btn hamburger", title="Menú"),
                html.H2("Dashboard", className="page-title"),
                html.Div([
                    dcc.Input(id="top-search", placeholder="Search contacts, leads, opportunities...", type="text", className="top-search"),
                    html.Button("🔔", id="btn-bell", className="icon-btn", title="Notifications"),
                    html.Button("⚙️", id="btn-settings", className="icon-btn", title="Settings"),
                    html.Span("demo", className="user-chip")
                ], className="top-actions")
            ], className="topbar-inner")
        ], className="header"),
        html.Div(id="backdrop", style={"display": "none"}),
        html.Main([
            dcc.Loading(page_container, type="dot")
        ], className="content-main")
    ], className="content")
], className="app-shell")


@callback(Output("sidebar-links", "children"), Input("url", "pathname"))
def _update_active_links(pathname: str):
    return _build_sidebar_links(pathname or "/")


@callback(
    Output("ui-store", "data"),
    Input("btn-menu", "n_clicks"),
    Input("backdrop", "n_clicks"),
    Input("url", "pathname"),
    State("ui-store", "data"),
    prevent_initial_call=True,
)
def _toggle_sidebar(n_menu, n_backdrop, _pathname, ui):
    ui = ui or {"sidebar_open": False}
    ctx = dash.ctx.triggered_id  # type: ignore[attr-defined]
    if ctx == "btn-menu":
        ui["sidebar_open"] = not ui.get("sidebar_open", False)
    else:
        # Cerrar en backdrop o navegación
        ui["sidebar_open"] = False
    return ui


@callback(
    Output("sidebar", "className"),
    Output("backdrop", "style"),
    Input("ui-store", "data"),
)
def _apply_sidebar_state(ui):
    open_ = (ui or {}).get("sidebar_open", False)
    cls = "sidebar open" if open_ else "sidebar"
    backdrop_style = {"display": "block"} if open_ else {"display": "none"}
    return cls, backdrop_style


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
