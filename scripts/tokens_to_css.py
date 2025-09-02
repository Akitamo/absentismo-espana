import json
from pathlib import Path

TOKENS = Path("design/tokens.json")
OUT = Path("apps/dash/assets/theme.css")


def main():
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    c = tokens["colors"]
    t = tokens["typography"]
    s = tokens["spacing"]
    b = tokens["borders"]
    layout = tokens.get("layout", {})

    css = f''':root {{
  --color-bg: {c.get('background')};
  --color-surface: {c.get('surface')};
  --color-text: {c['text'].get('primary')};
  --color-muted: {c['text'].get('secondary')};
  --color-primary: {c.get('primary')};
  --color-primary-hover: {c.get('primary_hover')};
  --border-color: {c.get('border')};
  --radius: {b['radius'].get('md')};
  --gap-sm: {s.get('sm')};
  --gap-md: {s.get('md')};
  --gap-lg: {s.get('lg')};
  --font-family: {t.get('fontFamily')};
  --font-size-sm: {t['fontSize'].get('sm')};
  --font-size-base: {t['fontSize'].get('base')};
  --font-size-xl: {t['fontSize'].get('xl')};
  --font-weight-regular: {t['fontWeight'].get('regular')};
  --font-weight-bold: {t['fontWeight'].get('bold')};
  --content-width: {layout.get('contentWidth','1200px')};
}}

body {{ background: var(--color-bg); color: var(--color-text); font-family: var(--font-family); }}
header, main {{ max-width: var(--content-width); margin: 0 auto; }}

.nav {{ display:flex; gap: var(--gap-md); padding: 8px 16px; }}
.nav a {{ color: var(--color-muted); text-decoration: none; padding: 6px 10px; border-radius: 8px; }}
.nav a.active, .nav a:hover {{ color: var(--color-primary); background: #eef3ff; }}

.filters {{ display: grid; grid-template-columns: repeat(3, minmax(180px, 1fr)); gap: var(--gap-md); margin: 8px 0 12px; }}
.filter {{ background: var(--color-surface); padding: 8px 12px; border-radius: var(--radius); border: 1px solid var(--border-color); }}

.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--gap-md); margin: 12px 0; }}
.kpi-card {{ background: var(--color-surface); border: 1px solid var(--border-color); border-radius: var(--radius); padding: 12px; }}
.kpi-title {{ color: var(--color-muted); font-size: var(--font-size-sm); }}
.kpi-value {{ font-size: var(--font-size-xl); font-weight: var(--font-weight-bold); margin-top: 4px; }}
.kpi-subtitle {{ color: var(--color-muted); font-size: var(--font-size-sm); margin-top: 2px; }}

.main {{ display: grid; grid-template-columns: 2fr 1fr; gap: var(--gap-md); }}
'''

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(css, encoding="utf-8")
    print(f"OK: generated {OUT}")


if __name__ == "__main__":
    main()

