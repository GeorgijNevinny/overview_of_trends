"""Streamlit (данные с FastAPI)"""

import os
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# стили при запуске из корня или из frontend
try:
    from frontend.styles import (
        apply_custom_styles,
        COLOR_FILL,
        COLOR_MAIN,
        COLOR_SEASONAL,
        COLOR_VOL,
    )
except ModuleNotFoundError:
    from styles import (
        apply_custom_styles,
        COLOR_FILL,
        COLOR_MAIN,
        COLOR_SEASONAL,
        COLOR_VOL,
    )

apply_custom_styles()

# адрес бэкенда и глубина окна STL
API_BASE_URL = os.getenv("FINANCE_API_URL", "http://127.0.0.1:8000")
STL_DAYS = 365


# график цены и три метрики
def show_prices(df):
    df["date"] = pd.to_datetime(df["date"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["close"],
            mode="lines",
            line=dict(color=COLOR_MAIN, width=3),
            fill="tozeroy",
            fillcolor=COLOR_FILL,
        )
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=400,
        showlegend=False,
        xaxis_title="Дата",
        yaxis_title="USD",
    )
    st.plotly_chart(fig, use_container_width=True)

    last = df["close"].iloc[-1]
    first = df["close"].iloc[0]
    diff = last - first
    pct = diff / first * 100
    change = str(round(diff, 2)) + " (" + str(round(pct, 2)) + "%)"

    c1, c2, c3 = st.columns(3)
    c1.metric("Текущая цена", "$" + str(round(last, 2)), change)
    c2.metric("Максимум", "$" + str(round(df["close"].max(), 2)))
    c3.metric("Минимум", "$" + str(round(df["close"].min(), 2)))


# одна вкладка декомпозиции STL
def show_stl_tab(tab, data, key, color, mode="lines", line_width=3, marker_size=4):
    with tab:
        chart_df = pd.DataFrame(data[key])
        if len(chart_df) == 0:
            st.write("Нет данных")
            return

        chart_df["date"] = pd.to_datetime(chart_df["date"])
        fig = go.Figure()

        if mode == "markers":
            fig.add_trace(
                go.Scatter(
                    x=chart_df["date"],
                    y=chart_df["value"],
                    mode="markers",
                    marker=dict(color=color, size=marker_size),
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=chart_df["date"],
                    y=chart_df["value"],
                    mode="lines",
                    line=dict(color=color, width=line_width),
                )
            )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=350,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)


st.title("Финансовый мониторинг")
st.markdown("---")

# список компаний с API
r = requests.get(API_BASE_URL + "/companies", timeout=20)
if r.status_code != 200:
    st.error("Не удалось загрузить компании. Код: " + str(r.status_code))
    st.stop()

df_companies = pd.DataFrame(r.json())
tickers = df_companies["ticker"].tolist()

# фильтры пользователя
selected_ticker = st.selectbox("Компания", tickers)
period = st.radio("Период", ["1M", "6M", "1Y", "5Y"], horizontal=True)

# история цен по выбранному тикеру
r = requests.get(
    API_BASE_URL + "/prices/" + selected_ticker,
    params={"period": period},
    timeout=30,
)
if r.status_code != 200:
    st.error("Не удалось загрузить цены. Код: " + str(r.status_code))
    st.stop()

df = pd.DataFrame(r.json())
if len(df) == 0:
    st.warning("Нет данных по ценам.")
else:
    show_prices(df)

st.subheader("STL (последние " + str(STL_DAYS) + " дн.)")

# тренд, сезонность и шум
r = requests.get(
    API_BASE_URL + "/stl/" + selected_ticker,
    params={"days": STL_DAYS},
    timeout=30,
)
if r.status_code != 200:
    st.warning("STL недоступен: " + r.text)
else:
    data = r.json()
    tab1, tab2, tab3 = st.tabs(["Тренд", "Сезонность", "Шум"])
    show_stl_tab(tab1, data, "trend", COLOR_MAIN, line_width=3)
    show_stl_tab(tab2, data, "seasonal", COLOR_SEASONAL, line_width=2)
    show_stl_tab(tab3, data, "resid", COLOR_VOL, mode="markers")
