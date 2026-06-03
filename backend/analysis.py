# STL-разложение цены закрытия

import pandas as pd
from statsmodels.tsa.seasonal import STL


def perform_stl_analysis(df, window_days=365):
    if len(df) == 0:
        return None
    if "close" not in df.columns:
        return None

    work = df.copy()
    work["date"] = pd.to_datetime(work["date"], format="mixed")
    work = work.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    work = work.set_index("date")
    prices = work["close"].resample("D").ffill()
    prices = prices.tail(window_days)

    if len(prices) < 30:
        return None

    try:
        model = STL(prices, period=30, seasonal=13, robust=True)
        return model.fit()
    except Exception:
        return None
