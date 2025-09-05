from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc, html

from apps.dash.plotly_theme import plotly_template


def build_absentismo_kpi(
    current: float,
    previous: Optional[float],
    series: Optional[pd.DataFrame],
    *,
    prev_label: Optional[str] = None,
    value_col: str = "tasa_absentismo",
    previous_yoy: Optional[float] = None,
    yoy_label: Optional[str] = None,
):
    """
    Crea una figura KPI con Indicator (number+delta) y un sparkline inferior.

    - current: valor actual de tasa de absentismo (porcentaje 0-100).
    - previous: valor del periodo anterior para delta (puede ser None).
    - series: DataFrame con columnas ['periodo', 'tasa_absentismo'] para sparkline.
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.08,
        specs=[[{"type": "indicator"}], [{"type": "xy"}]],
    )

    delta_ref = float(previous) if previous is not None else float(current)

    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=float(current or 0.0),
            number=dict(suffix=" %", valueformat=".2f"),
            delta=dict(
                reference=delta_ref,
                relative=True,  # mostrar % relativo respecto al trimestre anterior
                valueformat="+.2%",
                increasing=dict(color="#ef4444"),  # peor si sube
                decreasing=dict(color="#10b981"),  # mejor si baja
            ),
        ),
        row=1,
        col=1,
    )

    if isinstance(series, pd.DataFrame) and not series.empty:
        # Asegurar orden cronológico ascendente y limitar a últimos 12 periodos
        s = series.copy()
        if "periodo" in s.columns:
            # Ya viene en ASC desde DataService, pero normalizamos por si acaso
            try:
                s = s.sort_values("periodo")
            except Exception:
                pass
        s = s.tail(12)

        x = s["periodo"].tolist() if "periodo" in s.columns else list(range(len(s)))
        # Elegir columna para el sparkline (absentismo por defecto; IT si se indica)
        if value_col in s.columns:
            y = s[value_col].tolist()
        else:
            # Fallback: intenta primera columna numérica
            _num = s.select_dtypes(include=["number"])
            y = _num.iloc[:, 0].tolist() if not _num.empty else []
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line=dict(color="#1B59F8", width=2),
                fill="tozeroy",
                fillcolor="rgba(27, 89, 248, 0.10)",
                hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>",
            ),
            row=2,
            col=1,
        )
        fig.update_xaxes(visible=False, row=2, col=1)
        # Ajustar rango Y para resaltar variaciones (padding dinámico)
        try:
            y_float = [float(v) for v in y if v is not None]
            if y_float:
                y_min, y_max = min(y_float), max(y_float)
                pad = max(0.2, (y_max - y_min) * 0.15)
                fig.update_yaxes(visible=False, row=2, col=1, range=[y_min - pad, y_max + pad])
            else:
                fig.update_yaxes(visible=False, row=2, col=1)
        except Exception:
            fig.update_yaxes(visible=False, row=2, col=1)

    # Annotation to indicate comparison reference
    if prev_label:
        fig.add_annotation(xref="paper", yref="paper", x=0.01, y=0.52,
                           text=f"Comparación vs {prev_label}", showarrow=False,
                           font=dict(size=11, color="#6b7280"), align="left")

    fig.update_layout(
        template=plotly_template(),
        height=160,
        margin=dict(l=8, r=8, t=6, b=6),
        showlegend=False,
    )

    # Badges de variación QoQ y YoY
    def _rel(cur: float, ref: Optional[float]) -> Optional[float]:
        try:
            if ref is None or ref == 0:
                return None
            return (float(cur) - float(ref)) / abs(float(ref))
        except Exception:
            return None

    qoq_rel = _rel(current, previous)
    yoy_rel = _rel(current, previous_yoy)

    def _badge(label: str, rel: Optional[float]):
        if rel is None:
            return html.Span(f"N/A {label}", className="delta-badge")
        cls = "delta-badge up" if rel > 0 else ("delta-badge down" if rel < 0 else "delta-badge")
        sign = "+" if rel > 0 else ("" if rel == 0 else "")
        return html.Span(f"{sign}{rel*100:.2f}% {label}", className=cls)

    badges = html.Div([
        _badge(f"vs {prev_label}" if prev_label else "vs trim. ant.", qoq_rel),
        _badge(f"vs {yoy_label}" if yoy_label else "vs año ant.", yoy_rel),
    ], className="delta-badges")

    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False}),
        badges
    ])
