#!/bin/sh
set -e
cd /app

python backend/scripts/init_db.py

uvicorn backend.api:app --host 0.0.0.0 --port 8000 &
export FINANCE_API_URL="${FINANCE_API_URL:-http://127.0.0.1:8000}"

exec streamlit run frontend/app.py \
  --server.address=0.0.0.0 \
  --server.port=8501 \
  --server.headless=true
