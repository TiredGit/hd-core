#!/bin/sh
set -e

echo "Run migrations..."
uv run alembic upgrade head

echo "Create initial admin..."
uv run python -m app.init_admin

echo "Start app..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8001