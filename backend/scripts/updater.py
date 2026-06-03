"""
Обновление цен (для каждого тикера догружаем дни после последней даты в БД)
Запускать после init_db и первичной загрузки
"""
import os
import sqlite3
import sys
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

scripts_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(scripts_dir, "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.db_config import get_db_path

# сколько дней истории качаем, если в БД ещё нет дат по тикеру
HISTORY_DAYS = 365 * 5


def update_stock_data():
    """Догружает цены в таблицу prices с даты после последней записи."""

    db_path = get_db_path()

    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена по пути: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # тикеры из companies, если список пустой — из prices
    cursor.execute("SELECT ticker FROM companies")
    tickers = [row[0] for row in cursor.fetchall()]

    if not tickers:
        cursor.execute("SELECT DISTINCT ticker FROM prices")
        tickers = [row[0] for row in cursor.fetchall()]

    for ticker in tickers:
        cursor.execute(
            "SELECT MAX(date) FROM prices WHERE ticker = ?", (ticker,))
        row = cursor.fetchone()
        last_date_str = row[0] if row else None

        fallback_start = (
            datetime.now() - timedelta(days=HISTORY_DAYS)
        ).strftime('%Y-%m-%d')

        if last_date_str:
            try:
                last_date = pd.to_datetime(last_date_str, format="mixed")
                start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
            except Exception:
                start_date = fallback_start
        else:
            start_date = fallback_start

        today = datetime.now().strftime('%Y-%m-%d')

        if start_date > today:
            print(f"✔️ Данные для {ticker} уже актуальны.")
            continue

        print(f"🔄 Обновление {ticker}: с {start_date} по {today}")

        new_data = yf.download(
            ticker, start=start_date, end=today, progress=False)

        if new_data.empty:
            print(f"📭 Новых данных для {ticker} пока нет.")
            continue

        new_data = new_data.reset_index()
        new_data.columns = [col.lower() for col in new_data.columns]
        new_data['ticker'] = ticker

        cols = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
        new_data = new_data[cols]
        new_data['date'] = new_data['date'].dt.strftime('%Y-%m-%d')

        try:
            new_data.to_sql('prices', conn, if_exists='append', index=False)
            print(f"✅ Добавлено записей: {len(new_data)}")
        except sqlite3.IntegrityError:
            print(
                f"⚠️ Некоторые данные для {ticker} уже существуют (пропущено)")

    conn.close()


if __name__ == "__main__":
    update_stock_data()
