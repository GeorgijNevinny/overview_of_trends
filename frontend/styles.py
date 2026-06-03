# Цвета и стили Streamlit

import streamlit as st

COLOR_MAIN = "#AEC6CF"
COLOR_FILL = "rgba(174, 198, 207, 0.2)"
COLOR_VOL = "#FFD1DC"
COLOR_SEASONAL = "#F1CBFF"


def apply_custom_styles():
    st.set_page_config(page_title="Финансовый мониторинг", layout="wide")
    st.markdown(
        """
        <style>
        .main { padding-top: 2rem; }
        .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
