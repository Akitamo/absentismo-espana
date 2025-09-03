from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
import plotly.graph_objects as go


ROOT = Path(__file__).resolve().parents[2]
TOKENS = ROOT / "design" / "tokens.json"


@lru_cache(maxsize=1)
def load_tokens() -> dict:
    try:
        return json.loads(TOKENS.read_text(encoding="utf-8"))
    except Exception:
        # Fallback razonable
        return {
            "colors": {
                "primary": "#1B59F8",
                "border": "#e5e7eb",
                "text": {"primary": "#121212", "secondary": "#6b7280"},
                "surface": "#ffffff",
                "background": "#f7f8fa",
            },
            "typography": {"fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif"},
        }


def plotly_template() -> go.layout.Template:
    t = load_tokens()
    colors = t.get("colors", {})
    border = colors.get("border", "#e5e7eb")
    primary = colors.get("primary", "#1B59F8")
    surface = colors.get("surface", "#ffffff")
    background = colors.get("background", "#f7f8fa")
    text = (colors.get("text") or {})
    font_fam = (t.get("typography") or {}).get("fontFamily", "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif")

    template = go.layout.Template(
        layout=dict(
            font=dict(family=font_fam, color=text.get("primary", "#121212")),
            colorway=[primary, "#10b981", "#f59e0b", "#ef4444", "#6366f1"],
            paper_bgcolor=surface,
            plot_bgcolor=surface,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(
                gridcolor=border,
                linecolor=border,
                zerolinecolor=border,
                ticks="outside",
            ),
            yaxis=dict(
                gridcolor=border,
                linecolor=border,
                zerolinecolor=border,
                ticks="outside",
            ),
            legend=dict(bordercolor=border, borderwidth=0, orientation="h", yanchor="bottom", y=1.02, x=0),
        )
    )
    return template

