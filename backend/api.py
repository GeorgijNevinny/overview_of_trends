# FastAPI: компании, цены, STL

import os
import sqlite3

import pandas as pd
from fastapi import FastAPI, HTTPException

from backend.analysis import perform_stl_analysis
from backend.db_config import get_db_path

DB_PATH = get_db_path()
app = FastAPI(title="Finance API")


def check_database():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="База данных не найдена")


def stl_to_list(series):
    """Список точек {date, value} для ответа API (без NaN)."""
    points = []
    for date, value in series.items():
        if pd.notna(value):
            points.append({"date": str(date), "value": float(value)})
    return points


@app.get("/companies")
def companies():
    check_database()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT ticker, name FROM companies ORDER BY ticker", conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/prices/{ticker}")
def prices(ticker, period="1Y"):
    check_database()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT date, open, high, low, close, volume FROM prices "
        "WHERE ticker = ? ORDER BY date ASC",
        conn,
        params=(ticker,),
    )
    conn.close()

    if len(df) == 0:
        raise HTTPException(status_code=404, detail="Нет цен для этого тикера")

    df["date"] = pd.to_datetime(df["date"], format="mixed")
    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    last_date = df["date"].max()

    if period == "1M":
        start = last_date - pd.DateOffset(months=1)
    elif period == "6M":
        start = last_date - pd.DateOffset(months=6)
    elif period == "1Y":
        start = last_date - pd.DateOffset(years=1)
    else:
        start = last_date - pd.DateOffset(years=5)

    df = df[df["date"] >= start].sort_values("date")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df.to_dict(orient="records")


@app.get("/stl/{ticker}")
def stl(ticker: str, days: int = 365):
    if days < 30:
        raise HTTPException(status_code=400, detail="Нужно минимум 30 дней")

    check_database()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT date, close FROM prices WHERE ticker = ? ORDER BY date ASC",
        conn,
        params=(ticker,),
    )
    conn.close()

    if len(df) == 0:
        raise HTTPException(status_code=404, detail="Нет цен для этого тикера")

    df["date"] = pd.to_datetime(df["date"], format="mixed")
    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    df = df.tail(days)

    result = perform_stl_analysis(df, window_days=days)
    if result is None:
        raise HTTPException(status_code=400, detail="Мало данных для STL")

    return {
        "ticker": ticker,
        "days": days,
        "trend": stl_to_list(result.trend),
        "seasonal": stl_to_list(result.seasonal),
        "resid": stl_to_list(result.resid),
    }
