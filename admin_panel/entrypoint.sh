#!/bin/bash
set -e

while ! exec 6<>/dev/tcp/postgres/5432; do
  echo "Waiting for postgres..."
  sleep 1
done
echo "Postgres is available!"

echo "Running migrations..."
alembic -c /app/admin_panel/alembic.ini upgrade head

echo "Starting server..."
exec uvicorn admin_panel.main:app --host 0.0.0.0 --port 8000