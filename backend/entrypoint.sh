#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

url = os.environ["DATABASE_URL"]
for i in range(30):
    try:
        engine = create_engine(url)
        with engine.connect():
            pass
        engine.dispose()
        print("Database is reachable.")
        break
    except OperationalError as exc:
        print(f"DB not ready ({exc}), retry {i + 1}/30...")
        time.sleep(1)
else:
    raise SystemExit("Database not reachable, giving up.")
PY

echo "Running migrations..."
alembic upgrade head

echo "Seeding database..."
python -m app.db.seed

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
