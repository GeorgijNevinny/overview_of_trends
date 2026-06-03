# Финансовый мониторинг

Небольшое приложение для просмотра цен акций и их разложения на тренд, сезонность и шум.

Бэкенд на FastAPI читает данные из SQLite и отдаёт их по API. Фронт на Streamlit показывает графики: цену и STL-разложение через statsmodels. Цены подтягиваются с Yahoo Finance через yfinance - для первой загрузки и обновлений нужен интернет.

## Что нужно

Python 3.11 или новее. Проверить версию:

```bash
python3 --version
```

Если `python3` не находится, попробуйте `python --version`.

## Как запустить

Все команды выполняйте из корня проекта, где лежат `requirements.txt`, папки `backend/` и `frontend/`.

Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

На Windows вместо `source .venv/bin/activate` используйте `.\.venv\Scripts\Activate.ps1`.

Дальше один раз подготовьте базу и скачайте цены:

```bash
python backend/scripts/init_db.py
python backend/scripts/data_fetcher.py
```

Второй шаг может занять несколько минут. Пока цены не загружены, в интерфейсе не будет списка компаний.

Запустите бэкенд в первом терминале и оставьте его открытым:

```bash
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

Во втором терминале снова перейдите в корень проекта, активируйте `.venv` и запустите фронт:

```bash
streamlit run frontend/app.py
```

Откройте в браузере адрес, который покажет Streamlit — обычно http://localhost:8501. Документация API: http://127.0.0.1:8000/docs.

Бэкенд должен работать одновременно с фронтом, иначе данные не подтянутся.

Чтобы позже обновить цены:

```bash
python backend/scripts/updater.py
```

## Настройки (если понадобятся)

По умолчанию база лежит в `backend/database/finance_app.db`, а Streamlit ходит на API по адресу `http://127.0.0.1:8000`. Это можно переопределить переменными `FINANCE_DB_PATH` и `FINANCE_API_URL`.

## Docker

Из корня репозитория:

```bash
docker build -t finance-monitor .
docker run --rm -p 8000:8000 -p 8501:8501 finance-monitor
```

При старте контейнер создаёт пустую базу, но цены нужно загрузить отдельно:

```bash
docker exec -it ИМЯ_КОНТЕЙНЕРА python backend/scripts/data_fetcher.py
```

После этого интерфейс доступен на http://localhost:8501.
