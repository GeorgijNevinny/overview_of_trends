"""
Первичная загрузка данных в бд
"""
import os
import sqlite3
import sys

scripts_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(scripts_dir, "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import yfinance as yf

from backend.db_config import get_db_path


def get_manual_tickers():
    """
    Возвращает только список тикеров.
    """
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "V", "JPM",
        "WMT", "MA", "UNH", "HD", "PG", "COST", "ORCL", "ADBE", "AMD",
        "NFLX", "CRM", "XOM", "BAC", "DIS", "CSCO", "INTC", "PFE", "KO",
        "PEP", "NKE", "ABT", "LLY", "AVGO", "CVX", "ABBV", "MRK", "ACN",
        "MCD", "TMO", "WFC", "DHR", "LIN", "TXN", "PM", "MS", "RTX",
        "HON", "GE", "AMGN"
    ]


def update_data():
    """
    Получает данные из библиотеки yfinance и сохраняет их в базу данных.
    """

    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    tickers_list = get_manual_tickers()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    count = 0
    total = len(tickers_list)

    for ticker_symbol in tickers_list:
        count += 1
        # Yahoo Finance: классы с точкой в тикере пишут через дефис (BRK.B → BRK-B)
        clean_ticker = ticker_symbol.replace('.', '-')
        print(f"[{count}/{total}] Обработка {clean_ticker}...")

        try:
            ticker_obj = yf.Ticker(clean_ticker)

            # Получаем название компании из yfinance
            # Сначала проверим, нет ли его уже в БД, чтобы сэкономить время
            cursor.execute(
                "SELECT name FROM companies WHERE ticker = ?", (clean_ticker,))
            res = cursor.fetchone()

            if res and res[0]:
                full_name = res[0]
            else:
                # Если в базе нет, то загружаем
                full_name = ticker_obj.info.get('longName', clean_ticker)
                cursor.execute(
                    "INSERT OR REPLACE INTO companies (ticker, name) VALUES (?, ?)",
                    (clean_ticker, full_name)
                )
                print(f"🏢 Название загружено: {full_name}")

            # Загружаем историю цен
            hist = ticker_obj.history(period="5y")

            if not hist.empty:
                hist = hist.reset_index()
                data_to_insert = []

                for _, row in hist.iterrows():
                    # Форматируем дату в зависимости от того, есть ли там время
                    date_str = row['Date'].strftime('%Y-%m-%d')

                    data_to_insert.append((
                        clean_ticker,
                        date_str,
                        round(row['Open'], 4),
                        round(row['High'], 4),
                        round(row['Low'], 4),
                        round(row['Close'], 4),
                        int(row['Volume'])
                    ))

                # Перезапись при повторном прогоне скрипта
                cursor.executemany(
                    """ INSERT OR REPLACE INTO prices 
                    (ticker, date, open, high, low, close, volume) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    data_to_insert
                )
            else:
                print(f"⚠️ Цены для {clean_ticker} не найдены.")

        except Exception as e:
            print(f"❌ Ошибка {clean_ticker}: {e}")
            continue

    conn.commit()
    conn.close()
    print("✅ Данные загружены")


if __name__ == "__main__":
    update_data()
