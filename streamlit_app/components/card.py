from contextlib import contextmanager
import streamlit as st

@contextmanager
def card(title: str | None = None, subtitle: str | None = None, icon: str | None = None):
    """Card estándar basado en contenedor nativo (border=True). No HTML envolvente."""
    c = st.container(border=True)
    with c:
        if title or subtitle or icon:
            cols = st.columns([1, 12]) if icon else None
            if icon:
                with cols[0]: st.markdown(f"## {icon}")
                with cols[1]:
                    if title: st.markdown(f"**{title}**")
                    if subtitle: st.caption(subtitle)
            else:
                if title: st.markdown(f"**{title}**")
                if subtitle: st.caption(subtitle)
        yield

def skeleton(lines: int = 3):
    for _ in range(lines):
        st.markdown(
            "<div style='height:12px;background:rgba(0,0,0,0.06);border-radius:6px;margin:8px 0;'></div>",
            unsafe_allow_html=True
        )

def error(msg: str, hint: str | None = None):
    st.error(msg)
    if hint: st.caption(hint)
