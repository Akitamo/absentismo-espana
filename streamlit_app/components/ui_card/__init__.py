from __future__ import annotations
from pathlib import Path
import json
import streamlit as st
import streamlit.components.v1 as components
from typing import Any, Optional

# Local/dev o empaquetado
_COMPONENT_NAME = "ui_card"
_FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"
if _FRONTEND_DIR.exists():
    _ui_card = components.declare_component(
        _COMPONENT_NAME, path=str(_FRONTEND_DIR)
    )
else:
    # fallback: sirve dev server (vite) si está corriendo
    _ui_card = components.declare_component(_COMPONENT_NAME, url="http://localhost:5173")

def metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    icon: Optional[str] = None,
    height: int = 120,
    key: Optional[str] = None,
    tokens: Optional[dict] = None,
) -> Any:
    """KPI/Metric card."""
    props = {
        "type": "metric",
        "title": title,
        "subtitle": delta,
        "icon": icon or "",
        "value": value,
        "height": height,
        "tokens": tokens or {},
    }
    return _ui_card(name=_COMPONENT_NAME, default=None, key=key, **props)

def plotly_card(
    title: str,
    subtitle: Optional[str],
    fig_json: str,
    height: int = 360,
    key: Optional[str] = None,
    tokens: Optional[dict] = None,
    modebar: bool = False,
) -> Any:
    """Card que renderiza Plotly dentro del componente (no usa st.plotly_chart)."""
    props = {
        "type": "plotly",
        "title": title,
        "subtitle": subtitle or "",
        "icon": "",
        "height": height,
        "fig": json.loads(fig_json),
        "modebar": modebar,
        "tokens": tokens or {},
    }
    return _ui_card(name=_COMPONENT_NAME, default=None, key=key, **props)

def table_card(
    title: str,
    html: str,
    subtitle: Optional[str] = None,
    height: int = 300,
    key: Optional[str] = None,
    tokens: Optional[dict] = None,
) -> Any:
    """Card con HTML (por ejemplo, tabla) seguro."""
    props = {
        "type": "html",
        "title": title,
        "subtitle": subtitle or "",
        "icon": "",
        "height": height,
        "html": html,
        "tokens": tokens or {},
    }
    return _ui_card(name=_COMPONENT_NAME, default=None, key=key, **props)