FROM python:3.11

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FINANCE_API_URL=http://127.0.0.1:8000

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN mkdir -p backend/database && chmod +x docker-entrypoint.sh

EXPOSE 8000 8501

ENTRYPOINT ["./docker-entrypoint.sh"]
