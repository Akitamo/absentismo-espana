"""
Genera apps/dash/assets/theme.css a partir de design/tokens.json.
Uso: python scripts/tokens_to_css.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "design" / "tokens.json"
CSS_OUT = ROOT / "apps" / "dash" / "assets" / "theme.css"


def kebab(s: str) -> str:
    return s.replace("_", "-")


def main() -> None:
    data = json.loads(TOKENS.read_text(encoding="utf-8"))

    colors = data.get("colors", {})
    typography = data.get("typography", {})
    spacing = data.get("spacing", {})
    borders = data.get("borders", {})
    layout = data.get("layout", {})

    # Variables base mapeadas desde tokens
    vars_map = {
        "--color-bg": colors.get("background", "#f7f8fa"),
        "--color-surface": colors.get("surface", "#ffffff"),
        "--color-text": (colors.get("text", {}) or {}).get("primary", "#121212"),
        "--color-muted": (colors.get("text", {}) or {}).get("secondary", "#6b7280"),
        "--color-primary": colors.get("primary", "#1B59F8"),
        "--color-primary-hover": colors.get("primary_hover", "#1547c5"),
        "--border-color": colors.get("border", "#e5e7eb"),
        "--radius": (borders.get("radius", {}) or {}).get("md", "10px"),
        "--gap-sm": spacing.get("sm", "8px"),
        "--gap-md": spacing.get("md", "12px"),
        "--gap-lg": spacing.get("lg", "16px"),
        "--font-family": typography.get("fontFamily", "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif"),
        "--font-size-sm": (typography.get("fontSize", {}) or {}).get("sm", "12px"),
        "--font-size-base": (typography.get("fontSize", {}) or {}).get("base", "14px"),
        "--font-size-xl": (typography.get("fontSize", {}) or {}).get("xl", "24px"),
        "--font-weight-regular": (typography.get("fontWeight", {}) or {}).get("regular", 400),
        "--font-weight-bold": (typography.get("fontWeight", {}) or {}).get("bold", 700),
        "--content-width": layout.get("contentWidth", "1320px"),
    }

    root_vars = ":root {\n" + "\n".join([f"  {k}: {v};" for k, v in vars_map.items()]) + "\n}\n\n"

    # Bloques base de estilos (alineados con DESIGN_SYSTEM.md)
    base_blocks = (
        "body { background: var(--color-bg); color: var(--color-text); font-family: var(--font-family); }\n"
        "header, main { max-width: var(--content-width); margin: 0 auto; }\n\n"
        ".nav { display:flex; gap: var(--gap-md); padding: 8px 16px; }\n"
        ".nav a { color: var(--color-muted); text-decoration: none; padding: 6px 10px; border-radius: 8px; }\n"
        ".nav a.active, .nav a:hover { color: var(--color-primary); background: #eef3ff; }\n\n"
        ".filters { display: grid; grid-template-columns: repeat(3, minmax(180px, 1fr)); gap: var(--gap-md); margin: 8px 0 12px; }\n"
        ".filter { background: var(--color-surface); padding: 8px 12px; border-radius: var(--radius); border: 1px solid var(--border-color); }\n\n"
        ".kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--gap-md); margin: 12px 0; }\n"
        ".kpi-card { background: var(--color-surface); border: 1px solid var(--border-color); border-radius: var(--radius); padding: 12px; }\n"
        ".kpi-title { color: var(--color-muted); font-size: var(--font-size-sm); }\n"
        ".kpi-value { font-size: var(--font-size-xl); font-weight: var(--font-weight-bold); margin-top: 4px; }\n"
        ".kpi-subtitle { color: var(--color-muted); font-size: var(--font-size-sm); margin-top: 2px; }\n\n"
        ".main { display: grid; grid-template-columns: 2fr 1fr; gap: var(--gap-md); }\n"
    )

    CSS_OUT.parent.mkdir(parents=True, exist_ok=True)
    CSS_OUT.write_text(root_vars + base_blocks, encoding="utf-8")
    print(f"Escrito: {CSS_OUT}")


if __name__ == "__main__":
    main()

