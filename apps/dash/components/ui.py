from __future__ import annotations

from typing import Iterable, Optional, Union
from dash import html, dcc


Child = Union[str, int, float, html.Div, dcc.Loading, dcc.Graph, object]


def _to_children(x: Optional[Union[Child, Iterable[Child]]]):
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]


def card(
    *,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    actions: Optional[Iterable[Child]] = None,
    body: Optional[Union[Child, Iterable[Child]]] = None,
    footer: Optional[Union[Child, Iterable[Child]]] = None,
    className: Optional[str] = None,
    id: Optional[str] = None,
    loading: bool = False,
    variant: Optional[str] = None,
):
    """
    Card wrapper para unificar estilo de contenedores (gráficas, tablas, bloques KPI).

    - title/subtitle: cabecera opcional con acciones a la derecha.
    - body: contenido principal. Si loading=True, se envuelve en dcc.Loading.
    - footer: pie opcional (leyendas, notas, CTA).
    - variant: añade clase `card--{variant}` (p.ej. 'kpi', 'compact', 'scroll').
    """

    classes = ["card"]
    if className:
        classes.append(className)
    if variant:
        classes.append(f"card--{variant}")

    header = None
    if title or subtitle or actions:
        header = html.Div([
            html.Div([
                html.Div(title or "", className="card-title"),
                html.Div(subtitle or "", className="card-subtitle") if subtitle else None,
            ], className="card-titlewrap"),
            html.Div(_to_children(actions), className="card-actions") if actions else None,
        ], className="card-header")

    content = html.Div(_to_children(body), className="card-body")
    if loading:
        content = dcc.Loading(content, type="dot")

    footer_div = html.Div(_to_children(footer), className="card-footer") if footer else None

    return html.Div([c for c in [header, content, footer_div] if c], className=" ".join(classes), id=id)

