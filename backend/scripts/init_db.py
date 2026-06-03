"""
Создание файла SQLite и таблиц companies и prices (один раз или после удаления БД).
"""
import os
import sqlite3
import sys

scripts_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(scripts_dir, "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.db_config import get_db_path


def init_db():
    """
    Инициализирует базу данных, создает нужную папку при необходимости.
    """

    db_path = get_db_path()
    db_folder = os.path.dirname(db_path)

    if not os.path.exists(db_folder):
        os.makedirs(db_folder)  # например backend/database/

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Таблица названий компаний
        c.execute(
            '''CREATE TABLE IF NOT EXISTS companies(
            ticker TEXT PRIMARY KEY,
            name TEXT
            )'''
        )

        # Таблица цен с уникальным индексом по тикеру и дате
        c.execute(
            '''CREATE TABLE IF NOT EXISTS prices(
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
            )'''
        )

        conn.commit()
        conn.close()
        print("✅ База данных инициализирована")
    except Exception:
        print("❌ Ошибка инициализации базы данных.")


if __name__ == "__main__":
    init_db()
