import streamlit as st

def figure_plotly(fig, *, modebar: bool = False):
    cfg = {'displayModeBar': modebar}
    st.plotly_chart(fig, use_container_width=True, config=cfg)

def figure_altair(chart):
    st.altair_chart(chart, use_container_width=True)

def figure_mpl(fig):
    st.pyplot(fig, use_container_width=True)
