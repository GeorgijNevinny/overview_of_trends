# Путь к файлу SQLite

import os


def get_db_path():
    env_path = os.getenv("FINANCE_DB_PATH")
    if env_path:
        return env_path

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(backend_dir, "database", "finance_app.db")
