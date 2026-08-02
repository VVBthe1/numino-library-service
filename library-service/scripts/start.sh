#!/bin/sh
set -e
alembic upgrade head
PYTHONPATH=/app python scripts/seed.py
python -m app.rpc.server &
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
